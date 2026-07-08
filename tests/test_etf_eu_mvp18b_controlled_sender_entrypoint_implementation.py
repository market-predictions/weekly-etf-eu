from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp18b_controlled_sender_entrypoint_implementation import ARTIFACT, CONTRACT, NOTES, SENDER, WRITER, WORKFLOW, validate


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding='utf-8'))


def test_files_exist() -> None:
    for path in [CONTRACT, ARTIFACT, NOTES, SENDER, WRITER, WORKFLOW]:
        assert path.exists()


def test_artifact_core() -> None:
    data = _artifact()
    assert data['work_package_id'] == 'ETF-EU-MVP18B'
    assert data['source_work_package'] == 'ETF-EU-MVP18'
    assert data['reference_architecture_repo'] == 'market-predictions/weekly-etf'
    assert data['source_of_truth_repo'] == 'market-predictions/weekly-etf-eu'
    assert data['port_behavior_not_us_assumptions'] is True
    assert data['us_assumptions_copied'] is False
    assert data['implementation_status'] == 'controlled_sender_entrypoint_implemented_workflow_wiring_blocked'
    assert data['selected_next_package'] == 'ETF-EU-MVP18B-FIX'


def test_sender_and_writer_support() -> None:
    sender = SENDER.read_text(encoding='utf-8')
    assert '--confirm-controlled-send' in sender
    assert 'etf_eu_controlled_transport_result_v1' in sender
    assert 'transport_succeeded_unconfirmed' in sender
    assert 'redacted_hash_only' in sender
    writer = WRITER.read_text(encoding='utf-8')
    assert '--mvp18-controlled' in writer
    assert '--transport-result-path' in writer
    assert 'mvp18_controlled_post' in writer


def test_workflow_wiring_not_completed_yet() -> None:
    data = _artifact()
    assert data['workflow_wiring_completed'] is False
    assert data['workflow_write_blocked_by_connector'] is True
    assert data['existing_workflow_still_placeholder'] is True
    assert 'MVP15 guarded transport placeholder' in WORKFLOW.read_text(encoding='utf-8')


def test_boundaries() -> None:
    data = _artifact()
    for key in ['real_transport_performed', 'receipt_confirmed', 'completion_claimed', 'private_values_exposed', 'plain_contact_values_exposed', 'portfolio_mutation', 'funding_authority', 'valuation_grade']:
        assert data[key] is False
    assert data['recipient_policy'] == 'redacted_hash_only'


def test_validator_passes() -> None:
    result = validate()
    assert result['status'] == 'valid'
    assert result['selected_next_package'] == 'ETF-EU-MVP18B-FIX'
