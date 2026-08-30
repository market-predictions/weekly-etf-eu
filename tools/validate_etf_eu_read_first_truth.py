#!/usr/bin/env python3
"""Fail if stable ETF-EU read-first files regain volatile routing snapshots.

This validator is deliberately small: GitHub/control-plane live evidence owns volatile
SHA/issue/PR/claim state. Narrative docs own stable architecture and policy only.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
READ_FIRST = (
    ROOT / "control/SYSTEM_INDEX.md",
    ROOT / "control/CURRENT_STATE.md",
    ROOT / "control/NEXT_ACTIONS.md",
)

FORBIDDEN = {
    "hard-coded main SHA assignment": re.compile(r"(?im)^\s*(?:main_sha|main_baseline)\s*[:=]"),
    "hard-coded current issue assignment": re.compile(r"(?im)^\s*(?:current_report_issue|current_issue)\s*[:=]"),
    "volatile fresh-cycle lifecycle label": re.compile(r"FRESH_REPORT_CYCLE_\d+_(?:ACTIVE|OPEN)"),
    "volatile active issue prose": re.compile(r"(?im)^\s*(?:the\s+)?active\s+(?:fresh-report\s+)?lineage\s+is\s+issue\s+#\d+"),
}


def main() -> int:
    blockers: list[str] = []
    for path in READ_FIRST:
        text = path.read_text(encoding="utf-8")
        for label, pattern in FORBIDDEN.items():
            if pattern.search(text):
                blockers.append(f"{path.relative_to(ROOT)}: {label}")

    state_model = ROOT / "docs/ETF_MINIMUM_STATE_MODEL.md"
    state_text = state_model.read_text(encoding="utf-8")
    if "report-derived explicit state layer" in state_text.lower():
        blockers.append(f"{state_model.relative_to(ROOT)}: retired report-derived authority wording")
    if "output/etf_portfolio_state.json" in state_text:
        blockers.append(f"{state_model.relative_to(ROOT)}: U.S. state filename in EU current state contract")

    roadmap = ROOT / "docs/roadmaps/CURRENT.md"
    if not roadmap.exists():
        blockers.append("docs/roadmaps/CURRENT.md: current roadmap pointer missing")

    architecture = ROOT / "docs/architecture/WEEKLY_ETF_EU_PRODUCT_ARCHITECTURE_V2.md"
    runbook = ROOT / "docs/runbooks/WEEKLY_ETF_EU_REALIZATION_RUNBOOK_V1.md"
    for required in (architecture, runbook):
        if not required.exists():
            blockers.append(f"{required.relative_to(ROOT)}: canonical Revision V2 document missing")

    if blockers:
        print("ETF_EU_READ_FIRST_TRUTH: FAIL")
        for blocker in blockers:
            print(f"- {blocker}")
        return 1

    print("ETF_EU_READ_FIRST_TRUTH: PASS")
    print(f"read_first_files={len(READ_FIRST)}")
    print("volatile_operational_truth=LIVE_GITHUB_CONTROL_PLANE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
