from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp19_fix_client_package_and_ucits_close_fetch import ARTIFACT, CLOSE_RUNNER, PACKAGE_RENDERER, SENDER, WORKFLOW, validate


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding='utf-8'))


def test_artifact_identity() -> None:
    data = _artifact()
    assert data['work_package_id'] == 'ETF-EU-MVP19-FIX'
    assert data['source_work_package'] == 'ETF-EU-MVP19'
    assert data['reference_architecture_repo'] == 'market-predictions/weekly-etf'
    assert data['source_of_truth_repo'] == 'market-predictions/weekly-etf-eu'
    assert data['port_behavior_not_us_assumptions'] is True
    assert data['us_assumptions_copied'] is False


def test_implementation_files_exist() -> None:
    assert CLOSE_RUNNER.exists()
    assert PACKAGE_RENDERER.exists()
    assert SENDER.exists()
    assert WORKFLOW.exists()


def test_sender_and_workflow_require_pdf_package() -> None:
    sender = SENDER.read_text(encoding='utf-8')
    workflow = WORKFLOW.read_text(encoding='utf-8')
    assert '--require-pdf-package' in sender
    assert '--delivery-package-manifest' in sender
    assert '--require-pdf-package' in workflow
    assert '--delivery-package-manifest' in workflow
    assert 'validate_etf_eu_delivery_package_manifest.py' in workflow


def test_no_authority_or_resend_flags() -> None:
    data = _artifact()
    for key in ['resend_performed', 'delivery_success_closed', 'receipt_confirmed', 'completion_claimed', 'valuation_grade', 'funding_authority', 'portfolio_mutation', 'production_delivery_authority']:
        assert data[key] is False


def test_next_package_mapping() -> None:
    data = _artifact()
    assert data['readiness_status'] == 'client_package_or_price_fetch_hardening_still_required'
    assert data['selected_next_package'] == 'ETF-EU-MVP19-FIX2'


def test_validator_passes() -> None:
    assert validate()['status'] == 'valid'
