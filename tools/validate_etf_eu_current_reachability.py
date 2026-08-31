#!/usr/bin/env python3
"""Fail closed if executable ETF EU roots can still reach retired architecture."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

WORKFLOW_DIR = Path(".github/workflows")
CURRENT_BUILDER = Path("tools/build_etf_eu_thin_kernel_package.py")
RUNTIME_DIR = Path("runtime")
CURRENT_RUNTIME_DIR = RUNTIME_DIR / "current"
CONTROLLED_TRANSPORT_WORKFLOW = Path(".github/workflows/send-weekly-etf-eu-controlled-transport.yml")

REQUIRED_TOP_LEVEL_RUNTIME_FILES = (
    "__init__.py",
    "adapt_weekly_etf_macro_for_eu.py",
    "check_etf_eu_delivery_receipt.py",
    "send_etf_eu_controlled_report.py",
    "write_etf_eu_delivery_evidence.py",
)
ALLOWED_TOP_LEVEL_RUNTIME_DIRS = ("current",)

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

CONTROLLED_TRANSPORT_REQUIRED_MARKERS = (
    "Require main delivery surface",
    "validate_etf_eu_guarded_delivery_authority.py",
    "confirm_guarded_send_second",
    "Verify approved commit is in current main lineage",
    "runtime.send_etf_eu_controlled_report",
    "--stage post",
    "runtime.check_etf_eu_delivery_receipt",
    "Persist controlled transport evidence",
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


def _validate_runtime_namespace() -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    if not RUNTIME_DIR.exists():
        return [{"type": "runtime_namespace_missing", "path": str(RUNTIME_DIR), "token": ""}]

    required = set(REQUIRED_TOP_LEVEL_RUNTIME_FILES)
    allowed_dirs = set(ALLOWED_TOP_LEVEL_RUNTIME_DIRS)
    present_files = {path.name for path in RUNTIME_DIR.iterdir() if path.is_file()}
    present_dirs = {path.name for path in RUNTIME_DIR.iterdir() if path.is_dir() and path.name != "__pycache__"}

    for name in sorted(required - present_files):
        blockers.append({
            "type": "required_runtime_helper_missing",
            "path": str(RUNTIME_DIR / name),
            "token": name,
        })
    for name in sorted(present_files - required):
        blockers.append({
            "type": "unexpected_top_level_runtime_executor",
            "path": str(RUNTIME_DIR / name),
            "token": name,
        })
    for name in sorted(present_dirs - allowed_dirs):
        blockers.append({
            "type": "unexpected_top_level_runtime_directory",
            "path": str(RUNTIME_DIR / name),
            "token": name,
        })
    for name in sorted(allowed_dirs - present_dirs):
        blockers.append({
            "type": "required_runtime_directory_missing",
            "path": str(RUNTIME_DIR / name),
            "token": name,
        })
    return blockers


def _validate_controlled_transport_main_write(workflows: list[Path]) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    if CONTROLLED_TRANSPORT_WORKFLOW not in workflows:
        blockers.append({
            "type": "controlled_transport_missing",
            "path": str(CONTROLLED_TRANSPORT_WORKFLOW),
            "token": "",
        })
        return blockers
    text = CONTROLLED_TRANSPORT_WORKFLOW.read_text(encoding="utf-8", errors="replace")
    folded = text.casefold()
    for marker in CONTROLLED_TRANSPORT_REQUIRED_MARKERS:
        if marker.casefold() not in folded:
            blockers.append({
                "type": "controlled_transport_main_write_guard_missing",
                "path": str(CONTROLLED_TRANSPORT_WORKFLOW),
                "token": marker,
            })
    return blockers


def validate() -> dict[str, object]:
    blockers: list[dict[str, str]] = []
    workflows = _active_workflows()
    current_roots = [CURRENT_BUILDER]
    if CURRENT_RUNTIME_DIR.exists():
        current_roots.extend(sorted(CURRENT_RUNTIME_DIR.glob("*.py")))

    missing = [str(path) for path in (CURRENT_BUILDER, CURRENT_RUNTIME_DIR) if not path.exists()]
    blockers.extend({"type": "missing_current_root", "path": path, "token": ""} for path in missing)
    blockers.extend(_validate_runtime_namespace())

    blockers.extend(_scan(workflows + current_roots, RETIRED_EXECUTOR_TOKENS, "retired_executor_reachable"))

    non_transport_workflows = [path for path in workflows if path != CONTROLLED_TRANSPORT_WORKFLOW]
    blockers.extend(_scan(non_transport_workflows, FORBIDDEN_AUTHORITY_TOKENS, "direct_main_write_reachable"))
    blockers.extend(_validate_controlled_transport_main_write(workflows))

    blockers.extend(_scan(workflows + current_roots, ARCHIVE_IMPORT_TOKENS, "archive_execution_reachable"))

    result = {
        "schema_version": "etf_eu_current_reachability_v3",
        "valid": not blockers,
        "verdict": "PASS" if not blockers else "FAIL",
        "active_workflow_count": len(workflows),
        "current_runtime_module_count": len([path for path in current_roots if path.parent == CURRENT_RUNTIME_DIR]),
        "runtime_namespace": {
            "required_top_level_files": list(REQUIRED_TOP_LEVEL_RUNTIME_FILES),
            "allowed_top_level_directories": list(ALLOWED_TOP_LEVEL_RUNTIME_DIRS),
        },
        "retired_executor_tokens": list(RETIRED_EXECUTOR_TOKENS),
        "controlled_transport_main_write_exception": {
            "workflow": str(CONTROLLED_TRANSPORT_WORKFLOW),
            "scope": "post_transport_delivery_and_receipt_evidence_only",
            "required_markers": list(CONTROLLED_TRANSPORT_REQUIRED_MARKERS),
        },
        "blockers": blockers,
    }
    return result


def main() -> int:
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
