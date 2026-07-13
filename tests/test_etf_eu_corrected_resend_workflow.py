from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/send-weekly-etf-eu-corrected-report.yml"


def _source() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_workflow_is_manual_only() -> None:
    source = _source()
    assert "workflow_dispatch:" in source
    assert "push:" not in source
    assert "validate_only" in source
    assert "dry_run" in source
    assert "send" in source


def test_send_requires_explicit_correction_confirmation() -> None:
    source = _source()
    guard = 'if [ "$MODE" = send ] && [ "$CONFIRMATION" != confirm_corrected_resend ]'
    assert guard in source
    assert source.index(guard) < source.index("MRKT_RPRTS_SMTP_HOST")


def test_secrets_are_scoped_to_send_step() -> None:
    source = _source()
    send_step = source.index("- name: Send corrected report")
    secret_start = source.index("MRKT_RPRTS_SMTP_HOST")
    assert secret_start > send_step
    assert "MRKT_RPRTS_SMTP_PASS" not in source[:send_step]


def test_workflow_uses_correction_package_and_existing_runner() -> None:
    source = _source()
    assert "prepare_etf_eu_corrected_resend_package.py" in source
    assert "validate_etf_eu_corrected_resend_package.py" in source
    assert "validate_etf_eu_corrected_resend_queue.py" in source
    assert "runtime.send_etf_eu_current_package_delivery" in source
    assert "etf_eu_corrected_transport_result_${CORR_RID}.json" in source
    assert "etf_eu_corrected_delivery_evidence_${CORR_RID}.json" in source


def test_workflow_does_not_select_malformed_original_pdfs() -> None:
    source = _source()
    assert "output/fresh_generation/weekly_etf_eu_review_nl_260712.pdf" not in source
    assert "output/fresh_generation/weekly_etf_eu_review_260712.pdf" not in source


def test_dry_run_has_no_send_authorization() -> None:
    source = _source()
    dry_start = source.index("- name: Dry run")
    auth_start = source.index("- name: Authorize send")
    dry_block = source[dry_start:auth_start]
    assert "--mode dry_run" in dry_block
    assert "MRKT_RPRTS_SMTP" not in dry_block
    assert "confirm_corrected_resend" not in dry_block
