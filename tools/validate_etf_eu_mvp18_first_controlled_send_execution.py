from __future__ import annotations

import json
from pathlib import Path

A = Path('output/client_surface/etf_eu_mvp18_first_controlled_send_execution_20260708_000000.json')
C = Path('control/ETF_EU_MVP18_FIRST_CONTROLLED_SEND_EXECUTION_V1.md')
N = Path('output/client_surface/etf_eu_mvp18_first_controlled_send_execution_notes_20260708_000000.md')


def validate() -> dict:
    assert A.exists()
    assert C.exists()
    assert N.exists()
    d = json.loads(A.read_text(encoding='utf-8'))
    assert d['work_package_id'] == 'ETF-EU-MVP18'
    assert d['source_work_package'] == 'ETF-EU-MVP17'
    assert d['reference_architecture_repo'] == 'market-predictions/weekly-etf'
    assert d['source_of_truth_repo'] == 'market-predictions/weekly-etf-eu'
    assert d['port_behavior_not_us_assumptions'] is True
    assert d['us_assumptions_copied'] is False
    assert d['mvp17_readiness_status'] == 'first_controlled_execution_ready'
    assert d['mvp17_selected_next_package'] == 'ETF-EU-MVP18'
    assert d['workflow_dispatch_performed'] is True
    assert d['workflow_status'] == 'completed'
    assert d['workflow_conclusion'] == 'success'
    assert d['requested_delivery_mode'] == 'send'
    assert d['requested_send_confirmation'] == 'confirm_guarded_send'
    assert d['confirmation_precondition_step_success'] is True
    assert d['mvp09_evidence_gate_step_success'] is True
    assert d['run_bundle_step_success'] is True
    assert d['delivery_manifest_step_success'] is True
    assert d['recipient_policy'] == 'redacted_hash_only'
    assert d['plaintext_contacts_exposed'] is False
    assert d['private_values_exposed'] is False
    assert d['portfolio_mutation'] is False
    assert d['funding_authority'] is False
    assert d['valuation_grade'] is False
    assert not (d['completion_claimed'] is True and d['receipt_confirmed'] is False)
    status = d['execution_status']
    assert status in {'first_controlled_transport_attempted', 'first_controlled_execution_placeholder_verified', 'first_controlled_execution_failed_or_unconfirmed'}
    if status == 'first_controlled_transport_attempted':
        assert d['selected_next_package'] == 'ETF-EU-MVP19'
    elif status == 'first_controlled_execution_placeholder_verified':
        assert d['selected_next_package'] == 'ETF-EU-MVP18B'
        assert d['transport_attempted'] is False
        assert d['real_sender_entrypoint_called'] is False
        assert d['transport_status'] == 'not_attempted'
    else:
        assert d['selected_next_package'] == 'ETF-EU-MVP18-FIX'
    assert not d['selected_next_package'].startswith('ETF-EU-WP15')
    assert d['selected_next_package'] != 'OPERATOR_ACTION_REQUIRED'
    return {'status': 'valid', 'work_package_id': 'ETF-EU-MVP18', 'execution_status': status, 'selected_next_package': d['selected_next_package']}


if __name__ == '__main__':
    print(json.dumps(validate(), indent=2))
