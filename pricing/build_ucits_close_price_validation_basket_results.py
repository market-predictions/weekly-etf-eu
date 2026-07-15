from __future__ import annotations

import argparse
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

RATE_LIMIT_ERROR_TOKENS = ("YFRateLimitError", "Too Many Requests", "Rate limited", "rate limit", "429")
MIN_PAUSE_SECONDS = 10.0
MIN_RATE_LIMIT_COOLDOWN_SECONDS = 300.0


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError('PyYAML is required')
    return yaml.safe_load(path.read_text(encoding='utf-8')) or {}


def _is_rate_limit_exception(exc: Exception) -> bool:
    text = f'{type(exc).__name__}:{exc}'
    return any(token in text for token in RATE_LIMIT_ERROR_TOKENS)


def _usable_close(value: object) -> float | None:
    try:
        close = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    if not math.isfinite(close) or close <= 0:
        return None
    return close


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
    pause_seconds: float,
    rate_limit_cooldown_seconds: float,
    max_attempts: int,
    rate_limit_mode: str,
) -> tuple[str, float | None, str | None, str | None, list[str], int, bool, bool]:
    blockers: list[str] = []
    yf = _configure_yfinance()
    if yf is None:
        return 'fetch_failed', None, None, None, ['yfinance_not_available'], 0, False, False
    rate_limited = False
    stop_batch = False
    attempts = max(1, int(max_attempts))
    for attempt in range(1, attempts + 1):
        if attempt > 1:
            time.sleep(max(0.0, pause_seconds))
        try:
            history = yf.Ticker(symbol).history(period='10d', interval='1d', auto_adjust=False)
        except Exception as exc:
            if _is_rate_limit_exception(exc):
                rate_limited = True
                blockers.append(f'yfinance_rate_limited_attempt_{attempt}:{type(exc).__name__}')
                if rate_limit_mode == 'stop':
                    blockers.append('batch_stopped_to_respect_yahoo_rate_limit')
                    stop_batch = True
                    return 'fetch_failed', None, None, None, blockers, attempt, rate_limited, stop_batch
                if attempt < attempts:
                    time.sleep(max(0.0, rate_limit_cooldown_seconds))
                    continue
                return 'fetch_failed', None, None, None, blockers, attempt, rate_limited, stop_batch
            return 'fetch_failed', None, None, None, [f'yfinance_exception:{type(exc).__name__}'], attempt, rate_limited, stop_batch
        if history is None or history.empty or 'Close' not in history:
            return 'fetch_failed', None, None, None, ['no_close_history_returned'], attempt, rate_limited, stop_batch
        close_series = history['Close'].dropna()
        if close_series.empty:
            return 'fetch_failed', None, None, None, ['no_non_null_close'], attempt, rate_limited, stop_batch
        close_value = _usable_close(close_series.iloc[-1])
        close_index = close_series.index[-1]
        close_date = str(getattr(close_index, 'date', lambda: close_index)())
        if close_value is None:
            return 'fetch_failed', None, close_date, _utc_now(), ['non_usable_close'], attempt, rate_limited, stop_batch
        return 'priced_non_authoritative', close_value, close_date, _utc_now(), blockers, attempt, rate_limited, stop_batch
    return 'fetch_failed', None, None, None, blockers or ['max_attempts_exhausted'], attempts, rate_limited, stop_batch


def _skipped_rate_limit_row(line: dict[str, Any], *, request_index: int, pause_seconds: float, rate_limit_cooldown_seconds: float) -> dict[str, Any]:
    return {
        'basket_id': line.get('basket_id'),
        'fund_name': line.get('fund_name'),
        'isin': line.get('isin'),
        'instrument_type': line.get('instrument_type'),
        'exchange': line.get('exchange'),
        'venue_code': line.get('venue_code'),
        'ticker': line.get('ticker'),
        'provider_symbol_yahoo': str(line.get('provider_symbol_yahoo') or '').strip(),
        'currency': line.get('currency'),
        'verification_status': str(line.get('verification_status') or 'candidate_requires_verification'),
        'pricing_status': 'fetch_failed',
        'close_date': None,
        'close_price': None,
        'source_id': 'yahoo_yfinance',
        'source_name': 'Yahoo/yfinance connectivity evidence',
        'source_quality_status': 'non_authoritative_connectivity_only',
        'source_agreement_status': 'not_agreement_gate_not_valuation_grade',
        'observed_at_utc': _utc_now(),
        'valuation_grade': False,
        'fundable': False,
        'blockers': ['not_attempted_due_to_prior_yahoo_rate_limit', 'batch_stopped_to_respect_yahoo_rate_limit'],
        'request_index': request_index,
        'attempt_count': 0,
        'rate_limited': False,
        'pause_seconds_before_request': 0.0,
        'rate_limit_cooldown_seconds': rate_limit_cooldown_seconds,
    }


def _row_from_line(
    line: dict[str, Any],
    *,
    pause_seconds: float,
    rate_limit_cooldown_seconds: float,
    max_attempts: int,
    rate_limit_mode: str,
    request_index: int,
) -> tuple[dict[str, Any], bool]:
    symbol = str(line.get('provider_symbol_yahoo') or '').strip()
    verification_status = str(line.get('verification_status') or 'candidate_requires_verification')
    attempt_count = 0
    rate_limited = False
    stop_batch = False
    if verification_status == 'policy_review_required_not_ucits' or line.get('instrument_type') != 'UCITS ETF':
        status = 'policy_review_required_not_ucits'
        close_price = None
        close_date = None
        observed_at = _utc_now()
        blockers = ['not_ucits_policy_review_required']
    elif not symbol:
        status = 'fetch_failed'
        close_price = None
        close_date = None
        observed_at = _utc_now()
        blockers = ['missing_provider_symbol_yahoo']
    else:
        status, close_price, close_date, observed_at, blockers, attempt_count, rate_limited, stop_batch = _try_yfinance_close(
            symbol,
            pause_seconds=pause_seconds,
            rate_limit_cooldown_seconds=rate_limit_cooldown_seconds,
            max_attempts=max_attempts,
            rate_limit_mode=rate_limit_mode,
        )
        if verification_status == 'candidate_requires_verification' and status == 'priced_non_authoritative':
            blockers = blockers + ['identity_or_line_verification_pending']
    row = {
        'basket_id': line.get('basket_id'),
        'fund_name': line.get('fund_name'),
        'isin': line.get('isin'),
        'instrument_type': line.get('instrument_type'),
        'exchange': line.get('exchange'),
        'venue_code': line.get('venue_code'),
        'ticker': line.get('ticker'),
        'provider_symbol_yahoo': symbol,
        'currency': line.get('currency'),
        'verification_status': verification_status,
        'pricing_status': status,
        'close_date': close_date,
        'close_price': close_price,
        'source_id': 'yahoo_yfinance',
        'source_name': 'Yahoo/yfinance connectivity evidence',
        'source_quality_status': 'non_authoritative_connectivity_only',
        'source_agreement_status': 'not_agreement_gate_not_valuation_grade',
        'observed_at_utc': observed_at,
        'valuation_grade': False,
        'fundable': False,
        'blockers': blockers,
        'request_index': request_index,
        'attempt_count': attempt_count,
        'rate_limited': rate_limited,
        'pause_seconds_before_request': pause_seconds if request_index > 1 else 0.0,
        'rate_limit_cooldown_seconds': rate_limit_cooldown_seconds,
    }
    return row, stop_batch


def build_results(
    *,
    basket_path: Path,
    run_id: str,
    output_dir: Path,
    pause_seconds: float,
    rate_limit_cooldown_seconds: float,
    max_attempts: int,
    rate_limit_mode: str,
) -> Path:
    pause_seconds = max(float(pause_seconds), MIN_PAUSE_SECONDS)
    rate_limit_cooldown_seconds = max(float(rate_limit_cooldown_seconds), MIN_RATE_LIMIT_COOLDOWN_SECONDS)
    basket = _load_yaml(basket_path)
    lines = list(basket.get('trading_lines') or [])
    rows: list[dict[str, Any]] = []
    batch_stopped_for_rate_limit = False
    for index, line in enumerate(lines, start=1):
        if batch_stopped_for_rate_limit:
            rows.append(_skipped_rate_limit_row(dict(line), request_index=index, pause_seconds=pause_seconds, rate_limit_cooldown_seconds=rate_limit_cooldown_seconds))
            continue
        if index > 1:
            time.sleep(max(0.0, pause_seconds))
        row, stop_batch = _row_from_line(
            dict(line),
            pause_seconds=pause_seconds,
            rate_limit_cooldown_seconds=rate_limit_cooldown_seconds,
            max_attempts=max_attempts,
            rate_limit_mode=rate_limit_mode,
            request_index=index,
        )
        rows.append(row)
        if stop_batch:
            batch_stopped_for_rate_limit = True
    venues = {str(row['exchange']) for row in rows if row.get('exchange')}
    currencies = {str(row['currency']) for row in rows if row.get('currency')}
    priced = [row for row in rows if row.get('pricing_status') == 'priced_non_authoritative' and row.get('close_price') is not None]
    failed = [row for row in rows if row.get('pricing_status') == 'fetch_failed']
    payload = {
        'schema_version': 'ucits_close_price_validation_basket_results_v1',
        'run_id': run_id,
        'source_basket': str(basket_path),
        'generated_at_utc': _utc_now(),
        'line_count': len(rows),
        'priced_line_count': len(priced),
        'failed_line_count': len(failed),
        'venue_count': len(venues),
        'currency_count': len(currencies),
        'min_threshold_met': len(rows) >= 8 and len(venues) >= 3 and len(currencies) >= 2,
        'throttle_policy': {
            'source': 'yahoo_yfinance',
            'official_published_limit_found': False,
            'requests_are_serialized': True,
            'pause_seconds_between_symbols': pause_seconds,
            'rate_limit_mode': rate_limit_mode,
            'rate_limit_cooldown_seconds': rate_limit_cooldown_seconds,
            'max_attempts_per_symbol': max_attempts,
            'default_policy': 'pause_between_requests_and_stop_batch_on_rate_limit_by_default',
            'minimum_policy_enforced': True,
        },
        'rate_limit_observed': any(row.get('rate_limited') for row in rows),
        'batch_stopped_for_rate_limit': batch_stopped_for_rate_limit,
        'valuation_grade': False,
        'funding_authority': False,
        'portfolio_mutation': False,
        'production_delivery_authority': False,
        'rows': rows,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / f'ucits_close_price_validation_basket_results_{run_id}.json'
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(
        'UCITS_CLOSE_PRICE_VALIDATION_BASKET_RESULTS_OK'
        f' | path={out}'
        f' | priced={len(priced)}'
        f' | lines={len(rows)}'
        f' | pause_seconds={pause_seconds}'
        f' | rate_limit_mode={rate_limit_mode}'
        f' | stopped_for_rate_limit={batch_stopped_for_rate_limit}'
    )
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--basket', default='config/ucits_close_price_validation_basket.yml')
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--output-dir', default='output/pricing')
    parser.add_argument('--pause-seconds', type=float, default=15.0)
    parser.add_argument('--rate-limit-cooldown-seconds', type=float, default=600.0)
    parser.add_argument('--max-attempts', type=int, default=2)
    parser.add_argument('--rate-limit-mode', choices=('stop', 'sleep'), default='stop')
    args = parser.parse_args()
    build_results(
        basket_path=Path(args.basket),
        run_id=args.run_id,
        output_dir=Path(args.output_dir),
        pause_seconds=args.pause_seconds,
        rate_limit_cooldown_seconds=args.rate_limit_cooldown_seconds,
        max_attempts=args.max_attempts,
        rate_limit_mode=args.rate_limit_mode,
    )


if __name__ == '__main__':
    main()
