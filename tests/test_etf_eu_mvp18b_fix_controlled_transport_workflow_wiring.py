from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp18b_fix_controlled_transport_workflow_wiring import ARTIFACT, CONTRACT, NOTES, WORKFLOW, SENDER, WRITER, validate


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding='utf-8'))


def test_files_exist() -> None:
    for path in [CONTRACT, ARTIFACT, NOTES, WORKFLOW, SENDER, WRITER]:
        assert path.exists()


def test_artifact_core() -> None:
    data = _artifact()
    assert data['work_package_id'] == 'ETF-EU-MVP18B-FIX'
    assert data['source_work_package'] == 'ETF-EU-MVP18B'
    assert data['reference_architecture_repo'] == 'market-predictions/weekly-etf'
    assert data['source_of_truth_repo'] == 'market-predictions/weekly-etf-eu'
    assert data['port_behavior_not_us_assumptions'] is True
    assert data['us_assumptions_copied'] is False
    assert data['implementation_status'] == 'controlled_transport_workflow_wired_ready_for_single_run'
    assert data['selected_next_package'] == 'ETF-EU-MVP18C'


def test_controlled_workflow_contract() -> None:
    data = _artifact()
    assert data['standalone_controlled_transport_workflow_created'] is True
    assert data['primary_bootstrap_workflow_changed'] is False
    assert data['controlled_transport_workflow_requires_manual_dispatch'] is True
    assert data['controlled_transport_workflow_requires_send_mode'] is True
    assert data['controlled_transport_workflow_requires_second_confirmation'] is True
    assert data['controlled_transport_workflow_requires_report_suffix'] is True
    text = WORKFLOW.read_text(encoding='utf-8')
    assert 'Weekly ETF EU controlled transport' in text
    assert 'workflow_dispatch' in text
    assert 'delivery_mode' in text
    assert 'send_confirmation' in text
    assert 'report_suffix' in text
    assert 'confirm_guarded_send' in text


def test_entrypoint_and_evidence_calls() -> None:
    text = WORKFLOW.read_text(encoding='utf-8')
    assert 'runtime.send_etf_eu_controlled_report' in text
    assert 'runtime.write_etf_eu_delivery_evidence' in text
    assert 'runtime.check_etf_eu_delivery_receipt' in text
    assert '--mvp18-controlled' in text
    assert '--transport-result-path' in text
    sender = SENDER.read_text(encoding='utf-8')
    assert '--confirm-controlled-send' in sender
    writer = WRITER.read_text(encoding='utf-8')
    assert '--mvp18-controlled' in writer


def test_boundary_flags() -> None:
    data = _artifact()
    for key in ['real_transport_performed', 'receipt_confirmed', 'completion_claimed', 'private_values_exposed', 'plain_contact_values_exposed', 'portfolio_mutation', 'funding_authority', 'valuation_grade']:
        assert data[key] is False
    assert data['recipient_policy'] == 'redacted_hash_only'


def test_validator_passes() -> None:
    result = validate()
    assert result['status'] == 'valid'
    assert result['selected_next_package'] == 'ETF-EU-MVP18C'
