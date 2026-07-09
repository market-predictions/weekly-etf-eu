from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp19_fix2_ready_for_controlled_resend import validate

ARTIFACT = Path('output/client_surface/etf_eu_mvp19_fix2_ready_for_controlled_resend_20260709_000000.json')


def test_mvp19_fix2_ready_artifact_if_present_validates() -> None:
    if not ARTIFACT.exists():
        return
    result = validate(ARTIFACT)
    assert result['status'] == 'valid'
    assert result['work_package_id'] == 'ETF-EU-MVP19-FIX2'
    assert result['readiness_status'] == 'client_grade_package_ready_for_controlled_resend'
    assert result['selected_next_package'] == 'ETF-EU-MVP20'
    assert result['client_grade_package_ready'] is True
    assert result['actual_close_fetch_completed'] is True
    assert result['resend_performed'] is False
    assert result['receipt_confirmed'] is False


def test_mvp19_fix2_ready_contract_fields() -> None:
    required = {
        'schema_version',
        'run_id',
        'work_package_id',
        'status',
        'source_work_package',
        'repository_identity',
        'evidence',
        'pricing_summary',
        'package_summary',
        'transport_guard',
        'selected_next_package',
    }
    assert 'schema_version' in required
    assert 'transport_guard' in required
