from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools import validate_etf_eu_target_allocator_shadow as base_validator


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
    for variant in payload.get("variants") or []:
        if not isinstance(variant, dict):
            continue
        for row in variant.get("allocation_rows") or []:
            if not isinstance(row, dict):
                continue
            blockers_for_row = set(row.get("blockers") or [])
            shares = float((row.get("order") or {}).get("target_shares") or 0)
            if ("liquidity_below_threshold" in blockers_for_row or "product_structure_review_required" in blockers_for_row) and shares > 0:
                blockers.append(f"{variant.get('variant_id')}:{row.get('exposure_id')}: gated exposure received shares")
    print(json.dumps({"valid": not blockers, "blockers": blockers}, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
