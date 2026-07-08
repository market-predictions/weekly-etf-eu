from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp18_first_controlled_send_execution import A, C, N, validate


def _artifact() -> dict:
    return json.loads(A.read_text(encoding='utf-8'))


def test_files_exist() -> None:
    assert A.exists()
    assert C.exists()
    assert N.exists()


def test_artifact_identity_and_source() -> None:
    d = _artifact()
    assert d['work_package_id'] == 'ETF-EU-MVP18'
    assert d['source_work_package'] == 'ETF-EU-MVP17'
    assert d['reference_architecture_repo'] == 'market-predictions/weekly-etf'
    assert d['source_of_truth_repo'] == 'market-predictions/weekly-etf-eu'
    assert d['mvp17_readiness_status'] == 'first_controlled_execution_ready'


def test_workflow_evidence() -> None:
    d = _artifact()
    assert d['workflow_run_id'] == '28978585453'
    assert d['workflow_status'] == 'completed'
    assert d['workflow_conclusion'] == 'success'
    assert d['workflow_job_id'] == '85991661805'
    assert d['requested_delivery_mode'] == 'send'
    assert d['requested_send_confirmation'] == 'confirm_guarded_send'
    assert d['confirmation_precondition_step_success'] is True
    assert d['mvp09_evidence_gate_step_success'] is True
    assert d['run_bundle_step_success'] is True
    assert d['delivery_manifest_step_success'] is True


def test_placeholder_outcome() -> None:
    d = _artifact()
    assert d['guarded_placeholder_step_success'] is True
    assert d['real_sender_entrypoint_called'] is False
    assert d['transport_attempted'] is False
    assert d['transport_status'] == 'not_attempted'
    assert d['execution_status'] == 'first_controlled_execution_placeholder_verified'
    assert d['selected_next_package'] == 'ETF-EU-MVP18B'


def test_boundary_and_objects() -> None:
    d = _artifact()
    assert d['recipient_policy'] == 'redacted_hash_only'
    for key in ['plaintext_contacts_exposed', 'private_values_exposed', 'portfolio_mutation', 'funding_authority', 'valuation_grade', 'receipt_confirmed', 'completion_claimed', 'us_assumptions_copied']:
        assert d[key] is False
    assert d['transport_evidence']['real_sender_entrypoint_called'] is False
    assert d['receipt_evidence']['receipt_confirmed'] is False
    assert d['boundary_decision']['recipient_policy'] == 'redacted_hash_only'
    assert d['next_step_decision']['recommended_next_package'] == 'ETF-EU-MVP18B'


def test_validator_passes() -> None:
    result = validate()
    assert result['status'] == 'valid'
    assert result['execution_status'] == 'first_controlled_execution_placeholder_verified'
    assert result['selected_next_package'] == 'ETF-EU-MVP18B'
