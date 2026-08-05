from __future__ import annotations

import json
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


def routine_state_path(manifest_path: Path) -> Path:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifacts = payload.get("state_artifacts") if isinstance(payload.get("state_artifacts"), dict) else {}
    record = artifacts.get("production_convergence_state")
    if not isinstance(record, dict) or not record.get("path"):
        raise RuntimeError("Routine manifest does not bind a convergence-state path")
    state_path = Path(str(record["path"]))
    if not state_path.is_file():
        raise RuntimeError(f"Routine convergence-state file is unavailable: {state_path}")
    return state_path


def run_with_activated_allocation_surface(
    *args: str,
    cwd: Path = legacy.ROOT,
    capture: bool = False,
) -> str:
    routed = list(args)
    if routed:
        routed[0] = ROUTES.get(routed[0], routed[0])
    if routed and routed[0] == "tools/validate_etf_eu_converged_routine_manifest.py":
        if len(routed) < 2:
            raise RuntimeError("Routine manifest validator invocation is missing the manifest path")
        if "--state" not in routed:
            routed.extend(["--state", str(routine_state_path(Path(routed[1])))])
    return run_with_compact_model_proposal(*routed, cwd=cwd, capture=capture)


def main() -> None:
    legacy.run = run_with_activated_allocation_surface
    legacy.main()


if __name__ == "__main__":
    main()
