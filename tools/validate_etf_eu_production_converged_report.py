from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag
from pypdf import PdfReader


REQUIRED_SECTIONS = {
    "section-1", "section-2", "section-2A", "section-3", "section-4", "section-4A",
    "section-5", "section-6", "section-7", "section-7A", "section-8", "section-9",
    "section-10", "section-11", "section-12", "section-13", "section-14", "section-15", "section-16",
}
FUNDED_TICKERS = {"VWCE", "EUNA", "SXR8"}
FUNDED_ISINS = {"IE00BK5BQT80", "IE00BDBRDM35", "IE00B5BMR087"}
STAGE_1_ISINS = {"IE00BMC38736": "L0CK", "IE00BG0J4C88": "L0CK"}
PROHIBITED_VISIBLE = (
    "schaduwrapport", "schaduwoutput", "schaduwpoort", "schaduwplan", "schaduwintentie",
    "shadow report", "shadow output", "shadow gate", "shadow plan", "shadow intent",
    "funding_authority", "execution_authority", "portfolio_mutation", "allocation_authority",
    "ai_compute_infrastructure", "cyber_security", "non_us_developed_equities",
    "agri_food_security", "defense_resilience", "grid_power",
)
PROHIBITED_STALE = (
    "156 VVSM", "995 LOCK", "995 L0CK", "VVSM/SMH", "LOCK/LOCK",
    "BUY 156", "BUY 995", "14.804530%", "10.187710%",
)


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def visible_text(html: str) -> tuple[BeautifulSoup, str]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "head"]):
        tag.extract()
    return soup, " ".join(soup.get_text(" ", strip=True).split())


def text_from_pdf(path: Path) -> tuple[str, int]:
    reader = PdfReader(str(path))
    text = " ".join((page.extract_text() or "") for page in reader.pages)
    return " ".join(text.split()), len(reader.pages)


def find_row(section: Tag, needle: str) -> Tag | None:
    for row in section.select("tbody tr"):
        if needle in row.get_text(" ", strip=True):
            return row
    return None


def validate_language(language: str, record: dict[str, Any], state: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    blockers: list[str] = []
    html_path = Path(str(record.get("html") or ""))
    pdf_path = Path(str(record.get("pdf") or ""))
    if not html_path.is_file():
        return [f"{language}: HTML missing"], {}
    if not pdf_path.is_file() or pdf_path.stat().st_size <= 0:
        return [f"{language}: PDF missing or empty"], {}

    raw_html = html_path.read_text(encoding="utf-8")
    soup, text = visible_text(raw_html)
    folded = text.casefold()
    section_ids = {str(tag.get("id")) for tag in soup.select("section[id]")}
    missing_sections = sorted(REQUIRED_SECTIONS - section_ids)
    if missing_sections:
        blockers.append(f"{language}: missing sections {missing_sections}")

    expected_hero = "Beleggersrapport" if language == "nl" else "Investor report"
    if expected_hero not in text:
        blockers.append(f"{language}: client report hero label missing")
    expected_banner = "Productiestatus:" if language == "nl" else "Production status:"
    if expected_banner not in text:
        blockers.append(f"{language}: production-convergence banner missing")

    for ticker in FUNDED_TICKERS:
        if ticker not in text:
            blockers.append(f"{language}: funded ticker missing: {ticker}")
    for isin in FUNDED_ISINS:
        if isin not in text:
            blockers.append(f"{language}: funded ISIN missing: {isin}")

    promoted = [row for row in state.get("promoted_exposures") or [] if isinstance(row, dict)]
    for row in promoted:
        isin = str(row.get("isin") or "")
        if isin and isin not in text:
            blockers.append(f"{language}: promoted candidate ISIN missing: {isin}")
    if "IE00BG0J4C88" in text and "L0CK" not in text:
        blockers.append(f"{language}: exact Xetra symbol L0CK missing")

    for token in PROHIBITED_VISIBLE:
        if token.casefold() in folded:
            blockers.append(f"{language}: visible internal/shadow token: {token}")
    for token in PROHIBITED_STALE:
        if token.casefold() in folded:
            blockers.append(f"{language}: stale simulated trade content: {token}")

    section_13 = soup.find("section", id="section-13")
    section_14 = soup.find("section", id="section-14")
    if not isinstance(section_13, Tag):
        blockers.append(f"{language}: final action section missing")
    else:
        for isin in ("IE00BMC38736", "IE00BG0J4C88"):
            row = find_row(section_13, isin)
            if row is None:
                blockers.append(f"{language}: final action row missing for {isin}")
                continue
            row_text = row.get_text(" ", strip=True).casefold()
            required = ("geblokkeerd", "cash") if language == "nl" else ("blocked", "cash")
            if not all(value in row_text for value in required):
                blockers.append(f"{language}: Stage-1 final action is not visibly blocked for {isin}")
            if not re.search(r"\b0[,.]00%", row.get_text(" ", strip=True)):
                blockers.append(f"{language}: actionable Stage-1 target is not zero for {isin}")

    if not isinstance(section_14, Tag):
        blockers.append(f"{language}: proposed changes section missing")
    else:
        section_14_text = section_14.get_text(" ", strip=True).casefold()
        required = (
            ("uitvoerbare handelsintenties: geen", "geblokkeerd", "cash aanhouden")
            if language == "nl" else
            ("executable trade intents: none", "blocked", "retain cash")
        )
        for value in required:
            if value not in section_14_text:
                blockers.append(f"{language}: no-trade decision surface missing: {value}")
        if section_14.select_one("table.production-decision-table") is None:
            blockers.append(f"{language}: production decision table missing")

    pdf_text, page_count = text_from_pdf(pdf_path)
    pdf_folded = pdf_text.casefold()
    if page_count < 6 or page_count > 14:
        blockers.append(f"{language}: PDF page count outside 6-14: {page_count}")
    if expected_hero.casefold() not in pdf_folded:
        blockers.append(f"{language}: PDF hero text missing")
    for token in PROHIBITED_VISIBLE:
        if token.casefold() in pdf_folded:
            blockers.append(f"{language}: PDF visible internal/shadow token: {token}")
    for token in PROHIBITED_STALE:
        if token.casefold() in pdf_folded:
            blockers.append(f"{language}: PDF stale simulated trade content: {token}")

    return blockers, {
        "html": str(html_path),
        "pdf": str(pdf_path),
        "page_count": page_count,
        "section_count": len(section_ids),
        "visible_text_length": len(text),
        "pdf_text_length": len(pdf_text),
    }


def validate(manifest: dict[str, Any], state: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    blockers: list[str] = []
    if manifest.get("schema_version") != "etf_eu_production_converged_report_manifest_v1":
        blockers.append("unexpected report manifest schema")
    if manifest.get("client_renderer_mode") != "synchronized_premium_production_candidate":
        blockers.append("unexpected client renderer mode")
    if manifest.get("official_portfolio_position_count") != 3:
        blockers.append("manifest official position count must be three")
    if manifest.get("stage_1_decision") != "blocked":
        blockers.append("manifest Stage-1 decision must be blocked")
    if manifest.get("executable_trade_intents") != []:
        blockers.append("manifest executable trade intents must be empty")
    authority = manifest.get("authority") if isinstance(manifest.get("authority"), dict) else {}
    for key in (
        "portfolio_mutation", "ledger_write", "funding_authority", "execution_authority",
        "activation_authority", "production_delivery_authority",
    ):
        if authority.get(key) is not False:
            blockers.append(f"manifest authority {key} must be false")

    details: dict[str, Any] = {}
    languages = manifest.get("languages") if isinstance(manifest.get("languages"), dict) else {}
    for language in ("nl", "en"):
        record = languages.get(language)
        if not isinstance(record, dict):
            blockers.append(f"manifest language missing: {language}")
            continue
        language_blockers, language_details = validate_language(language, record, state)
        blockers.extend(language_blockers)
        details[language] = language_details
    return blockers, details


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = load(args.manifest)
    state = load(args.state)
    blockers, details = validate(manifest, state)
    result = {
        "artifact_type": "etf_eu_production_converged_report_validation",
        "valid": not blockers,
        "blockers": blockers,
        "languages": details,
        "funded_position_count": state.get("official_portfolio", {}).get("position_count"),
        "promoted_exposure_count": len(state.get("promoted_exposures") or []),
        "stage_1_decision": state.get("stage_1_decision", {}).get("value"),
    }
    text = json.dumps(result, indent=2, ensure_ascii=False)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
