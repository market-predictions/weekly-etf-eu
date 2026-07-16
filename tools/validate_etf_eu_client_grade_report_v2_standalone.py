from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SECTIONS = {
    "nl": [
        "Besliscockpit", "Portefeuille en kapitaal", "Regime- en beleidsdashboard",
        "Structurele UCITS-kansenradar", "Belangrijkste risico’s en invalidaties",
        "Portefeuilleontwikkeling", "Conclusie", "Allocatiekaart", "Tweede-orde-effecten",
        "UCITS-kandidaten en prijsbewijs", "Verificatiefunnel", "Review huidige posities",
        "Vervanging, rotatie en vermijdingsradar", "Input voor de volgende run", "Disclaimer",
    ],
    "en": [
        "Decision cockpit", "Portfolio and capital", "Regime and policy dashboard",
        "Structural UCITS opportunity radar", "Key risks and invalidations",
        "Portfolio development", "Conclusion", "Allocation map", "Second-order effects",
        "UCITS candidates and pricing evidence", "Verification funnel", "Current-position review",
        "Replacement, rotation and avoidance radar", "Input for the next run", "Disclaimer",
    ],
}

FORBIDDEN = [
    "valuation_grade=", "funding_authority=", "portfolio_mutation=",
    "production_delivery_authority=", "candidate_requires_verification",
    "verified_ucits_trading_line", "priced_non_authoritative", "fetch_failed",
    "funded_model_position_active", "```", "|---|",
]

NL_FORBIDDEN = [
    "refresh macro policy pack", "verify broker availability", "strengthen pricing source agreement",
    "take a separate allocation decision before funding", "Inverse of leveraged producten",
]

FUNDED_STALE = {
    "nl": [
        "Eerste modelpositie actief",
        "eerste modelaankoop uitgevoerd",
        "VWCE-capaciteit blijft cash totdat de exacte handelslijn is geverifieerd",
        "EUNA, SXRV en semiconductorblootstelling blijven geblokkeerd",
        "Bevestig brokerbeschikbaarheid",
        "Geen inzet vóór identiteit, KID, broker en lijn zijn bevestigd",
    ],
    "en": [
        "First model position active",
        "first model purchase executed",
        "VWCE capacity remains cash until the exact trading line is verified",
        "EUNA, SXRV and semiconductor exposure remain blocked",
        "Confirm broker availability",
        "No allocation before identity, KID, broker and trading line are confirmed",
    ],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_text(path: Path) -> str:
    if not path.exists():
        raise RuntimeError(f"Missing artifact: {path}")
    return path.read_text(encoding="utf-8")


def pdf_text(path: Path) -> str:
    return subprocess.run(["pdftotext", "-layout", str(path), "-"], check=True, text=True, capture_output=True).stdout


def page_count(path: Path) -> int:
    raw = subprocess.run(["pdfinfo", str(path)], check=True, text=True, capture_output=True).stdout
    match = re.search(r"^Pages:\s+(\d+)\s*$", raw, flags=re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not determine page count: {path}")
    return int(match.group(1))


def ticker_of(row: dict[str, Any]) -> str:
    return str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()


def funded_state_blockers(state: dict[str, Any]) -> list[str]:
    portfolio = state.get("portfolio") if isinstance(state.get("portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    if not positions:
        return []

    blockers: list[str] = []
    funded_tickers = {ticker_of(row) for row in positions if ticker_of(row)}
    consistency = state.get("funded_consistency") if isinstance(state.get("funded_consistency"), dict) else {}
    if consistency.get("position_count") != len(positions):
        blockers.append("funded consistency position count mismatch")
    for key in ["allocation_map_reconciled", "opportunity_radar_reconciled", "broker_neutral_model_language"]:
        if consistency.get(key) is not True:
            blockers.append(f"funded consistency flag missing: {key}")
    if set(consistency.get("funded_tickers") or []) != funded_tickers:
        blockers.append("funded consistency ticker set mismatch")

    for lane in state.get("opportunity_radar") or []:
        if not isinstance(lane, dict):
            continue
        lane_tickers = {str(value).strip().upper() for value in (lane.get("candidate_tickers") or lane.get("tickers") or [])}
        active = lane_tickers & funded_tickers
        if active:
            if lane.get("status") != "funded_model_position_active":
                blockers.append("funded opportunity lane is not marked active: " + ",".join(sorted(active)))
            if int(lane.get("funded_count") or 0) < 1:
                blockers.append("funded opportunity lane count missing: " + ",".join(sorted(active)))
            next_copy = " ".join(
                [str(lane.get("next_confirmation_nl") or ""), str(lane.get("next_confirmation_en") or "")]
            ).casefold()
            if "brokerbeschikbaarheid" in next_copy or "broker availability" in next_copy:
                blockers.append("funded opportunity lane contains broker-dependent model gate: " + ",".join(sorted(active)))
        elif lane.get("status") == "funded_model_position_active":
            blockers.append("opportunity lane marked funded without a funded position")

    allocation_text = json.dumps(state.get("allocation_map") or [], ensure_ascii=False).casefold()
    next_text = json.dumps((state.get("next_run_input") or {}).get("required_actions") or [], ensure_ascii=False).casefold()
    narrative = allocation_text + " " + next_text
    stale_tokens = [
        "brokerbeschikbaarheid", "broker availability",
        "vwce-capaciteit blijft cash totdat de exacte handelslijn is geverifieerd",
        "vwce capacity remains cash until the exact trading line is verified",
        "repair aggregate-bond share-class identity before any bond allocation",
        "verify the preferred global-core trading line before releasing its blocked capacity",
    ]
    for token in stale_tokens:
        if token in narrative:
            blockers.append("funded state contains stale narrative: " + token)
    return blockers


def validate_language(state: dict[str, Any], language: str, html_path: Path, pdf_path: Path) -> dict[str, Any]:
    html = read_text(html_path)
    extracted = pdf_text(pdf_path)
    combined = html + "\n" + extracted
    folded = combined.casefold()
    missing = [token for token in SECTIONS[language] if token.casefold() not in folded]
    forbidden = [token for token in FORBIDDEN if token.casefold() in folded]
    if language == "nl":
        forbidden.extend(token for token in NL_FORBIDDEN if token.casefold() in folded)
    pages = page_count(pdf_path)
    blockers: list[str] = []
    if missing:
        blockers.append("missing sections: " + ", ".join(missing))
    if forbidden:
        blockers.append("forbidden tokens: " + ", ".join(sorted(set(forbidden))))
    if not 6 <= pages <= 14:
        blockers.append(f"page count outside 6-14: {pages}")

    investor = "Beleggersrapport" if language == "nl" else "Investor report"
    analyst = "Analistenrapport" if language == "nl" else "Analyst report"
    if investor.casefold() not in folded or analyst.casefold() not in folded:
        blockers.append("investor/analyst hierarchy missing")
    if combined.upper().count("ISIN") < 8:
        blockers.append("ISIN-first evidence not sufficiently visible")
    research = "alleen onderzoek" if language == "nl" else "research only"
    if research.casefold() not in folded:
        blockers.append("U.S. references are not labelled research-only")

    macro = state.get("macro") if isinstance(state.get("macro"), dict) else {}
    if macro.get("fresh_for_report") is not True:
        disclosure = "Macro-refresh vereist" if language == "nl" else "Macro refresh required"
        if disclosure.casefold() not in folded:
            blockers.append("stale macro disclosure missing")

    curve = state.get("equity_curve") if isinstance(state.get("equity_curve"), dict) else {}
    svg_visible = 'class="equity-curve-svg"' in html
    cash_callout_visible = 'class="cash-callout"' in html
    if curve.get("show_chart") is True:
        if not svg_visible:
            blockers.append("equity curve should be visible but is absent")
        if curve.get("latest_nav_matches_state") is not True:
            blockers.append("equity curve does not reconcile to current NAV")
    else:
        if svg_visible:
            blockers.append("equity curve is visible despite insufficient meaningful history")
        if not cash_callout_visible:
            blockers.append("cash-preservation callout missing while equity curve is suppressed")

    portfolio = state.get("portfolio") if isinstance(state.get("portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    funded_surface_blockers: list[str] = []
    if positions:
        expected_label = f"{len(positions)} modelposities actief" if language == "nl" else f"{len(positions)} model positions active"
        if expected_label.casefold() not in folded:
            funded_surface_blockers.append("funded position-count summary missing")
        for row in positions:
            ticker = ticker_of(row)
            if ticker and ticker.casefold() not in folded:
                funded_surface_blockers.append("funded ticker missing from client output: " + ticker)
        for token in FUNDED_STALE[language]:
            if token.casefold() in folded:
                funded_surface_blockers.append("stale funded-state wording: " + token)
    blockers.extend(funded_surface_blockers)

    return {
        "language": language,
        "html_path": str(html_path),
        "pdf_path": str(pdf_path),
        "page_count": pages,
        "missing_sections": missing,
        "forbidden_tokens": sorted(set(forbidden)),
        "investor_analyst_hierarchy_passed": not any("hierarchy" in blocker for blocker in blockers),
        "isin_first_visible": combined.upper().count("ISIN") >= 8,
        "research_only_labelling_passed": research.casefold() in folded,
        "macro_freshness_disclosure_passed": not any("macro disclosure" in blocker for blocker in blockers),
        "equity_curve_contract_passed": not any("equity curve" in blocker or "cash-preservation" in blocker for blocker in blockers),
        "funded_surface_consistency_passed": not funded_surface_blockers,
        "passed": not blockers,
        "blockers": blockers,
    }


def validate(args: argparse.Namespace) -> dict[str, Any]:
    state = json.loads(read_text(Path(args.state)))
    blockers: list[str] = []
    if state.get("state_valid") is not True:
        blockers.append("normalized report state invalid")
    authority = state.get("authority") if isinstance(state.get("authority"), dict) else {}
    if authority.get("canonical_identity") != "isin_first":
        blockers.append("canonical identity is not ISIN-first")
    if authority.get("us_etfs_research_only") is not True:
        blockers.append("U.S. ETFs are not constrained to research-only status")
    for field in ["valuation_grade", "funding_authority", "portfolio_mutation", "production_delivery_authority"]:
        if authority.get(field) is not False:
            blockers.append(f"authority field must remain false: {field}")

    state_consistency = funded_state_blockers(state)
    blockers.extend(state_consistency)
    dutch = validate_language(state, "nl", Path(args.dutch_html), Path(args.dutch_pdf))
    english = validate_language(state, "en", Path(args.english_html), Path(args.english_pdf))
    blockers.extend("NL: " + blocker for blocker in dutch["blockers"])
    blockers.extend("EN: " + blocker for blocker in english["blockers"])
    return {
        "schema_version": "etf_eu_client_grade_report_v2_validation_v2",
        "artifact_type": "etf_eu_client_grade_report_v2_validation",
        "generated_at_utc": utc_now(),
        "run_id": state.get("run_id"),
        "source_run_id": state.get("source_run_id"),
        "report_date": state.get("report_date"),
        "dutch": dutch,
        "english": english,
        "funded_state_consistency_passed": not state_consistency,
        "client_grade_v2_passed": not blockers,
        "transport_attempted": False,
        "send_executed": False,
        "portfolio_mutation": False,
        "blockers": blockers,
        "warnings": state.get("warnings") or [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Weekly ETF EU client-grade v2 report outputs.")
    parser.add_argument("--state", required=True)
    parser.add_argument("--dutch-html", required=True)
    parser.add_argument("--dutch-pdf", required=True)
    parser.add_argument("--english-html", required=True)
    parser.add_argument("--english-pdf", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    result = validate(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    if args.strict and result["client_grade_v2_passed"] is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
