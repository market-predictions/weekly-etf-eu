from __future__ import annotations

import json
from pathlib import Path

CONTRACT = Path('control/ETF_EU_MVP18B_CONTROLLED_SENDER_ENTRYPOINT_IMPLEMENTATION_V1.md')
ARTIFACT = Path('output/client_surface/etf_eu_mvp18b_controlled_sender_entrypoint_implementation_20260708_000000.json')
NOTES = Path('output/client_surface/etf_eu_mvp18b_controlled_sender_entrypoint_implementation_notes_20260708_000000.md')
SENDER = Path('runtime/send_etf_eu_controlled_report.py')
WRITER = Path('runtime/write_etf_eu_delivery_evidence.py')
WORKFLOW = Path('.github/workflows/send-weekly-etf-eu-report.yml')


def validate() -> dict:
    for path in [CONTRACT, ARTIFACT, NOTES, SENDER, WRITER, WORKFLOW]:
        assert path.exists(), f'missing {path}'
    data = json.loads(ARTIFACT.read_text(encoding='utf-8'))
    assert data['work_package_id'] == 'ETF-EU-MVP18B'
    assert data['source_work_package'] == 'ETF-EU-MVP18'
    assert data['reference_architecture_repo'] == 'market-predictions/weekly-etf'
    assert data['source_of_truth_repo'] == 'market-predictions/weekly-etf-eu'
    assert data['port_behavior_not_us_assumptions'] is True
    assert data['us_assumptions_copied'] is False
    assert data['mvp18_execution_status'] == 'first_controlled_execution_placeholder_verified'
    assert data['sender_entrypoint_created'] is True
    assert data['sender_entrypoint_path'] == 'runtime/send_etf_eu_controlled_report.py'
    assert data['sender_entrypoint_requires_explicit_confirmation_flag'] is True
    assert data['sender_entrypoint_writes_transport_result'] is True
    assert data['sender_entrypoint_uses_redacted_hash_evidence'] is True
    assert data['evidence_writer_extended'] is True
    assert data['evidence_writer_supports_mvp18_controlled'] is True
    assert data['workflow_wiring_completed'] is False
    assert data['workflow_write_blocked_by_connector'] is True
    assert data['existing_workflow_still_placeholder'] is True
    for key in ['real_transport_performed', 'receipt_confirmed', 'completion_claimed', 'private_values_exposed', 'plain_contact_values_exposed', 'portfolio_mutation', 'funding_authority', 'valuation_grade']:
        assert data[key] is False
    assert data['recipient_policy'] == 'redacted_hash_only'
    assert data['selected_next_package'] == 'ETF-EU-MVP18B-FIX'
    sender_text = SENDER.read_text(encoding='utf-8')
    for token in ['--confirm-controlled-send', 'etf_eu_controlled_transport_result_v1', 'redacted_hash_only', 'transport_succeeded_unconfirmed']:
        assert token in sender_text
    writer_text = WRITER.read_text(encoding='utf-8')
    for token in ['--mvp18-controlled', '--transport-result-path', 'mvp18_controlled_post', 'transport_succeeded_unconfirmed']:
        assert token in writer_text
    workflow_text = WORKFLOW.read_text(encoding='utf-8')
    assert 'MVP15 guarded transport placeholder' in workflow_text
    return {'status': 'valid', 'work_package_id': 'ETF-EU-MVP18B', 'implementation_status': data['implementation_status'], 'selected_next_package': data['selected_next_package']}


if __name__ == '__main__':
    print(json.dumps(validate(), indent=2))
