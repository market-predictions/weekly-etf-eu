#!/usr/bin/env python3
"""Fail closed when another product's executable assets leak into Weekly ETF EU.

Provider names and retained historical donor source files are not product identity by
themselves. The release boundary is stricter for *active GitHub Actions workflows*:
no executable workflow in Weekly ETF EU may invoke the US Weekly ETF runtime/report
path or the FX production path. Retired workflows do not remain as `.yml.disabled`
pseudo-workflows; Git history is the default provenance source and any exceptional
forensic copies live outside `.github/workflows/` under `archive/workflows/`.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PROHIBITED_ROOT_PATHS = ("prediction.py", "daily_outputs", "mt5_output", "gpt.txt")
PROHIBITED_FX_WORKFLOW_TOKENS = (
    "python prediction.py",
    "daily_outputs/latest",
    "FX_BACKTEST",
    "DailyTradeBias",
    "market-predictions/daily-fx",
    "today_prediction_ranking",
    "Today_Predictions.zip",
)
PROHIBITED_US_DONOR_WORKFLOW_TOKENS = (
    "pricing.run_pricing_pass",
    "output/etf_portfolio_state.json",
    "weekly_analysis_pro_",
    "send_report.py",
    "import send_report",
    "etf.txt",
    "etf-pro.txt",
)


def _active_workflows(root: Path) -> list[Path]:
    workflow_dir = root / ".github" / "workflows"
    if not workflow_dir.is_dir():
        return []
    return [
        path
        for path in sorted(workflow_dir.iterdir())
        if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}
    ]


def validate(root: Path) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    for relative in PROHIBITED_ROOT_PATHS:
        if (root / relative).exists():
            blockers.append({"type": "misplaced_product_asset", "path": relative})

    workflow_dir = root / ".github" / "workflows"
    disabled_graveyard = sorted(path.name for path in workflow_dir.glob("*.disabled")) if workflow_dir.exists() else []
    for name in disabled_graveyard:
        blockers.append({"type": "retired_disabled_workflow_in_active_namespace", "path": f".github/workflows/{name}"})

    for path in _active_workflows(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        folded = text.casefold()
        for token in PROHIBITED_FX_WORKFLOW_TOKENS:
            if token.casefold() in folded:
                blockers.append(
                    {
                        "type": "fx_token_in_active_workflow",
                        "path": str(path.relative_to(root)),
                        "token": token,
                    }
                )
        for token in PROHIBITED_US_DONOR_WORKFLOW_TOKENS:
            if token.casefold() in folded:
                blockers.append(
                    {
                        "type": "us_donor_token_in_active_workflow",
                        "path": str(path.relative_to(root)),
                        "token": token,
                    }
                )

    return {
        "schema_version": "weekly_etf_eu_repository_boundary_validation_v3",
        "product": "weekly_etf_eu",
        "valid": not blockers,
        "verdict": "PASS" if not blockers else "FAIL",
        "blockers": blockers,
        "prohibited_root_paths": list(PROHIBITED_ROOT_PATHS),
        "prohibited_fx_workflow_tokens": list(PROHIBITED_FX_WORKFLOW_TOKENS),
        "prohibited_us_donor_workflow_tokens": list(PROHIBITED_US_DONOR_WORKFLOW_TOKENS),
        "active_workflows_scanned": len(_active_workflows(root)),
        "disabled_workflow_graveyard_count": len(disabled_graveyard),
        "retired_workflow_provenance": "git_history_by_default_forensic_exceptions_under_archive_workflows",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(args.root.resolve())
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
