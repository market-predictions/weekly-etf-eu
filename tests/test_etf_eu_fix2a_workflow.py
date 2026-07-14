from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / ".github/workflows/repair-weekly-etf-eu-client-surface.yml"
RESEND = ROOT / ".github/workflows/send-weekly-etf-eu-corrected-report.yml"
SUPERSESSION = ROOT / "output/delivery_control/etf_eu_corrected_resend_package_supersession_20260713_000000.json"


def test_client_surface_preview_has_no_transport_or_mail_secrets() -> None:
    source = PREVIEW.read_text(encoding="utf-8")
    for token in (
        "MRKT_RPRTS_SMTP_HOST",
        "MRKT_RPRTS_SMTP_PASS",
        "MRKT_RPRTS_MAIL_TO",
        "send_confirmation",
        "send_etf_eu_current_package_delivery",
        "check_etf_eu_delivery_receipt",
    ):
        assert token not in source
    assert "visual_review_passed" not in source or "write_etf_eu_visual_review_pending.py" in source
    assert "manual visual inspection required" not in source


def test_preview_orders_sanitization_before_render_and_pdf_gate() -> None:
    source = PREVIEW.read_text(encoding="utf-8")
    assert source.index("Sanitize Dutch and English client Markdown") < source.index("Render sanitized Dutch and English previews")
    assert source.index("Validate clean client surfaces") < source.index("Validate PDF machine contract")
    assert source.index("Validate authority separation") < source.index("Render first middle and last pages")


def test_old_correction_package_is_superseded() -> None:
    source = SUPERSESSION.read_text(encoding="utf-8")
    assert '"superseded": true' in source
    assert '"live_send_allowed": false' in source
    assert '"superseded_by_correction_control_id": "20260713_180000"' in source


def test_corrected_resend_workflow_is_dynamic_and_still_guarded() -> None:
    source = RESEND.read_text(encoding="utf-8")
    assert "correction_control_id" in source
    assert "repair_run_id" in source
    assert "20260713_180000" in source
    assert "delivery_mode: send" not in source
    assert "confirm_corrected_resend" in source
    assert source.index("Prepare and validate package") < source.index("Send corrected report")
    assert source.index("Authorize send") < source.index("Send corrected report")
