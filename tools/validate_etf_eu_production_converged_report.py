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
AUTHORITY_KEYS = (
    "portfolio_mutation", "ledger_write", "funding_authority", "execution_authority",
    "activation_authority", "production_delivery_authority",
)
ALLOWED_STAGE_VALUES = {"blocked", "partially_activated", "activated"}


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def normalize_ticker(value: Any) -> str:
    ticker = str(value or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def visible_text(html: str) -> tuple[BeautifulSoup, str]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "head"]):
        tag.extract()
    return soup, " ".join(soup.get_text(" ", strip=True).split())


def text_from_pdf(path: Path) -> tuple[str, int]:
    reader = PdfReader(str(path))
    text = " ".join((page.extract_text() or "") for page in reader.pages)
    return " ".join(text.split()), len(reader.pages)


def find_row(section: Tag, *needles: str) -> Tag | None:
    values = [value for value in needles if value]
    for row in section.select("tr"):
        row_text = row.get_text(" ", strip=True)
        if any(value in row_text for value in values):
            return row
    return None


def official_positions(state: dict[str, Any]) -> list[dict[str, Any]]:
    portfolio = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    if not positions:
        raise RuntimeError("State official portfolio positions are missing")
    return positions


def position_identity(row: dict[str, Any]) -> tuple[str, str]:
    ticker = normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
    isin = str(row.get("isin") or row.get("instrument_isin") or "").strip().upper()
    return ticker, isin


def state_stage(state: dict[str, Any]) -> tuple[str, set[str], set[str]]:
    raw = state.get("stage_1_decision")
    if isinstance(raw, dict):
        value = str(raw.get("value") or raw.get("status") or "").strip()
        activated = {normalize_ticker(item) for item in raw.get("activated_tickers") or [] if normalize_ticker(item)}
        monitored = {
            normalize_ticker(item) for item in raw.get("remaining_monitored_tickers") or [] if normalize_ticker(item)
        }
    else:
        value = str(raw or "").strip()
        activated, monitored = set(), set()
    return value, activated, monitored


def promoted_identity_map(state: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for row in state.get("promoted_exposures") or []:
        if not isinstance(row, dict):
            continue
        ticker = normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
        isin = str(row.get("isin") or "").strip().upper()
        if ticker:
            result[ticker] = isin
    for row in official_positions(state):
        ticker, isin = position_identity(row)
        if ticker and isin:
            result.setdefault(ticker, isin)
    return result


def numeric_variants(value: Any) -> set[str]:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return set()
    en = f"{number:,.2f}"
    nl = en.replace(",", "X").replace(".", ",").replace("X", ".")
    return {en, nl, en.replace(",", ""), nl.replace(".", "")}


def validate_manifest_state_contract(
    manifest: dict[str, Any], state: dict[str, Any]
) -> tuple[list[str], dict[str, Any]]:
    blockers: list[str] = []
    positions = official_positions(state)
    identities = [position_identity(row) for row in positions]
    tickers = {ticker for ticker, _ in identities if ticker}
    isins = {isin for _, isin in identities if isin}
    portfolio = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    declared_count = portfolio.get("position_count")
    if declared_count != len(positions):
        blockers.append("state official position count does not match positions")

    stage, activated, monitored = state_stage(state)
    if stage not in ALLOWED_STAGE_VALUES:
        blockers.append(f"unsupported state Stage-1 decision: {stage or 'missing'}")
    if stage == "blocked" and activated:
        blockers.append("blocked state cannot contain activated tickers")
    if stage in {"partially_activated", "activated"} and not activated:
        blockers.append("activated state does not identify activated tickers")
    if activated - tickers:
        blockers.append(f"activated tickers are not funded positions: {sorted(activated - tickers)}")
    if monitored & tickers:
        blockers.append(f"monitored tickers are incorrectly funded: {sorted(monitored & tickers)}")

    if manifest.get("schema_version") != "etf_eu_production_converged_report_manifest_v1":
        blockers.append("unexpected report manifest schema")
    mode = str(manifest.get("client_renderer_mode") or "")
    if not mode:
        blockers.append("client renderer mode missing")
    if stage in {"partially_activated", "activated"} and "activated" not in mode:
        blockers.append("activated state is not rendered with an activated client mode")
    if stage == "blocked" and "activated" in mode:
        blockers.append("blocked state is rendered with an activated client mode")

    manifest_count = manifest.get("official_portfolio_position_count")
    if manifest_count != len(positions):
        blockers.append(
            f"manifest official position count mismatch: expected {len(positions)}, got {manifest_count}"
        )
    if manifest.get("stage_1_decision") != stage:
        blockers.append(
            f"manifest Stage-1 decision mismatch: expected {stage}, got {manifest.get('stage_1_decision')}"
        )

    manifest_tickers = manifest.get("official_portfolio_tickers") or manifest.get("funded_tickers")
    if manifest_tickers is not None:
        normalized = {normalize_ticker(item) for item in manifest_tickers if normalize_ticker(item)}
        if normalized != tickers:
            blockers.append(f"manifest funded ticker roster mismatch: {sorted(normalized)} != {sorted(tickers)}")
    manifest_isins = manifest.get("official_portfolio_isins") or manifest.get("funded_isins")
    if manifest_isins is not None:
        normalized_isins = {str(item).strip().upper() for item in manifest_isins if str(item).strip()}
        if normalized_isins != isins:
            blockers.append("manifest funded ISIN roster mismatch")

    intents = manifest.get("executable_trade_intents")
    if not isinstance(intents, list):
        blockers.append("manifest executable trade intents must be a list")
    elif intents:
        blockers.append("pre-send report package contains executable trade intents")

    state_authority = state.get("authority") if isinstance(state.get("authority"), dict) else {}
    manifest_authority = manifest.get("authority") if isinstance(manifest.get("authority"), dict) else {}
    for key in AUTHORITY_KEYS:
        if state_authority.get(key) is not False:
            blockers.append(f"state authority {key} must be false")
        if manifest_authority.get(key) is not False:
            blockers.append(f"manifest authority {key} must be false")

    return blockers, {
        "tickers": sorted(tickers),
        "isins": sorted(isins),
        "position_count": len(positions),
        "stage_1_decision": stage,
        "activated_tickers": sorted(activated),
        "remaining_monitored_tickers": sorted(monitored),
        "client_renderer_mode": mode,
    }


def validate_language(
    language: str,
    record: dict[str, Any],
    state: dict[str, Any],
    contract: dict[str, Any],
) -> tuple[list[str], dict[str, Any]]:
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
        blockers.append(f"{language}: production status banner missing")

    for ticker in contract["tickers"]:
        if ticker not in text:
            blockers.append(f"{language}: funded ticker missing: {ticker}")
    for isin in contract["isins"]:
        if isin and isin not in text:
            blockers.append(f"{language}: funded ISIN missing: {isin}")

    for token in PROHIBITED_VISIBLE:
        if token.casefold() in folded:
            blockers.append(f"{language}: visible internal/shadow token: {token}")
    for token in PROHIBITED_STALE:
        if token.casefold() in folded:
            blockers.append(f"{language}: stale simulated trade content: {token}")

    portfolio = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    for field in ("nav_eur", "cash_eur"):
        variants = numeric_variants(portfolio.get(field))
        if variants and not any(value in text for value in variants):
            blockers.append(f"{language}: authoritative {field} value missing")

    section_13 = soup.find("section", id="section-13")
    section_14 = soup.find("section", id="section-14")
    identity_map = promoted_identity_map(state)
    if not isinstance(section_13, Tag):
        blockers.append(f"{language}: final action section missing")
    else:
        for ticker in contract["activated_tickers"] + contract["remaining_monitored_tickers"]:
            row = find_row(section_13, ticker, identity_map.get(ticker, ""))
            if row is None:
                blockers.append(f"{language}: Stage-1 row missing for {ticker}")
                continue
            row_text = row.get_text(" ", strip=True)
            if ticker in contract["remaining_monitored_tickers"] and not re.search(r"\b0[,.]00%", row_text):
                blockers.append(f"{language}: monitored Stage-1 target is not zero for {ticker}")
            if ticker in contract["activated_tickers"]:
                percentages = [float(value.replace(",", ".")) for value in re.findall(r"(\d+[,.]\d+)%", row_text)]
                if not any(value > 0 for value in percentages):
                    blockers.append(f"{language}: activated Stage-1 target is not positive for {ticker}")

    if not isinstance(section_14, Tag):
        blockers.append(f"{language}: proposed changes section missing")
    elif section_14.find("table") is None:
        blockers.append(f"{language}: proposed changes table missing")

    pdf_text, page_count = text_from_pdf(pdf_path)
    pdf_folded = pdf_text.casefold()
    if page_count < 6 or page_count > 14:
        blockers.append(f"{language}: PDF page count outside 6-14: {page_count}")
    if expected_hero.casefold() not in pdf_folded:
        blockers.append(f"{language}: PDF hero text missing")
    for ticker in contract["tickers"]:
        if ticker.casefold() not in pdf_folded:
            blockers.append(f"{language}: PDF funded ticker missing: {ticker}")
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
    blockers, contract = validate_manifest_state_contract(manifest, state)
    details: dict[str, Any] = {"contract": contract}
    languages = manifest.get("languages") if isinstance(manifest.get("languages"), dict) else {}
    for language in ("nl", "en"):
        record = languages.get(language)
        if not isinstance(record, dict):
            blockers.append(f"manifest language missing: {language}")
            continue
        language_blockers, language_details = validate_language(language, record, state, contract)
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
        "artifact_type": "etf_eu_production_converged_report_validation_v2",
        "valid": not blockers,
        "blockers": blockers,
        "contract": details.get("contract"),
        "languages": {key: value for key, value in details.items() if key in {"nl", "en"}},
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
