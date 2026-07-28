from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


STAGE_1_CANDIDATES = {"ai_compute_infrastructure", "cyber_security"}
ALLOWLIST_BLOCKER = "stage_1_candidate_not_allowlisted"


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Allocator artifact must be a JSON object")
    return payload


def num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def validate(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_eu_target_allocator_shadow_v3":
        blockers.append("unexpected schema_version")
    authority = payload.get("authority") if isinstance(payload.get("authority"), dict) else {}
    for key in ("portfolio_mutation", "funding_authority", "execution_authority", "production_delivery_authority"):
        if authority.get(key) is not False:
            blockers.append(f"authority {key} must be false")
    if payload.get("preferred_shadow_variant") != "staged_policy_driven_v1":
        blockers.append("policy-driven variant is not preferred")

    policy = payload.get("policy_contract") if isinstance(payload.get("policy_contract"), dict) else {}
    stage = policy.get("stage_1") if isinstance(policy.get("stage_1"), dict) else {}
    if policy.get("schema_version") != "etf_eu_transition_policy_v1":
        blockers.append("transition policy contract missing")
    expected_limits = {
        "maximum_positions": 8.0,
        "maximum_gross_turnover_pct_nav": 25.0,
        "minimum_post_stage_cash_pct_nav": 35.0,
        "maximum_new_direct_position_pct_nav": 15.0,
        "minimum_median_daily_traded_value_eur_20d": 500000.0,
        "maximum_price_age_calendar_days": 7.0,
    }
    for key, expected in expected_limits.items():
        if abs(num(stage.get(key)) - expected) > 0.0001:
            blockers.append(f"unexpected policy limit {key}")
    if set(stage.get("candidate_exposures") or []) != STAGE_1_CANDIDATES:
        blockers.append("Stage-1 candidate exposure allowlist mismatch")
    if stage.get("registry_expansion_must_not_reopen_stage_1_selection") is not True:
        blockers.append("registry-expansion Stage-1 boundary missing")

    variants = {str(row.get("variant_id")): row for row in payload.get("variants") or [] if isinstance(row, dict)}
    required_variants = {"strict_mapped_replication", "efficient_max_eight_positions", "staged_cash_first_50pct", "staged_policy_driven_v1"}
    if not required_variants.issubset(variants):
        blockers.append("required comparison variants missing")
        return blockers
    preferred = variants["staged_policy_driven_v1"]
    if preferred.get("progress_factor") is not None:
        blockers.append("policy-driven variant must not use a fixed progress factor")
    checks = preferred.get("policy_checks") if isinstance(preferred.get("policy_checks"), dict) else {}
    for key in (
        "within_position_limit",
        "within_turnover_cap",
        "minimum_cash_reserve_met",
        "new_position_caps_met",
        "effective_theme_caps_met",
        "incumbents_retained",
        "cash_nonnegative",
    ):
        if checks.get(key) is not True:
            blockers.append(f"policy check failed: {key}")

    summary = preferred.get("summary") if isinstance(preferred.get("summary"), dict) else {}
    if num(summary.get("gross_turnover_pct_nav")) > 25.0001:
        blockers.append("turnover cap exceeded")
    if num(summary.get("projected_cash_weight_pct")) < 34.9999:
        blockers.append("cash reserve below policy")
    if int(num(summary.get("position_count"))) > 8:
        blockers.append("position limit exceeded")
    if num(summary.get("gross_sell_value_eur")) != 0:
        blockers.append("stage one may not sell incumbents")

    rows = {str(row.get("exposure_id")): row for row in preferred.get("allocation_rows") or [] if isinstance(row, dict)}
    for exposure_id in STAGE_1_CANDIDATES:
        row = rows.get(exposure_id)
        if not row or row.get("selected") is not True:
            blockers.append(f"eligible stage-one exposure not selected: {exposure_id}")
            continue
        if ALLOWLIST_BLOCKER in (row.get("blockers") or []):
            blockers.append(f"allowlisted exposure received allowlist blocker: {exposure_id}")
        shares = num((row.get("order") or {}).get("target_shares"))
        if shares <= 0 or abs(shares - round(shares)) > 0.000001:
            blockers.append(f"whole-share order missing: {exposure_id}")
        if num(row.get("variant_target_weight_pct")) > 15.0001:
            blockers.append(f"direct position cap exceeded: {exposure_id}")
        if num(row.get("effective_post_stage_exposure_lower_bound_pct_nav")) > num(row.get("effective_theme_cap_pct_nav")) + 0.0001:
            blockers.append(f"effective theme cap exceeded: {exposure_id}")
    ai = rows.get("ai_compute_infrastructure") or {}
    if num(ai.get("embedded_incumbent_exposure_lower_bound_pct_nav")) <= 0:
        blockers.append("embedded incumbent semiconductor exposure was not applied")

    for exposure_id, row in rows.items():
        if exposure_id not in STAGE_1_CANDIDATES:
            if row.get("selected") is True:
                blockers.append(f"non-allowlisted exposure selected in Stage 1: {exposure_id}")
            if num((row.get("order") or {}).get("target_shares")) > 0:
                blockers.append(f"non-allowlisted exposure received shares: {exposure_id}")
            if ALLOWLIST_BLOCKER not in (row.get("blockers") or []):
                blockers.append(f"non-allowlisted exposure missing policy blocker: {exposure_id}")
        if row.get("selected") is not True and num((row.get("order") or {}).get("target_shares")) > 0:
            blockers.append(f"unselected exposure received shares: {exposure_id}")
        if row.get("eligible") is not True and num((row.get("order") or {}).get("target_shares")) > 0:
            blockers.append(f"ineligible exposure received shares: {exposure_id}")

    ixua = rows.get("non_us_developed_equities") or {}
    if ixua.get("selected") is True or num((ixua.get("order") or {}).get("target_shares")) > 0:
        blockers.append("IXUA entered Stage 1 after registry expansion")
    if ALLOWLIST_BLOCKER not in (ixua.get("blockers") or []):
        blockers.append("IXUA Stage-1 policy blocker missing")

    legacy = [row for row in preferred.get("legacy_rows") or [] if isinstance(row, dict)]
    if {str(row.get("ticker")) for row in legacy} != {"VWCE", "EUNA", "SXR8"}:
        blockers.append("legacy position set changed")
    if any(row.get("side") != "HOLD" or num(row.get("share_delta")) != 0 for row in legacy):
        blockers.append("incumbent hold boundary violated")

    overlap = payload.get("incumbent_overlap_review") if isinstance(payload.get("incumbent_overlap_review"), dict) else {}
    if overlap.get("schema_version") != "etf_eu_incumbent_overlap_review_v1":
        blockers.append("overlap review lineage missing")
    if not preferred.get("stage_2_entry_conditions"):
        blockers.append("stage-two entry conditions missing")
    if not preferred.get("stage_2_source_priority"):
        blockers.append("stage-two source priority missing")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    payload = load(args.artifact)
    blockers = validate(payload)
    print(json.dumps({"valid": not blockers, "blockers": blockers}, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
