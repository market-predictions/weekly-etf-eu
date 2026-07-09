from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp19_client_grade_delivery_and_ucits_price_expansion import ARTIFACT, EN_REPORT, NL_REPORT, validate
from tools.validate_ucits_close_price_validation_basket import validate as validate_basket


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding='utf-8'))


def test_mvp19_artifact_core() -> None:
    data = _artifact()
    assert data['work_package_id'] == 'ETF-EU-MVP19'
    assert data['source_work_package'] == 'ETF-EU-MVP18C'
    assert data['reference_architecture_repo'] == 'market-predictions/weekly-etf'
    assert data['source_of_truth_repo'] == 'market-predictions/weekly-etf-eu'
    assert data['port_behavior_not_us_assumptions'] is True
    assert data['us_assumptions_copied'] is False


def test_package_not_ready_yet() -> None:
    data = _artifact()
    assert data['client_grade_package_ready'] is False
    assert data['pdf_output_available'] is False
    assert data['markdown_only_delivery_detected'] is True
    assert data['stale_delivery_wording_detected'] is True
    assert data['main_surface_us_proxy_exposure_detected'] is True
    assert data['readiness_status'] == 'ucits_pricing_or_package_hardening_required'
    assert data['selected_next_package'] == 'ETF-EU-MVP19-FIX'


def test_uploaded_report_defects_are_detectable() -> None:
    nl = NL_REPORT.read_text(encoding='utf-8')
    en = EN_REPORT.read_text(encoding='utf-8')
    assert 'geen e-maillevering uitgevoerd' in nl
    assert 'no email delivery was performed' in en
    assert 'SPY' in nl
    assert 'SPY' in en


def test_ucits_close_price_basket_thresholds() -> None:
    result = validate_basket()
    assert result['status'] == 'valid'
    assert result['trading_line_count'] >= 8
    assert result['venue_count'] >= 3
    assert result['currency_count'] >= 2
    assert result['valuation_grade'] is False
    assert result['funding_authority'] is False


def test_mvp19_validator_passes() -> None:
    result = validate()
    assert result['status'] == 'valid'
    assert result['selected_next_package'] == 'ETF-EU-MVP19-FIX'
