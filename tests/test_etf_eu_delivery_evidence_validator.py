from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_delivery_evidence import validate


def _write_fixture(tmp_path: Path, **updates: object) -> Path:
    sender = tmp_path / "send_etf_eu_report_runtime_html.py"
    preflight = tmp_path / "preflight.json"
    base = tmp_path / "base.json"
    nl = tmp_path / "weekly_etf_eu_review_nl_260708.md"
    en = tmp_path / "weekly_etf_eu_review_260708.md"
    for path in [sender, preflight, base, nl, en]:
        path.write_text("x", encoding="utf-8")
    payload = {
        "schema_version": "etf_eu_delivery_evidence_v1",
        "artifact_type": "etf_eu_controlled_send_delivery_evidence",
        "generated_at_utc": "2026-07-08T00:00:00Z",
        "run_id": "20260708_000000",
        "report_date": "2026-07-08",
        "report_suffix": "260708",
        "delivery_status": "not_attempted",
        "delivery_status_meaning": "controlled-send evidence writer implemented but no outbound delivery executed",
        "recipient_data_policy": "redacted_hash_only",
        "sender_entrypoint_path": str(sender),
        "dutch_primary_report_path": str(nl),
        "english_companion_report_path": str(en),
        "controlled_send_preflight_manifest": str(preflight),
        "base_delivery_manifest": str(base),
        "language_count": 2,
        "languages": [
            {
                "language": "nl",
                "report_path": str(nl),
                "source_manifest_path": "source.json",
                "source_manifest_type": "mvp09_fixture_no_send_evidence",
                "timestamp_utc": "2026-07-08T00:00:00Z",
                "mode": "fixture_no_send",
                "report": "Dutch primary client report",
                "recipient_hash": "sha256:redacted-nl-fixture",
                "recipient_redacted": True,
                "html_body": False,
                "pdf_attached": "no",
                "attachments": [],
                "attachment_count": 0,
                "pdf_attachments": [],
            },
            {
                "language": "en",
                "report_path": str(en),
                "source_manifest_path": "source.json",
                "source_manifest_type": "mvp09_fixture_no_send_evidence",
                "timestamp_utc": "2026-07-08T00:00:00Z",
                "mode": "fixture_no_send",
                "report": "English companion report",
                "recipient_hash": "sha256:redacted-en-fixture",
                "recipient_redacted": True,
                "html_body": False,
                "pdf_attached": "no",
                "attachments": [],
                "attachment_count": 0,
                "pdf_attachments": [],
            },
        ],
        "source": {"writer": "runtime/write_etf_eu_delivery_evidence.py"},
        "secret_values_exposed": False,
        "recipient_plaintext_values_exposed": False,
        "production_delivery": False,
        "email_delivery": False,
        "pdf_generation": False,
        "delivery_receipt": False,
        "delivery_success": False,
        "delivery_error": None,
    }
    payload.update(updates)
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_validator_accepts_no_send_fixture(tmp_path: Path) -> None:
    path = _write_fixture(tmp_path)
    result = validate(path)
    assert result["status"] == "valid"
    assert result["delivery_status"] == "not_attempted"
    assert result["delivery_success"] is False
    assert result["recipient_data_policy"] == "redacted_hash_only"
    assert result["languages"] == ["en", "nl"]


def test_validator_rejects_plaintext_recipient_hash(tmp_path: Path) -> None:
    path = _write_fixture(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["languages"][0]["recipient_hash"] = "person@example.com"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(AssertionError, match="recipient_hash"):
        validate(path)


def test_validator_rejects_missing_caveat_for_success_status(tmp_path: Path) -> None:
    path = _write_fixture(
        tmp_path,
        delivery_status="smtp_sendmail_returned_no_exception",
        delivery_status_meaning="sendmail returned without raising",
        email_delivery=True,
        production_delivery=True,
        delivery_receipt=True,
        delivery_success=True,
    )
    with pytest.raises(AssertionError, match="caveat"):
        validate(path)


def test_validator_rejects_not_attempted_with_email_delivery_true(tmp_path: Path) -> None:
    path = _write_fixture(tmp_path, email_delivery=True)
    with pytest.raises(AssertionError, match="email_delivery"):
        validate(path)
