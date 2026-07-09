from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp18c_single_controlled_transport_run import A, E, R, T, validate


def test_artifacts_exist() -> None:
    for path in [A, T, E, R]:
        assert path.exists()


def test_core_evidence() -> None:
    d = json.loads(A.read_text(encoding='utf-8'))
    assert d['work_package_id'] == 'ETF-EU-MVP18C'
    assert d['workflow_run_id'] == '29011148042'
    assert d['workflow_conclusion'] == 'success'
    assert d['transport_status'] == 'transport_succeeded_unconfirmed'
    assert d['receipt_confirmed'] is False
    assert d['completion_claimed'] is False
    assert d['selected_next_package'] == 'ETF-EU-MVP19'


def test_transport_and_evidence() -> None:
    t = json.loads(T.read_text(encoding='utf-8'))
    e = json.loads(E.read_text(encoding='utf-8'))
    r = json.loads(R.read_text(encoding='utf-8'))
    assert t['real_sender_entrypoint_called'] is True
    assert t['transport_attempted'] is True
    assert t['transport_status'] == 'transport_succeeded_unconfirmed'
    assert t['recipient_plaintext_values_exposed'] is False
    assert e['delivery_status'] == 'transport_succeeded_unconfirmed'
    assert e['delivery_success'] is False
    assert r['receipt_confirmed'] is False
    assert r['delivery_success_claimed'] is False


def test_validator_passes() -> None:
    assert validate()['status'] == 'valid'
