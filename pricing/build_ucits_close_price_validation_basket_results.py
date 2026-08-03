from __future__ import annotations

import argparse
import csv
import io
import json
import math
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

RATE_LIMIT_ERROR_TOKENS = ("YFRateLimitError", "Too Many Requests", "Rate limited", "rate limit", "429")
MIN_PAUSE_SECONDS = 10.0
MIN_RATE_LIMIT_COOLDOWN_SECONDS = 300.0
STOOQ_URL = "https://stooq.com/q/d/l/"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _is_rate_limit_exception(exc: Exception) -> bool:
    text = f"{type(exc).__name__}:{exc}"
    return any(token in text for token in RATE_LIMIT_ERROR_TOKENS)


def _usable_close(value: object) -> float | None:
    try:
        close = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    if not math.isfinite(close) or close <= 0:
        return None
    return close


def _parse_report_date(value: str | None) -> date:
    if value:
        return date.fromisoformat(value)
    return datetime.now(timezone.utc).date()


def _stooq_symbol(line: dict[str, Any]) -> str:
    explicit = str(line.get("provider_symbol_stooq") or "").strip().lower()
    if explicit:
        return explicit
    yahoo = str(line.get("provider_symbol_yahoo") or "").strip().lower()
    if yahoo.endswith(".as"):
        return yahoo[:-3] + ".nl"
    if yahoo.endswith(".l"):
        return yahoo[:-2] + ".uk"
    return yahoo


def _try_stooq_close(line: dict[str, Any], report_date: date) -> tuple[str, float | None, str | None, str | None, list[str], str]:
    symbol = _stooq_symbol(line)
    if not symbol:
        return "fetch_failed", None, None, None, ["missing_provider_symbol_stooq"], symbol
    start = report_date - timedelta(days=35)
    params = {
        "s": symbol,
        "i": "d",
        "d1": start.strftime("%Y%m%d"),
        "d2": report_date.strftime("%Y%m%d"),
    }
    try:
        response = requests.get(
            STOOQ_URL,
            params=params,
            timeout=25,
            headers={"User-Agent": "Mozilla/5.0 ETF-EU-Routine/1.0", "Accept": "text/csv,text/plain,*/*"},
        )
    except Exception as exc:
        return "fetch_failed", None, None, None, [f"stooq_exception:{type(exc).__name__}"], symbol
    if response.status_code != 200:
        return "fetch_failed", None, None, _utc_now(), [f"stooq_http_status:{response.status_code}"], symbol
    text = response.text.strip()
    if not text or text.casefold().startswith("no data"):
        return "fetch_failed", None, None, _utc_now(), ["stooq_no_data"], symbol
    try:
        rows = list(csv.DictReader(io.StringIO(text)))
    except Exception as exc:
        return "fetch_failed", None, None, _utc_now(), [f"stooq_csv_parse:{type(exc).__name__}"], symbol
    accepted: list[tuple[date, float]] = []
    for row in rows:
        try:
            row_date = date.fromisoformat(str(row.get("Date") or ""))
        except ValueError:
            continue
        close = _usable_close(row.get("Close"))
        if close is not None and row_date <= report_date:
            accepted.append((row_date, close))
    if not accepted:
        return "fetch_failed", None, None, _utc_now(), ["stooq_no_usable_completed_close_on_or_before_report_date"], symbol
    row_date, close = max(accepted, key=lambda item: item[0])
    return "priced_non_authoritative", close, row_date.isoformat(), _utc_now(), [], symbol


def _configure_yfinance() -> object | None:
    try:
        import yfinance as yf  # type: ignore
    except Exception:
        return None
    try:
        yf.config.network.retries = 0
    except Exception:
        pass
    try:
        yf.config.debug.hide_exceptions = False
    except Exception:
        pass
    return yf


def _try_yfinance_close(
    symbol: str,
    *,
    report_date: date,
    pause_seconds: float,
    rate_limit_cooldown_seconds: float,
    max_attempts: int,
    rate_limit_mode: str,
) -> tuple[str, float | None, str | None, str | None, list[str], int, bool, bool]:
    blockers: list[str] = []
    yf = _configure_yfinance()
    if yf is None:
        return "fetch_failed", None, None, None, ["yfinance_not_available"], 0, False, False
    rate_limited = False
    stop_batch = False
    attempts = max(1, int(max_attempts))
    for attempt in range(1, attempts + 1):
        if attempt > 1:
            time.sleep(max(0.0, pause_seconds))
        try:
            history = yf.Ticker(symbol).history(period="1mo", interval="1d", auto_adjust=False)
        except Exception as exc:
            if _is_rate_limit_exception(exc):
                rate_limited = True
                blockers.append(f"yfinance_rate_limited_attempt_{attempt}:{type(exc).__name__}")
                if rate_limit_mode == "stop":
                    blockers.append("batch_stopped_to_respect_yahoo_rate_limit")
                    stop_batch = True
                    return "fetch_failed", None, None, None, blockers, attempt, rate_limited, stop_batch
                if attempt < attempts:
                    time.sleep(max(0.0, rate_limit_cooldown_seconds))
                    continue
                return "fetch_failed", None, None, None, blockers, attempt, rate_limited, stop_batch
            return "fetch_failed", None, None, None, [f"yfinance_exception:{type(exc).__name__}"], attempt, rate_limited, stop_batch
        if history is None or history.empty or "Close" not in history:
            return "fetch_failed", None, None, None, ["no_close_history_returned"], attempt, rate_limited, stop_batch
        accepted: list[tuple[date, float]] = []
        for index_value, raw_close in history["Close"].dropna().items():
            index_date = getattr(index_value, "date", lambda: index_value)()
            if isinstance(index_date, datetime):
                index_date = index_date.date()
            close = _usable_close(raw_close)
            if isinstance(index_date, date) and close is not None and index_date <= report_date:
                accepted.append((index_date, close))
        if not accepted:
            return "fetch_failed", None, None, _utc_now(), ["no_usable_completed_close_on_or_before_report_date"], attempt, rate_limited, stop_batch
        close_date, close_value = max(accepted, key=lambda item: item[0])
        return "priced_non_authoritative", close_value, close_date.isoformat(), _utc_now(), blockers, attempt, rate_limited, stop_batch
    return "fetch_failed", None, None, None, blockers or ["max_attempts_exhausted"], attempts, rate_limited, stop_batch


def _row_from_line(
    line: dict[str, Any],
    *,
    report_date: date,
    pause_seconds: float,
    rate_limit_cooldown_seconds: float,
    max_attempts: int,
    rate_limit_mode: str,
    request_index: int,
) -> tuple[dict[str, Any], bool]:
    yahoo_symbol = str(line.get("provider_symbol_yahoo") or "").strip()
    verification_status = str(line.get("verification_status") or "candidate_requires_verification")
    attempt_count = 0
    rate_limited = False
    stop_batch = False
    source_id = "none"
    source_name = "No accepted connectivity source"
    provider_symbol_stooq = _stooq_symbol(line)

    if verification_status == "policy_review_required_not_ucits" or line.get("instrument_type") != "UCITS ETF":
        status, close_price, close_date, observed_at = "policy_review_required_not_ucits", None, None, _utc_now()
        blockers = ["not_ucits_policy_review_required"]
    else:
        status, close_price, close_date, observed_at, stooq_blockers, provider_symbol_stooq = _try_stooq_close(line, report_date)
        blockers = list(stooq_blockers)
        if status == "priced_non_authoritative":
            source_id = "stooq_daily_csv"
            source_name = "Stooq daily completed-close connectivity evidence"
        elif yahoo_symbol:
            (
                status,
                close_price,
                close_date,
                observed_at,
                yahoo_blockers,
                attempt_count,
                rate_limited,
                stop_batch,
            ) = _try_yfinance_close(
                yahoo_symbol,
                report_date=report_date,
                pause_seconds=pause_seconds,
                rate_limit_cooldown_seconds=rate_limit_cooldown_seconds,
                max_attempts=max_attempts,
                rate_limit_mode=rate_limit_mode,
            )
            blockers.extend(yahoo_blockers)
            if status == "priced_non_authoritative":
                source_id = "yahoo_yfinance"
                source_name = "Yahoo/yfinance completed-close connectivity evidence"
        else:
            blockers.append("missing_provider_symbol_yahoo")
        if verification_status == "candidate_requires_verification" and status == "priced_non_authoritative":
            blockers.append("identity_or_line_verification_pending")

    row = {
        "basket_id": line.get("basket_id"),
        "fund_name": line.get("fund_name"),
        "isin": line.get("isin"),
        "instrument_type": line.get("instrument_type"),
        "exchange": line.get("exchange"),
        "venue_code": line.get("venue_code"),
        "ticker": line.get("ticker"),
        "provider_symbol_stooq": provider_symbol_stooq,
        "provider_symbol_yahoo": yahoo_symbol,
        "currency": line.get("currency"),
        "verification_status": verification_status,
        "pricing_status": status,
        "close_date": close_date,
        "close_price": close_price,
        "source_id": source_id,
        "source_name": source_name,
        "source_quality_status": "non_authoritative_connectivity_only",
        "source_agreement_status": "not_agreement_gate_not_valuation_grade",
        "observed_at_utc": observed_at,
        "requested_report_date": report_date.isoformat(),
        "completed_close_on_or_before_report_date": close_date is not None and close_date <= report_date.isoformat(),
        "valuation_grade": False,
        "fundable": False,
        "blockers": sorted(set(blockers)),
        "request_index": request_index,
        "attempt_count": attempt_count,
        "rate_limited": rate_limited,
        "pause_seconds_before_request": pause_seconds if request_index > 1 else 0.0,
        "rate_limit_cooldown_seconds": rate_limit_cooldown_seconds,
    }
    return row, stop_batch


def build_results(
    *,
    basket_path: Path,
    run_id: str,
    output_dir: Path,
    report_date: str | None,
    pause_seconds: float,
    rate_limit_cooldown_seconds: float,
    max_attempts: int,
    rate_limit_mode: str,
) -> Path:
    pause_seconds = max(float(pause_seconds), MIN_PAUSE_SECONDS)
    rate_limit_cooldown_seconds = max(float(rate_limit_cooldown_seconds), MIN_RATE_LIMIT_COOLDOWN_SECONDS)
    resolved_report_date = _parse_report_date(report_date)
    basket = _load_yaml(basket_path)
    lines = list(basket.get("trading_lines") or [])
    rows: list[dict[str, Any]] = []
    batch_stopped_for_rate_limit = False
    for index, line in enumerate(lines, start=1):
        if index > 1:
            time.sleep(max(0.0, pause_seconds))
        row, stop_batch = _row_from_line(
            dict(line),
            report_date=resolved_report_date,
            pause_seconds=pause_seconds,
            rate_limit_cooldown_seconds=rate_limit_cooldown_seconds,
            max_attempts=max_attempts,
            rate_limit_mode=rate_limit_mode,
            request_index=index,
        )
        rows.append(row)
        if stop_batch:
            batch_stopped_for_rate_limit = True
            break
    if batch_stopped_for_rate_limit:
        attempted_ids = {row.get("basket_id") for row in rows}
        for index, line in enumerate(lines, start=1):
            if line.get("basket_id") in attempted_ids:
                continue
            rows.append(
                {
                    "basket_id": line.get("basket_id"),
                    "fund_name": line.get("fund_name"),
                    "isin": line.get("isin"),
                    "instrument_type": line.get("instrument_type"),
                    "exchange": line.get("exchange"),
                    "venue_code": line.get("venue_code"),
                    "ticker": line.get("ticker"),
                    "provider_symbol_stooq": _stooq_symbol(dict(line)),
                    "provider_symbol_yahoo": str(line.get("provider_symbol_yahoo") or "").strip(),
                    "currency": line.get("currency"),
                    "verification_status": str(line.get("verification_status") or "candidate_requires_verification"),
                    "pricing_status": "fetch_failed",
                    "close_date": None,
                    "close_price": None,
                    "source_id": "none",
                    "source_name": "Not attempted after secondary-source throttle",
                    "source_quality_status": "non_authoritative_connectivity_only",
                    "source_agreement_status": "not_agreement_gate_not_valuation_grade",
                    "observed_at_utc": _utc_now(),
                    "requested_report_date": resolved_report_date.isoformat(),
                    "completed_close_on_or_before_report_date": False,
                    "valuation_grade": False,
                    "fundable": False,
                    "blockers": ["not_attempted_due_to_prior_yahoo_rate_limit"],
                    "request_index": index,
                    "attempt_count": 0,
                    "rate_limited": False,
                    "pause_seconds_before_request": 0.0,
                    "rate_limit_cooldown_seconds": rate_limit_cooldown_seconds,
                }
            )
    rows.sort(key=lambda row: int(row.get("request_index") or 0))
    venues = {str(row["exchange"]) for row in rows if row.get("exchange")}
    currencies = {str(row["currency"]) for row in rows if row.get("currency")}
    priced = [row for row in rows if row.get("pricing_status") == "priced_non_authoritative" and row.get("close_price") is not None]
    failed = [row for row in rows if row.get("pricing_status") == "fetch_failed"]
    payload = {
        "schema_version": "ucits_close_price_validation_basket_results_v1",
        "run_id": run_id,
        "report_date": resolved_report_date.isoformat(),
        "source_basket": str(basket_path),
        "generated_at_utc": _utc_now(),
        "line_count": len(rows),
        "priced_line_count": len(priced),
        "failed_line_count": len(failed),
        "venue_count": len(venues),
        "currency_count": len(currencies),
        "min_threshold_met": len(rows) >= 8 and len(venues) >= 3 and len(currencies) >= 2,
        "source_chain": ["stooq_daily_csv", "yahoo_yfinance"],
        "throttle_policy": {
            "primary_source": "stooq_daily_csv",
            "secondary_source": "yahoo_yfinance",
            "requests_are_serialized": True,
            "pause_seconds_between_symbols": pause_seconds,
            "rate_limit_mode": rate_limit_mode,
            "rate_limit_cooldown_seconds": rate_limit_cooldown_seconds,
            "max_attempts_per_yahoo_symbol": max_attempts,
            "minimum_policy_enforced": True,
        },
        "rate_limit_observed": any(row.get("rate_limited") for row in rows),
        "batch_stopped_for_rate_limit": batch_stopped_for_rate_limit,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "rows": rows,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / f"ucits_close_price_validation_basket_results_{run_id}.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "UCITS_CLOSE_PRICE_VALIDATION_BASKET_RESULTS_OK"
        f" | path={out}"
        f" | report_date={resolved_report_date}"
        f" | priced={len(priced)}"
        f" | lines={len(rows)}"
        f" | sources={','.join(payload['source_chain'])}"
        f" | yahoo_rate_limit={payload['rate_limit_observed']}"
    )
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--basket", default="config/ucits_close_price_validation_basket.yml")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date")
    parser.add_argument("--output-dir", default="output/pricing")
    parser.add_argument("--pause-seconds", type=float, default=15.0)
    parser.add_argument("--rate-limit-cooldown-seconds", type=float, default=600.0)
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--rate-limit-mode", choices=("stop", "sleep"), default="stop")
    args = parser.parse_args()
    build_results(
        basket_path=Path(args.basket),
        run_id=args.run_id,
        output_dir=Path(args.output_dir),
        report_date=args.report_date,
        pause_seconds=args.pause_seconds,
        rate_limit_cooldown_seconds=args.rate_limit_cooldown_seconds,
        max_attempts=args.max_attempts,
        rate_limit_mode=args.rate_limit_mode,
    )


if __name__ == "__main__":
    main()
