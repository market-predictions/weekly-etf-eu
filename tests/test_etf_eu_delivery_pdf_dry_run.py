from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.build_etf_eu_delivery_pdf_dry_run import build_delivery_pdf_dry_run_manifest
from tools.validate_etf_eu_delivery_pdf_dry_run import EtfEuDeliveryPdfDryRunError, validate_delivery_pdf_dry_run

ARTIFACT = Path("output/delivery/etf_eu_delivery_pdf_dry_run_20260618_000000.json")


def _write(tmp_path: Path, payload: dict) -> Path:
    artifact = tmp_path / "dry_run.json"
    artifact.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


def test_valid_committed_dry_run_artifact_passes() -> None:
    result = validate_delivery_pdf_dry_run(ARTIFACT)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP14I"


def test_builder_defaults_are_dry_run_only() -> None:
    payload = build_delivery_pdf_dry_run_manifest()
    assert payload["schema_version"] == "etf_eu_delivery_pdf_dry_run_v1"
    assert payload["dry_run_only"] is True
    assert payload["production_delivery"] is False
    assert payload["recipient_activation"] is False
    assert payload["send_attempted"] is False
    assert payload["real_receipt"] is False
    assert payload["selected_next_package"] == "WP14I"


@pytest.mark.parametrize(
    "flag",
    [
        "production_delivery",
        "recipient_activation",
        "send_attempted",
        "real_receipt",
        "proof_claimed",
        "mail_transport_enabled",
        "smtp_configured",
        "secrets_present",
        "real_recipients",
        "portfolio_mutation",
        "candidate_promotion",
        "funding_authority",
        "valuation_grade",
    ],
)
def test_true_delivery_or_authority_flag_fails(tmp_path: Path, flag: str) -> None:
    payload = build_delivery_pdf_dry_run_manifest()
    payload[flag] = True
    artifact = _write(tmp_path, payload)
    with pytest.raises(EtfEuDeliveryPdfDryRunError, match=f"{flag} must be false"):
        validate_delivery_pdf_dry_run(artifact)


def test_missing_report_path_fails(tmp_path: Path) -> None:
    payload = build_delivery_pdf_dry_run_manifest()
    payload["report_path"] = "output/missing_report.md"
    artifact = _write(tmp_path, payload)
    with pytest.raises(EtfEuDeliveryPdfDryRunError, match="report_path does not exist"):
        validate_delivery_pdf_dry_run(artifact)


def test_missing_pricing_artifact_path_fails(tmp_path: Path) -> None:
    payload = build_delivery_pdf_dry_run_manifest()
    payload["pricing_artifact_path"] = "output/pricing/missing.json"
    artifact = _write(tmp_path, payload)
    with pytest.raises(EtfEuDeliveryPdfDryRunError, match="pricing_artifact_path does not exist"):
        validate_delivery_pdf_dry_run(artifact)


def test_missing_selected_next_package_fails(tmp_path: Path) -> None:
    payload = build_delivery_pdf_dry_run_manifest()
    payload["selected_next_package"] = ""
    artifact = _write(tmp_path, payload)
    with pytest.raises(EtfEuDeliveryPdfDryRunError, match="selected_next_package missing"):
        validate_delivery_pdf_dry_run(artifact)


def test_dry_run_only_must_be_true(tmp_path: Path) -> None:
    payload = build_delivery_pdf_dry_run_manifest()
    payload["dry_run_only"] = False
    artifact = _write(tmp_path, payload)
    with pytest.raises(EtfEuDeliveryPdfDryRunError, match="dry_run_only must be true"):
        validate_delivery_pdf_dry_run(artifact)
