from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_STATE = Path("output/etf_eu_portfolio_state.json")
US_PROXY_TICKERS = {
    "SPY",
    "QQQ",
    "SMH",
    "GLD",
    "GSG",
    "PPA",
    "PAVE",
    "URNM",
    "IWM",
    "TLT",
    "KWEB",
    "ICLN",
    "SOXX",
    "ITA",
    "GRID",
    "URA",
    "NLR",
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ticker(row: dict[str, Any]) -> str:
    return str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()


def validate(path: Path) -> None:
    payload = _read_json(path)
    positions = payload.get("positions") or []
    errors: list[str] = []
    for row in positions:
        ticker = _ticker(row)
        isin = str(row.get("isin") or "").strip()
        investability = str(row.get("investability_status") or "").strip().lower()
        if ticker in US_PROXY_TICKERS:
            errors.append(f"us_proxy_as_eu_holding:{ticker}")
        if ticker and ticker != "CASH" and not isin:
            errors.append(f"missing_isin:{ticker}")
        if ticker and ticker != "CASH" and investability not in {"fundable", "verified_fundable"}:
            errors.append(f"not_verified_fundable:{ticker}:{investability or 'missing'}")
    if errors:
        raise RuntimeError("EU UCITS holding validation failed: " + "; ".join(errors))
    print(f"EU_UCITS_HOLDING_VALIDATION_OK | state={path} | positions={len(positions)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default=str(DEFAULT_STATE))
    args = parser.parse_args()
    validate(Path(args.state))


if __name__ == "__main__":
    main()
