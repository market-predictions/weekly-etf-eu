import json
from pathlib import Path

import pytest

from runtime.build_etf_eu_run_bundle import build_run_bundle_manifest, write_run_bundle_manifest
from tools.validate_etf_eu_run_bundle import validate_manifest


def test_run_bundle_manifest_without_delivery_manifest_is_valid(tmp_path: Path):
    path = write_run_bundle_manifest(
        tmp_path,
        run_id="20260605_070115",
        report_date="2026-06-05",
        dutch_report_path="output/weekly_etf_eu_review_nl_260605.md",
        english_report_path="output/weekly_etf_eu_review_260605.md",
        valuation_artifact_path="output/pricing/ucits_valuation_prices_20260605_070115.json",
        fundability_artifact_path="output/fundability/ucits_fundability_gate_20260605_070115.json",
        validation_evidence_path="output/validation/etf_eu_shadow_validation_evidence_20260605_070115.json",
        created_at_utc="2026-06-05T07:05:00Z",
    )

    validate_manifest(path)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert path == tmp_path / "20260605_070115" / "etf_eu_run_bundle_manifest.json"
    assert payload["delivery_manifest_status"] == "not_available"
    assert payload["delivery_manifest_path_or_null"] is None
    assert payload["production_delivery"] is False
    assert payload["email_delivery"] is False
    assert payload["pdf_generation"] is False
    assert payload["delivery_receipt"] is False


def test_run_bundle_manifest_with_delivery_manifest_is_valid(tmp_path: Path):
    path = write_run_bundle_manifest(
        tmp_path,
        run_id="20260605_070115",
        report_date="2026-06-05",
        dutch_report_path="output/weekly_etf_eu_review_nl_260605.md",
        english_report_path="output/weekly_etf_eu_review_260605.md",
        valuation_artifact_path="output/pricing/ucits_valuation_prices_20260605_070115.json",
        fundability_artifact_path="output/fundability/ucits_fundability_gate_20260605_070115.json",
        validation_evidence_path="output/validation/etf_eu_shadow_validation_evidence_20260605_070115.json",
        delivery_manifest_path="output/delivery/etf_eu_delivery_manifest_20260605_070115.json",
        created_at_utc="2026-06-05T07:05:00Z",
    )

    validate_manifest(path)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["delivery_manifest_status"] == "available"
    assert payload["delivery_manifest_path_or_null"] == "output/delivery/etf_eu_delivery_manifest_20260605_070115.json"
    assert payload["production_delivery"] is False
    assert payload["email_delivery"] is False
    assert payload["pdf_generation"] is False
    assert payload["delivery_receipt"] is False


def test_not_available_manifest_cannot_reference_delivery_manifest(tmp_path: Path):
    payload = build_run_bundle_manifest(
        run_id="20260605_070115",
        report_date="2026-06-05",
        dutch_report_path="output/weekly_etf_eu_review_nl_260605.md",
        english_report_path="output/weekly_etf_eu_review_260605.md",
        valuation_artifact_path="output/pricing/ucits_valuation_prices_20260605_070115.json",
        fundability_artifact_path="output/fundability/ucits_fundability_gate_20260605_070115.json",
        validation_evidence_path="output/validation/etf_eu_shadow_validation_evidence_20260605_070115.json",
        created_at_utc="2026-06-05T07:05:00Z",
    )
    payload["delivery_manifest_path_or_null"] = "output/delivery/etf_eu_delivery_manifest_20260605_070115.json"
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(RuntimeError, match="not_available requires delivery_manifest_path_or_null=null"):
        validate_manifest(manifest)


def test_run_bundle_manifest_cannot_enable_delivery_flags(tmp_path: Path):
    payload = build_run_bundle_manifest(
        run_id="20260605_070115",
        report_date="2026-06-05",
        dutch_report_path="output/weekly_etf_eu_review_nl_260605.md",
        english_report_path="output/weekly_etf_eu_review_260605.md",
        valuation_artifact_path="output/pricing/ucits_valuation_prices_20260605_070115.json",
        fundability_artifact_path="output/fundability/ucits_fundability_gate_20260605_070115.json",
        validation_evidence_path="output/validation/etf_eu_shadow_validation_evidence_20260605_070115.json",
        created_at_utc="2026-06-05T07:05:00Z",
    )
    payload["email_delivery"] = True
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(RuntimeError, match="email_delivery must remain false"):
        validate_manifest(manifest)
