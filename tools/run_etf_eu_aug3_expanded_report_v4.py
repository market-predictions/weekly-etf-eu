from __future__ import annotations

from pathlib import Path

from tools import run_etf_eu_aug3_expanded_report as legacy
from tools.run_etf_eu_aug3_expanded_report_v3 import run_with_reconciled_stage1


def run_with_client_safe_proposal_language(
    *args: str,
    cwd: Path = legacy.ROOT,
    capture: bool = False,
) -> str:
    routed = list(args)
    if routed and routed[0] == "runtime/add_etf_eu_current_close_monitor.py":
        routed[0] = "runtime/add_etf_eu_expanded_allocation_monitor_v2.py"
    return run_with_reconciled_stage1(*routed, cwd=cwd, capture=capture)


def main() -> None:
    legacy.run = run_with_client_safe_proposal_language
    legacy.main()


if __name__ == "__main__":
    main()
