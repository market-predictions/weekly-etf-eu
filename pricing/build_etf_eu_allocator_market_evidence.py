from __future__ import annotations

import argparse
import json
import math
import statistics
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        result = float(value)
        return result if math.isfinite(result) else default
    except (TypeError, ValueError):
        return default


def _registry_index(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("registry_id")): row
        for row in (registry.get("funds") or [])
        if isinstance(row, dict) and row.get("registry_id")
    }


def _primary_line(fund: dict[str, Any]) -> dict[str, Any] | None:
    lines = [row for row in (fund.get("trading_lines") or []) if isinstance(row, dict)]
    verified = [
        row
        for row in lines
        if str(row.get("line_verification_status") or "").startswith("verified_ucits_trading_line")
        and str(row.get("trading_currency") or "").upper() == "EUR"
    ]
    for row in verified:
        if row.get("primary_line") is True:
            return row
    return verified[0] if verified else None


def _provider_symbols(line: dict[str, Any]) -> list[str]:
    values: list[str] = []
    raw_many = line.get("provider_symbols_yahoo")
    if isinstance(raw_many, list):
        values.extend(str(item).strip() for item in raw_many if str(item).strip())
    for key in ("pricing_symbol_yahoo", "provider_symbol_yahoo"):
        value = str(line.get(key) or "").strip()
        if value:
            values.append(value)
    ticker = str(line.get("exchange_ticker") or "").strip()
    venue = str(line.get("venue_code") or "").upper()
    if ticker and venue == "XETR":
        values.append(f"{ticker}.DE")
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _mapping_candidate(mapping: dict[str, Any], registry: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [row for row in (mapping.get("candidates") or []) if isinstance(row, dict)]
    candidates.sort(key=lambda row: row.get("preferred") is not True)
    for candidate in candidates:
        fund = registry.get(str(candidate.get("registry_id") or ""))
        if fund:
            return fund
    return None


def _identity_gate(fund: dict[str, Any] | None, line: dict[str, Any] | None) -> tuple[bool, list[str]]:
    blockers: list[str] = []
    if not fund:
        return False, ["fund_not_mapped"]
    if str(fund.get("instrument_type") or "") != "UCITS ETF":
        blockers.append("product_type_not_ucits_etf")
    if not str(fund.get("isin") or "").strip() or str(fund.get("isin") or "").upper() == "TBD":
        blockers.append("isin_missing")
    if str(fund.get("ucits_status") or "") not in {"confirmed", "confirmed_by_fund_name"}:
        blockers.append("ucits_status_unconfirmed")
    if str(fund.get("priips_kid_status") or "") != "available":
        blockers.append("priips_kid_unavailable")
    if not line:
        blockers.append("verified_eur_trading_line_missing")
    return not blockers, blockers


def _date_of(index_value: Any) -> date | None:
    try:
        candidate = index_value.date() if callable(getattr(index_value, "date", None)) else index_value
        return date.fromisoformat(str(candidate)[:10])
    except (TypeError, ValueError):
        return None


def _quote_value(container: Any, key: str) -> float | None:
    try:
        if hasattr(container, "get"):
            value = container.get(key)
        else:
            value = getattr(container, key)
        result = float(value)
        return result if math.isfinite(result) and result > 0 else None
    except Exception:
        return None


def _fetch_symbol(symbols: list[str], report_date: date, liquidity_sessions: int, risk_sessions: int) -> dict[str, Any]:
    try:
        import yfinance as yf
    except Exception:
        return {"status": "fetch_failed", "blockers": ["yfinance_not_available"], "attempted_symbols": symbols}

    errors: list[str] = []
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period="6mo", interval="1d", auto_adjust=False)
        except Exception as exc:
            errors.append(f"{symbol}:{type(exc).__name__}")
            continue
        if history is None or history.empty or "Close" not in history:
            errors.append(f"{symbol}:no_daily_history")
            continue

        eligible_rows: list[dict[str, float | str]] = []
        for index, row in history.iterrows():
            session_date = _date_of(index)
            close_value = _num(row.get("Close"), default=0.0)
            volume_value = _num(row.get("Volume"), default=0.0)
            if session_date and session_date < report_date and close_value > 0:
                eligible_rows.append({"date": session_date.isoformat(), "close": close_value, "volume": max(volume_value, 0.0)})
        if not eligible_rows:
            errors.append(f"{symbol}:no_completed_close_before_report_date")
            continue

        latest = eligible_rows[-1]
        liquidity_rows = eligible_rows[-max(1, liquidity_sessions):]
        traded_values = [row["close"] * row["volume"] for row in liquidity_rows if row["volume"] > 0]
        volumes = [row["volume"] for row in liquidity_rows if row["volume"] > 0]
        nonzero_ratio = len(traded_values) / len(liquidity_rows) if liquidity_rows else 0.0

        risk_rows = eligible_rows[-max(2, risk_sessions):]
        closes = [float(row["close"]) for row in risk_rows]
        log_returns = [math.log(closes[index] / closes[index - 1]) for index in range(1, len(closes)) if closes[index - 1] > 0]
        annualized_volatility = statistics.stdev(log_returns) * math.sqrt(252) * 100.0 if len(log_returns) >= 2 else None
        running_peak = 0.0
        drawdowns: list[float] = []
        for close in closes:
            running_peak = max(running_peak, close)
            if running_peak > 0:
                drawdowns.append((close / running_peak - 1.0) * 100.0)
        max_drawdown = min(drawdowns) if drawdowns else None

        bid = ask = None
        quote_errors: list[str] = []
        try:
            fast_info = ticker.fast_info
            bid = _quote_value(fast_info, "bid")
            ask = _quote_value(fast_info, "ask")
        except Exception as exc:
            quote_errors.append(f"fast_info:{type(exc).__name__}")
        if not bid or not ask or ask < bid:
            bid = ask = None
            try:
                info = ticker.info
                bid = _quote_value(info, "bid")
                ask = _quote_value(info, "ask")
            except Exception as exc:
                quote_errors.append(f"info:{type(exc).__name__}")
        spread_bps = None
        if bid and ask and ask >= bid:
            midpoint = (bid + ask) / 2.0
            spread_bps = (ask - bid) / midpoint * 10000.0 if midpoint > 0 else None

        return {
            "status": "priced_completed_close",
            "selected_symbol": symbol,
            "attempted_symbols": symbols,
            "completed_close_date": latest["date"],
            "completed_close_price_eur": round(float(latest["close"]), 8),
            "liquidity_session_count": len(liquidity_rows),
            "median_daily_volume_units": round(statistics.median(volumes), 4) if volumes else 0.0,
            "median_daily_traded_value_eur": round(statistics.median(traded_values), 2) if traded_values else 0.0,
            "nonzero_volume_session_ratio": round(nonzero_ratio, 6),
            "annualized_volatility_pct": round(annualized_volatility, 4) if annualized_volatility is not None else None,
            "maximum_drawdown_pct": round(max_drawdown, 4) if max_drawdown is not None else None,
            "quote_bid_eur": round(bid, 8) if bid else None,
            "quote_ask_eur": round(ask, 8) if ask else None,
            "quote_spread_bps": round(spread_bps, 4) if spread_bps is not None else None,
            "quote_observed_at_utc": _utc_now() if bid and ask else None,
            "quote_errors": quote_errors,
            "blockers": [],
        }
    return {"status": "fetch_failed", "blockers": errors or ["no_provider_symbols"], "attempted_symbols": symbols}


def _liquidity_threshold(target_weight: float, policy: dict[str, Any]) -> float:
    thresholds = ((policy.get("liquidity") or {}).get("thresholds_eur_per_day") or {})
    if target_weight > 10.0:
        return _num(thresholds.get("above_10_pct"))
    if target_weight >= 3.0:
        return _num(thresholds.get("from_3_to_10_pct"))
    return _num(thresholds.get("below_3_pct"))


def build(
    shared_target: dict[str, Any],
    portfolio: dict[str, Any],
    registry_payload: dict[str, Any],
    mapping_payload: dict[str, Any],
    policy: dict[str, Any],
    report_date: date,
) -> dict[str, Any]:
    registry = _registry_index(registry_payload)
    mappings = mapping_payload.get("exposures") if isinstance(mapping_payload.get("exposures"), dict) else {}
    targets = {
        str(row.get("exposure_id")): _num(row.get("target_weight_pct"))
        for row in (shared_target.get("exposure_targets") or [])
        if isinstance(row, dict) and row.get("exposure_id")
    }
    target_rows: list[dict[str, Any]] = []
    for exposure_id, target_weight in targets.items():
        mapping = mappings.get(exposure_id) if isinstance(mappings.get(exposure_id), dict) else {}
        fund = _mapping_candidate(mapping, registry)
        line = _primary_line(fund or {})
        identity_ok, identity_blockers = _identity_gate(fund, line)
        symbols = _provider_symbols(line or {})
        market = _fetch_symbol(
            symbols,
            report_date,
            int(((policy.get("liquidity") or {}).get("lookback_sessions") or 20)),
            int(((policy.get("risk") or {}).get("volatility_lookback_sessions") or 60)),
        ) if identity_ok else {"status": "not_fetched_identity_blocked", "blockers": identity_blockers, "attempted_symbols": symbols}
        threshold = _liquidity_threshold(target_weight, policy)
        traded_value = _num(market.get("median_daily_traded_value_eur"))
        liquidity_pass = bool(market.get("status") == "priced_completed_close" and traded_value >= threshold)
        spread = market.get("quote_spread_bps")
        maximum_spread = _num((policy.get("liquidity") or {}).get("maximum_quote_spread_bps"), 60.0)
        spread_status = "unavailable_review_required" if spread is None else ("pass" if _num(spread) <= maximum_spread else "fail")
        blockers = list(identity_blockers) + list(market.get("blockers") or [])
        if market.get("status") != "priced_completed_close":
            blockers.append("completed_close_missing")
        if market.get("status") == "priced_completed_close" and not liquidity_pass:
            blockers.append("liquidity_below_threshold")
        if spread_status == "fail":
            blockers.append("quote_spread_above_threshold")
        if spread_status == "unavailable_review_required":
            blockers.append("quote_spread_unavailable")
        status = "blocked"
        if identity_ok and market.get("status") == "priced_completed_close" and liquidity_pass and spread_status == "pass":
            status = "eligible_shadow_allocator"
        elif identity_ok and market.get("status") == "priced_completed_close" and liquidity_pass and spread_status == "unavailable_review_required":
            status = "eligible_pending_spread_review"
        target_rows.append({
            "exposure_id": exposure_id,
            "donor_target_weight_pct": target_weight,
            "registry_id": fund.get("registry_id") if fund else None,
            "fund_name": fund.get("fund_name") if fund else None,
            "isin": fund.get("isin") if fund else None,
            "ter_pct": fund.get("ter_pct") if fund else None,
            "replication_method": fund.get("replication_method") if fund else None,
            "exchange": line.get("exchange") if line else None,
            "venue_code": line.get("venue_code") if line else None,
            "exchange_ticker": line.get("exchange_ticker") if line else None,
            "trading_currency": line.get("trading_currency") if line else None,
            "identity_gate_passed": identity_ok,
            "liquidity_threshold_eur_per_day": threshold,
            "liquidity_gate_passed": liquidity_pass,
            "spread_status": spread_status,
            "allocator_market_status": status,
            "blockers": sorted(set(blockers)),
            "market": market,
        })

    incumbent_rows: list[dict[str, Any]] = []
    for position in portfolio.get("positions") or []:
        if not isinstance(position, dict):
            continue
        isin = str(position.get("isin") or "")
        fund = next((row for row in registry.values() if str(row.get("isin") or "") == isin), None)
        line = None
        if fund:
            ticker = str(position.get("ticker") or position.get("exchange_ticker") or "").upper()
            lines = [row for row in (fund.get("trading_lines") or []) if isinstance(row, dict)]
            line = next((row for row in lines if str(row.get("exchange_ticker") or "").upper() == ticker), None) or _primary_line(fund)
        symbols = _provider_symbols(line or {})
        market = _fetch_symbol(
            symbols,
            report_date,
            int(((policy.get("liquidity") or {}).get("lookback_sessions") or 20)),
            int(((policy.get("risk") or {}).get("volatility_lookback_sessions") or 60)),
        ) if symbols else {"status": "fetch_failed", "blockers": ["provider_symbol_missing"], "attempted_symbols": []}
        incumbent_rows.append({
            "ticker": position.get("ticker") or position.get("exchange_ticker"),
            "isin": isin,
            "fund_name": position.get("fund_name"),
            "shares": position.get("shares"),
            "current_weight_pct": position.get("current_weight_pct"),
            "registry_id": fund.get("registry_id") if fund else None,
            "market": market,
        })

    return {
        "schema_version": "etf_eu_allocator_market_evidence_v1",
        "artifact_type": "etf_eu_allocator_market_evidence",
        "generated_at_utc": _utc_now(),
        "report_date": report_date.isoformat(),
        "completed_close_policy": "latest_daily_bar_strictly_before_report_date",
        "source_quality": "non_authoritative_connectivity_and_market_observation_only",
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "target_rows": target_rows,
        "incumbent_rows": incumbent_rows,
        "summary": {
            "target_count": len(target_rows),
            "priced_count": sum(1 for row in target_rows if (row.get("market") or {}).get("status") == "priced_completed_close"),
            "liquidity_pass_count": sum(1 for row in target_rows if row.get("liquidity_gate_passed") is True),
            "spread_pass_count": sum(1 for row in target_rows if row.get("spread_status") == "pass"),
            "eligible_count": sum(1 for row in target_rows if row.get("allocator_market_status") == "eligible_shadow_allocator"),
            "eligible_pending_spread_count": sum(1 for row in target_rows if row.get("allocator_market_status") == "eligible_pending_spread_review"),
            "blocked_count": sum(1 for row in target_rows if row.get("allocator_market_status") == "blocked"),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build completed-close, liquidity and quote-spread evidence for the EU allocator")
    parser.add_argument("--shared-portfolio-target", type=Path, required=True)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, default=Path("config/shared_exposure_ucits_map.yml"))
    parser.add_argument("--policy", type=Path, default=Path("config/etf_eu_allocator_policy.yml"))
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = build(
        shared_target=_load_json(args.shared_portfolio_target),
        portfolio=_load_json(args.portfolio_state),
        registry_payload=_load_yaml(args.registry),
        mapping_payload=_load_yaml(args.mapping),
        policy=_load_yaml(args.policy),
        report_date=date.fromisoformat(args.report_date),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))
    print(args.output)


if __name__ == "__main__":
    main()
