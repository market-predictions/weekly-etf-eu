from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime import build_etf_eu_target_allocator_shadow as allocator


MIN_MEDIAN_DAILY_TRADED_VALUE_EUR = 500_000.0
FROZEN_COMPARISON_CANDIDATES = {"ai_compute_infrastructure", "cyber_security"}
FROZEN_SET_BLOCKER = "comparison_candidate_not_in_frozen_set"


def load_policy(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected YAML object: {path}")
    return payload


def validate_comparison_scope(policy: dict[str, Any]) -> set[str]:
    section = policy.get("comparison_variants") if isinstance(policy.get("comparison_variants"), dict) else {}
    frozen = {str(value) for value in section.get("frozen_candidate_exposures") or [] if str(value)}
    if frozen != FROZEN_COMPARISON_CANDIDATES:
        raise RuntimeError("Frozen comparison candidate set is missing or unexpected")
    if section.get("registry_expansion_must_not_change_comparison_compositions") is not True:
        raise RuntimeError("Comparison-invariance policy boundary is missing")
    return frozen


def base_eligibility(row: dict[str, Any], evidence: dict[str, Any]) -> tuple[bool, list[str]]:
    blockers: list[str] = []
    candidate = row.get("preferred_ucits_candidate") if isinstance(row.get("preferred_ucits_candidate"), dict) else None
    if not candidate:
        blockers.append("no_ucits_equivalent")
    else:
        if candidate.get("instrument_type") != "UCITS ETF":
            blockers.append("product_type_blocked")
        if candidate.get("priips_kid_status") != "available":
            blockers.append("kid_missing")
        if not allocator.candidate_line(row):
            blockers.append("trading_line_unverified")
    status = str(evidence.get("status") or "")
    if not status.startswith("priced_") or evidence.get("completed_close") is not True:
        blockers.append("pricing_missing_or_stale")
    if allocator.num(evidence.get("close_price")) <= 0:
        blockers.append("pricing_missing_or_stale")
    if allocator.num(evidence.get("median_daily_traded_value_eur_20d")) < MIN_MEDIAN_DAILY_TRADED_VALUE_EUR:
        blockers.append("liquidity_below_threshold")
    if str(evidence.get("candidate_role")) == "donor_target_structure_review":
        blockers.append("product_structure_review_required")
    blockers = sorted(set(blockers))
    return not blockers, blockers


def frozen_eligibility(
    row: dict[str, Any],
    evidence: dict[str, Any],
    frozen: set[str],
) -> tuple[bool, list[str]]:
    _eligible, blockers = base_eligibility(row, evidence)
    blockers = list(blockers)
    if str(row.get("exposure_id") or "") not in frozen:
        blockers.append(FROZEN_SET_BLOCKER)
    blockers = sorted(set(blockers))
    return not blockers, blockers


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

    policy = load_policy(args.policy)
    frozen = validate_comparison_scope(policy)

    def eligibility(row: dict[str, Any], evidence: dict[str, Any]) -> tuple[bool, list[str]]:
        return frozen_eligibility(row, evidence, frozen)

    allocator.eligible_target = eligibility
    sync = allocator.load(args.sync_shadow)
    portfolio = allocator.load(args.portfolio_state)
    evidence = allocator.load(args.transition_evidence)
    allocator.build(sync, portfolio, evidence, args.output, args.cost_bps, args.position_limit)

    payload = allocator.load(args.output)
    payload["schema_version"] = "etf_eu_target_allocator_shadow_v2"
    payload["eligibility_policy"] = {
        "recomputed_from_current_candidate_and_transition_evidence": True,
        "stale_sync_reason_codes_are_not_inherited": True,
        "minimum_median_daily_traded_value_eur_20d": MIN_MEDIAN_DAILY_TRADED_VALUE_EUR,
        "product_structure_review_blocks_allocation": True,
        "dated_non_authoritative_cache_may_satisfy_shadow_pricing_gate": True,
        "cached_evidence_does_not_create_funding_authority": True,
        "comparison_candidate_exposures_frozen": sorted(frozen),
        "registry_expansion_must_not_change_comparison_compositions": True,
        "non_frozen_candidate_blocker": FROZEN_SET_BLOCKER,
    }
    payload["comparison_scope"] = policy.get("comparison_variants")
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
