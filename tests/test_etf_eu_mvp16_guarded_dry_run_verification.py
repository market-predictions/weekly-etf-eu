from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp16_guarded_dry_run_verification import A, C, N, validate


def test_files_exist() -> None:
    assert A.exists()
    assert C.exists()
    assert N.exists()


def test_artifact_core() -> None:
    d = json.loads(A.read_text(encoding='utf-8'))
    assert d['work_package_id'] == 'ETF-EU-MVP16'
    assert d['source_work_package'] == 'ETF-EU-MVP15-FIX'
    assert d['reference_architecture_repo'] == 'market-predictions/weekly-etf'
    assert d['source_of_truth_repo'] == 'market-predictions/weekly-etf-eu'
    assert d['workflow_run_id'] == '28976148251'
    assert d['workflow_status'] == 'completed'
    assert d['workflow_conclusion'] == 'success'
    assert d['requested_mode'] == 'dry_run'
    assert d['requested_confirmation'] == 'not_confirmed'
    assert d['protected_path_active'] is False
    assert d['dry_run_status'] == 'guarded_dry_run_verified'
    assert d['selected_next_package'] == 'ETF-EU-MVP17'


def test_false_boundary_core() -> None:
    d = json.loads(A.read_text(encoding='utf-8'))
    for key in ['completion_claimed', 'receipt_confirmed', 'private_values_exposed', 'plain_contact_values_exposed', 'portfolio_mutation', 'funding_authority', 'valuation_grade', 'us_assumptions_copied']:
        assert d[key] is False


def test_validator_passes() -> None:
    assert validate()['status'] == 'valid'
