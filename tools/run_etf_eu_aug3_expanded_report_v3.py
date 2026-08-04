from __future__ import annotations

from pathlib import Path

from tools import run_etf_eu_aug3_expanded_report as legacy
from tools.run_etf_eu_aug3_expanded_report_v2 import run_with_rollover_safe_pricing


def run_with_reconciled_stage1(
    *args: str,
    cwd: Path = legacy.ROOT,
    capture: bool = False,
) -> str:
    routed = list(args)
    if routed and routed[0] == "runtime/add_etf_eu_current_close_monitor.py":
        routed[0] = "runtime/add_etf_eu_expanded_allocation_monitor.py"
    result = run_with_rollover_safe_pricing(*routed, cwd=cwd, capture=capture)
    if args and args[0] == "runtime/apply_etf_eu_routine_valuation_to_convergence_state.py":
        state_path = args[1]
        run_with_rollover_safe_pricing(
            "runtime/reconcile_etf_eu_stage1_current_evidence.py",
            state_path,
            "--allocator",
            "output/routine_preview/sync/etf_eu_target_allocator_shadow.json",
            cwd=legacy.ROOT,
            capture=False,
        )
    return result


def main() -> None:
    legacy.run = run_with_reconciled_stage1
    legacy.main()


if __name__ == "__main__":
    main()
