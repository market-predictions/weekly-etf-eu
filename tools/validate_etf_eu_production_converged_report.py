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
STAGE_1_ISINS = {
    "IE00BMC38736": "VVSM",
    "IE00BG0J4C88": "L0CK",
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
ALLOWED_MODES = {
    "blocked": {
        "renderer": "synchronized_premium_production_candidate",
        "position_count": 3,
    },
    "partially_activated": {
        "renderer": "activated_four_position_premium_production_candidate",
        "position_count": 4,
    },
}


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


def find_row(section: Tag, needle: str) -> Tag | None:
    for row in section.select("tbody tr"):
        if needle in row.get_text(" ", strip=True):
            return row
    return None


def state_contract(state: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    blockers: list[str] = []
    portfolio = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    funded_tickers = {
        normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
        for row in positions
        if normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
    }
    funded_isins = {str(row.get("isin") or "").strip() for row in positions if str(row.get("isin") or "").strip()}
    declared_count = portfolio.get("position_count")
    if declared_count != len(positions):
        blockers.append(f"state official position count mismatch: declared={declared_count} actual={len(positions)}")

    stage = state.get("stage_1_decision") if isinstance(state.get("stage_1_decision"), dict) else {}
    stage_value = str(stage.get("value") or "").strip()
    mode = ALLOWED_MODES.get(stage_value)
    if mode is None:
        blockers.append(f"unsupported Stage-1 decision: {stage_value!r}")
        mode = {}
    elif declared_count != mode["position_count"]:
        blockers.append(
            f"state position count {declared_count!r} is incompatible with Stage-1 mode {stage_value!r}"
        )

    activated = {normalize_ticker(value) for value in stage.get("activated_tickers") or [] if normalize_ticker(value)}
    monitored = {
        normalize_ticker(value)
        for value in stage.get("remaining_monitored_tickers") or []
        if normalize_ticker(value)
    }
    if stage_value == "blocked" and activated:
        blockers.append("blocked Stage-1 state may not contain activated tickers")
    if stage_value == "partially_activated":
        if not activated:
            blockers.append("partially activated Stage-1 state requires activated tickers")
        if not activated.issubset(funded_tickers):
            blockers.append(
                f"activated tickers are not funded: {sorted(activated - funded_tickers)}"
            )
        if portfolio.get("model_portfolio_only") is not True:
            blockers.append("activated portfolio must remain model-only")
        if portfolio.get("real_broker_execution") is not False:
            blockers.append("activated portfolio must not imply real broker execution")
        activation = portfolio.get("last_model_capital_activation") or state.get("model_capital_activation") or {}
        if not isinstance(activation, dict) or not activation.get("activation_id"):
            blockers.append("activated portfolio provenance is missing")

    executable = stage.get("executable_trade_intents")
    if executable is None:
        executable = []
    if not isinstance(executable, list):
        blockers.append("Stage-1 executable trade intents must be a list")
        executable = []

    authority = state.get("authority") if isinstance(state.get("authority"), dict) else {}
    for key in (
        "portfolio_mutation", "ledger_write", "funding_authority", "execution_authority",
        "activation_authority", "production_delivery_authority",
    ):
        if authority.get(key) is not False:
            blockers.append(f"state authority {key} must be false for report generation")

    return blockers, {
        "portfolio": portfolio,
        "funded_tickers": funded_tickers,
        "funded_isins": funded_isins,
        "position_count": declared_count,
        "stage_value": stage_value,
        "renderer_mode": mode.get("renderer"),
        "activated_tickers": activated,
        "monitored_tickers": monitored,
        "executable_trade_intents": executable,
        "authority": authority,
    }


def validate_manifest_state(
    manifest: dict[str, Any],
    state: dict[str, Any],
) -> tuple[list[str], dict[str, Any]]:
    blockers, contract = state_contract(state)
    if manifest.get("schema_version") != "etf_eu_production_converged_report_manifest_v1":
        blockers.append("unexpected report manifest schema")
    if manifest.get("client_renderer_mode") != contract.get("renderer_mode"):
        blockers.append(
            "manifest renderer mode does not match authoritative Stage-1 state: "
            f"expected={contract.get('renderer_mode')!r} actual={manifest.get('client_renderer_mode')!r}"
        )
    if manifest.get("official_portfolio_position_count") != contract.get("position_count"):
        blockers.append("manifest official position count does not match state")
    if manifest.get("stage_1_decision") != contract.get("stage_value"):
        blockers.append("manifest Stage-1 decision does not match state")
    manifest_activated = {
        normalize_ticker(value) for value in manifest.get("activated_tickers") or [] if normalize_ticker(value)
    }
    manifest_monitored = {
        normalize_ticker(value)
        for value in manifest.get("remaining_monitored_tickers") or []
        if normalize_ticker(value)
    }
    if manifest_activated != contract.get("activated_tickers"):
        blockers.append(
            f"manifest activated ticker scope mismatch: expected={sorted(contract.get('activated_tickers') or [])} "
            f"actual={sorted(manifest_activated)}"
        )
    if manifest_monitored != contract.get("monitored_tickers"):
        blockers.append(
            f"manifest monitored ticker scope mismatch: expected={sorted(contract.get('monitored_tickers') or [])} "
            f"actual={sorted(manifest_monitored)}"
        )
    if manifest.get("executable_trade_intents") != contract.get("executable_trade_intents"):
        blockers.append("manifest executable trade intents do not match state")
    if manifest.get("model_portfolio_only") not in (None, contract["portfolio"].get("model_portfolio_only")):
        blockers.append("manifest model-only flag does not match state")
    if manifest.get("real_broker_execution") not in (None, contract["portfolio"].get("real_broker_execution")):
        blockers.append("manifest broker-execution flag does not match state")

    manifest_authority = manifest.get("authority") if isinstance(manifest.get("authority"), dict) else {}
    for key, expected in contract.get("authority", {}).items():
        if key in {
            "portfolio_mutation", "ledger_write", "funding_authority", "execution_authority",
            "activation_authority", "production_delivery_authority",
        } and manifest_authority.get(key) is not expected:
            blockers.append(f"manifest authority {key} does not match state")
    return blockers, contract


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
        blockers.append(f"{language}: production-convergence banner missing")

    for ticker in sorted(contract.get("funded_tickers") or []):
        if ticker not in text:
            blockers.append(f"{language}: funded ticker missing: {ticker}")
    for isin in sorted(contract.get("funded_isins") or []):
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

    stage_value = contract.get("stage_value")
    activated = set(contract.get("activated_tickers") or set())
    monitored = set(contract.get("monitored_tickers") or set())
    section_13 = soup.find("section", id="section-13")
    section_14 = soup.find("section", id="section-14")
    if not isinstance(section_13, Tag):
        blockers.append(f"{language}: final action section missing")
    else:
        for isin, ticker in STAGE_1_ISINS.items():
            row = find_row(section_13, isin)
            if row is None:
                blockers.append(f"{language}: final action row missing for {isin}")
                continue
            row_text = row.get_text(" ", strip=True).casefold()
            if ticker in activated:
                required = ("actief", "model") if language == "nl" else ("active", "model")
                if not all(value in row_text for value in required):
                    blockers.append(f"{language}: activated Stage-1 row is not visibly active for {ticker}")
                if "geblokkeerd" in row_text or "blocked" in row_text:
                    blockers.append(f"{language}: activated Stage-1 row is still visibly blocked for {ticker}")
            else:
                required = ("geblokkeerd", "cash") if language == "nl" else ("blocked", "cash")
                if not all(value in row_text for value in required):
                    blockers.append(f"{language}: monitored Stage-1 row is not visibly blocked for {ticker}")
                if not re.search(r"\b0[,.]00%", row.get_text(" ", strip=True)):
                    blockers.append(f"{language}: monitored Stage-1 target is not zero for {ticker}")

    if not isinstance(section_14, Tag):
        blockers.append(f"{language}: proposed changes section missing")
    else:
        section_14_text = section_14.get_text(" ", strip=True).casefold()
        if stage_value == "blocked":
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
        else:
            required = (
                ("l0ck", "vvsm", "model", "geen echte brokerorder")
                if language == "nl" else
                ("l0ck", "vvsm", "model", "no real broker order")
            )
            for value in required:
                if value not in section_14_text and value not in folded:
                    blockers.append(f"{language}: activated model decision surface missing: {value}")
            if soup.select_one(".activated-allocation-status") is None:
                blockers.append(f"{language}: activated allocation status box missing")

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
        "stage_1_mode": stage_value,
        "funded_tickers": sorted(contract.get("funded_tickers") or []),
    }


def validate(manifest: dict[str, Any], state: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    blockers, contract = validate_manifest_state(manifest, state)
    details: dict[str, Any] = {
        "contract": {
            "position_count": contract.get("position_count"),
            "stage_1_decision": contract.get("stage_value"),
            "renderer_mode": contract.get("renderer_mode"),
            "funded_tickers": sorted(contract.get("funded_tickers") or []),
            "activated_tickers": sorted(contract.get("activated_tickers") or []),
            "monitored_tickers": sorted(contract.get("monitored_tickers") or []),
        }
    }
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
    contract = details.get("contract", {})
    result = {
        "artifact_type": "etf_eu_production_converged_report_validation",
        "valid": not blockers,
        "blockers": blockers,
        "languages": {key: value for key, value in details.items() if key in {"nl", "en"}},
        "funded_position_count": contract.get("position_count"),
        "funded_tickers": contract.get("funded_tickers"),
        "activated_tickers": contract.get("activated_tickers"),
        "remaining_monitored_tickers": contract.get("monitored_tickers"),
        "stage_1_decision": contract.get("stage_1_decision"),
        "renderer_mode": contract.get("renderer_mode"),
        "promoted_exposure_count": len(state.get("promoted_exposures") or []),
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
