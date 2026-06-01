from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

SCHEMA_VERSION = "yahoo_ucits_close_diagnostics_v1"
DEFAULT_SOURCE_POLICY = Path("config/ucits_pricing_source_policy.yml")
DEFAULT_OUTPUT_DIR = Path("output/pricing")


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _safe_float(value: Any) -> float | None:
    try:
        result = float(value)
    except Exception:
        return None
    if result != result or result <= 0:
        return None
    return result


def _iter_requests(policy: dict[str, Any]) -> list[dict[str, Any]]:
    requests: list[dict[str, Any]] = []
    for line in policy.get("trading_line_policies") or []:
        if not isinstance(line, dict):
            continue
        registry = {
            "registry_id": _text(line.get("registry_id")),
            "isin": _text(line.get("isin")),
            "exchange": _text(line.get("exchange")),
            "exchange_ticker": _text(line.get("exchange_ticker")),
            "trading_currency": _text(line.get("trading_currency")),
            "provider_symbol": _text(line.get("provider_symbol")),
        }
        for source in line.get("source_order") or []:
            if isinstance(source, dict) and source.get("source_id") == "yahoo_yfinance" and source.get("symbol"):
                requests.append({"registry": registry, "source": dict(source), "symbol": _text(source.get("symbol"))})
    return requests


def _fetch_symbol(symbol: str) -> dict[str, Any]:
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="10d", interval="1d", auto_adjust=False, actions=False)
        currency = None
        fast_info_error = None
        try:
            fast_info = dict(ticker.fast_info or {})
            currency = fast_info.get("currency")
        except Exception as exc:
            fast_info = {}
            fast_info_error = str(exc)
        if history is None or history.empty or "Close" not in history.columns:
            return {"fetch_status": "no_history", "observed_currency": currency, "fast_info_error": fast_info_error, "history_rows": 0}
        closes = history["Close"].dropna()
        if closes.empty:
            return {"fetch_status": "history_without_close", "observed_currency": currency, "fast_info_error": fast_info_error, "history_rows": int(len(history))}
        last_index = closes.index[-1]
        return {
            "fetch_status": "history_observed",
            "history_rows": int(len(history)),
            "history_start": history.index[0].date().isoformat() if hasattr(history.index[0], "date") else None,
            "history_end": history.index[-1].date().isoformat() if hasattr(history.index[-1], "date") else None,
            "observed_last_close": _safe_float(closes.iloc[-1]),
            "observed_last_close_date": last_index.date().isoformat() if hasattr(last_index, "date") else str(last_index)[:10],
            "observed_currency": currency,
            "fast_info_subset": {key: fast_info.get(key) for key in ["currency", "exchange", "timezone", "quoteType"] if key in fast_info},
            "fast_info_error": fast_info_error,
        }
    except Exception as exc:
        return {"fetch_status": "fetch_failed", "fetch_error": str(exc)}


def _build_row(request: dict[str, Any]) -> dict[str, Any]:
    registry = request["registry"]
    symbol = request["symbol"]
    observed = _fetch_symbol(symbol)
    expected_currency = _text(registry.get("trading_currency"))
    observed_currency = _text(observed.get("observed_currency"))
    close_observed = observed.get("observed_last_close") is not None and bool(observed.get("observed_last_close_date"))
    currency_match = bool(expected_currency and observed_currency and expected_currency.upper() == observed_currency.upper())
    ambiguity_flags: list[str] = []
    ambiguity_flags.append("isin_not_verified_by_yahoo_diagnostic")
    if not observed_currency:
        ambiguity_flags.append("currency_missing")
    elif not currency_match:
        ambiguity_flags.append("currency_mismatch")
    if not close_observed:
        ambiguity_flags.append("close_or_date_missing")
    if "." not in symbol:
        ambiguity_flags.append("exchange_suffix_missing")
    return {
        **registry,
        "source_id": "yahoo_yfinance",
        "yahoo_symbol": symbol,
        "source_policy_status": request.get("source", {}).get("status"),
        "source_policy_authority": request.get("source", {}).get("authority"),
        "diagnostic_status": "close_observed" if close_observed else observed.get("fetch_status", "unknown"),
        "observed": observed,
        "mapping_diagnostics": {
            "currency_matches_registry": currency_match,
            "isin_match_status": "not_verified",
            "symbol_has_exchange_suffix": "." in symbol,
            "line_mapping_unambiguous": False,
            "ambiguity_flags": ambiguity_flags,
        },
        "diagnostic_only": True,
        "authority": False,
        "candidate_close_extraction": False,
        "completed_session_validation": False,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
    }


def build(source_policy: Path, output_dir: Path, run_id: str) -> Path:
    policy = _load_yaml(source_policy)
    rows = [_build_row(request) for request in _iter_requests(policy)]
    artifact = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_policy": str(source_policy),
        "diagnostic_only": True,
        "authority": False,
        "candidate_close_extraction": False,
        "completed_session_validation": False,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "close_observed_count": sum(1 for row in rows if row.get("diagnostic_status") == "close_observed"),
            "unambiguous_mapping_count": 0,
            "authority_note": "Yahoo/yfinance rows remain connectivity diagnostics only and cannot feed valuation until policy is explicitly revised.",
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"yahoo_ucits_close_diagnostics_{run_id}.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(f"YAHOO_UCITS_CLOSE_DIAGNOSTICS_OK | artifact={path} | rows={len(rows)}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-policy", default=str(DEFAULT_SOURCE_POLICY))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    build(Path(args.source_policy), Path(args.output_dir), args.run_id)


if __name__ == "__main__":
    main()
