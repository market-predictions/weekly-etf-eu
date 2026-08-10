from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from runtime.reconcile_etf_eu_funded_markdown import validate_funded_markdown


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def validate(state_path: Path, dutch_markdown: Path, english_markdown: Path) -> dict[str, Any]:
    state = _read_json(state_path)
    nl_text = dutch_markdown.read_text(encoding="utf-8")
    en_text = english_markdown.read_text(encoding="utf-8")

    nl_blockers = validate_funded_markdown(nl_text, state, language="nl")
    en_blockers = validate_funded_markdown(en_text, state, language="en")
    blockers = [f"NL: {item}" for item in nl_blockers] + [f"EN: {item}" for item in en_blockers]

    portfolio = state.get("portfolio") if isinstance(state.get("portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    funded_tickers = sorted(
        str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()
        for row in positions
        if str(row.get("exchange_ticker") or row.get("ticker") or "").strip()
    )

    return {
        "schema_version": "etf_eu_markdown_delivery_validation_v1",
        "artifact_type": "etf_eu_markdown_delivery_validation",
        "state": str(state_path),
        "dutch_markdown": str(dutch_markdown),
        "english_markdown": str(english_markdown),
        "funded_position_count": len(positions),
        "funded_tickers": funded_tickers,
        "passed": not blockers,
        "blockers": blockers,
        "delivery_authority": False,
        "send_executed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate state-derived NL/EN Markdown delivery artifacts.")
    parser.add_argument("--state", required=True)
    parser.add_argument("--dutch-markdown", required=True)
    parser.add_argument("--english-markdown", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    result = validate(Path(args.state), Path(args.dutch_markdown), Path(args.english_markdown))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    if args.strict and result["passed"] is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
