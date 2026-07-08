from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp17_first_controlled_execution_readiness_decision import A, C, N, validate


def test_files_exist() -> None:
    assert A.exists()
    assert C.exists()
    assert N.exists()


def test_artifact_core() -> None:
    d = json.loads(A.read_text(encoding='utf-8'))
    assert d['work_package_id'] == 'ETF-EU-MVP17'
    assert d['source_work_package'] == 'ETF-EU-MVP16'
    assert d['reference_architecture_repo'] == 'market-predictions/weekly-etf'
    assert d['source_of_truth_repo'] == 'market-predictions/weekly-etf-eu'
    assert d['mvp16_dry_run_status'] == 'guarded_dry_run_verified'
    assert d['mvp16_workflow_run_id'] == '28976148251'
    assert d['mvp16_workflow_conclusion'] == 'success'
    assert d['mvp16_requested_mode'] == 'dry_run'
    assert d['mvp16_requested_confirmation'] == 'not_confirmed'
    assert d['mvp16_protected_path_active'] is False
    assert d['readiness_status'] == 'first_controlled_execution_ready'
    assert d['selected_next_package'] == 'ETF-EU-MVP18'


def test_mvp18_objects() -> None:
    d = json.loads(A.read_text(encoding='utf-8'))
    p = d['execution_preconditions_for_mvp18']
    assert p['manual_workflow_dispatch_required'] is True
    assert p['delivery_mode_send_required'] is True
    assert p['send_confirmation_required'] is True
    assert p['send_confirmation_required_value'] == 'confirm_guarded_send'
    assert p['recipient_policy'] == 'redacted_hash_only'
    assert p['delayed_receipt_check_minutes'] == 10
    e = d['evidence_requirements_for_mvp18']
    assert e['workflow_run_id_required'] is True
    assert e['recipient_hashes_only'] is True
    assert e['plaintext_contacts_allowed'] is False
    r = d['delayed_receipt_check_requirements']
    assert r['delayed_check_required'] is True
    assert r['delay_minutes'] == 10


def test_boundary_flags_false() -> None:
    d = json.loads(A.read_text(encoding='utf-8'))
    for key in ['delivery_mode_send_used', 'send_confirmation_used', 'guarded_operation_performed', 'completion_claimed', 'receipt_confirmed', 'private_values_exposed', 'plain_contact_values_exposed', 'portfolio_mutation', 'funding_authority', 'valuation_grade', 'us_assumptions_copied']:
        assert d[key] is False
        assert d['boundary_decision'][key] is False


def test_next_step_and_validator() -> None:
    d = json.loads(A.read_text(encoding='utf-8'))
    assert d['next_step_decision']['recommended_next_package'] == 'ETF-EU-MVP18'
    assert d['next_step_decision']['fallback_next_package'] == 'ETF-EU-MVP17-FIX'
    assert not d['selected_next_package'].startswith('ETF-EU-WP15')
    assert d['selected_next_package'] != 'OPERATOR_ACTION_REQUIRED'
    assert validate()['status'] == 'valid'
