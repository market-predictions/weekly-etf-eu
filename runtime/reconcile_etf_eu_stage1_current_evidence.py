from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def preferred_variant(allocator: dict[str, Any]) -> dict[str, Any]:
    variant_id = str(allocator.get("preferred_shadow_variant") or "staged_policy_driven_v1")
    for variant in allocator.get("variants") or []:
        if isinstance(variant, dict) and variant.get("variant_id") == variant_id:
            return variant
    raise RuntimeError(f"Preferred allocator variant not found: {variant_id}")


def selected_rows(variant: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("exposure_id")): row
        for row in variant.get("allocation_rows") or []
        if isinstance(row, dict) and row.get("selected") is True and row.get("eligible") is True
    }


def apply(state_path: Path, allocator_path: Path) -> None:
    state = load_object(state_path)
    allocator = load_object(allocator_path)
    variant = preferred_variant(allocator)
    selected = selected_rows(variant)
    if not {"ai_compute_infrastructure", "cyber_security"}.issubset(selected):
        raise RuntimeError("Expected VVSM and cybersecurity Stage-1 rows to be selected and eligible")

    remaining_blockers: list[str] = []
    proposals: list[dict[str, Any]] = []
    for candidate in state.get("stage_1_review_candidates") or []:
        if not isinstance(candidate, dict):
            continue
        exposure_id = str(candidate.get("exposure_id") or "")
        allocation = selected.get(exposure_id)
        if allocation is None:
            continue
        ticker = str(allocation.get("candidate", {}).get("ticker") or candidate.get("exchange_symbol") or "")
        display_ticker = "L0CK" if ticker == "LOCK" else ticker
        order = allocation.get("order") or {}
        candidate_evidence = allocation.get("candidate") or {}

        blockers = [f"{display_ticker}:timestamped_bid_ask_quote_size"]
        blockers_nl = ["timestamped bied-, laat- en quote-sizebewijs ontbreekt"]
        blockers_en = ["timestamped bid, ask and quote-size evidence is unavailable"]
        if candidate.get("donor_fresh_add_direction") is not True:
            blockers.append("donor_fresh_add_direction_absent")
            blockers_nl.append("de donor geeft geen nieuwe kooprichting")
            blockers_en.append("the donor does not emit a fresh-add direction")
        blockers.append("explicit_model_capital_activation_confirmation_absent")
        blockers_nl.append("expliciete modelkapitaalactivatie is niet bevestigd")
        blockers_en.append("explicit model-capital activation has not been confirmed")

        proposal = {
            "exposure_id": exposure_id,
            "ticker": display_ticker,
            "fund_name": candidate_evidence.get("fund_name") or candidate.get("fund_name"),
            "isin": candidate_evidence.get("isin") or candidate.get("isin"),
            "target_weight_pct": allocation.get("variant_target_weight_pct"),
            "target_shares": order.get("target_shares"),
            "share_delta": order.get("share_delta"),
            "side": order.get("side"),
            "price_eur": candidate_evidence.get("price_eur"),
            "price_date": candidate_evidence.get("price_date"),
            "gross_trade_value_eur": order.get("gross_trade_value_eur"),
            "estimated_cost_eur": order.get("estimated_cost_eur"),
            "median_daily_traded_value_eur_20d": candidate_evidence.get("median_daily_traded_value_eur_20d"),
            "evidence_status": candidate_evidence.get("evidence_status"),
            "evidence_source_quality": candidate_evidence.get("evidence_source_quality"),
            "execution_status": "shadow_proposal_not_authorized_not_executed",
        }
        proposals.append(proposal)
        candidate.update(
            {
                "analytical_allocator_weight_pct": allocation.get("variant_target_weight_pct"),
                "actionable_target_weight_pct": 0.0,
                # Preserve the canonical client-action contract used by the
                # production-convergence validator. The richer proposal state
                # is carried in a separate non-authorizing field.
                "client_action": "blocked_monitor",
                "expanded_client_action": "shadow_buy_proposal_blocked_pending_authority",
                "current_completed_close_pass": True,
                "accepted_liquidity_measurement_pass": True,
                "timestamped_bid_ask_quote_size_pass": False,
                "current_price_eur": candidate_evidence.get("price_eur"),
                "current_price_date": candidate_evidence.get("price_date"),
                "median_daily_traded_value_eur_20d": candidate_evidence.get("median_daily_traded_value_eur_20d"),
                "proposed_shadow_order": proposal,
                "blockers": blockers,
                "blockers_nl": blockers_nl,
                "blockers_en": blockers_en,
                "portfolio_mutation": False,
                "allocation_authority": False,
            }
        )
        remaining_blockers.extend(blockers)

    summary = variant.get("summary") or {}
    stage = state.setdefault("stage_1_decision", {})
    stage.update(
        {
            "value": "blocked",
            # Preserve the canonical state status while exposing the more
            # precise current blocker classification separately.
            "status": "blocked_not_activation_ready",
            "expanded_status": "blocked_pending_quote_donor_and_explicit_activation_authority",
            "blockers": sorted(set(remaining_blockers)),
            "blocker_count": len(set(remaining_blockers)),
            "stage_1_activation_authorized": False,
            "official_state_applied": False,
            "executable_trade_intents": [],
            "shadow_expansion_proposal": {
                "variant_id": variant.get("variant_id"),
                "proposed_position_count": summary.get("position_count"),
                "projected_cash_eur": summary.get("projected_cash_eur"),
                "projected_cash_weight_pct": summary.get("projected_cash_weight_pct"),
                "gross_buy_value_eur": summary.get("gross_buy_value_eur"),
                "gross_turnover_pct_nav": summary.get("gross_turnover_pct_nav"),
                "estimated_transaction_cost_eur": summary.get("estimated_transaction_cost_eur"),
                "proposed_orders": proposals,
                "portfolio_mutation": False,
                "real_broker_execution": False,
                "activation_authority": False,
            },
        }
    )
    state["current_evidence_reconciliation"] = {
        "applied": True,
        "allocator_path": str(allocator_path),
        "selected_exposures": sorted(selected),
        "fresh_close_and_liquidity_blockers_removed": True,
        "remaining_authority_and_execution_blockers_preserved": True,
        "portfolio_mutation": False,
        "real_broker_execution": False,
    }
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "ETF_EU_STAGE1_CURRENT_EVIDENCE_RECONCILED"
        f" | proposals={len(proposals)}"
        f" | positions={summary.get('position_count')}"
        f" | projected_cash={summary.get('projected_cash_eur')}"
        f" | official_state_applied=false"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path)
    parser.add_argument("--allocator", type=Path, required=True)
    args = parser.parse_args()
    apply(args.state, args.allocator)


if __name__ == "__main__":
    main()
