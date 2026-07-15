from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_corrected_delivery_closeout import validate


def _write(path: Path, payload: dict) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def _fixture(tmp_path: Path) -> Path:
    package = {
        "correction_control_id": "20260713_180000",
        "combined_machine_gate_passed": True,
        "visual_review_passed": True,
        "authority_separation_gate_passed": True,
    }
    transport = {
        "run_id": "20260715_152543",
        "delivery_mode": "send",
        "transport_attempted": True,
        "transport_success": True,
        "send_executed": True,
    }
    delivery = {
        "attachment_count": 4,
        "original_transport_evidence_overwritten": False,
    }
    receipt = {
        "mailbox_search_performed": True,
        "matching_message_found": True,
        "receipt_confirmed": True,
        "attachment_count_seen": 4,
        "expected_attachment_set_seen": True,
    }
    receipt_evidence = {
        "receipt_confirmed": True,
        "additional_resend_required": False,
    }
    run_manifest = {
        "runtime_run_id": "20260715_152543",
        "transport_result": str(tmp_path / "transport.json"),
        "delivery_evidence": str(tmp_path / "delivery.json"),
    }
    paths = {
        "package_manifest": _write(tmp_path / "package.json", package),
        "transport_result": _write(tmp_path / "transport.json", transport),
        "delivery_evidence": _write(tmp_path / "delivery.json", delivery),
        "receipt_check": _write(tmp_path / "receipt.json", receipt),
        "receipt_evidence": _write(tmp_path / "receipt_evidence.json", receipt_evidence),
        "corrected_run_manifest": _write(tmp_path / "run.json", run_manifest),
    }
    closeout = {
        "source_run_id": "20260712_125000",
        "source_runtime_run_id": "20260712_182002",
        "correction_control_id": "20260713_180000",
        "repair_run_id": "20260713_180000",
        "transport_runtime_run_id": "20260715_152543",
        "github_workflow_run_id": 29428021408,
        "report_date": "2026-07-12",
        "report_suffix": "260712",
        **paths,
        "client_surface_clean": True,
        "corrected_client_output_valid": True,
        "pdf_machine_gate_passed": True,
        "pdf_visual_gate_passed": True,
        "authority_separation_gate_passed": True,
        "transport_attempted": True,
        "transport_success": True,
        "send_executed": True,
        "delivery_status": "smtp_sendmail_returned_no_exception",
        "receipt_check_status": "receipt_confirmed",
        "receipt_confirmed": True,
        "expected_attachment_set_seen": True,
        "attachment_count_seen": 4,
        "dutch_primary_pdf_seen": True,
        "dutch_primary_html_seen": True,
        "english_companion_pdf_seen": True,
        "english_companion_html_seen": True,
        "additional_resend_required": False,
        "duplicate_send_prevented": True,
        "original_transport_evidence_overwritten": False,
        "recipient_plaintext_values_exposed": False,
        "secret_values_exposed": False,
        "raw_email_content_stored": False,
        "raw_mailbox_headers_stored": False,
        "raw_receipt_pdf_stored_in_github": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "production_delivery_cycle_closed": True,
        "routine_production_ready": True,
        "next_operating_mode": "routine_production",
        "next_action": "RUN_NEXT_ROUTINE_WEEKLY_ETF_EU_REPORT",
        "blockers": [],
    }
    path = tmp_path / "closeout.json"
    _write(path, closeout)
    return path


def _mutate(path: Path, key: str, value) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload[key] = value
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_valid_closeout_returns_to_routine_production(tmp_path: Path) -> None:
    result = validate(_fixture(tmp_path))
    assert result["closeout_valid"] is True
    assert result["additional_resend_required"] is False
    assert result["routine_production_ready"] is True
    assert result["next_action"] == "RUN_NEXT_ROUTINE_WEEKLY_ETF_EU_REPORT"


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("transport_success", False),
        ("receipt_confirmed", False),
        ("attachment_count_seen", 3),
        ("dutch_primary_pdf_seen", False),
        ("english_companion_pdf_seen", False),
        ("correction_control_id", "20260713_000000"),
        ("transport_runtime_run_id", "20260715_999999"),
        ("additional_resend_required", True),
    ],
)
def test_invalid_closeout_state_fails(tmp_path: Path, key: str, value) -> None:
    path = _fixture(tmp_path)
    _mutate(path, key, value)
    with pytest.raises(RuntimeError):
        validate(path)


def test_dry_run_transport_cannot_close(tmp_path: Path) -> None:
    path = _fixture(tmp_path)
    closeout = json.loads(path.read_text(encoding="utf-8"))
    transport_path = Path(closeout["transport_result"])
    transport = json.loads(transport_path.read_text(encoding="utf-8"))
    transport["delivery_mode"] = "dry_run"
    transport_path.write_text(json.dumps(transport), encoding="utf-8")
    with pytest.raises(RuntimeError):
        validate(path)


def test_independent_mailbox_search_is_required(tmp_path: Path) -> None:
    path = _fixture(tmp_path)
    closeout = json.loads(path.read_text(encoding="utf-8"))
    receipt_path = Path(closeout["receipt_check"])
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["mailbox_search_performed"] = False
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(RuntimeError):
        validate(path)


def test_raw_mailbox_fields_fail(tmp_path: Path) -> None:
    path = _fixture(tmp_path)
    closeout = json.loads(path.read_text(encoding="utf-8"))
    receipt_path = Path(closeout["receipt_check"])
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["subject"] = "raw subject"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(RuntimeError):
        validate(path)


def test_superseded_package_path_fails(tmp_path: Path) -> None:
    path = _fixture(tmp_path)
    _mutate(path, "package_manifest", str(tmp_path / "20260713_000000" / "package.json"))
    with pytest.raises(RuntimeError):
        validate(path)
