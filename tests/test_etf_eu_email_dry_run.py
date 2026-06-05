import json
from pathlib import Path

import pytest

from runtime.build_etf_eu_email_dry_run import build_email_dry_run, write_email_dry_run
from tools.validate_etf_eu_email_dry_run import validate_email_dry_run


def test_email_dry_run_is_valid_with_missing_wp9_and_wp11_artifacts(tmp_path: Path):
    path = write_email_dry_run(
        tmp_path,
        run_id="20260605_000000",
        report_date="2026-06-05",
        attachment_paths=[
            "output/weekly_etf_eu_review_nl_260605.md",
            "output/weekly_etf_eu_review_260605.md",
        ],
        created_at_utc="2026-06-05T00:00:00Z",
    )

    validate_email_dry_run(path)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "etf_eu_email_dry_run_v1"
    assert payload["status"] == "design_only_blocked"
    assert payload["recipient_allowlist_status"] == "not_configured"
    assert payload["delivery_manifest_path"] is None
    assert payload["delivery_manifest_status"] == "not_available"
    assert payload["pdf_paths_or_null"] is None
    assert payload["pdf_status"] == "not_available"
    assert payload["send_attempted"] is False
    assert payload["email_delivery"] is False
    assert payload["delivery_receipt"] is False
    assert payload["production_delivery"] is False
    assert payload["authority"]["email_delivery"] is False
    assert payload["authority"]["production_delivery"] is False


def test_email_dry_run_can_reference_manifest_and_shadow_pdf_paths_without_enabling_delivery(tmp_path: Path):
    path = write_email_dry_run(
        tmp_path,
        run_id="20260605_010203",
        report_date="2026-06-05",
        recipient_allowlist_status="placeholder_only",
        attachment_paths=[
            "output/weekly_etf_eu_review_nl_260605.md",
            "output/weekly_etf_eu_review_260605.md",
        ],
        delivery_manifest_path="output/delivery/etf_eu_delivery_manifest_20260605_010203.json",
        pdf_paths=[
            "output/pdf/weekly_etf_eu_review_nl_260605.pdf",
            "output/pdf/weekly_etf_eu_review_260605.pdf",
        ],
        created_at_utc="2026-06-05T01:02:03Z",
    )

    validate_email_dry_run(path)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["delivery_manifest_status"] == "available"
    assert payload["pdf_status"] == "shadow_paths_available"
    assert payload["send_attempted"] is False
    assert payload["authority"]["mail_transport_configured"] is False
    assert payload["authority"]["external_mail_api_enabled"] is False
    assert payload["authority"]["recipient_activation"] is False


def test_email_dry_run_rejects_send_attempted_true(tmp_path: Path):
    payload = build_email_dry_run(
        run_id="20260605_000000",
        report_date="2026-06-05",
        created_at_utc="2026-06-05T00:00:00Z",
    )
    payload["send_attempted"] = True
    artifact = tmp_path / "email_dry_run.json"
    artifact.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(RuntimeError, match="send_attempted must remain false"):
        validate_email_dry_run(artifact)


def test_email_dry_run_rejects_email_delivery_true(tmp_path: Path):
    payload = build_email_dry_run(
        run_id="20260605_000000",
        report_date="2026-06-05",
        created_at_utc="2026-06-05T00:00:00Z",
    )
    payload["email_delivery"] = True
    artifact = tmp_path / "email_dry_run.json"
    artifact.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(RuntimeError, match="email_delivery must remain false"):
        validate_email_dry_run(artifact)


def test_email_dry_run_rejects_active_recipient_allowlist(tmp_path: Path):
    payload = build_email_dry_run(
        run_id="20260605_000000",
        report_date="2026-06-05",
        recipient_allowlist_status="active",
        created_at_utc="2026-06-05T00:00:00Z",
    )
    artifact = tmp_path / "email_dry_run.json"
    artifact.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(RuntimeError, match="recipient_allowlist_status must remain inactive"):
        validate_email_dry_run(artifact)
