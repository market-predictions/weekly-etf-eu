from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import validate_etf_eu_target_allocator_shadow as base_validator


FROZEN_EXPOSURES = {"ai_compute_infrastructure", "cyber_security"}
FROZEN_BLOCKER = "comparison_candidate_not_in_frozen_set"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    payload = base_validator.load(args.artifact)
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_eu_target_allocator_shadow_v2":
        blockers.append("unexpected schema_version")
    compatibility = dict(payload)
    compatibility["schema_version"] = "etf_eu_target_allocator_shadow_v1"
    blockers.extend(base_validator.validate(compatibility))

    policy = payload.get("eligibility_policy") if isinstance(payload.get("eligibility_policy"), dict) else {}
    if policy.get("recomputed_from_current_candidate_and_transition_evidence") is not True:
        blockers.append("current evidence recomputation policy missing")
    if policy.get("stale_sync_reason_codes_are_not_inherited") is not True:
        blockers.append("stale synchronization reason isolation missing")
    if float(policy.get("minimum_median_daily_traded_value_eur_20d") or 0) < 500000:
        blockers.append("liquidity threshold below required floor")
    if policy.get("product_structure_review_blocks_allocation") is not True:
        blockers.append("product structure review gate missing")
    if set(policy.get("comparison_candidate_exposures_frozen") or []) != FROZEN_EXPOSURES:
        blockers.append("frozen comparison candidate set mismatch")
    if policy.get("registry_expansion_must_not_change_comparison_compositions") is not True:
        blockers.append("comparison-invariance boundary missing")
    if policy.get("non_frozen_candidate_blocker") != FROZEN_BLOCKER:
        blockers.append("frozen-set blocker code mismatch")

    scope = payload.get("comparison_scope") if isinstance(payload.get("comparison_scope"), dict) else {}
    if set(scope.get("frozen_candidate_exposures") or []) != FROZEN_EXPOSURES:
        blockers.append("comparison scope does not record the frozen exposure set")
    if scope.get("registry_expansion_must_not_change_comparison_compositions") is not True:
        blockers.append("comparison scope invariance flag missing")

    for variant in payload.get("variants") or []:
        if not isinstance(variant, dict):
            continue
        variant_id = str(variant.get("variant_id") or "")
        rows = {
            str(row.get("exposure_id")): row
            for row in variant.get("allocation_rows") or []
            if isinstance(row, dict) and row.get("exposure_id")
        }
        for exposure_id, row in rows.items():
            row_blockers = set(row.get("blockers") or [])
            shares = float((row.get("order") or {}).get("target_shares") or 0)
            if ("liquidity_below_threshold" in row_blockers or "product_structure_review_required" in row_blockers) and shares > 0:
                blockers.append(f"{variant_id}:{exposure_id}: gated exposure received shares")
            if exposure_id not in FROZEN_EXPOSURES:
                if FROZEN_BLOCKER not in row_blockers:
                    blockers.append(f"{variant_id}:{exposure_id}: frozen-set blocker missing")
                if shares > 0:
                    blockers.append(f"{variant_id}:{exposure_id}: non-frozen exposure received shares")
                if row.get("selected") is True:
                    blockers.append(f"{variant_id}:{exposure_id}: non-frozen exposure selected")
            elif FROZEN_BLOCKER in row_blockers:
                blockers.append(f"{variant_id}:{exposure_id}: frozen exposure received frozen-set blocker")

        ixua = rows.get("non_us_developed_equities") or {}
        if float((ixua.get("order") or {}).get("target_shares") or 0) > 0:
            blockers.append(f"{variant_id}: IXUA entered frozen comparison composition")
        if ixua and FROZEN_BLOCKER not in set(ixua.get("blockers") or []):
            blockers.append(f"{variant_id}: IXUA frozen-set blocker missing")

    print(json.dumps({"valid": not blockers, "blockers": blockers}, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
