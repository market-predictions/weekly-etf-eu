from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_ucits_close_price_validation_basket import BASKET, validate

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def _data() -> dict:
    assert yaml is not None
    return yaml.safe_load(BASKET.read_text(encoding='utf-8'))


def test_basket_validator_passes() -> None:
    result = validate()
    assert result['status'] == 'valid'
    assert result['trading_line_count'] >= 8
    assert result['venue_count'] >= 3
    assert result['currency_count'] >= 2


def test_no_authority_flags() -> None:
    data = _data()
    assert data['authority']['portfolio_mutation'] is False
    assert data['authority']['funding_authority'] is False
    assert data['authority']['valuation_grade'] is False
    assert data['authority']['us_etfs_allowed_as_investable_candidates'] is False


def test_lines_are_ucits_or_policy_review() -> None:
    data = _data()
    lines = data['trading_lines']
    assert len(lines) >= 8
    for row in lines:
        assert row['instrument_type'] == 'UCITS ETF'
        assert row['isin'] != 'TBD'
        assert row['provider_symbol_yahoo']
        assert row['valuation_grade'] is False
        assert row['fundable'] is False
    excluded = data['excluded_or_policy_review']
    assert any(row['verification_status'] == 'policy_review_required_not_ucits' for row in excluded)
