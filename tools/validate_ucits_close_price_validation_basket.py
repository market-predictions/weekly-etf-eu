from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

BASKET = Path('config/ucits_close_price_validation_basket.yml')
US_ETF_TICKERS = {'SPY', 'SMH', 'GLD', 'PAVE', 'QQQ', 'DIA', 'IWM'}


def _load(path: Path = BASKET) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError('PyYAML is required')
    return yaml.safe_load(path.read_text(encoding='utf-8')) or {}


def validate(path: Path = BASKET) -> dict[str, Any]:
    data = _load(path)
    assert data['schema_version'] == 'ucits_close_price_validation_basket_v1'
    assert data['basket_status'] == 'controlled_validation_universe'
    assert data['authority']['portfolio_mutation'] is False
    assert data['authority']['funding_authority'] is False
    assert data['authority']['valuation_grade'] is False
    assert data['authority']['us_etfs_allowed_as_investable_candidates'] is False
    lines = list(data.get('trading_lines') or [])
    assert len(lines) >= int(data['minimum_thresholds']['min_trading_lines'])
    venues = {row['exchange'] for row in lines}
    currencies = {row['currency'] for row in lines}
    assert len(venues) >= int(data['minimum_thresholds']['min_venues'])
    assert len(currencies) >= int(data['minimum_thresholds']['min_currencies'])
    assert data['minimum_thresholds']['no_nan_in_client_surface'] is True
    assert data['minimum_thresholds']['unresolved_prices_go_to_diagnostics_only'] is True
    for row in lines:
        assert row['instrument_type'] == 'UCITS ETF'
        assert row['isin'] and row['isin'] != 'TBD'
        assert row['provider_symbol_yahoo']
        assert row['currency'] in {'EUR', 'USD', 'GBP'}
        assert row['valuation_grade'] is False
        assert row['fundable'] is False
        assert row['verification_status'] in {'verified_ucits_trading_line', 'candidate_requires_verification'}
        if row['ticker'] in US_ETF_TICKERS:
            assert row['isin'].startswith('IE'), 'ticker collision must remain ISIN-first UCITS evidence'
    excluded = list(data.get('excluded_or_policy_review') or [])
    assert excluded
    assert any(row['verification_status'] == 'policy_review_required_not_ucits' for row in excluded)
    return {
        'status': 'valid',
        'basket': str(path),
        'trading_line_count': len(lines),
        'venue_count': len(venues),
        'currency_count': len(currencies),
        'valuation_grade': False,
        'funding_authority': False,
    }


if __name__ == '__main__':
    print(json.dumps(validate(), indent=2))
