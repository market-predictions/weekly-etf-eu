#!/usr/bin/env python3
"""Fail closed if executable ETF EU roots can still reach retired architecture.

This is intentionally a small textual reachability audit. The architecture has a tiny
set of executable roots; retired modules may exist temporarily during migration, but
no active workflow or current builder may call them. Once no current references remain,
those retired modules can be deleted with Git history as provenance.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

WORKFLOW_DIR = Path(".github/workflows")
CURRENT_BUILDER = Path("tools/build_etf_eu_thin_kernel_package.py")
CURRENT_RUNTIME_DIR = Path("runtime/current")

RETIRED_EXECUTOR_TOKENS = (
    "build_etf_eu_client_grade_report_state_v2",
    "apply_etf_eu_current_reunderwriting",
    "apply_etf_eu_donor_parity_contract",
    "build_etf_eu_donor_discovery_bridge",
    "build_etf_eu_routine_report_package_v2",
    "build_etf_eu_routine_report_package.py",
    "render_etf_eu_client_grade_v2_funded",
    "polish_etf_eu_client_grade_html",
    "finalize_etf_eu_client_surface_semantics",
    "finalize_etf_eu_markdown_semantics",
    "reconcile_etf_eu_funded_markdown",
    "synchronize_etf_eu",
    "scrub_etf_eu",
    "fix_etf_eu",
    "build_etf_eu_target_allocation_envelope",
)

FORBIDDEN_AUTHORITY_TOKENS = (
    "git push origin main",
    "git push origin HEAD:main",
)

ARCHIVE_IMPORT_TOKENS = (
    "archive.workflows",
    "archive/workflows/",
)


def _active_workflows() -> list[Path]:
    if not WORKFLOW_DIR.exists():
        return []
    return sorted(
        path for path in WORKFLOW_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}
    )


def _scan(paths: Iterable[Path], tokens: tuple[str, ...], blocker_type: str) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        folded = text.casefold()
        for token in tokens:
            if token.casefold() in folded:
                blockers.append({"type": blocker_type, "path": str(path), "token": token})
    return blockers


def validate() -> dict[str, object]:
    blockers: list[dict[str, str]] = []
    workflows = _active_workflows()
    current_roots = [CURRENT_BUILDER]
    if CURRENT_RUNTIME_DIR.exists():
        current_roots.extend(sorted(CURRENT_RUNTIME_DIR.glob("*.py")))

    missing = [str(path) for path in (CURRENT_BUILDER, CURRENT_RUNTIME_DIR) if not path.exists()]
    blockers.extend({"type": "missing_current_root", "path": path, "token": ""} for path in missing)

    # Retired semantic/state/allocator executors are forbidden from every active
    # workflow and from the Thin Current Kernel itself.
    blockers.extend(_scan(workflows + current_roots, RETIRED_EXECUTOR_TOKENS, "retired_executor_reachable"))
    blockers.extend(_scan(workflows, FORBIDDEN_AUTHORITY_TOKENS, "direct_main_write_reachable"))
    blockers.extend(_scan(workflows + current_roots, ARCHIVE_IMPORT_TOKENS, "archive_execution_reachable"))

    result = {
        "schema_version": "etf_eu_current_reachability_v1",
        "valid": not blockers,
        "verdict": "PASS" if not blockers else "FAIL",
        "active_workflow_count": len(workflows),
        "current_runtime_module_count": len([path for path in current_roots if path.parent == CURRENT_RUNTIME_DIR]),
        "retired_executor_tokens": list(RETIRED_EXECUTOR_TOKENS),
        "blockers": blockers,
    }
    return result


def main() -> int:
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
