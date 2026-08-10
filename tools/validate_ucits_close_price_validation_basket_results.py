from __future__ import annotations

import argparse
import json
from pathlib import Path

from pricing.ucits_close_price_validation_contract_v2 import validate_artifact


def validate(
    path: Path,
    *,
    portfolio_state: Path = Path("output/etf_eu_portfolio_state.json"),
    expected_report_date: str | None = None,
) -> dict[str, object]:
    result = validate_artifact(
        path,
        expected_report_date=expected_report_date,
        portfolio_state_path=portfolio_state,
        require_funded_consensus=True,
    )
    if result["valid"] is not True:
        raise AssertionError("; ".join(result["blockers"]))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate the canonical Weekly ETF EU v2 completed-close pricing contract."
    )
    parser.add_argument("--artifact", required=True)
    parser.add_argument(
        "--portfolio-state",
        default="output/etf_eu_portfolio_state.json",
    )
    parser.add_argument("--expected-report-date")
    args = parser.parse_args()
    try:
        result = validate(
            Path(args.artifact),
            portfolio_state=Path(args.portfolio_state),
            expected_report_date=args.expected_report_date,
        )
    except AssertionError as exc:
        result = validate_artifact(
            Path(args.artifact),
            expected_report_date=args.expected_report_date,
            portfolio_state_path=Path(args.portfolio_state),
            require_funded_consensus=True,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        raise SystemExit(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
