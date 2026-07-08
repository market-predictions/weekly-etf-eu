from __future__ import annotations

import json
from pathlib import Path

CONTRACT = Path('control/ETF_EU_MVP18B_FIX_CONTROLLED_TRANSPORT_WORKFLOW_WIRING_V1.md')
ARTIFACT = Path('output/client_surface/etf_eu_mvp18b_fix_controlled_transport_workflow_wiring_20260708_000000.json')
NOTES = Path('output/client_surface/etf_eu_mvp18b_fix_controlled_transport_workflow_wiring_notes_20260708_000000.md')
WORKFLOW = Path('.github/workflows/send-weekly-etf-eu-controlled-transport.yml')
SENDER = Path('runtime/send_etf_eu_controlled_report.py')
WRITER = Path('runtime/write_etf_eu_delivery_evidence.py')
RECEIPT = Path('runtime/check_etf_eu_delivery_receipt.py')


def validate() -> dict:
    for path in [CONTRACT, ARTIFACT, NOTES, WORKFLOW, SENDER, WRITER, RECEIPT]:
        assert path.exists(), f'missing {path}'
    data = json.loads(ARTIFACT.read_text(encoding='utf-8'))
    assert data['work_package_id'] == 'ETF-EU-MVP18B-FIX'
    assert data['source_work_package'] == 'ETF-EU-MVP18B'
    assert data['reference_architecture_repo'] == 'market-predictions/weekly-etf'
    assert data['source_of_truth_repo'] == 'market-predictions/weekly-etf-eu'
    assert data['port_behavior_not_us_assumptions'] is True
    assert data['us_assumptions_copied'] is False
    assert data['standalone_controlled_transport_workflow_created'] is True
    assert data['primary_bootstrap_workflow_changed'] is False
    assert data['controlled_transport_workflow_path'] == '.github/workflows/send-weekly-etf-eu-controlled-transport.yml'
    assert data['controlled_transport_workflow_requires_manual_dispatch'] is True
    assert data['controlled_transport_workflow_requires_send_mode'] is True
    assert data['controlled_transport_workflow_requires_second_confirmation'] is True
    assert data['controlled_transport_workflow_requires_report_suffix'] is True
    for key in ['real_transport_performed', 'receipt_confirmed', 'completion_claimed', 'private_values_exposed', 'plain_contact_values_exposed', 'portfolio_mutation', 'funding_authority', 'valuation_grade']:
        assert data[key] is False
    assert data['recipient_policy'] == 'redacted_hash_only'
    assert data['selected_next_package'] == 'ETF-EU-MVP18C'
    workflow = WORKFLOW.read_text(encoding='utf-8')
    for token in ['Weekly ETF EU controlled transport', 'workflow_dispatch', 'delivery_mode', 'send_confirmation', 'report_suffix', 'confirm_guarded_send', 'runtime.send_etf_eu_controlled_report', 'runtime.write_etf_eu_delivery_evidence', 'runtime.check_etf_eu_delivery_receipt']:
        assert token in workflow
    for token in ['ETF_EU_TRANSPORT_HOST', 'ETF_EU_TRANSPORT_PORT', 'ETF_EU_TRANSPORT_USER', 'ETF_EU_TRANSPORT_AUTH', 'ETF_EU_FROM_ADDRESS', 'ETF_EU_TO_NL', 'ETF_EU_TO_EN']:
        assert token in workflow
    sender = SENDER.read_text(encoding='utf-8')
    assert '--confirm-controlled-send' in sender
    assert 'etf_eu_controlled_transport_result_v1' in sender
    writer = WRITER.read_text(encoding='utf-8')
    assert '--mvp18-controlled' in writer
    assert '--transport-result-path' in writer
    return {'status': 'valid', 'work_package_id': 'ETF-EU-MVP18B-FIX', 'implementation_status': data['implementation_status'], 'selected_next_package': data['selected_next_package']}


if __name__ == '__main__':
    print(json.dumps(validate(), indent=2))
