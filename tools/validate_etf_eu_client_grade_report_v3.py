from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.validate_etf_eu_client_grade_report_v2_standalone import read_text, validate_language


SHADOW_CLIENT_MARKERS = [
    "35% minimum cash",
    "15% maximum new",
    "50% cash-first",
    "25% turnover ceiling",
    "18% semiconductor cap",
    "Max. nieuwe ETF",
    "Max. new ETF",
    "reserve minimaal 7,50%",
    "reserve at least 7.50%",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ticker_of(row: dict[str, Any]) -> str:
    return str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()


def validate(args: argparse.Namespace) -> dict[str, Any]:
    state = json.loads(read_text(Path(args.state)))
    blockers: list[str] = []
    warnings: list[str] = []

    if state.get("state_valid") is not True:
        blockers.append("normalized report state invalid")
    authority = state.get("authority") if isinstance(state.get("authority"), dict) else {}
    if authority.get("canonical_identity") != "isin_first":
        blockers.append("canonical identity is not ISIN-first")
    if authority.get("us_etfs_research_only") is not True:
        blockers.append("U.S. ETFs are not constrained to research-only status")
    for field in ["funding_authority", "portfolio_mutation", "production_delivery_authority"]:
        if authority.get(field) is not False:
            blockers.append(f"authority field must remain false: {field}")
    if authority.get("shadow_policy_used_for_current_allocation") is not False:
        blockers.append("shadow transition policy is not explicitly excluded from current allocation")
    if authority.get("retired_fixed_percentage_used") is not False:
        blockers.append("retired fixed percentage is not explicitly excluded")
    if authority.get("historical_target_used_for_current_trade") is not False:
        blockers.append("historical target is not explicitly excluded from current trade authority")
    if authority.get("broker_specific_permission_required_for_model") is not False:
        blockers.append("broker-specific permission is incorrectly required for model investability")
    if authority.get("broker_permission_required_for_real_execution") is not True:
        blockers.append("real-execution broker permission boundary is not explicit")

    portfolio = state.get("portfolio") if isinstance(state.get("portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    funded = {ticker_of(row) for row in positions if ticker_of(row)}
    if len(funded) != len(positions) or not funded:
        blockers.append("funded position set is empty or contains duplicate tickers")

    consistency = state.get("funded_consistency") if isinstance(state.get("funded_consistency"), dict) else {}
    if consistency.get("position_count") != len(positions):
        blockers.append("funded consistency position count mismatch")
    if set(consistency.get("funded_tickers") or []) != funded:
        blockers.append("funded consistency ticker set mismatch")
    if consistency.get("allocation_map_current_actuals_only") is not True:
        blockers.append("allocation map is not proven current-actuals-only")
    if consistency.get("historical_targets_client_authority") is not False:
        blockers.append("historical target metadata retains client authority")
    if consistency.get("broker_neutral_model_language") is not True:
        blockers.append("broker-neutral model language flag missing")

    reviews = [row for row in state.get("current_reunderwriting") or [] if isinstance(row, dict)]
    review_tickers = {ticker_of(row) for row in reviews if ticker_of(row)}
    if review_tickers != funded or len(reviews) != len(positions):
        blockers.append(f"current re-underwriting coverage mismatch: funded={sorted(funded)} reviews={sorted(review_tickers)}")
    for row in reviews:
        ticker = ticker_of(row)
        for field in ["fresh_cash_test", "would_initiate_today", "cash_policy_flag", "required_next_action", "current_price_status"]:
            if not row.get(field):
                blockers.append(f"{ticker}: current re-underwriting field missing: {field}")

    if state.get("client_renderer_mode") != "client_grade_v3_donor_converged":
        blockers.append("current client renderer is not donor-converged v3")

    dutch = validate_language(state, "nl", Path(args.dutch_html), Path(args.dutch_pdf))
    english = validate_language(state, "en", Path(args.english_html), Path(args.english_pdf))
    blockers.extend("NL: " + blocker for blocker in dutch["blockers"])
    blockers.extend("EN: " + blocker for blocker in english["blockers"])

    combined_html = read_text(Path(args.dutch_html)) + "\n" + read_text(Path(args.english_html))
    leaked = [marker for marker in SHADOW_CLIENT_MARKERS if marker.casefold() in combined_html.casefold()]
    if leaked:
        blockers.append("retired/shadow client authority leak: " + ", ".join(leaked))

    if "gemeten ingebedde semiconductor" not in combined_html.casefold() and "measured embedded semiconductor" not in combined_html.casefold():
        warnings.append("embedded-semiconductor lower-bound wording not visible in v3 client surface")

    equity = state.get("equity_curve") if isinstance(state.get("equity_curve"), dict) else {}
    if equity.get("latest_nav_matches_state") is not True:
        blockers.append("equity/valuation history does not reconcile to current NAV")

    payload = {
        "schema_version": "etf_eu_client_grade_report_v3_validation_v1",
        "artifact_type": "etf_eu_client_grade_report_v3_validation",
        "generated_at_utc": utc_now(),
        "run_id": state.get("run_id"),
        "report_date": state.get("report_date"),
        "client_renderer_mode": state.get("client_renderer_mode"),
        "funded_tickers": sorted(funded),
        "current_reunderwriting_tickers": sorted(review_tickers),
        "dutch": dutch,
        "english": english,
        "shadow_client_markers": leaked,
        "warnings": warnings,
        "blockers": blockers,
        "client_grade_v3_passed": not blockers,
        "client_grade_v2_passed": not blockers,
        "valid": not blockers,
    }
    if getattr(args, "strict", False) and blockers:
        raise RuntimeError(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the donor-converged Weekly ETF EU client-grade v3 report")
    parser.add_argument("--state", required=True)
    parser.add_argument("--dutch-html", required=True)
    parser.add_argument("--dutch-pdf", required=True)
    parser.add_argument("--english-html", required=True)
    parser.add_argument("--english-pdf", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    payload = validate(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    if args.strict and payload["blockers"]:
        raise SystemExit("ETF_EU_CLIENT_GRADE_V3_VALIDATION_FAILED")
    print(f"ETF_EU_CLIENT_GRADE_V3_VALIDATION_OK | output={output}")


if __name__ == "__main__":
    main()
