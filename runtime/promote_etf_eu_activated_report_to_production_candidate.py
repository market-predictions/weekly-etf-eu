from __future__ import annotations

import argparse
import copy
import json
import re
import tempfile
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, NavigableString, Tag
from weasyprint import HTML

from runtime import promote_etf_eu_sister_report_to_production_candidate as legacy

EXPECTED_FUNDED = {"VWCE", "EUNA", "SXR8", "L0CK"}
STAGE1_ROWS = {
    "L0CK": "IE00BG0J4C88",
    "VVSM": "IE00BMC38736",
}


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def normalize_ticker(value: Any) -> str:
    ticker = str(value or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def validate_activated_state(state: dict[str, Any]) -> None:
    if state.get("schema_version") != "etf_eu_production_convergence_state_v1":
        raise RuntimeError("Invalid production-convergence state")
    portfolio = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    funded = {
        normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
        for row in positions
        if normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
    }
    if funded != EXPECTED_FUNDED or portfolio.get("position_count") != 4:
        raise RuntimeError(f"Activated promoter funded set mismatch: {sorted(funded)}")
    if portfolio.get("model_portfolio_only") is not True or portfolio.get("real_broker_execution") is not False:
        raise RuntimeError("Activated promoter model-only authority boundary is invalid")
    activation = portfolio.get("last_model_capital_activation") or state.get("model_capital_activation") or {}
    if not activation.get("activation_id"):
        raise RuntimeError("Activated promoter provenance is missing")
    stage = state.get("stage_1_decision") if isinstance(state.get("stage_1_decision"), dict) else {}
    if stage.get("value") != "partially_activated":
        raise RuntimeError("Activated promoter requires partially_activated Stage-1 state")
    if {normalize_ticker(value) for value in stage.get("activated_tickers") or []} != {"L0CK"}:
        raise RuntimeError("Activated promoter requires L0CK activation scope")
    if {normalize_ticker(value) for value in stage.get("remaining_monitored_tickers") or []} != {"VVSM"}:
        raise RuntimeError("Activated promoter requires VVSM monitoring scope")
    if stage.get("executable_trade_intents") != []:
        raise RuntimeError("Activated promoter requires empty executable trade intents")


def replace_section(target: BeautifulSoup, source: BeautifulSoup, section_id: str) -> None:
    source_section = source.find("section", id=section_id)
    target_section = target.find("section", id=section_id)
    if not isinstance(source_section, Tag) or not isinstance(target_section, Tag):
        raise RuntimeError(f"Activated promoter section missing: {section_id}")
    replacement = BeautifulSoup(str(source_section), "html.parser").find("section")
    if not isinstance(replacement, Tag):
        raise RuntimeError(f"Activated promoter section clone failed: {section_id}")
    target_section.replace_with(replacement)


def replace_row_text(row: Tag, replacements: tuple[tuple[str, str], ...]) -> None:
    for node in list(row.find_all(string=True)):
        if not isinstance(node, NavigableString):
            continue
        original = str(node)
        updated = original
        for pattern, replacement in replacements:
            updated = re.sub(pattern, replacement, updated, flags=re.IGNORECASE)
        if updated != original:
            node.replace_with(updated)


def append_row_note(soup: BeautifulSoup, row: Tag, text: str, css_class: str) -> None:
    cells = row.find_all("td", recursive=False)
    target = cells[-1] if cells else row
    note = soup.new_tag("span", attrs={"class": css_class})
    note.string = text
    target.append(" ")
    target.append(note)


def synchronize_stage1_action_rows(
    soup: BeautifulSoup,
    state: dict[str, Any],
    language: str,
) -> None:
    section = soup.find("section", id="section-13")
    if not isinstance(section, Tag):
        raise RuntimeError("Activated promoter Section 13 missing")
    stage = state.get("stage_1_decision") if isinstance(state.get("stage_1_decision"), dict) else {}
    activated = {normalize_ticker(value) for value in stage.get("activated_tickers") or []}
    monitored = {normalize_ticker(value) for value in stage.get("remaining_monitored_tickers") or []}

    for ticker, isin in STAGE1_ROWS.items():
        row = next(
            (candidate for candidate in section.select("tbody tr") if isin in candidate.get_text(" ", strip=True)),
            None,
        )
        if not isinstance(row, Tag):
            raise RuntimeError(f"Activated promoter final-action row missing: {ticker}")

        if ticker in activated:
            replacements = (
                (
                    (r"\bgeblokkeerd\b", "actief"),
                    (r"\bblocked\b", "actief"),
                    (r"cash aanhouden", "modelpositie actief"),
                    (r"retain cash", "modelpositie actief"),
                    (r"geen activering", "modelpositie actief"),
                    (r"not activated", "modelpositie actief"),
                )
                if language == "nl"
                else (
                    (r"\bblocked\b", "active"),
                    (r"\bgeblokkeerd\b", "active"),
                    (r"retain cash", "model position active"),
                    (r"cash aanhouden", "model position active"),
                    (r"not activated", "model position active"),
                    (r"geen activering", "model position active"),
                )
            )
            replace_row_text(row, replacements)
            row_text = row.get_text(" ", strip=True).casefold()
            required = ("actief", "model") if language == "nl" else ("active", "model")
            if not all(token in row_text for token in required):
                append_row_note(
                    soup,
                    row,
                    "Modelpositie actief" if language == "nl" else "Model position active",
                    "activated-final-action-note",
                )
            row_text = row.get_text(" ", strip=True).casefold()
            if "blocked" in row_text or "geblokkeerd" in row_text:
                raise RuntimeError(f"Activated final-action row still blocked: {ticker}")

        elif ticker in monitored:
            replacements = (
                (
                    (r"\bactief\b", "geblokkeerd"),
                    (r"\bactive\b", "geblokkeerd"),
                    (r"modelpositie actief", "geblokkeerd · cash aanhouden · doel 0,00%"),
                    (r"model position active", "geblokkeerd · cash aanhouden · doel 0,00%"),
                )
                if language == "nl"
                else (
                    (r"\bactive\b", "blocked"),
                    (r"\bactief\b", "blocked"),
                    (r"model position active", "blocked · retain cash · target 0.00%"),
                    (r"modelpositie actief", "blocked · retain cash · target 0.00%"),
                )
            )
            replace_row_text(row, replacements)
            row_text = row.get_text(" ", strip=True).casefold()
            required = ("geblokkeerd", "cash") if language == "nl" else ("blocked", "cash")
            zero_target = bool(re.search(r"\b0[,.]00%", row.get_text(" ", strip=True)))
            if not all(token in row_text for token in required) or not zero_target:
                append_row_note(
                    soup,
                    row,
                    (
                        "Geblokkeerd · cash aanhouden · doel 0,00%"
                        if language == "nl"
                        else "Blocked · retain cash · target 0.00%"
                    ),
                    "monitored-final-action-note",
                )
            row_text = row.get_text(" ", strip=True).casefold()
            if not all(token in row_text for token in required):
                raise RuntimeError(f"Monitored final-action row lacks blocked/cash status: {ticker}")


def patch_client_copy(soup: BeautifulSoup, language: str) -> None:
    notice = soup.select_one(".notice")
    if not isinstance(notice, Tag):
        raise RuntimeError("Client notice missing")
    notice.string = (
        "Dit rapport is informatief en educatief. De modelportefeuille bevat vier posities. L0CK is als modelpositie geactiveerd; VVSM blijft gemonitord. Er is geen echte brokerorder uitgevoerd."
        if language == "nl"
        else "This report is informational and educational. The model portfolio contains four positions. L0CK is active as a model position; VVSM remains monitored. No real broker order was placed."
    )
    banner = soup.select_one(".production-convergence-banner")
    if isinstance(banner, Tag):
        banner.string = (
            "Productiestatus: premium clientrapport · vier modelposities · L0CK actief · VVSM gemonitord · geen echte brokerorder."
            if language == "nl"
            else "Production status: premium client report · four model positions · L0CK active · VVSM monitored · no real broker order."
        )
    replacements = (
        {
            "officiële portefeuille ongewijzigd": "modelportefeuille met vier posities",
            "geen nieuwe transactie": "geen echte brokerorder",
            "drie posities": "vier posities",
            "nieuwe inzet blijft geblokkeerd": "VVSM blijft gemonitord",
        }
        if language == "nl"
        else {
            "official portfolio unchanged": "four-position model portfolio",
            "no new trade": "no real broker order",
            "three positions": "four positions",
            "new deployment remains blocked": "VVSM remains monitored",
        }
    )
    for node in list(soup.find_all(string=True)):
        parent_name = getattr(node.parent, "name", "")
        if parent_name in {"script", "style", "head"}:
            continue
        text = str(node)
        updated = text
        for old, new in replacements.items():
            updated = updated.replace(old, new)
        updated = re.sub(
            r"\bschaduwpoort\b",
            "modelbeoordelingspoort",
            updated,
            flags=re.IGNORECASE,
        )
        updated = re.sub(
            r"\bshadow[ -]gate\b",
            "model review gate",
            updated,
            flags=re.IGNORECASE,
        )
        if updated != text:
            node.replace_with(updated)


def promote(source_manifest: Path, state_path: Path, output_dir: Path) -> Path:
    source = load_object(source_manifest)
    state = load_object(state_path)
    validate_activated_state(state)

    compatibility = copy.deepcopy(state)
    compatibility_stage = compatibility.setdefault("stage_1_decision", {})
    compatibility_stage.update(
        {
            "value": "blocked",
            "status": "blocked_not_activation_ready",
            "stage_1_activation_authorized": False,
            "official_state_applied": False,
            "executable_trade_intents": [],
        }
    )
    with tempfile.TemporaryDirectory(prefix="etf_eu_activated_promoter_") as temp_dir:
        temp_state = Path(temp_dir) / "compatibility_state.json"
        temp_state.write_text(json.dumps(compatibility, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        manifest_path = legacy.promote(source_manifest, temp_state, output_dir)

    manifest = load_object(manifest_path)
    for language in ("nl", "en"):
        source_record = (source.get("languages") or {}).get(language) or {}
        output_record = (manifest.get("languages") or {}).get(language) or {}
        source_html = Path(str(source_record.get("html") or ""))
        output_html = Path(str(output_record.get("html") or ""))
        output_pdf = Path(str(output_record.get("pdf") or ""))
        if not source_html.exists() or not output_html.exists():
            raise RuntimeError(f"Activated promoter language files missing: {language}")
        source_soup = BeautifulSoup(source_html.read_text(encoding="utf-8"), "html.parser")
        output_soup = BeautifulSoup(output_html.read_text(encoding="utf-8"), "html.parser")
        replace_section(output_soup, source_soup, "section-2")
        replace_section(output_soup, source_soup, "section-13")
        replace_section(output_soup, source_soup, "section-14")
        synchronize_stage1_action_rows(output_soup, state, language)
        patch_client_copy(output_soup, language)
        rendered = str(output_soup)
        output_html.write_text(rendered, encoding="utf-8")
        HTML(string=rendered, base_url=str(output_html.parent.resolve())).write_pdf(str(output_pdf))
        output_record["activated_production_promotion"] = "l0ck_funded_vvsm_monitored_v3"

    portfolio = state["official_portfolio"]
    manifest.update(
        {
            "production_convergence_state": str(state_path),
            "client_renderer_mode": "activated_four_position_premium_production_candidate",
            "official_portfolio_position_count": 4,
            "stage_1_decision": "partially_activated",
            "activated_tickers": ["L0CK"],
            "remaining_monitored_tickers": ["VVSM"],
            "model_portfolio_only": True,
            "real_broker_execution": False,
            "executable_trade_intents": [],
            "activation_id": (portfolio.get("last_model_capital_activation") or {}).get("activation_id"),
            "authority": dict(state.get("authority") or {}),
        }
    )
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(manifest_path)
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Promote activated ETF EU report to client-facing production candidate")
    parser.add_argument("source_manifest", type=Path)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    promote(args.source_manifest, args.state, args.output_dir)


if __name__ == "__main__":
    main()
