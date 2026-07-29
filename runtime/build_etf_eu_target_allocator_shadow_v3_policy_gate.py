from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import build_etf_eu_target_allocator_shadow_v3 as base


BLOCKER = "stage_1_candidate_not_allowlisted"


def install_candidate_gate(policy: dict[str, Any]) -> set[str]:
    stage = policy.get("stage_1") if isinstance(policy.get("stage_1"), dict) else {}
    allowlist = {
        str(value)
        for value in stage.get("candidate_exposures") or []
        if str(value)
    }
    if allowlist != {"ai_compute_infrastructure", "cyber_security"}:
        raise RuntimeError("Stage-1 candidate exposure set is missing or unexpected")
    if stage.get("registry_expansion_must_not_reopen_stage_1_selection") is not True:
        raise RuntimeError("Registry-expansion Stage-1 boundary is missing")

    original_eligibility = base.eligibility

    def gated_eligibility(
        row: dict[str, Any],
        evidence: dict[str, Any],
        stage_policy: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        eligible, blockers = original_eligibility(row, evidence, stage_policy)
        exposure_id = str(row.get("exposure_id") or "")
        blockers = list(blockers)
        if exposure_id not in allowlist:
            blockers.append(BLOCKER)
        blockers = sorted(set(blockers))
        return not blockers, blockers

    base.eligibility = gated_eligibility
    return allowlist


def main() -> None:
    parser = argparse.ArgumentParser(description="Build policy-gated EU target allocator shadow")
    parser.add_argument("--base-allocator", type=Path, required=True)
    parser.add_argument("--sync-shadow", type=Path, required=True)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--transition-evidence", type=Path, required=True)
    parser.add_argument("--overlap-review", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=Path("config/etf_eu_transition_policy_v1.yml"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    policy = base.load_yaml(args.policy)
    install_candidate_gate(policy)
    base.build(
        base.load_json(args.base_allocator),
        base.load_json(args.sync_shadow),
        base.load_json(args.portfolio_state),
        base.load_json(args.transition_evidence),
        base.load_json(args.overlap_review),
        policy,
        args.output,
    )


if __name__ == "__main__":
    main()
