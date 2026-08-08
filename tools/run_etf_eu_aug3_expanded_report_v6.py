from __future__ import annotations

from pathlib import Path

from tools import run_etf_eu_aug3_expanded_report as legacy
from tools.run_etf_eu_aug3_expanded_report_v5 import run_with_compact_model_proposal


ROUTES = {
    "runtime/add_etf_eu_current_close_monitor.py": "runtime/add_etf_eu_activated_allocation_surface_v2.py",
    "runtime/build_etf_eu_production_convergence_state.py": "runtime/build_etf_eu_production_convergence_state_v2.py",
    "runtime/apply_etf_eu_routine_valuation_to_client_report.py": "runtime/apply_etf_eu_routine_valuation_to_client_report_v2.py",
    "runtime/finalize_etf_eu_sister_report_nl_language.py": "runtime/finalize_etf_eu_sister_report_nl_language_v2.py",
    "runtime/compact_etf_eu_policy_transition_surface.py": "runtime/compact_etf_eu_policy_transition_surface_v2.py",
    "runtime/promote_etf_eu_sister_report_to_production_candidate.py": "runtime/promote_etf_eu_activated_report_to_production_candidate.py",
    "tools/validate_etf_eu_target_allocator_shadow_v3.py": "tools/validate_etf_eu_target_allocator_shadow_v3_activated.py",
    "tools/run_etf_eu_allocator_report_validation_bundle.py": "tools/run_etf_eu_allocator_report_validation_bundle_v2.py",
}


def value_after(items: list[str], flag: str) -> str:
    try:
        return items[items.index(flag) + 1]
    except (ValueError, IndexError) as exc:
        raise RuntimeError(f"Missing required routed argument: {flag}") from exc


def run_with_activated_allocation_surface(
    *args: str,
    cwd: Path = legacy.ROOT,
    capture: bool = False,
) -> str:
    routed = list(args)
    if routed:
        routed[0] = ROUTES.get(routed[0], routed[0])

    # The release package cannot be built around a merely self-consistent state.
    # First bind the current convergence state to the authoritative allocation
    # envelope and persist a machine-readable PASS/FAIL artifact.
    if routed and routed[0] == "tools/build_etf_eu_converged_routine_package.py":
        state_path = Path(value_after(routed, "--state"))
        stem = state_path.stem
        prefix = "etf_eu_production_convergence_state_"
        run_id = stem[len(prefix):] if stem.startswith(prefix) else stem
        validation_path = legacy.ROOT / "output" / "routine_preview" / f"etf_eu_portfolio_policy_validation_{run_id}.json"
        run_with_compact_model_proposal(
            "tools/validate_etf_eu_portfolio_policy.py",
            "--policy",
            "config/etf_eu_portfolio_policy_v2.yml",
            "--state",
            str(state_path),
            "--output",
            str(validation_path),
            cwd=cwd,
        )
        routed.extend(["--portfolio-policy-validation", str(validation_path)])

    return run_with_compact_model_proposal(*routed, cwd=cwd, capture=capture)


def main() -> None:
    legacy.run = run_with_activated_allocation_surface
    legacy.main()


if __name__ == "__main__":
    main()
