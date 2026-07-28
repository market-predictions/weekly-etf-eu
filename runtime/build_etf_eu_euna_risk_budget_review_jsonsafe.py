from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import build_etf_eu_euna_risk_budget_review as base


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Build JSON-safe EUNA risk-budget counterfactual review")
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--allocator", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=Path("config/etf_eu_euna_risk_budget_policy_v1.yml"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload = base.build(
        base.load_json(args.panel),
        base.load_json(args.allocator),
        base.load_yaml(args.policy),
    )
    normalized = json_safe(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(normalized, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
