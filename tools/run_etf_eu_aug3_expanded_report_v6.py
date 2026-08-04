from __future__ import annotations

from pathlib import Path

from tools import run_etf_eu_aug3_expanded_report as legacy
from tools.run_etf_eu_aug3_expanded_report_v5 import run_with_compact_model_proposal


ROUTES = {
    "runtime/add_etf_eu_current_close_monitor.py": "runtime/add_etf_eu_activated_allocation_surface.py",
    "runtime/build_etf_eu_production_convergence_state.py": "runtime/build_etf_eu_production_convergence_state_v2.py",
    "runtime/apply_etf_eu_routine_valuation_to_client_report.py": "runtime/apply_etf_eu_routine_valuation_to_client_report_v2.py",
    "tools/validate_etf_eu_target_allocator_shadow_v3.py": "tools/validate_etf_eu_target_allocator_shadow_v3_activated.py",
}


def run_with_activated_allocation_surface(
    *args: str,
    cwd: Path = legacy.ROOT,
    capture: bool = False,
) -> str:
    routed = list(args)
    if routed:
        routed[0] = ROUTES.get(routed[0], routed[0])
    return run_with_compact_model_proposal(*routed, cwd=cwd, capture=capture)


def main() -> None:
    legacy.run = run_with_activated_allocation_surface
    legacy.main()


if __name__ == "__main__":
    main()
