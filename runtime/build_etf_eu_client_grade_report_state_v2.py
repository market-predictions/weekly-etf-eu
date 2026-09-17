from __future__ import annotations

import json
import tempfile
from argparse import Namespace
from pathlib import Path
from typing import Any

from pricing.ucits_close_price_validation_contract_v2 import (
    AUTHORIZED_EXACT_STATUSES,
    SCHEMA_VERSION,
    validate_artifact,
)
from runtime.build_etf_eu_client_grade_report_state import build_state as build_legacy_state
from runtime.render_etf_eu_client_grade_v2_funded import funded_overlay
from runtime.revalue_etf_eu_model_portfolio import revalue_portfolio


def _canonical_pricing_rows(pricing_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in pricing_payload.get("rows") or []:
        if not isinstance(source, dict):
            continue
        authority_status = str(source.get("source_agreement_status") or "").strip()
        authorized = authority_status in AUTHORIZED_EXACT_STATUSES and source.get("valuation_grade") is True
        rows.append(
            {
                "basket_id": source.get("basket_id"),
                "ticker": str(source.get("ticker") or "").strip().upper(),
                "isin": str(source.get("isin") or "").strip().upper(),
                "fund_name": source.get("fund_name"),
                "instrument_type": source.get("instrument_type"),
                "exchange": source.get("exchange"),
                "venue_code": source.get("venue_code"),
                "currency": source.get("currency"),
                "close_date": source.get("close_date"),
                "close_price": source.get("close_price"),
                "authority_status": authority_status,
                "verification_status": authority_status,
                "authorized": authorized,
                "valuation_grade": source.get("valuation_grade") is True,
                "primary_provider": source.get("primary_provider"),
                "verification_providers": list(source.get("verification_providers") or []),
                "same_date_provider_count": int(source.get("same_date_provider_count") or 0),
                "static_identity_binding": source.get("static_identity_binding") is True,
                "static_primary_provider_symbol_binding": source.get("static_primary_provider_symbol_binding") is True,
                "blockers": list(source.get("blockers") or []),
            }
        )
    return sorted(rows, key=lambda row: (str(row.get("fund_name") or ""), str(row.get("ticker") or "")))


def _canonical_verification_funnel(
    pricing_rows: list[dict[str, Any]],
    *,
    funded_position_count: int,
    cash_eur: Any,
) -> dict[str, Any]:
    verified = [row for row in pricing_rows if row.get("authority_status") == "fresh_exact_verified"]
    primary_only = [row for row in pricing_rows if row.get("authority_status") == "fresh_exact_unverified"]
    authorized = [row for row in pricing_rows if row.get("authorized") is True]
    priced = [row for row in pricing_rows if row.get("close_price") not in (None, "")]
    return {
        "observed_lines": len(pricing_rows),
        "priced_lines": len(priced),
        "authorized_lines": len(authorized),
        "verified_lines": len(verified),
        "primary_only_lines": len(primary_only),
        "unresolved_lines": len(pricing_rows) - len(authorized),
        "funded_positions": funded_position_count,
        "cash_eur": cash_eur,
        "pricing_vocabulary": sorted(AUTHORIZED_EXACT_STATUSES),
        "decision": "canonical_pricing_authority_then_separate_fundability_and_allocation_decision",
    }


def build_state(args: Namespace) -> dict[str, Any]:
    pricing_path = Path(args.pricing_artifact)
    portfolio_path = Path(args.portfolio_state)
    pricing_validation = validate_artifact(
        pricing_path,
        expected_report_date=args.report_date,
        portfolio_state_path=portfolio_path,
        require_funded_consensus=True,
    )
    if pricing_validation["valid"] is not True:
        raise RuntimeError(
            "Canonical v2 pricing contract failed: " + "; ".join(pricing_validation["blockers"])
        )

    pricing_payload = json.loads(pricing_path.read_text(encoding="utf-8"))
    protected_portfolio = json.loads(portfolio_path.read_text(encoding="utf-8"))
    derived_portfolio = revalue_portfolio(
        protected_portfolio,
        pricing_payload,
        report_date=args.report_date,
    )

    compatibility_payload = dict(pricing_payload)
    compatibility_payload["min_threshold_met"] = True

    with tempfile.TemporaryDirectory(prefix="etf_eu_pricing_v2_") as tmpdir:
        compatibility_path = Path(tmpdir) / "pricing_v2_layout_compat.json"
        derived_portfolio_path = Path(tmpdir) / "derived_report_portfolio.json"
        compatibility_path.write_text(
            json.dumps(compatibility_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        derived_portfolio_path.write_text(
            json.dumps(derived_portfolio, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        legacy_args = Namespace(**vars(args))
        legacy_args.pricing_artifact = str(compatibility_path)
        legacy_args.portfolio_state = str(derived_portfolio_path)
        state = build_legacy_state(legacy_args)

    state_portfolio = state.get("portfolio") if isinstance(state.get("portfolio"), dict) else {}
    for key in (
        "last_model_capital_activation",
        "last_valuation_refresh",
        "valuation_source",
        "last_broker_neutral_allocation_activation",
    ):
        if key in protected_portfolio:
            state_portfolio[key] = protected_portfolio[key]
    state_portfolio["derived_valuation"] = derived_portfolio.get("derived_valuation")
    state["portfolio"] = state_portfolio

    blockers = [
        blocker
        for blocker in state.get("blockers") or []
        if blocker != "pricing coverage threshold not met"
    ]
    pricing_policy = pricing_payload.get("pricing_authority_policy") or {}
    canonical_rows = _canonical_pricing_rows(pricing_payload)

    state["schema_version"] = "etf_eu_client_grade_report_state_v3"
    state["sources"]["pricing_artifact"] = str(pricing_path)
    state["sources"]["protected_portfolio_state"] = str(portfolio_path)
    state["pricing"] = {
        "contract_schema": SCHEMA_VERSION,
        "contract_validation": pricing_validation,
        "report_date": pricing_payload.get("report_date"),
        "report_pricing_gate_passed": pricing_payload.get("report_pricing_gate_passed") is True,
        "funded_position_count": pricing_validation["funded_position_count"],
        "funded_evidence": pricing_validation["funded_evidence"],
        "funded_exact_primary_pricing_required": True,
        "second_provider_required_for_liveness": pricing_policy.get("second_provider_required_for_liveness") is True,
        "funded_two_provider_consensus_required": False,
        "pricing_authority_mode": pricing_policy.get("mode"),
        "pricing_authority": "canonical_completed_close_primary_plus_verification",
        "authorized_statuses": sorted(AUTHORIZED_EXACT_STATUSES),
        "rows": canonical_rows,
        "derived_portfolio_valuation": derived_portfolio.get("derived_valuation"),
    }
    state["pricing_contract"] = {
        "schema_version": SCHEMA_VERSION,
        "artifact": str(pricing_path),
        "expected_report_date": args.report_date,
        "report_date": pricing_validation["report_date"],
        "report_pricing_gate_passed": pricing_payload.get("report_pricing_gate_passed") is True,
        "funded_position_count": pricing_validation["funded_position_count"],
        "funded_evidence": pricing_validation["funded_evidence"],
        "funded_exact_primary_pricing_required": True,
        "second_provider_required_for_liveness": pricing_policy.get("second_provider_required_for_liveness") is True,
        "funded_two_provider_consensus_required": False,
        "pricing_authority_mode": pricing_policy.get("mode"),
        "authorized_statuses": sorted(AUTHORIZED_EXACT_STATUSES),
        "validation": pricing_validation,
        "derived_valuation_nav_eur": derived_portfolio.get("nav_eur"),
        "protected_portfolio_mutated": False,
    }
    state["verification_funnel"] = _canonical_verification_funnel(
        canonical_rows,
        funded_position_count=int(state_portfolio.get("position_count") or len(state_portfolio.get("positions") or [])),
        cash_eur=state_portfolio.get("cash_eur"),
    )
    state["blockers"] = blockers
    state["state_valid"] = not blockers and pricing_validation["valid"] is True

    state = funded_overlay(state)
    positions = [
        row
        for row in (state.get("portfolio") or {}).get("positions", [])
        if isinstance(row, dict)
    ]
    state["funded_position_count"] = len(positions)
    state["funded_tickers"] = sorted(
        str(row.get("ticker") or row.get("exchange_ticker") or "").strip().upper()
        for row in positions
        if str(row.get("ticker") or row.get("exchange_ticker") or "").strip()
    )
    state["protected_portfolio_state_mutated"] = False
    return state


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--portfolio-state", required=True)
    parser.add_argument("--valuation-history", required=True)
    parser.add_argument("--pricing-artifact", required=True)
    parser.add_argument("--macro-pack", required=True)
    parser.add_argument("--registry", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--source-run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    state = build_state(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "ETF_EU_CLIENT_GRADE_REPORT_STATE_V3_OK"
        f" | output={output}"
        f" | funded_positions={state['funded_position_count']}"
        f" | pricing_gate={state['pricing_contract']['report_pricing_gate_passed']}"
        " | protected_portfolio_mutated=false"
    )


if __name__ == "__main__":
    main()
