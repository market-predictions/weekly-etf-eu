from __future__ import annotations

import json
from pathlib import Path

from tools.validate_ucits_close_price_validation_basket import validate as validate_basket

CONTRACT = Path('control/ETF_EU_MVP19_CLIENT_GRADE_DELIVERY_AND_UCITS_PRICE_EXPANSION_V1.md')
ARTIFACT = Path('output/client_surface/etf_eu_mvp19_client_grade_delivery_and_ucits_price_expansion_20260709_000000.json')
NOTES = Path('output/client_surface/etf_eu_mvp19_client_grade_delivery_and_ucits_price_expansion_notes_20260709_000000.md')
NL_REPORT = Path('output/weekly_etf_eu_review_nl_260708.md')
EN_REPORT = Path('output/weekly_etf_eu_review_260708.md')


def _load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding='utf-8'))


def validate() -> dict:
    for path in [CONTRACT, ARTIFACT, NOTES, NL_REPORT, EN_REPORT]:
        assert path.exists(), f'missing {path}'
    data = _load()
    assert data['work_package_id'] == 'ETF-EU-MVP19'
    assert data['source_work_package'] == 'ETF-EU-MVP18C'
    assert data['reference_architecture_repo'] == 'market-predictions/weekly-etf'
    assert data['source_of_truth_repo'] == 'market-predictions/weekly-etf-eu'
    assert data['port_behavior_not_us_assumptions'] is True
    assert data['us_assumptions_copied'] is False
    assert data['mvp18c_transport_status'] == 'transport_succeeded_unconfirmed'
    assert data['mvp18c_receipt_confirmed'] is False
    assert data['mvp18c_completion_claimed'] is False
    assert data['delivery_success_closed'] is False
    assert data['client_grade_package_ready'] is False
    assert data['pdf_output_available'] is False
    assert data['markdown_only_delivery_detected'] is True
    assert data['stale_delivery_wording_detected'] is True
    assert data['main_surface_us_proxy_exposure_detected'] is True
    assert data['main_surface_tbd_candidate_exposure_detected'] is True
    assert data['ucits_close_price_validation_basket_created'] is True
    basket = validate_basket()
    assert basket['trading_line_count'] >= 8
    assert basket['venue_count'] >= 3
    assert basket['currency_count'] >= 2
    assert data['ucits_close_price_minimum_threshold_met'] is True
    assert data['ucits_close_price_actual_fetch_completed'] is False
    assert data['valuation_grade'] is False
    assert data['funding_authority'] is False
    assert data['portfolio_mutation'] is False
    assert data['production_delivery_authority'] is False
    assert data['readiness_status'] == 'ucits_pricing_or_package_hardening_required'
    assert data['selected_next_package'] == 'ETF-EU-MVP19-FIX'
    nl = NL_REPORT.read_text(encoding='utf-8')
    en = EN_REPORT.read_text(encoding='utf-8')
    assert 'geen e-maillevering uitgevoerd' in nl
    assert 'no email delivery was performed' in en
    assert 'SPY' in nl and 'SPY' in en
    return {
        'status': 'valid',
        'work_package_id': 'ETF-EU-MVP19',
        'readiness_status': data['readiness_status'],
        'selected_next_package': data['selected_next_package'],
        'ucits_lines': basket['trading_line_count'],
    }


if __name__ == '__main__':
    print(json.dumps(validate(), indent=2))
