from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected YAML object: {path}")
    return payload


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def preferred_variant(allocator: dict[str, Any]) -> dict[str, Any]:
    preferred_id = str(allocator.get("preferred_shadow_variant") or "")
    for row in allocator.get("variants") or []:
        if isinstance(row, dict) and str(row.get("variant_id")) == preferred_id:
            return row
    raise RuntimeError("Preferred allocator variant not found")


def allocation_index(preferred: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("exposure_id")): row
        for row in preferred.get("allocation_rows") or []
        if isinstance(row, dict) and row.get("exposure_id")
    }


def legacy_index(preferred: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("ticker")): row
        for row in preferred.get("legacy_rows") or []
        if isinstance(row, dict) and row.get("ticker")
    }


def product_index(evidence: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("ticker")): row
        for row in evidence.get("candidates") or []
        if isinstance(row, dict) and row.get("ticker")
    }


def sync_index(sync: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("exposure_id")): row
        for row in sync.get("exposure_rows") or []
        if isinstance(row, dict) and row.get("exposure_id")
    }


def build(
    allocator: dict[str, Any],
    sync: dict[str, Any],
    product_evidence: dict[str, Any],
    euna_review: dict[str, Any],
    donor_pin: dict[str, Any],
    policy: dict[str, Any],
    stage_1_operational_state: dict[str, Any] | None,
    activation_authorization: dict[str, Any] | None,
) -> dict[str, Any]:
    for source in (allocator, sync, euna_review):
        if source.get("portfolio_mutation") is not False and source is not allocator:
            raise RuntimeError("Input violates the non-mutation boundary")
    allocator_authority = allocator.get("authority") if isinstance(allocator.get("authority"), dict) else {}
    if allocator_authority.get("portfolio_mutation") is not False or allocator_authority.get("execution_authority") is not False:
        raise RuntimeError("Allocator violates shadow authority")

    destination = policy.get("destination") if isinstance(policy.get("destination"), dict) else {}
    limits = policy.get("limits") if isinstance(policy.get("limits"), dict) else {}
    gates = policy.get("entry_gates") if isinstance(policy.get("entry_gates"), dict) else {}
    preferred = preferred_variant(allocator)
    allocations = allocation_index(preferred)
    legacy = legacy_index(preferred)
    products = product_index(product_evidence)
    sync_rows = sync_index(sync)

    exposure_id = str(destination.get("exposure_id"))
    ticker = str(destination.get("ticker"))
    destination_row = allocations.get(exposure_id, {})
    product_row = products.get(ticker, {})
    sync_row = sync_rows.get(exposure_id, {})
    summary = preferred.get("summary") if isinstance(preferred.get("summary"), dict) else {}
    current_cash_weight = num(summary.get("projected_cash_weight_pct"))
    donor_target_weight = num(destination_row.get("donor_target_weight_pct"))
    destination_cap = num(destination.get("maximum_destination_weight_pct_nav"))
    turnover_cap = num(limits.get("maximum_stage_2_gross_turnover_pct_nav"))
    cash_floor = num(limits.get("protected_cash_floor_pct_nav"))
    excess_cash_capacity = max(0.0, current_cash_weight - cash_floor)

    sxr8 = legacy.get("SXR8", {})
    nav = num((allocator.get("current_portfolio") or {}).get("nav_eur"))
    sxr8_target_value = num(sxr8.get("target_market_value_eur"))
    sxr8_weight = sxr8_target_value / nav * 100.0 if nav else 0.0
    sxr8_cap = min(num(limits.get("maximum_sxr8_reduction_pct_nav_per_run")), sxr8_weight)

    theoretical_target = min(donor_target_weight, destination_cap, turnover_cap)
    cash_source = min(theoretical_target, excess_cash_capacity)
    remaining = max(0.0, theoretical_target - cash_source)
    sxr8_source = min(remaining, sxr8_cap)
    remaining -= sxr8_source

    euna_classification = euna_review.get("classification") if isinstance(euna_review.get("classification"), dict) else {}
    euna_decision = euna_review.get("decision") if isinstance(euna_review.get("decision"), dict) else {}
    euna_release_available = bool(
        euna_classification.get("low_volatility_diversifier_pass") is False
        or num(euna_review.get("current_euna_weight_pct")) > 8.0
    )
    euna_source = 0.0

    source_capacity = {
        "excess_cash_above_floor_pct_nav": round(excess_cash_capacity, 6),
        "cash_source_used_pct_nav": round(cash_source, 6),
        "sxr8_current_weight_pct_nav": round(sxr8_weight, 6),
        "sxr8_source_capacity_pct_nav": round(sxr8_cap, 6),
        "sxr8_source_used_pct_nav": round(sxr8_source, 6),
        "euna_source_available": euna_release_available,
        "euna_source_used_pct_nav": euna_source,
        "unfunded_capacity_pct_nav": round(remaining, 6),
        "theoretical_destination_weight_pct_nav": round(theoretical_target - remaining, 6),
        "projected_cash_weight_after_capacity_use_pct_nav": round(current_cash_weight - cash_source, 6),
    }

    blockers: list[str] = []
    pin_valid = (
        donor_pin.get("contract_release_id") == "weekly_etf_shared_contract_v1_0_0"
        and donor_pin.get("donor_commit_sha") == "455201b4736dda41df07644d78b6797282a29fc7"
        and donor_pin.get("mutable_donor_branch_allowed") is False
    )
    if not pin_valid:
        blockers.append("immutable_donor_pin_invalid")

    stage_1_state = stage_1_operational_state or {}
    if stage_1_state.get("stage_1_authorized") is not True:
        blockers.append("stage_1_not_authorized")
    if stage_1_state.get("stage_1_applied_to_official_state") is not True:
        blockers.append("stage_1_not_applied_to_official_state")
    if stage_1_state.get("stage_1_receipt_confirmed") is not True:
        blockers.append("stage_1_receipt_not_confirmed")
    if not stage_1_state.get("official_post_stage_1_state_path"):
        blockers.append("official_post_stage_1_state_missing")

    grade_map = {
        "identity_grade": str(gates.get("destination_identity_grade_required")),
        "document_grade": str(gates.get("destination_document_grade_required")),
        "valuation_grade": str(gates.get("destination_valuation_grade_required")),
        "tradability_grade": str(gates.get("destination_tradability_grade_required")),
    }
    for grade_name, required in grade_map.items():
        grade = product_row.get(grade_name) if isinstance(product_row.get(grade_name), dict) else {}
        if grade.get("status") != required:
            blockers.append(f"destination_{grade_name}_not_{required}")
    if product_row.get("activation_ready") is not True:
        blockers.append("destination_not_activation_ready")

    if sync_row.get("shared_desired_direction") != "add_candidate":
        blockers.append("donor_add_direction_not_confirmed")
    if euna_review.get("schema_version") != "etf_eu_euna_risk_budget_review_v1":
        blockers.append("euna_risk_budget_review_missing_or_invalid")
    if euna_decision.get("stage_1_decision_valid") is not True:
        blockers.append("euna_risk_budget_decision_invalid")
    if euna_decision.get("stage_2_automatic_sale") is not False:
        blockers.append("euna_automatic_sale_boundary_invalid")

    authorization = activation_authorization or {}
    if authorization.get("stage_2_activation_authorized") is not True:
        blockers.append("separate_stage_2_activation_authorization_missing")

    if theoretical_target < num(limits.get("minimum_trade_size_pct_nav")):
        blockers.append("minimum_stage_2_trade_size_not_met")
    if remaining > 0.0001:
        blockers.append("governed_funding_capacity_insufficient")

    readiness = "ready_for_separate_activation_review" if not blockers else "blocked"
    executable_intents: list[dict[str, Any]] = []

    return {
        "schema_version": "etf_eu_stage_2_readiness_v1",
        "artifact_type": "etf_eu_stage_2_transition_readiness",
        "generated_at_utc": utc_now(),
        "contract_release_id": donor_pin.get("contract_release_id"),
        "donor_commit_sha": donor_pin.get("donor_commit_sha"),
        "destination": {
            "exposure_id": exposure_id,
            "ticker": ticker,
            "isin": destination.get("isin"),
            "exchange": destination.get("exchange"),
            "currency": destination.get("currency"),
            "donor_target_weight_pct_nav": round(donor_target_weight, 6),
            "stage_2_maximum_weight_pct_nav": round(destination_cap, 6),
        },
        "current_shadow_state": {
            "stage_1_projected_cash_weight_pct_nav": round(current_cash_weight, 6),
            "stage_1_projected_position_count": summary.get("position_count"),
            "sxr8_weight_pct_nav": round(sxr8_weight, 6),
            "euna_weight_pct_nav": round(num(euna_review.get("current_euna_weight_pct")), 6),
        },
        "capacity_analysis": source_capacity,
        "funding_source_order": [
            {
                "priority": 1,
                "source_id": "excess_cash_above_floor",
                "simulated_capacity_pct_nav": round(excess_cash_capacity, 6),
                "simulated_use_pct_nav": round(cash_source, 6),
            },
            {
                "priority": 2,
                "source_id": "sxr8_overlap_reduction",
                "simulated_capacity_pct_nav": round(sxr8_cap, 6),
                "simulated_use_pct_nav": round(sxr8_source, 6),
            },
            {
                "priority": 3,
                "source_id": "euna_risk_budget_release",
                "simulated_capacity_pct_nav": 0.0,
                "simulated_use_pct_nav": 0.0,
                "available": euna_release_available,
            },
        ],
        "entry_gate_results": {
            "immutable_donor_pin_pass": pin_valid,
            "stage_1_operational_state_pass": not any(code.startswith("stage_1_") or code == "official_post_stage_1_state_missing" for code in blockers),
            "destination_identity_pass": ((product_row.get("identity_grade") or {}).get("status") == "pass"),
            "destination_document_pass": ((product_row.get("document_grade") or {}).get("status") == "pass"),
            "destination_valuation_pass": ((product_row.get("valuation_grade") or {}).get("status") == "pass"),
            "destination_tradability_pass": ((product_row.get("tradability_grade") or {}).get("status") == "pass"),
            "destination_activation_ready": product_row.get("activation_ready") is True,
            "donor_add_direction_pass": sync_row.get("shared_desired_direction") == "add_candidate",
            "euna_risk_budget_pass": euna_decision.get("stage_1_decision_valid") is True and euna_decision.get("stage_2_automatic_sale") is False,
            "separate_activation_authorization_pass": authorization.get("stage_2_activation_authorized") is True,
        },
        "readiness": readiness,
        "blockers": sorted(set(blockers)),
        "executable_trade_intents": executable_intents,
        "rollback": policy.get("rollback"),
        "interpretation_boundary": "Capacity analysis only. No official Stage-1 state, accepted IXUA cutover evidence or Stage-2 authorization is present.",
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
        "activation_authority": False,
        "production_delivery_authority": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build ETF EU Stage-2 readiness artifact")
    parser.add_argument("--allocator", type=Path, required=True)
    parser.add_argument("--sync-shadow", type=Path, required=True)
    parser.add_argument("--product-evidence", type=Path, required=True)
    parser.add_argument("--euna-review", type=Path, required=True)
    parser.add_argument("--donor-pin", type=Path, default=Path("config/weekly_etf_donor_contract_pin.json"))
    parser.add_argument("--policy", type=Path, default=Path("config/etf_eu_stage_2_transition_policy_v1.yml"))
    parser.add_argument("--stage-1-operational-state", type=Path)
    parser.add_argument("--activation-authorization", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    stage_1_state = load_json(args.stage_1_operational_state) if args.stage_1_operational_state else None
    authorization = load_json(args.activation_authorization) if args.activation_authorization else None
    payload = build(
        load_json(args.allocator),
        load_json(args.sync_shadow),
        load_yaml(args.product_evidence),
        load_json(args.euna_review),
        load_json(args.donor_pin),
        load_yaml(args.policy),
        stage_1_state,
        authorization,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
