from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_ucits_close_price_validation_basket_results import validate

FIXTURE = Path('output/pricing/ucits_close_price_validation_basket_results_20260709_000000.json')


def test_results_fixture_if_present_is_valid() -> None:
    if not FIXTURE.exists():
        return
    result = validate(FIXTURE)
    assert result['status'] == 'valid'
    assert result['line_count'] >= 8
    assert result['venue_count'] >= 3
    assert result['currency_count'] >= 2
    assert result['valuation_grade'] is False
    assert result['funding_authority'] is False


def test_result_schema_contract_on_sample() -> None:
    sample = {
        'schema_version': 'ucits_close_price_validation_basket_results_v1',
        'run_id': 'sample',
        'source_basket': 'config/ucits_close_price_validation_basket.yml',
        'generated_at_utc': '2026-07-09T00:00:00Z',
        'line_count': 8,
        'priced_line_count': 1,
        'failed_line_count': 7,
        'venue_count': 3,
        'currency_count': 2,
        'min_threshold_met': True,
        'valuation_grade': False,
        'funding_authority': False,
        'portfolio_mutation': False,
        'production_delivery_authority': False,
        'rows': []
    }
    required = {'schema_version', 'run_id', 'source_basket', 'rows', 'valuation_grade', 'funding_authority', 'portfolio_mutation'}
    assert required.issubset(sample.keys())
