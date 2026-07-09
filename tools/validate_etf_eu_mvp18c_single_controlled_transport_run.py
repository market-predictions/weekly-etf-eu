from __future__ import annotations

import json
from pathlib import Path

A = Path('output/client_surface/etf_eu_mvp18c_single_controlled_transport_run_20260709_101818.json')
C = Path('control/ETF_EU_MVP18C_SINGLE_CONTROLLED_TRANSPORT_RUN_V1.md')
N = Path('output/client_surface/etf_eu_mvp18c_single_controlled_transport_run_notes_20260709_101818.md')
T = Path('output/delivery/etf_eu_transport_result_20260709_101818.json')
E = Path('output/delivery/etf_eu_delivery_evidence_20260709_101818.json')
R = Path('output/delivery/etf_eu_receipt_check_20260709_101818.json')


def validate() -> dict:
    for path in [A, C, N, T, E, R]:
        assert path.exists(), f'missing {path}'
    d = json.loads(A.read_text(encoding='utf-8'))
    t = json.loads(T.read_text(encoding='utf-8'))
    e = json.loads(E.read_text(encoding='utf-8'))
    r = json.loads(R.read_text(encoding='utf-8'))
    assert d['work_package_id'] == 'ETF-EU-MVP18C'
    assert d['source_work_package'] == 'ETF-EU-MVP18B-FIX'
    assert d['workflow_run_id'] == '29011148042'
    assert d['workflow_job_id'] == '86094818706'
    assert d['workflow_conclusion'] == 'success'
    assert d['artifact_commit_sha'] == '162b6511818bf00f0f3e5902cb95a3d892d1600c'
    assert d['transport_status'] == 'transport_succeeded_unconfirmed'
    assert d['receipt_confirmed'] is False
    assert d['completion_claimed'] is False
    assert d['selected_next_package'] == 'ETF-EU-MVP19'
    assert t['real_sender_entrypoint_called'] is True
    assert t['transport_attempted'] is True
    assert t['transport_status'] == 'transport_succeeded_unconfirmed'
    assert t['receipt_confirmed'] is False
    assert e['delivery_status'] == 'transport_succeeded_unconfirmed'
    assert e['delivery_success'] is False
    assert e['recipient_plaintext_values_exposed'] is False
    assert r['receipt_confirmed'] is False
    assert r['delivery_success_claimed'] is False
    return {'status': 'valid', 'work_package_id': 'ETF-EU-MVP18C', 'selected_next_package': d['selected_next_package']}


if __name__ == '__main__':
    print(json.dumps(validate(), indent=2))
