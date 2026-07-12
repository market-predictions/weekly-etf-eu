from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/repair-weekly-etf-eu-routine-pdf.yml"


def test_repair_preview_workflow_has_deterministic_persistence_path() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")

    assert "Record stable renderer decision" not in source
    assert "text += \"\"\"" not in source
    assert "Upload repair preview for review" in source
    assert "Persist repair preview and QA evidence" in source
    assert source.index("Upload repair preview for review") < source.index(
        "Persist repair preview and QA evidence"
    )


def test_repair_preview_workflow_remains_no_send() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    forbidden = [
        "MRKT_RPRTS_SMTP_HOST",
        "MRKT_RPRTS_SMTP_PASS",
        "MRKT_RPRTS_MAIL_TO",
        "send_confirmation",
        "send_etf_eu_current_package_delivery",
        "check_etf_eu_delivery_receipt",
    ]
    for token in forbidden:
        assert token not in source
