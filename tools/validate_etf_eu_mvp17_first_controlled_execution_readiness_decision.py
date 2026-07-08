from __future__ import annotations

import json
from pathlib import Path

A = Path('output/client_surface/etf_eu_mvp17_first_controlled_execution_readiness_decision_20260708_000000.json')
C = Path('control/ETF_EU_MVP17_FIRST_CONTROLLED_EXECUTION_READINESS_DECISION_V1.md')
N = Path('output/client_surface/etf_eu_mvp17_first_controlled_execution_readiness_decision_notes_20260708_000000.md')


def validate() -> dict:
    assert A.exists()
    assert C.exists()
    assert N.exists()
    d = json.loads(A.read_text(encoding='utf-8'))
    assert d['work_package_id'] == 'ETF-EU-MVP17'
    assert d['source_work_package'] == 'ETF-EU-MVP16'
    assert d['reference_architecture_repo'] == 'market-predictions/weekly-etf'
    assert d['source_of_truth_repo'] == 'market-predictions/weekly-etf-eu'
    assert d['port_behavior_not_us_assumptions'] is True
    assert d['us_assumptions_copied'] is False
    assert d['mvp16_dry_run_status'] == 'guarded_dry_run_verified'
    assert d['mvp16_workflow_conclusion'] == 'success'
    assert d['mvp16_requested_mode'] == 'dry_run'
    assert d['mvp16_requested_confirmation'] == 'not_confirmed'
    assert d['mvp16_protected_path_active'] is False
    assert d['readiness_status'] == 'first_controlled_execution_ready'
    assert d['selected_next_package'] == 'ETF-EU-MVP18'
    for key in ['delivery_mode_send_used', 'send_confirmation_used', 'guarded_operation_performed', 'completion_claimed', 'receipt_confirmed', 'private_values_exposed', 'plain_contact_values_exposed', 'portfolio_mutation', 'funding_authority', 'valuation_grade']:
        assert d[key] is False
    return {'status': 'valid', 'work_package_id': 'ETF-EU-MVP17', 'selected_next_package': d['selected_next_package']}


if __name__ == '__main__':
    print(json.dumps(validate(), indent=2))
