from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError('PyYAML is required')
    return yaml.safe_load(path.read_text(encoding='utf-8')) or {}


def _try_yfinance_close(symbol: str) -> tuple[str, float | None, str | None, str | None, list[str]]:
    blockers: list[str] = []
    try:
        import yfinance as yf  # type: ignore
    except Exception:
        return 'fetch_failed', None, None, None, ['yfinance_not_available']
    try:
        history = yf.Ticker(symbol).history(period='10d', interval='1d', auto_adjust=False)
    except Exception as exc:
        return 'fetch_failed', None, None, None, [f'yfinance_exception:{type(exc).__name__}']
    if history is None or history.empty or 'Close' not in history:
        return 'fetch_failed', None, None, None, ['no_close_history_returned']
    close_series = history['Close'].dropna()
    if close_series.empty:
        return 'fetch_failed', None, None, None, ['no_non_null_close']
    close_value = float(close_series.iloc[-1])
    close_index = close_series.index[-1]
    close_date = str(getattr(close_index, 'date', lambda: close_index)())
    if close_value <= 0:
        blockers.append('non_positive_close')
        return 'fetch_failed', close_value, close_date, _utc_now(), blockers
    return 'priced_non_authoritative', close_value, close_date, _utc_now(), blockers


def _row_from_line(line: dict[str, Any]) -> dict[str, Any]:
    symbol = str(line.get('provider_symbol_yahoo') or '').strip()
    verification_status = str(line.get('verification_status') or 'candidate_requires_verification')
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
        status, close_price, close_date, observed_at, blockers = _try_yfinance_close(symbol)
        if verification_status == 'candidate_requires_verification' and status == 'priced_non_authoritative':
            blockers = blockers + ['identity_or_line_verification_pending']
    return {
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
    }


def build_results(*, basket_path: Path, run_id: str, output_dir: Path) -> Path:
    basket = _load_yaml(basket_path)
    lines = list(basket.get('trading_lines') or [])
    rows = [_row_from_line(dict(line)) for line in lines]
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
        'valuation_grade': False,
        'funding_authority': False,
        'portfolio_mutation': False,
        'production_delivery_authority': False,
        'rows': rows,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / f'ucits_close_price_validation_basket_results_{run_id}.json'
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f'UCITS_CLOSE_PRICE_VALIDATION_BASKET_RESULTS_OK | path={out} | priced={len(priced)} | lines={len(rows)}')
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--basket', default='config/ucits_close_price_validation_basket.yml')
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--output-dir', default='output/pricing')
    args = parser.parse_args()
    build_results(basket_path=Path(args.basket), run_id=args.run_id, output_dir=Path(args.output_dir))


if __name__ == '__main__':
    main()
