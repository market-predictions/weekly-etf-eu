from __future__ import annotations

from pathlib import Path

import pytest

from runtime.write_etf_eu_delivery_evidence import build_etf_eu_delivery_evidence


def _language(report_path: Path, language: str) -> dict[str, object]:
    return {
        "language": language,
        "report_path": str(report_path),
        "source_manifest_path": "source.json",
        "source_manifest_type": "mvp09_fixture_no_send_evidence",
        "timestamp_utc": "2026-07-08T00:00:00Z",
        "mode": "fixture_no_send",
        "report": "Dutch primary client report" if language == "nl" else "English companion report",
        "recipient_hash": f"sha256:redacted-{language}-fixture",
        "recipient_redacted": True,
        "html_body": False,
        "pdf_attached": "no",
        "attachments": [],
        "attachment_count": 0,
        "pdf_attachments": [],
    }


def test_build_not_attempted_delivery_evidence_has_safe_boundaries(tmp_path: Path) -> None:
    nl = tmp_path / "weekly_etf_eu_review_nl_260708.md"
    en = tmp_path / "weekly_etf_eu_review_260708.md"
    nl.write_text("nl", encoding="utf-8")
    en.write_text("en", encoding="utf-8")
    evidence = build_etf_eu_delivery_evidence(
        run_id="20260708_000000",
        report_date="2026-07-08",
        report_suffix="260708",
        sender_entrypoint_path=tmp_path / "sender.py",
        dutch_primary_report_path=nl,
        english_companion_report_path=en,
        controlled_send_preflight_manifest=tmp_path / "preflight.json",
        base_delivery_manifest=tmp_path / "base.json",
        delivery_status="not_attempted",
        delivery_status_meaning="controlled-send evidence writer implemented but no outbound delivery executed",
        languages=[_language(nl, "nl"), _language(en, "en")],
        source={"writer": "runtime/write_etf_eu_delivery_evidence.py"},
        generated_at_utc="2026-07-08T00:00:00Z",
    )

    assert evidence["schema_version"] == "etf_eu_delivery_evidence_v1"
    assert evidence["artifact_type"] == "etf_eu_controlled_send_delivery_evidence"
    assert evidence["delivery_status"] == "not_attempted"
    assert evidence["recipient_data_policy"] == "redacted_hash_only"
    assert evidence["language_count"] == 2
    assert {row["language"] for row in evidence["languages"]} == {"nl", "en"}
    assert evidence["production_delivery"] is False
    assert evidence["email_delivery"] is False
    assert evidence["pdf_generation"] is False
    assert evidence["delivery_receipt"] is False
    assert evidence["delivery_success"] is False
    assert evidence["secret_values_exposed"] is False
    assert evidence["recipient_plaintext_values_exposed"] is False


def test_success_status_requires_inbox_receipt_caveat(tmp_path: Path) -> None:
    nl = tmp_path / "weekly_etf_eu_review_nl_260708.md"
    en = tmp_path / "weekly_etf_eu_review_260708.md"
    nl.write_text("nl", encoding="utf-8")
    en.write_text("en", encoding="utf-8")

    with pytest.raises(RuntimeError, match="caveat"):
        build_etf_eu_delivery_evidence(
            run_id="20260708_000000",
            report_date="2026-07-08",
            report_suffix="260708",
            sender_entrypoint_path=tmp_path / "sender.py",
            dutch_primary_report_path=nl,
            english_companion_report_path=en,
            controlled_send_preflight_manifest=tmp_path / "preflight.json",
            base_delivery_manifest=tmp_path / "base.json",
            delivery_status="smtp_sendmail_returned_no_exception",
            delivery_status_meaning="sendmail returned without raising",
            languages=[_language(nl, "nl"), _language(en, "en")],
            source={"writer": "runtime/write_etf_eu_delivery_evidence.py"},
        )
