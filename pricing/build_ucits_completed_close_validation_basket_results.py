from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pricing.build_ucits_close_price_validation_basket_results import (
    MIN_PAUSE_SECONDS,
    MIN_RATE_LIMIT_COOLDOWN_SECONDS,
    _configure_yfinance,
    _is_rate_limit_exception,
    _load_yaml,
    _usable_close,
    _utc_now,
)


def _index_date(value: Any) -> date | None:
    try:
        candidate = value.date() if callable(getattr(value, "date", None)) else value
        return date.fromisoformat(str(candidate)[:10])
    except (TypeError, ValueError):
        return None


def select_latest_completed_close(close_series: Any, report_date: date) -> tuple[float | None, str | None]:
    eligible: list[tuple[date, float]] = []
    for index, value in close_series.items():
        close_date = _index_date(index)
        close_value = _usable_close(value)
        if close_date is not None and close_date < report_date and close_value is not None:
            eligible.append((close_date, close_value))
    if not eligible:
        return None, None
    selected_date, selected_value = max(eligible, key=lambda item: item[0])
    return selected_value, selected_date.isoformat()


def _try_completed_close(
    symbol: str,
    *,
    report_date: date,
    pause_seconds: float,
    rate_limit_cooldown_seconds: float,
    max_attempts: int,
    rate_limit_mode: str,
) -> tuple[str, float | None, str | None, str | None, list[str], int, bool, bool]:
    yf = _configure_yfinance()
    if yf is None:
        return "fetch_failed", None, None, None, ["yfinance_not_available"], 0, False, False
    blockers: list[str] = []
    rate_limited = False
    attempts = max(1, int(max_attempts))
    for attempt in range(1, attempts + 1):
        if attempt > 1:
            time.sleep(max(0.0, pause_seconds))
        try:
            history = yf.Ticker(symbol).history(period="15d", interval="1d", auto_adjust=False)
        except Exception as exc:
            if _is_rate_limit_exception(exc):
                rate_limited = True
                blockers.append(f"yfinance_rate_limited_attempt_{attempt}:{type(exc).__name__}")
                if rate_limit_mode == "stop":
                    blockers.append("batch_stopped_to_respect_yahoo_rate_limit")
                    return "fetch_failed", None, None, None, blockers, attempt, rate_limited, True
                if attempt < attempts:
                    time.sleep(max(0.0, rate_limit_cooldown_seconds))
                    continue
                return "fetch_failed", None, None, None, blockers, attempt, rate_limited, False
            return "fetch_failed", None, None, None, [f"yfinance_exception:{type(exc).__name__}"], attempt, rate_limited, False
        if history is None or history.empty or "Close" not in history:
            return "fetch_failed", None, None, None, ["no_close_history_returned"], attempt, rate_limited, False
        close_value, close_date = select_latest_completed_close(history["Close"].dropna(), report_date)
        if close_value is None or close_date is None:
            return "fetch_failed", None, None, _utc_now(), ["no_completed_close_strictly_before_report_date"], attempt, rate_limited, False
        return "priced_non_authoritative", close_value, close_date, _utc_now(), blockers, attempt, rate_limited, False
    return "fetch_failed", None, None, None, blockers or ["max_attempts_exhausted"], attempts, rate_limited, False


def _base_row(line: dict[str, Any], request_index: int, report_date: date, cooldown: float) -> dict[str, Any]:
    return {
        "basket_id": line.get("basket_id"),
        "fund_name": line.get("fund_name"),
        "isin": line.get("isin"),
        "instrument_type": line.get("instrument_type"),
        "exchange": line.get("exchange"),
        "venue_code": line.get("venue_code"),
        "ticker": line.get("ticker"),
        "provider_symbol_yahoo": str(line.get("provider_symbol_yahoo") or "").strip(),
        "currency": line.get("currency"),
        "verification_status": str(line.get("verification_status") or "candidate_requires_verification"),
        "source_id": "yahoo_yfinance",
        "source_name": "Yahoo/yfinance completed-close connectivity evidence",
        "source_quality_status": "non_authoritative_connectivity_only",
        "source_agreement_status": "not_agreement_gate_not_valuation_grade",
        "valuation_grade": False,
        "fundable": False,
        "request_index": request_index,
        "rate_limit_cooldown_seconds": cooldown,
        "report_date": report_date.isoformat(),
        "close_selection_policy": "latest_daily_bar_strictly_before_report_date",
    }


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
    row = _base_row(line, request_index, report_date, rate_limit_cooldown_seconds)
    symbol = row["provider_symbol_yahoo"]
    verification_status = row["verification_status"]
    if verification_status == "policy_review_required_not_ucits" or line.get("instrument_type") != "UCITS ETF":
        status, close_price, close_date, observed_at = "policy_review_required_not_ucits", None, None, _utc_now()
        blockers, attempts, rate_limited, stop_batch = ["not_ucits_policy_review_required"], 0, False, False
    elif not symbol:
        status, close_price, close_date, observed_at = "fetch_failed", None, None, _utc_now()
        blockers, attempts, rate_limited, stop_batch = ["missing_provider_symbol_yahoo"], 0, False, False
    else:
        status, close_price, close_date, observed_at, blockers, attempts, rate_limited, stop_batch = _try_completed_close(
            symbol,
            report_date=report_date,
            pause_seconds=pause_seconds,
            rate_limit_cooldown_seconds=rate_limit_cooldown_seconds,
            max_attempts=max_attempts,
            rate_limit_mode=rate_limit_mode,
        )
        if verification_status == "candidate_requires_verification" and status == "priced_non_authoritative":
            blockers = blockers + ["identity_or_line_verification_pending"]
    row.update(
        {
            "pricing_status": status,
            "close_date": close_date,
            "close_price": close_price,
            "observed_at_utc": observed_at,
            "blockers": blockers,
            "attempt_count": attempts,
            "rate_limited": rate_limited,
            "pause_seconds_before_request": pause_seconds if request_index > 1 else 0.0,
            "completed_close": bool(status == "priced_non_authoritative" and close_date and date.fromisoformat(close_date) < report_date),
        }
    )
    return row, stop_batch


def _skipped_row(line: dict[str, Any], request_index: int, report_date: date, cooldown: float) -> dict[str, Any]:
    row = _base_row(line, request_index, report_date, cooldown)
    row.update(
        {
            "pricing_status": "fetch_failed",
            "close_date": None,
            "close_price": None,
            "observed_at_utc": _utc_now(),
            "blockers": ["not_attempted_due_to_prior_yahoo_rate_limit", "batch_stopped_to_respect_yahoo_rate_limit"],
            "attempt_count": 0,
            "rate_limited": False,
            "pause_seconds_before_request": 0.0,
            "completed_close": False,
        }
    )
    return row


def build_results(
    *,
    basket_path: Path,
    run_id: str,
    report_date: date,
    output_dir: Path,
    pause_seconds: float,
    rate_limit_cooldown_seconds: float,
    max_attempts: int,
    rate_limit_mode: str,
) -> Path:
    pause_seconds = max(float(pause_seconds), MIN_PAUSE_SECONDS)
    rate_limit_cooldown_seconds = max(float(rate_limit_cooldown_seconds), MIN_RATE_LIMIT_COOLDOWN_SECONDS)
    lines = list((_load_yaml(basket_path).get("trading_lines") or []))
    rows: list[dict[str, Any]] = []
    stopped = False
    for index, line in enumerate(lines, start=1):
        if stopped:
            rows.append(_skipped_row(dict(line), index, report_date, rate_limit_cooldown_seconds))
            continue
        if index > 1:
            time.sleep(pause_seconds)
        row, stop_batch = _row_from_line(
            dict(line),
            report_date=report_date,
            pause_seconds=pause_seconds,
            rate_limit_cooldown_seconds=rate_limit_cooldown_seconds,
            max_attempts=max_attempts,
            rate_limit_mode=rate_limit_mode,
            request_index=index,
        )
        rows.append(row)
        stopped = stopped or stop_batch
    venues = {str(row["exchange"]) for row in rows if row.get("exchange")}
    currencies = {str(row["currency"]) for row in rows if row.get("currency")}
    priced = [row for row in rows if row.get("pricing_status") == "priced_non_authoritative" and row.get("close_price") is not None]
    failed = [row for row in rows if row.get("pricing_status") == "fetch_failed"]
    payload = {
        "schema_version": "ucits_close_price_validation_basket_results_v1",
        "artifact_type": "ucits_close_price_validation_basket_results",
        "run_id": run_id,
        "report_date": report_date.isoformat(),
        "source_basket": str(basket_path),
        "generated_at_utc": _utc_now(),
        "close_selection_policy": "latest_daily_bar_strictly_before_report_date",
        "completed_close_gate_passed": bool(priced and all(row.get("completed_close") for row in priced)),
        "line_count": len(rows),
        "priced_line_count": len(priced),
        "failed_line_count": len(failed),
        "venue_count": len(venues),
        "currency_count": len(currencies),
        "min_threshold_met": len(rows) >= 8 and len(venues) >= 3 and len(currencies) >= 2,
        "throttle_policy": {
            "source": "yahoo_yfinance",
            "requests_are_serialized": True,
            "pause_seconds_between_symbols": pause_seconds,
            "rate_limit_mode": rate_limit_mode,
            "rate_limit_cooldown_seconds": rate_limit_cooldown_seconds,
            "max_attempts_per_symbol": max_attempts,
        },
        "rate_limit_observed": any(row.get("rate_limited") for row in rows),
        "batch_stopped_for_rate_limit": stopped,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "rows": rows,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / f"ucits_close_price_validation_basket_results_{run_id}.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"UCITS_COMPLETED_CLOSE_RESULTS_OK | path={out} | priced={len(priced)} | lines={len(rows)} | report_date={report_date}")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--basket", default="config/ucits_close_price_validation_basket.yml")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--output-dir", default="output/pricing")
    parser.add_argument("--pause-seconds", type=float, default=15.0)
    parser.add_argument("--rate-limit-cooldown-seconds", type=float, default=600.0)
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--rate-limit-mode", choices=("stop", "sleep"), default="stop")
    args = parser.parse_args()
    build_results(
        basket_path=Path(args.basket),
        run_id=args.run_id,
        report_date=date.fromisoformat(args.report_date),
        output_dir=Path(args.output_dir),
        pause_seconds=args.pause_seconds,
        rate_limit_cooldown_seconds=args.rate_limit_cooldown_seconds,
        max_attempts=args.max_attempts,
        rate_limit_mode=args.rate_limit_mode,
    )


if __name__ == "__main__":
    main()
