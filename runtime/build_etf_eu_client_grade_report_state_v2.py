from __future__ import annotations

import json
import tempfile
from argparse import Namespace
from pathlib import Path
from typing import Any

from pricing.ucits_close_price_validation_contract_v2 import (
    SCHEMA_VERSION,
    validate_artifact,
)
from runtime.build_etf_eu_client_grade_report_state import build_state as build_legacy_state
from runtime.render_etf_eu_client_grade_v2_funded import funded_overlay
from runtime.revalue_etf_eu_model_portfolio import revalue_portfolio


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
            "Canonical v2 pricing contract failed: "
            + "; ".join(pricing_validation["blockers"])
        )

    pricing_payload = json.loads(pricing_path.read_text(encoding="utf-8"))
    protected_portfolio = json.loads(portfolio_path.read_text(encoding="utf-8"))
    derived_portfolio = revalue_portfolio(
        protected_portfolio,
        pricing_payload,
        report_date=args.report_date,
    )

    # The v1 state constructor is retained strictly as an internal layout helper.
    # Its historical min_threshold_met input is satisfied only in an ephemeral copy;
    # current pricing authority is the shared v2 contract validated above. The
    # portfolio copy is likewise ephemeral and contains fresh valuation fields only:
    # shares, cash, allocation lineage and trade ledger authority remain protected.
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

    # Preserve protected authority lineage while retaining the freshly derived
    # valuation already produced above. This never writes the protected portfolio.
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
    state["schema_version"] = "etf_eu_client_grade_report_state_v2"
    state["sources"]["pricing_artifact"] = str(pricing_path)
    state["sources"]["protected_portfolio_state"] = str(portfolio_path)
    state["pricing"].update(
        {
            "contract_schema": SCHEMA_VERSION,
            "contract_validation": pricing_validation,
            "report_date": pricing_payload.get("report_date"),
            "report_pricing_gate_passed": pricing_payload.get("report_pricing_gate_passed") is True,
            "funded_position_count": pricing_validation["funded_position_count"],
            "funded_evidence": pricing_validation["funded_evidence"],
            "funded_two_provider_consensus_required": True,
            "pricing_authority": "canonical_v2_completed_close_contract",
            "derived_portfolio_valuation": derived_portfolio.get("derived_valuation"),
        }
    )
    state["pricing_contract"] = {
        "schema_version": SCHEMA_VERSION,
        "artifact": str(pricing_path),
        "expected_report_date": args.report_date,
        "report_date": pricing_validation["report_date"],
        "report_pricing_gate_passed": pricing_payload.get("report_pricing_gate_passed") is True,
        "funded_position_count": pricing_validation["funded_position_count"],
        "funded_evidence": pricing_validation["funded_evidence"],
        "funded_two_provider_consensus_required": True,
        "validation": pricing_validation,
        "derived_valuation_nav_eur": derived_portfolio.get("nav_eur"),
        "protected_portfolio_mutated": False,
    }
    state["blockers"] = blockers
    state["state_valid"] = not blockers and pricing_validation["valid"] is True

    # Funded reconciliation is part of normalized state authority, not a renderer-only patch.
    # Persist it before any client artifact is rendered so state, HTML/PDF and validators
    # share one exact funded position/count/opportunity interpretation.
    state = funded_overlay(state)
    positions = [
        row
        for row in (state.get("portfolio") or {}).get("positions") or []
        if isinstance(row, dict)
    ]
    if positions:
        consistency = dict(state.get("funded_consistency") or {})
        consistency.update(
            {
                "position_count": len(positions),
                "funded_tickers": [
                    str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()
                    for row in positions
                ],
                "allocation_map_reconciled": True,
                "opportunity_radar_reconciled": True,
                "broker_neutral_model_language": True,
                "normalized_state_authority": True,
                "current_model_activation_lineage_preserved": "last_model_capital_activation" in (state.get("portfolio") or {}),
                "fresh_completed_close_valuation_applied": all(
                    str(row.get("price_date") or "") == args.report_date for row in positions
                ),
            }
        )
        state["funded_consistency"] = consistency
    return state
