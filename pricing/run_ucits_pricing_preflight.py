from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT_DIR = Path("output/pricing")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_candidate_file(output_dir: Path) -> Path:
    files = sorted(output_dir.glob("ucits_pricing_candidates_*.json"))
    if not files:
        raise RuntimeError(f"No UCITS pricing candidate artifacts found in {output_dir}")
    return files[-1]


def _run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _fetch_yfinance(symbol: str, period: str = "10d") -> dict[str, Any]:
    try:
        import yfinance as yf
    except ImportError as exc:
        return {
            "status": "unpriced_dependency_missing",
            "source": "yfinance",
            "error": f"yfinance import failed: {exc}",
        }
    try:
        history = yf.Ticker(symbol).history(period=period, auto_adjust=False)
        if history is None or history.empty:
            return {"status": "unpriced_no_history", "source": "yfinance", "error": "empty history"}
        row = history.dropna(how="all").tail(1)
        if row.empty:
            return {"status": "unpriced_no_history", "source": "yfinance", "error": "no non-empty rows"}
        idx = row.index[-1]
        close = row["Close"].iloc[-1]
        return {
            "status": "priced_non_authoritative",
            "source": "yfinance",
            "observed_date": str(getattr(idx, "date", lambda: idx)()),
            "close": None if close is None else float(close),
            "currency_warning": "trading_currency_from_registry_not_verified_by_yfinance",
        }
    except Exception as exc:  # pragma: no cover - depends on remote provider
        return {"status": "unpriced_provider_error", "source": "yfinance", "error": str(exc)}


def run_preflight(candidate_artifact: Path, output_dir: Path, run_id: str) -> Path:
    payload = _load_json(candidate_artifact)
    results: list[dict[str, Any]] = []
    for row in payload.get("candidates") or []:
        symbol = row.get("pricing_symbol_yahoo")
        result = _fetch_yfinance(str(symbol))
        results.append({
            "registry_id": row.get("registry_id"),
            "isin": row.get("isin"),
            "fund_name": row.get("fund_name"),
            "exchange": row.get("exchange"),
            "exchange_ticker": row.get("exchange_ticker"),
            "trading_currency": row.get("trading_currency"),
            "provider_symbol": row.get("provider_symbol"),
            "pricing_symbol_yahoo": symbol,
            "us_research_proxy": row.get("us_research_proxy"),
            "portfolio_mutation": False,
            "production_delivery": False,
            "funding_authority": False,
            "preflight_result": result,
        })
    artifact = {
        "schema_version": "ucits_pricing_preflight_v1",
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_candidate_artifact": str(candidate_artifact),
        "pricing_authority": "non_authoritative_connectivity_preflight",
        "portfolio_mutation": False,
        "production_delivery": False,
        "funding_authority": False,
        "results": results,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"ucits_pricing_preflight_{run_id}.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    priced = sum(1 for row in results if row.get("preflight_result", {}).get("status") == "priced_non_authoritative")
    print(f"UCITS_PRICING_PREFLIGHT_OK | artifact={path} | results={len(results)} | priced_non_authoritative={priced} | portfolio_mutation=false | delivery=false")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-artifact", default=None)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    candidate_artifact = Path(args.candidate_artifact) if args.candidate_artifact else _latest_candidate_file(output_dir)
    run_preflight(candidate_artifact, output_dir, args.run_id or _run_id())


if __name__ == "__main__":
    main()
