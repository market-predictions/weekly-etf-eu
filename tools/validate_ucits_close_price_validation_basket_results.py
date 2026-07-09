from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ALLOWED_STATUSES = {
    'priced_non_authoritative',
    'fetch_failed',
    'candidate_requires_verification',
    'policy_review_required_not_ucits',
    'diagnostics_only',
}
REQUIRED_ROW_FIELDS = {
    'basket_id', 'fund_name', 'isin', 'instrument_type', 'exchange', 'venue_code', 'ticker',
    'provider_symbol_yahoo', 'currency', 'verification_status', 'pricing_status', 'close_date',
    'close_price', 'source_id', 'source_name', 'source_quality_status', 'source_agreement_status',
    'observed_at_utc', 'valuation_grade', 'fundable', 'blockers', 'request_index', 'attempt_count',
    'rate_limited', 'pause_seconds_before_request', 'rate_limit_cooldown_seconds'
}


def validate(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding='utf-8'))
    assert data['schema_version'] == 'ucits_close_price_validation_basket_results_v1'
    assert data['source_basket'] == 'config/ucits_close_price_validation_basket.yml'
    assert data['valuation_grade'] is False
    assert data['funding_authority'] is False
    assert data['portfolio_mutation'] is False
    assert data['production_delivery_authority'] is False
    throttle = data.get('throttle_policy') or {}
    assert throttle['source'] == 'yahoo_yfinance'
    assert throttle['official_published_limit_found'] is False
    assert throttle['requests_are_serialized'] is True
    assert float(throttle['pause_seconds_between_symbols']) >= 10.0
    assert throttle.get('rate_limit_mode') in {'stop', 'sleep'}
    assert float(throttle['rate_limit_cooldown_seconds']) >= 300.0
    assert int(throttle['max_attempts_per_symbol']) >= 1
    rows = list(data.get('rows') or [])
    assert data['line_count'] == len(rows)
    assert len(rows) >= 8
    venues = {row['exchange'] for row in rows if row.get('exchange')}
    currencies = {row['currency'] for row in rows if row.get('currency')}
    assert data['venue_count'] == len(venues)
    assert data['currency_count'] == len(currencies)
    assert data['venue_count'] >= 3
    assert data['currency_count'] >= 2
    priced = 0
    failed = 0
    for row in rows:
        assert REQUIRED_ROW_FIELDS.issubset(row.keys())
        assert row['pricing_status'] in ALLOWED_STATUSES
        assert row['valuation_grade'] is False
        assert row['fundable'] is False
        assert isinstance(row['blockers'], list)
        assert row['source_quality_status'] == 'non_authoritative_connectivity_only'
        assert row['source_agreement_status'] == 'not_agreement_gate_not_valuation_grade'
        assert int(row['request_index']) >= 1
        skipped_due_rate_limit = 'not_attempted_due_to_prior_yahoo_rate_limit' in row['blockers']
        if int(row['request_index']) > 1 and not skipped_due_rate_limit:
            assert float(row['pause_seconds_before_request']) >= 10.0
        assert float(row['rate_limit_cooldown_seconds']) >= 300.0
        if row['pricing_status'] == 'priced_non_authoritative':
            assert row['close_price'] is not None
            assert float(row['close_price']) > 0
            assert row['close_date']
            priced += 1
        if row['pricing_status'] == 'fetch_failed':
            failed += 1
    assert data['priced_line_count'] == priced
    assert data['failed_line_count'] == failed
    assert data['min_threshold_met'] is True
    return {
        'status': 'valid',
        'artifact': str(path),
        'line_count': len(rows),
        'priced_line_count': priced,
        'venue_count': len(venues),
        'currency_count': len(currencies),
        'valuation_grade': False,
        'funding_authority': False,
        'throttle_policy': throttle,
        'batch_stopped_for_rate_limit': data.get('batch_stopped_for_rate_limit', False),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--artifact', required=True)
    args = parser.parse_args()
    print(json.dumps(validate(Path(args.artifact)), indent=2))


if __name__ == '__main__':
    main()
