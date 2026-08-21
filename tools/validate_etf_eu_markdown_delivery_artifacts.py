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


def _parse_eur_value(raw: str) -> float:
    value = (
        raw.strip()
        .replace("EUR", "")
        .replace("€", "")
        .replace("\u00a0", "")
        .replace(" ", "")
    )
    if not value:
        raise ValueError("empty monetary value")

    if "," in value and "." in value:
        if value.rfind(",") > value.rfind("."):
            value = value.replace(".", "").replace(",", ".")
        else:
            value = value.replace(",", "")
    elif "," in value:
        tail = value.rsplit(",", 1)[1]
        value = value.replace(",", ".") if len(tail) == 2 else value.replace(",", "")

    return float(value)


def _table_value(text: str, label: str) -> float:
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0] == label:
            return _parse_eur_value(cells[1])
    raise ValueError(f"missing portfolio table row: {label}")


def _portfolio_value_blockers(text: str, state: dict[str, Any], *, language: str) -> list[str]:
    portfolio = state.get("portfolio") if isinstance(state.get("portfolio"), dict) else {}
    if not portfolio:
        return ["report state is missing portfolio object"]

    labels = (
        {
            "Cash": "cash_eur",
            "Belegde marktwaarde": "invested_market_value_eur",
            "Totale portefeuillewaarde": "nav_eur",
        }
        if language == "nl"
        else {
            "Cash": "cash_eur",
            "Invested market value": "invested_market_value_eur",
            "Total portfolio value": "nav_eur",
        }
    )

    blockers: list[str] = []
    for label, state_key in labels.items():
        expected_raw = portfolio.get(state_key)
        if not isinstance(expected_raw, (int, float)):
            blockers.append(f"report state portfolio.{state_key} is missing or non-numeric")
            continue
        try:
            actual = _table_value(text, label)
        except ValueError as exc:
            blockers.append(str(exc))
            continue

        expected = float(expected_raw)
        if abs(actual - expected) > 0.01:
            blockers.append(
                f"portfolio value mismatch for {label}: markdown={actual:.2f}, state={expected:.2f}"
            )

    return blockers


def validate(state_path: Path, dutch_markdown: Path, english_markdown: Path) -> dict[str, Any]:
    state = _read_json(state_path)
    nl_text = dutch_markdown.read_text(encoding="utf-8")
    en_text = english_markdown.read_text(encoding="utf-8")

    nl_blockers = validate_funded_markdown(nl_text, state, language="nl")
    nl_blockers.extend(_portfolio_value_blockers(nl_text, state, language="nl"))
    en_blockers = validate_funded_markdown(en_text, state, language="en")
    en_blockers.extend(_portfolio_value_blockers(en_text, state, language="en"))
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
