from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PASSIVE_ACTIONS = {"hold"}


def _latest_plan(runtime_dir: Path) -> Path:
    pointer = runtime_dir / "latest_etf_rotation_plan_path.txt"
    if pointer.exists():
        raw = pointer.read_text(encoding="utf-8").strip()
        path = Path(raw)
        if path.exists():
            return path
        candidate = runtime_dir / path.name
        if candidate.exists():
            return candidate
    plans = sorted(runtime_dir.glob("etf_rotation_plan_*.json"))
    if not plans:
        raise RuntimeError(f"No etf_rotation_plan_*.json files found in {runtime_dir}")
    return plans[-1]


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def validate(plan: dict[str, Any], warning_only: bool = False) -> None:
    policy = plan.get("policy") or {}
    block_age = int(_num(policy.get("review_age_block_passive_hold"), 3))
    replace_threshold = _num(policy.get("release_score_replace_threshold"), 80)
    reduce_threshold = _num(policy.get("release_score_reduce_threshold"), 65)

    failures: list[str] = []
    warnings: list[str] = []
    for decision in plan.get("rotation_decisions") or []:
        ticker = str(decision.get("ticker") or "").upper()
        action = str(decision.get("action_code") or "")
        release = _num(decision.get("release_score"), 0.0)
        weeks = int(_num(decision.get("weeks_replaceable"), 0.0))
        override = str(decision.get("override_status") or "none")
        override_reason = str(decision.get("override_reason_code") or "").strip()

        if action in PASSIVE_ACTIONS and release >= replace_threshold:
            failures.append(f"{ticker}: passive hold with release_score={release:.0f} >= replace threshold {replace_threshold:.0f}")
        elif action in PASSIVE_ACTIONS and release >= reduce_threshold and weeks >= block_age:
            failures.append(f"{ticker}: passive hold with release_score={release:.0f} and weeks_replaceable={weeks} >= {block_age}")
        elif action == "hold_with_override" and (override == "none" or not override_reason):
            failures.append(f"{ticker}: hold_with_override without valid override metadata")
        elif action == "hold_with_override":
            warnings.append(f"{ticker}: hold_with_override accepted with reason={override_reason}")

    if failures and not warning_only:
        raise RuntimeError("ETF rotation discipline failed: " + " | ".join(failures))

    for item in warnings + failures:
        print(f"::warning title=ETF Rotation Discipline::{item}")

    status = "WARNING_ONLY" if warning_only else "OK"
    print(f"ETF_ROTATION_DISCIPLINE_{status} | decisions={len(plan.get('rotation_decisions') or [])} | findings={len(failures) + len(warnings)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-dir", default="output/runtime")
    parser.add_argument("--plan", default="")
    parser.add_argument("--warning-only", action="store_true")
    args = parser.parse_args()
    path = Path(args.plan) if args.plan else _latest_plan(Path(args.runtime_dir))
    validate(json.loads(path.read_text(encoding="utf-8")), warning_only=args.warning_only)


if __name__ == "__main__":
    main()
