from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import build_etf_eu_target_allocator_shadow as allocator
from runtime import build_etf_eu_target_allocator_shadow_v2 as v2


BLOCKER = "comparison_candidate_not_in_frozen_set"


def load_yaml(path: Path) -> dict[str, Any]:
    import yaml

    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected YAML object: {path}")
    return payload


def frozen_candidate_set(policy: dict[str, Any]) -> set[str]:
    section = policy.get("comparison_variants") if isinstance(policy.get("comparison_variants"), dict) else {}
    frozen = {str(value) for value in section.get("frozen_candidate_exposures") or [] if str(value)}
    if frozen != {"ai_compute_infrastructure", "cyber_security"}:
        raise RuntimeError("Frozen comparison candidate set is missing or unexpected")
    if section.get("registry_expansion_must_not_change_comparison_compositions") is not True:
        raise RuntimeError("Comparison-invariance policy boundary is missing")
    return frozen


def main() -> None:
    parser = argparse.ArgumentParser(description="Build frozen-universe v2 comparison allocator")
    parser.add_argument("--sync-shadow", type=Path, required=True)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--transition-evidence", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=Path("config/etf_eu_transition_policy_v1.yml"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cost-bps", type=float, default=10.0)
    parser.add_argument("--position-limit", type=int, default=8)
    args = parser.parse_args()

    policy = load_yaml(args.policy)
    frozen = frozen_candidate_set(policy)
    original_eligibility = v2.eligible_target

    def frozen_eligibility(row: dict[str, Any], evidence: dict[str, Any]) -> tuple[bool, list[str]]:
        eligible, blockers = original_eligibility(row, evidence)
        blockers = list(blockers)
        if str(row.get("exposure_id") or "") not in frozen:
            blockers.append(BLOCKER)
        blockers = sorted(set(blockers))
        return not blockers, blockers

    allocator.eligible_target = frozen_eligibility
    sync = allocator.load(args.sync_shadow)
    portfolio = allocator.load(args.portfolio_state)
    evidence = allocator.load(args.transition_evidence)
    allocator.build(sync, portfolio, evidence, args.output, args.cost_bps, args.position_limit)

    payload = allocator.load(args.output)
    payload["schema_version"] = "etf_eu_target_allocator_shadow_v2"
    payload["eligibility_policy"] = {
        "recomputed_from_current_candidate_and_transition_evidence": True,
        "stale_sync_reason_codes_are_not_inherited": True,
        "minimum_median_daily_traded_value_eur_20d": v2.MIN_MEDIAN_DAILY_TRADED_VALUE_EUR,
        "product_structure_review_blocks_allocation": True,
        "dated_non_authoritative_cache_may_satisfy_shadow_pricing_gate": True,
        "cached_evidence_does_not_create_funding_authority": True,
        "comparison_candidate_exposures_frozen": sorted(frozen),
        "registry_expansion_must_not_change_comparison_compositions": True,
        "non_frozen_candidate_blocker": BLOCKER,
    }
    payload["comparison_scope"] = policy.get("comparison_variants")
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
