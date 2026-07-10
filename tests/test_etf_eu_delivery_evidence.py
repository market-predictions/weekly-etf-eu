from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_delivery_evidence import validate


def _base_evidence(tmp_path: Path) -> Path:
    for rel in [
        "runtime/send_etf_eu_delivery_package.py",
        "output/weekly_etf_eu_review_nl_260709.md",
        "output/weekly_etf_eu_review_260709.md",
        "output/delivery_package/etf_eu_delivery_package_manifest_20260709_000000.json",
        "output/client_surface/etf_eu_mvp19_fix2_ready_for_controlled_resend_20260709_000000.json",
        "output/delivery_package/weekly_etf_eu_review_nl_260709.pdf",
        "output/delivery_package/weekly_etf_eu_review_260709.pdf",
        "output/delivery_package/weekly_etf_eu_review_nl_260709.html",
        "output/delivery_package/weekly_etf_eu_review_260709.html",
    ]:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture", encoding="utf-8")

    evidence = {
        "schema_version": "etf_eu_delivery_evidence_v1",
        "artifact_type": "etf_eu_controlled_send_delivery_evidence",
        "generated_at_utc": "2026-07-10T00:00:00Z",
        "run_id": "test_run",
        "report_date": "2026-07-09",
        "report_suffix": "260709",
        "delivery_status": "not_attempted",
        "delivery_status_meaning": "dry-run no outbound delivery executed",
        "recipient_data_policy": "redacted_hash_only",
        "sender_entrypoint_path": "runtime/send_etf_eu_delivery_package.py",
        "dutch_primary_report_path": "output/weekly_etf_eu_review_nl_260709.md",
        "english_companion_report_path": "output/weekly_etf_eu_review_260709.md",
        "controlled_send_preflight_manifest": "output/delivery_package/etf_eu_delivery_package_manifest_20260709_000000.json",
        "base_delivery_manifest": "output/delivery_package/etf_eu_delivery_package_manifest_20260709_000000.json",
        "language_count": 2,
        "languages": [
            {
                "language": "nl",
                "report_path": "output/weekly_etf_eu_review_nl_260709.md",
                "source_manifest_path": "output/delivery_package/etf_eu_delivery_package_manifest_20260709_000000.json",
                "source_manifest_type": "etf_eu_delivery_package_manifest_v1",
                "timestamp_utc": "2026-07-10T00:00:00Z",
                "mode": "mvp20a_real_transport",
                "report": "Dutch primary client report",
                "recipient_hash": "sha256:nl",
                "recipient_redacted": True,
                "html_body": True,
                "pdf_attached": "yes",
                "attachments": ["output/delivery_package/weekly_etf_eu_review_nl_260709.pdf"],
                "attachment_count": 1,
                "pdf_attachments": ["output/delivery_package/weekly_etf_eu_review_nl_260709.pdf"],
            },
            {
                "language": "en",
                "report_path": "output/weekly_etf_eu_review_260709.md",
                "source_manifest_path": "output/delivery_package/etf_eu_delivery_package_manifest_20260709_000000.json",
                "source_manifest_type": "etf_eu_delivery_package_manifest_v1",
                "timestamp_utc": "2026-07-10T00:00:00Z",
                "mode": "mvp20a_real_transport_companion",
                "report": "English companion report",
                "recipient_hash": "sha256:en",
                "recipient_redacted": True,
                "html_body": False,
                "pdf_attached": "yes",
                "attachments": ["output/delivery_package/weekly_etf_eu_review_260709.pdf"],
                "attachment_count": 1,
                "pdf_attachments": ["output/delivery_package/weekly_etf_eu_review_260709.pdf"],
            },
        ],
        "source": {"writer": "runtime/send_etf_eu_delivery_package.py"},
        "secret_values_exposed": False,
        "recipient_plaintext_values_exposed": False,
        "production_delivery": False,
        "email_delivery": False,
        "pdf_generation": False,
        "delivery_receipt": False,
        "delivery_success": False,
        "delivery_error": None,
        "receipt_status": "not_attempted",
        "transport_contract_version": "etf_eu_real_transport_evidence_contract_v1",
        "delivery_mode": "dry_run",
        "transport_attempted": False,
        "transport_success": False,
        "transport_error": None,
        "recipient_target_redacted": True,
        "dutch_primary_pdf": "output/delivery_package/weekly_etf_eu_review_nl_260709.pdf",
        "english_companion_pdf": "output/delivery_package/weekly_etf_eu_review_260709.pdf",
        "dutch_primary_html": "output/delivery_package/weekly_etf_eu_review_nl_260709.html",
        "english_companion_html": "output/delivery_package/weekly_etf_eu_review_260709.html",
        "delivery_package_manifest": "output/delivery_package/etf_eu_delivery_package_manifest_20260709_000000.json",
        "ready_artifact": "output/client_surface/etf_eu_mvp19_fix2_ready_for_controlled_resend_20260709_000000.json",
        "smtp_or_transport_provider": "dry_run_no_smtp",
        "message_id_or_receipt_reference": None,
        "receipt_confirmed": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
    }
    path = tmp_path / "output/delivery/etf_eu_delivery_evidence_test_run.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence), encoding="utf-8")
    return path


def test_mvp20a_transport_contract_validates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = validate(_base_evidence(tmp_path))
    assert result["status"] == "valid"
    assert result["transport_contract_version"] == "etf_eu_real_transport_evidence_contract_v1"
    assert result["transport_success"] is False
    assert result["receipt_confirmed"] is False


def test_transport_success_requires_message_or_receipt_reference(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    path = _base_evidence(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["delivery_status"] = "smtp_sendmail_returned_no_exception"
    data["delivery_status_meaning"] = "SMTP returned without exception; not an end-recipient inbox receipt"
    data["delivery_success"] = True
    data["email_delivery"] = True
    data["production_delivery"] = True
    data["transport_attempted"] = True
    data["transport_success"] = True
    data["delivery_mode"] = "send"
    data["message_id_or_receipt_reference"] = None
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(AssertionError, match="message id or receipt reference"):
        validate(path)
