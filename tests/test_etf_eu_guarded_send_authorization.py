from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

CONTRACT = Path("control/ETF_EU_EXPLICIT_GUARDED_SEND_AUTHORIZATION_CONTRACT_V1.md")
AUTH_PATH = Path("output/delivery_authorization/etf_eu_guarded_send_authorization_20260710_000000.json")
PREP_PATH = Path("output/delivery_prep/etf_eu_guarded_fresh_package_delivery_prep_20260710_000000.json")
ROUTINE_PATH = Path("output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json")
REQUIRED_PHRASE = "AUTHORIZE ETF-EU GUARDED SEND 20260710_000000"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_explicit_guarded_send_authorization_contract_exists() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    assert "ETF_EU_EXPLICIT_GUARDED_SEND_AUTHORIZATION_CONTRACT_V1" in text
    assert REQUIRED_PHRASE in text
    assert "MVP27 must not" in text
    assert "transport_execution_allowed=false" in text


def test_committed_authorization_artifact_is_blocked_without_exact_standalone_phrase() -> None:
    data = load_json(AUTH_PATH)
    assert data["authorization_status"] == "blocked_missing_guarded_confirmation_phrase"
    assert data["delivery_authorized"] is False
    assert data["guarded_confirmation_phrase_matched"] is False
    assert data["send_command_allowed"] is False
    assert data["workflow_dispatch_allowed"] is False
    assert data["run_queue_allowed"] is False
    assert data["transport_execution_allowed"] is False
    assert data["send_executed"] is False
    assert data["transport_attempted"] is False
    assert data["receipt_confirmed"] is False
    assert data["next_package"] == "ETF-EU-MVP27B_EXPLICIT_SEND_AUTHORIZATION_RETRY"


def test_authorization_artifact_preserves_redaction_and_no_secrets() -> None:
    data = load_json(AUTH_PATH)
    assert data["recipient_plaintext_values_exposed"] is False
    assert data["secret_values_exposed"] is False
    assert data["raw_receipt_pdf_stored_in_github"] is False


def test_routine_manifest_handoff_is_blocked() -> None:
    routine = load_json(ROUTINE_PATH)
    assert routine["delivery_authorization_artifact"] == str(AUTH_PATH)
    assert routine["routine_stage"] == "explicit_guarded_send_authorization_blocked"
    assert routine["delivery_authorized"] is False
    assert routine["send_command_allowed"] is False
    assert routine["workflow_dispatch_allowed"] is False
    assert routine["run_queue_allowed"] is False
    assert routine["transport_attempted"] is False
    assert routine["transport_success"] is False
    assert routine["receipt_confirmed"] is False


def test_validator_accepts_committed_blocked_artifact() -> None:
    result = subprocess.run(
        [sys.executable, "tools/validate_etf_eu_guarded_send_authorization.py", "--authorization", str(AUTH_PATH)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["authorization_status"] == "blocked_missing_guarded_confirmation_phrase"
    assert payload["delivery_authorized"] is False


def test_wrong_or_missing_phrase_does_not_authorize(tmp_path: Path) -> None:
    prep = load_json(PREP_PATH)
    routine = load_json(ROUTINE_PATH)
    routine["delivery_authorized"] = False
    routine["transport_attempted"] = False
    routine["transport_success"] = False
    routine["receipt_confirmed"] = False
    routine["valuation_grade"] = False
    routine["funding_authority"] = False
    routine["portfolio_mutation"] = False
    routine["production_delivery_authority"] = False
    prep_path = tmp_path / "prep.json"
    routine_path = tmp_path / "routine.json"
    out_path = tmp_path / "authorization.json"
    prep_path.write_text(json.dumps(prep, indent=2), encoding="utf-8")
    routine_path.write_text(json.dumps(routine, indent=2), encoding="utf-8")

    subprocess.run(
        [
            sys.executable,
            "tools/authorize_etf_eu_guarded_send.py",
            "--run-id", "20260710_000000",
            "--report-date", "2026-07-10",
            "--report-suffix", "260710",
            "--delivery-prep", str(prep_path),
            "--routine-manifest", str(routine_path),
            "--authorization-phrase", "send it",
            "--output", str(out_path),
        ],
        check=True,
    )
    data = load_json(out_path)
    assert data["delivery_authorized"] is False
    assert data["send_command_allowed"] is False
    assert data["transport_attempted"] is False


def test_exact_phrase_authorizes_future_send_only(tmp_path: Path) -> None:
    prep = load_json(PREP_PATH)
    routine = load_json(ROUTINE_PATH)
    for key in ["delivery_authorized", "transport_attempted", "transport_success", "receipt_confirmed", "valuation_grade", "funding_authority", "portfolio_mutation", "production_delivery_authority"]:
        routine[key] = False
    prep_path = tmp_path / "prep.json"
    routine_path = tmp_path / "routine.json"
    out_path = tmp_path / "authorization.json"
    prep_path.write_text(json.dumps(prep, indent=2), encoding="utf-8")
    routine_path.write_text(json.dumps(routine, indent=2), encoding="utf-8")

    subprocess.run(
        [
            sys.executable,
            "tools/authorize_etf_eu_guarded_send.py",
            "--run-id", "20260710_000000",
            "--report-date", "2026-07-10",
            "--report-suffix", "260710",
            "--delivery-prep", str(prep_path),
            "--routine-manifest", str(routine_path),
            "--authorization-phrase", REQUIRED_PHRASE,
            "--output", str(out_path),
        ],
        check=True,
    )
    data = load_json(out_path)
    assert data["delivery_authorized"] is True
    assert data["send_command_allowed"] is True
    assert data["workflow_dispatch_allowed"] is False
    assert data["run_queue_allowed"] is False
    assert data["transport_execution_allowed"] is False
    assert data["send_executed"] is False
    assert data["transport_attempted"] is False
    assert data["receipt_confirmed"] is False


@pytest.mark.parametrize("key", ["send_executed", "transport_attempted", "receipt_confirmed", "valuation_grade", "funding_authority", "portfolio_mutation", "production_delivery_authority"])
def test_builder_refuses_preexisting_authority_promotion(tmp_path: Path, key: str) -> None:
    prep = load_json(PREP_PATH)
    routine = load_json(ROUTINE_PATH)
    prep[key] = True
    for routine_key in ["delivery_authorized", "transport_attempted", "transport_success", "receipt_confirmed", "valuation_grade", "funding_authority", "portfolio_mutation", "production_delivery_authority"]:
        routine[routine_key] = False
    prep_path = tmp_path / "prep.json"
    routine_path = tmp_path / "routine.json"
    out_path = tmp_path / "authorization.json"
    prep_path.write_text(json.dumps(prep, indent=2), encoding="utf-8")
    routine_path.write_text(json.dumps(routine, indent=2), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "tools/authorize_etf_eu_guarded_send.py",
            "--run-id", "20260710_000000",
            "--report-date", "2026-07-10",
            "--report-suffix", "260710",
            "--delivery-prep", str(prep_path),
            "--routine-manifest", str(routine_path),
            "--authorization-phrase", REQUIRED_PHRASE,
            "--output", str(out_path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
