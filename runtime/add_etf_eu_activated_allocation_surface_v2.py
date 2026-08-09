from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, NavigableString, Tag
from weasyprint import HTML

from runtime import add_etf_eu_activated_allocation_surface as legacy
from runtime.synchronize_etf_eu_activated_front_page import synchronize_manifest

FINAL_PROMOTION_SECTION_SYNC_REQUIRED = "section-13:activated-L0CK:blocked-VVSM:client-safe"
FRONT_PAGE_STATE_SYNC_REQUIRED = "section-1+section-2+section-2A+section-4:authoritative-four-position:L0CK-active:v3"


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def normalize_ticker(value: Any) -> str:
    ticker = str(value or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def current_report_date(argv: list[str]) -> str:
    if "--report-date" not in argv:
        raise RuntimeError("Activated allocation surface requires --report-date")
    index = argv.index("--report-date")
    if index + 1 >= len(argv):
        raise RuntimeError("Activated allocation surface report date value is missing")
    return argv[index + 1]


def argument_value(argv: list[str], flag: str) -> str:
    if flag not in argv:
        raise RuntimeError(f"Activated allocation surface requires {flag}")
    index = argv.index(flag)
    if index + 1 >= len(argv):
        raise RuntimeError(f"Activated allocation surface value is missing for {flag}")
    return argv[index + 1]


def discover_activated_state(report_date: str) -> Path:
    candidates: list[tuple[float, Path]] = []
    for path in Path("output/routine_preview").glob("etf_eu_production_convergence_state_*.json"):
        try:
            payload = load_object(path)
        except Exception:
            continue
        if str(payload.get("report_date") or "") != report_date:
            continue
        portfolio = payload.get("official_portfolio") if isinstance(payload.get("official_portfolio"), dict) else {}
        positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
        tickers = {
            normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
            for row in positions
            if normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
        }
        activation = portfolio.get("last_model_capital_activation") or payload.get("model_capital_activation") or {}
        if tickers != {"VWCE", "EUNA", "SXR8", "L0CK"}:
            continue
        if not activation.get("activation_id"):
            continue
        stage = payload.get("stage_1_decision") if isinstance(payload.get("stage_1_decision"), dict) else {}
        if stage.get("value") != "partially_activated":
            continue
        candidates.append((path.stat().st_mtime, path))
    if not candidates:
        raise RuntimeError(f"No activated four-position convergence state found for {report_date}")
    candidates.sort(key=lambda item: item[0])
    selected = candidates[-1][1]
    print(f"ETF_EU_ACTIVATED_STATE_SELECTED | report_date={report_date} | state={selected}")
    return selected


def _position_rows(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    portfolio = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    return {
        normalize_ticker(row.get("ticker") or row.get("exchange_ticker")): row
        for row in portfolio.get("positions") or []
        if isinstance(row, dict) and normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
    }


def _replace_position_count_copy(section: Tag, position_count: int, language: str) -> None:
    replacements = (
        (
            (r"\bthree official positions\b", f"{position_count} official positions"),
            (r"\b3 official positions\b", f"{position_count} official positions"),
        )
        if language == "en"
        else (
            (r"\bdrie officiële posities\b", f"{position_count} officiële posities"),
            (r"\b3 officiële posities\b", f"{position_count} officiële posities"),
        )
    )
    for node in list(section.find_all(string=True)):
        if not isinstance(node, NavigableString):
            continue
        original = str(node)
        updated = original
        for pattern, replacement in replacements:
            updated = re.sub(pattern, replacement, updated, flags=re.IGNORECASE)
        if updated != original:
            node.replace_with(updated)


def _dedupe_funded_action_rows(section: Tag, positions: dict[str, dict[str, Any]], language: str) -> None:
    for ticker, position in positions.items():
        rows = [
            row
            for row in section.select("tbody tr")
            if ticker.casefold() in row.get_text(" ", strip=True).casefold()
        ]
        if len(rows) <= 1:
            continue
        weight = position.get("current_weight_pct")
        if weight is None:
            weight = position.get("weight_pct")
        if weight is None:
            raise RuntimeError(f"Cannot supersede duplicate {ticker} action rows without authoritative weight")
        authoritative_weight = legacy.pct(weight, language).casefold()
        matches = [row for row in rows if authoritative_weight in row.get_text(" ", strip=True).casefold()]
        if len(matches) != 1:
            raise RuntimeError(
                f"Expected exactly one authoritative {ticker} action row at {authoritative_weight}; found {len(matches)}"
            )
        keeper = matches[0]
        for row in rows:
            if row is not keeper:
                row.decompose()


def _retire_shadow_policy_controls(section: Tag, language: str) -> None:
    markers = (
        "fixed 50%",
        "minimum cash 35",
        "maximum new etf 15",
        "minimale cash 35",
        "maximale nieuwe etf 15",
    )
    for row in list(section.select("tr")):
        text = row.get_text(" ", strip=True).casefold()
        if any(marker in text for marker in markers):
            row.decompose()

    replacement = (
        "Allocation authority follows ETF_EU_RELEASE_LINEAGE_POLICY_V2 and the current protected portfolio state; no universal position cap or cash floor is asserted here."
        if language == "en"
        else "Allocatiebevoegdheid volgt ETF_EU_RELEASE_LINEAGE_POLICY_V2 en de actuele beschermde portefeuillestatus; hier wordt geen universele positielimiet of cashvloer gesteld."
    )
    for node in list(section.find_all(string=True)):
        if not isinstance(node, NavigableString):
            continue
        original = str(node)
        if any(marker in original.casefold() for marker in markers):
            node.replace_with(replacement)


def _enforce_authoritative_client_surface(soup: BeautifulSoup, state: dict[str, Any], language: str) -> None:
    positions = _position_rows(state)
    if not positions:
        raise RuntimeError("Authoritative portfolio positions missing for client-surface supersession")

    section_6 = soup.find("section", id="section-6")
    section_13 = soup.find("section", id="section-13")
    section_14 = soup.find("section", id="section-14")
    if not all(isinstance(section, Tag) for section in (section_6, section_13, section_14)):
        raise RuntimeError("Client-surface supersession requires Sections 6, 13 and 14")

    _replace_position_count_copy(section_6, len(positions), language)
    _dedupe_funded_action_rows(section_13, positions, language)
    _retire_shadow_policy_controls(section_14, language)

    visible = " ".join(section.get_text(" ", strip=True) for section in (section_6, section_13, section_14)).casefold()
    forbidden = (
        "three official positions",
        "3 official positions",
        "drie officiële posities",
        "3 officiële posities",
        "fixed 50%",
        "minimum cash 35",
        "maximum new etf 15",
        "minimale cash 35",
        "maximale nieuwe etf 15",
    )
    remaining = [marker for marker in forbidden if marker in visible]
    if remaining:
        raise RuntimeError(f"Stale client-surface fragments remain after authoritative supersession: {remaining}")

    for ticker in positions:
        rows = [
            row
            for row in section_13.select("tbody tr")
            if ticker.casefold() in row.get_text(" ", strip=True).casefold()
        ]
        if len(rows) > 1:
            raise RuntimeError(f"Duplicate funded action rows remain for {ticker}: {len(rows)}")


def _supersede_manifest_client_surface(manifest_path: Path, state_path: Path) -> None:
    state = load_object(state_path)
    manifest = load_object(manifest_path)
    languages = manifest.get("languages") if isinstance(manifest.get("languages"), dict) else {}
    for language in ("nl", "en"):
        record = languages.get(language) if isinstance(languages.get(language), dict) else {}
        html_value = record.get("html")
        pdf_value = record.get("pdf")
        if not html_value or not pdf_value:
            raise RuntimeError(f"Manifest is missing {language} HTML/PDF paths for client-surface supersession")
        html_path = Path(html_value)
        pdf_path = Path(pdf_value)
        soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
        _enforce_authoritative_client_surface(soup, state, language)
        html_path.write_text(str(soup), encoding="utf-8")
        HTML(filename=str(html_path), base_url=str(html_path.parent.resolve())).write_pdf(str(pdf_path))
        record["client_surface_supersession"] = "authoritative_v3"

    manifest["client_surface_supersession"] = {
        "applied": True,
        "authority": "protected_portfolio_state",
        "portfolio_mutation": False,
        "trade_ledger_mutation": False,
        "real_broker_execution": False,
        "production_delivery_authority": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    argv = list(sys.argv)
    if len(argv) < 2 or argv[1].startswith("-"):
        raise RuntimeError("Activated allocation surface requires manifest path as first argument")
    manifest_path = Path(argv[1])
    if "--state" not in argv:
        report_date = current_report_date(argv)
        state_path = discover_activated_state(report_date)
        argv.extend(["--state", str(state_path)])
        sys.argv = argv
    else:
        state_path = Path(argument_value(argv, "--state"))

    legacy.main()
    _supersede_manifest_client_surface(manifest_path, state_path)
    synchronize_manifest(manifest_path, state_path)


if __name__ == "__main__":
    main()
