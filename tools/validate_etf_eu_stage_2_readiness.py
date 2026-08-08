from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_BLOCKERS = {
    "stage_1_not_authorized",
    "stage_1_not_applied_to_official_state",
    "stage_1_receipt_not_confirmed",
    "official_post_stage_1_state_missing",
    "destination_document_grade_not_pass",
    "destination_valuation_grade_not_pass",
    "destination_tradability_grade_not_pass",
    "destination_not_activation_ready",
    "donor_add_direction_not_confirmed",
    "separate_stage_2_activation_authorization_missing",
}

PROTECTED_CASH_FLOOR_PCT_NAV = 25.0
MAXIMUM_SXR8_REDUCTION_PCT_NAV = 5.0
STAGE_2_DESTINATION_CAP_PCT_NAV = 15.0
TOLERANCE = 0.02


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Stage-2 readiness artifact must be a JSON object")
    return payload


def num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def close(left: float, right: float, tolerance: float = TOLERANCE) -> bool:
    return abs(left - right) <= tolerance


def validate(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_eu_stage_2_readiness_v1":
        blockers.append("unexpected schema_version")
    if payload.get("artifact_type") != "etf_eu_stage_2_transition_readiness":
        blockers.append("unexpected artifact_type")
    if payload.get("contract_release_id") != "weekly_etf_shared_contract_v1_0_0":
        blockers.append("donor contract release mismatch")
    if payload.get("donor_commit_sha") != "455201b4736dda41df07644d78b6797282a29fc7":
        blockers.append("donor commit pin mismatch")
    for key in (
        "portfolio_mutation",
        "funding_authority",
        "execution_authority",
        "activation_authority",
        "production_delivery_authority",
    ):
        if payload.get(key) is not False:
            blockers.append(f"{key} must be false")

    destination = payload.get("destination") if isinstance(payload.get("destination"), dict) else {}
    if destination.get("exposure_id") != "non_us_developed_equities":
        blockers.append("unexpected Stage-2 destination exposure")
    if destination.get("ticker") != "IXUA" or destination.get("isin") != "IE000R4ZNTN3":
        blockers.append("unexpected Stage-2 destination instrument")
    if destination.get("exchange") != "Xetra" or destination.get("currency") != "EUR":
        blockers.append("Stage-2 destination line mismatch")
    if abs(num(destination.get("donor_target_weight_pct_nav")) - 24.66) > 0.01:
        blockers.append("unexpected donor target weight")
    destination_cap = num(destination.get("stage_2_maximum_weight_pct_nav"))
    if not close(destination_cap, STAGE_2_DESTINATION_CAP_PCT_NAV, 0.001):
        blockers.append("Stage-2 destination cap mismatch")

    state = payload.get("current_shadow_state") if isinstance(payload.get("current_shadow_state"), dict) else {}
    current_cash = num(state.get("stage_1_projected_cash_weight_pct_nav"))
    sxr8_weight = num(state.get("sxr8_weight_pct_nav"))
    if current_cash < PROTECTED_CASH_FLOOR_PCT_NAV - TOLERANCE:
        blockers.append("Stage-1 shadow cash is below the Stage-2 protected cash floor")
    if num(state.get("stage_1_projected_position_count")) <= 0:
        blockers.append("Stage-1 projected position count is missing")

    capacity = payload.get("capacity_analysis") if isinstance(payload.get("capacity_analysis"), dict) else {}
    expected_excess_cash = max(0.0, current_cash - PROTECTED_CASH_FLOOR_PCT_NAV)
    theoretical_target = num(capacity.get("theoretical_destination_weight_pct_nav"))
    expected_cash_use = min(theoretical_target, expected_excess_cash)
    expected_sxr8_capacity = min(MAXIMUM_SXR8_REDUCTION_PCT_NAV, max(0.0, sxr8_weight))
    expected_remaining_after_cash = max(0.0, theoretical_target - expected_cash_use)
    expected_sxr8_use = min(expected_remaining_after_cash, expected_sxr8_capacity)
    expected_projected_cash = current_cash - expected_cash_use

    if not close(num(capacity.get("excess_cash_above_floor_pct_nav")), expected_excess_cash):
        blockers.append("excess-cash capacity is inconsistent with current Stage-1 cash")
    if not close(num(capacity.get("cash_source_used_pct_nav")), expected_cash_use):
        blockers.append("cash-source use is inconsistent with current Stage-1 cash")
    if not close(num(capacity.get("sxr8_current_weight_pct_nav")), sxr8_weight):
        blockers.append("SXR8 source weight is inconsistent with current Stage-1 state")
    if not close(num(capacity.get("sxr8_source_capacity_pct_nav")), expected_sxr8_capacity):
        blockers.append("SXR8 source capacity violates the 5% per-run cap")
    if not close(num(capacity.get("sxr8_source_used_pct_nav")), expected_sxr8_use):
        blockers.append("SXR8 source use is inconsistent with the funding waterfall")
    if not close(theoretical_target, STAGE_2_DESTINATION_CAP_PCT_NAV):
        blockers.append("theoretical destination capacity mismatch")
    if not close(num(capacity.get("projected_cash_weight_after_capacity_use_pct_nav")), expected_projected_cash):
        blockers.append("projected cash after Stage-2 capacity use is inconsistent")
    if expected_excess_cash >= theoretical_target - TOLERANCE:
        if expected_projected_cash < PROTECTED_CASH_FLOOR_PCT_NAV - TOLERANCE:
            blockers.append("projected protected cash floor violated")
    elif not close(expected_projected_cash, PROTECTED_CASH_FLOOR_PCT_NAV):
        blockers.append("cash-first waterfall did not stop at protected cash floor")
    if capacity.get("euna_source_available") is not False:
        blockers.append("EUNA must not be available as a Stage-2 source")
    if num(capacity.get("euna_source_used_pct_nav")) != 0.0:
        blockers.append("EUNA source use must be zero")
    if num(capacity.get("unfunded_capacity_pct_nav")) > 0.0001:
        blockers.append("governed Stage-2 capacity should fund the capped tranche")

    sources = payload.get("funding_source_order") if isinstance(payload.get("funding_source_order"), list) else []
    if [row.get("source_id") for row in sources if isinstance(row, dict)] != [
        "excess_cash_above_floor",
        "sxr8_overlap_reduction",
        "euna_risk_budget_release",
    ]:
        blockers.append("funding-source order mismatch")
    if [row.get("priority") for row in sources if isinstance(row, dict)] != [1, 2, 3]:
        blockers.append("funding-source priorities are not contiguous")
    source_by_id = {str(row.get("source_id")): row for row in sources if isinstance(row, dict)}
    cash_source = source_by_id.get("excess_cash_above_floor", {})
    sxr8_source = source_by_id.get("sxr8_overlap_reduction", {})
    euna_source = source_by_id.get("euna_risk_budget_release", {})
    if not close(num(cash_source.get("simulated_capacity_pct_nav")), expected_excess_cash):
        blockers.append("funding-order cash capacity mismatch")
    if not close(num(cash_source.get("simulated_use_pct_nav")), expected_cash_use):
        blockers.append("funding-order cash use mismatch")
    if not close(num(sxr8_source.get("simulated_capacity_pct_nav")), expected_sxr8_capacity):
        blockers.append("funding-order SXR8 capacity mismatch")
    if not close(num(sxr8_source.get("simulated_use_pct_nav")), expected_sxr8_use):
        blockers.append("funding-order SXR8 use mismatch")
    if euna_source.get("available") is not False or num(euna_source.get("simulated_use_pct_nav")) != 0.0:
        blockers.append("funding-order EUNA boundary mismatch")

    gates = payload.get("entry_gate_results") if isinstance(payload.get("entry_gate_results"), dict) else {}
    expected_gate_values = {
        "immutable_donor_pin_pass": True,
        "stage_1_operational_state_pass": False,
        "destination_identity_pass": True,
        "destination_document_pass": False,
        "destination_valuation_pass": False,
        "destination_tradability_pass": False,
        "destination_activation_ready": False,
        "donor_add_direction_pass": False,
        "euna_risk_budget_pass": True,
        "separate_activation_authorization_pass": False,
    }
    for key, expected in expected_gate_values.items():
        if gates.get(key) is not expected:
            blockers.append(f"entry gate {key} mismatch")

    if payload.get("readiness") != "blocked":
        blockers.append("current Stage-2 readiness must be blocked")
    actual_blockers = set(payload.get("blockers") or [])
    missing = sorted(REQUIRED_BLOCKERS - actual_blockers)
    if missing:
        blockers.append("required blockers missing: " + ", ".join(missing))
    if payload.get("executable_trade_intents") not in ([], None):
        blockers.append("blocked Stage-2 artifact must have no executable trade intents")

    rollback = payload.get("rollback") if isinstance(payload.get("rollback"), dict) else {}
    if rollback.get("automatic_reverse_orders") is not False:
        blockers.append("rollback must not create automatic reverse orders")
    if rollback.get("infer_orders_from_report_text") is not False:
        blockers.append("rollback must not infer orders from report text")
    if rollback.get("automatic_ledger_rewrite") is not False:
        blockers.append("rollback must not rewrite the ledger automatically")

    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ETF EU Stage-2 readiness")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    payload = load(args.path)
    blockers = validate(payload)
    print(json.dumps({
        "artifact_type": "etf_eu_stage_2_readiness_validation",
        "valid": not blockers,
        "blockers": blockers,
        "readiness": payload.get("readiness"),
        "stage_2_blockers": payload.get("blockers"),
        "capacity_analysis": payload.get("capacity_analysis"),
    }, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
