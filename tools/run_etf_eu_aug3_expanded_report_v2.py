from __future__ import annotations

from pathlib import Path
from typing import Any

from tools import run_etf_eu_aug3_expanded_report as legacy


_original_run = legacy.run


def run_with_rollover_safe_pricing(
    *args: str,
    cwd: Path = legacy.ROOT,
    capture: bool = False,
) -> str:
    routed = list(args)
    if routed and routed[0] == "pricing/build_current_session_close_results.py":
        routed[0] = "pricing/build_current_session_close_results_v2.py"
    return _original_run(*routed, cwd=cwd, capture=capture)


def main() -> None:
    legacy.run = run_with_rollover_safe_pricing
    legacy.main()


if __name__ == "__main__":
    main()
