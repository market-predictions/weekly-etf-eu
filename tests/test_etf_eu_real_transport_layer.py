from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.send_etf_eu_delivery_package import execute_transport
from tools.validate_etf_eu_delivery_evidence import validate as validate_delivery_evidence


def _write_minimal_package(root: Path) -> tuple[Path, Path]:
    package_dir = root / "output" / "delivery_package"
    package_dir.mkdir(parents=True, exist_ok=True)
    (root / "output").mkdir(parents=True, exist_ok=True)

    for path, content in {
        root / "output" / "weekly_etf_eu_review_nl_260709.md": "# Wekelijkse ETF EU Review 2026-07-09\n",
        root / "output" / "weekly_etf_eu_review_260709.md": "# Weekly ETF EU Review 2026-07-09\n",
        package_dir / "weekly_etf_eu_review_nl_260709.html": "<html><body>Dutch primary</body></html>",
        package_dir / "weekly_etf_eu_review_260709.html": "<html><body>English companion</body></html>",
    }.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    (package_dir / "weekly_etf_eu_review_nl_260709.pdf").write_bytes(b"%PDF-1.4 nl")
    (package_dir / "weekly_etf_eu_review_260709.pdf").write_bytes(b"%PDF-1.4 en")

    manifest = package_dir / "etf_eu_delivery_package_manifest_20260709_000000.json"
    manifest.write_text(json.dumps({
        "schema_version": "etf_eu_delivery_package_manifest_v1",
        "run_id": "20260709_000000",
        "report_suffix": "260709",
        "dutch_primary_pdf": "output/delivery_package/weekly_etf_eu_review_nl_260709.pdf",
        "english_companion_pdf": "output/delivery_package/weekly_etf_eu_review_260709.pdf",
        "dutch_primary_html": "output/delivery_package/weekly_etf_eu_review_nl_260709.html",
        "english_companion_html": "output/delivery_package/weekly_etf_eu_review_260709.html",
        "markdown_source_paths": [
            "output/weekly_etf_eu_review_nl_260709.md",
            "output/weekly_etf_eu_review_260709.md",
        ],
        "pdf_output_available": True,
        "html_output_available": True,
        "dutch_primary": True,
        "english_companion": True,
        "client_grade_package_ready": True,
        "stale_delivery_wording_present": False,
        "main_surface_us_proxy_exposure": False,
        "main_surface_tbd_candidate_exposure": False,
        "nan_price_in_client_surface": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
    }), encoding="utf-8")

    ready_dir = root / "output" / "client_surface"
    ready_dir.mkdir(parents=True, exist_ok=True)
    ready = ready_dir / "etf_eu_mvp19_fix2_ready_for_controlled_resend_20260709_000000.json"
    ready.write_text(json.dumps({
        "schema_version": "etf_eu_mvp19_fix2_ready_for_controlled_resend_v1",
        "work_package_id": "ETF-EU-MVP19-FIX2",
        "transport_guard": {
            "ready_for_controlled_resend": True,
            "resend_performed": False,
            "receipt_confirmed": False,
            "production_delivery_authority": False,
        },
    }), encoding="utf-8")
    return manifest, ready


def test_dry_run_writes_evidence_without_transport(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    manifest, ready = _write_minimal_package(tmp_path)

    result = execute_transport(
        run_id="test_run",
        report_date="2026-07-09",
        report_suffix="260709",
        delivery_package_manifest=manifest,
        ready_artifact=ready,
        output_dir=Path("output/delivery"),
        dry_run=True,
    )

    assert result["transport_attempted"] is False
    assert result["transport_success"] is False
    assert result["receipt_confirmed"] is False

    evidence = validate_delivery_evidence(Path(result["delivery_evidence_path"]))
    assert evidence["status"] == "valid"
    assert evidence["transport_attempted"] is False
    assert evidence["transport_success"] is False


def test_real_send_requires_recipient_configuration(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    manifest, ready = _write_minimal_package(tmp_path)
    monkeypatch.delenv("MRKT_RPRTS_MAIL_TO_NL", raising=False)
    monkeypatch.delenv("MRKT_RPRTS_MAIL_TO", raising=False)

    with pytest.raises(RuntimeError, match="MRKT_RPRTS_MAIL_TO"):
        execute_transport(
            run_id="test_run",
            report_date="2026-07-09",
            report_suffix="260709",
            delivery_package_manifest=manifest,
            ready_artifact=ready,
            output_dir=Path("output/delivery"),
            dry_run=False,
        )


def test_failed_transport_records_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import runtime.send_etf_eu_delivery_package as sender

    monkeypatch.chdir(tmp_path)
    manifest, ready = _write_minimal_package(tmp_path)
    monkeypatch.setenv("MRKT_RPRTS_MAIL_TO_NL", "client@example.com")
    monkeypatch.setenv("MRKT_RPRTS_MAIL_FROM", "reports@example.com")
    monkeypatch.setenv("MRKT_RPRTS_SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("MRKT_RPRTS_SMTP_USER", "user")
    monkeypatch.setenv("MRKT_RPRTS_SMTP_PASS", "pass")

    def fail_send(*args, **kwargs) -> None:
        raise RuntimeError("synthetic SMTP failure")

    monkeypatch.setattr(sender, "_send_message", fail_send)

    result = execute_transport(
        run_id="test_run",
        report_date="2026-07-09",
        report_suffix="260709",
        delivery_package_manifest=manifest,
        ready_artifact=ready,
        output_dir=Path("output/delivery"),
        dry_run=False,
    )

    assert result["transport_attempted"] is True
    assert result["transport_success"] is False
    assert "synthetic SMTP failure" in str(result["transport_error"])

    evidence = validate_delivery_evidence(Path(result["delivery_evidence_path"]))
    assert evidence["delivery_status"] == "smtp_sendmail_failed"
    assert evidence["transport_attempted"] is True
    assert evidence["transport_success"] is False


def test_workflow_uses_real_transport_runner() -> None:
    workflow = Path(".github/workflows/send-weekly-etf-eu-report.yml").read_text(encoding="utf-8")
    assert "runtime.send_etf_eu_delivery_package" in workflow
    assert "ETF_EU_TRANSPORT_EXECUTED=false" not in workflow
    assert "MVP15 guarded transport placeholder" not in workflow
    assert "env.ETF_EU_DELIVERY_MODE == 'send' && env.ETF_EU_SEND_CONFIRMATION == 'confirm_guarded_send'" in workflow
