from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime import build_etf_eu_target_allocator_shadow as allocator


MIN_MEDIAN_DAILY_TRADED_VALUE_EUR = 500_000.0


def eligible_target(row: dict[str, Any], evidence: dict[str, Any]) -> tuple[bool, list[str]]:
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
    if evidence.get("status") != "priced_non_authoritative" or evidence.get("completed_close") is not True:
        blockers.append("pricing_missing_or_stale")
    if allocator.num(evidence.get("close_price")) <= 0:
        blockers.append("pricing_missing_or_stale")
    if allocator.num(evidence.get("median_daily_traded_value_eur_20d")) < MIN_MEDIAN_DAILY_TRADED_VALUE_EUR:
        blockers.append("liquidity_below_threshold")
    if str(evidence.get("candidate_role")) == "donor_target_structure_review":
        blockers.append("product_structure_review_required")
    return not blockers, sorted(set(blockers))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync-shadow", type=Path, required=True)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--transition-evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cost-bps", type=float, default=10.0)
    parser.add_argument("--position-limit", type=int, default=8)
    args = parser.parse_args()

    allocator.eligible_target = eligible_target
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
    }
    args.output.write_text(__import__("json").dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
