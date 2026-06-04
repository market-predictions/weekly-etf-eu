import json
from pathlib import Path

import pytest

from runtime.build_etf_eu_delivery_manifest import build_blocked_design_manifest, write_blocked_design_manifest
from tools.validate_etf_eu_delivery_manifest import validate_manifest


def test_blocked_design_manifest_is_valid(tmp_path: Path):
    path = write_blocked_design_manifest(
        tmp_path,
        run_id="20260604_220814",
        report_date="2026-06-04",
        dutch_report_path="output/weekly_etf_eu_review_nl_260604.md",
        english_report_path="output/weekly_etf_eu_review_260604.md",
        valuation_artifact_path="output/pricing/ucits_valuation_prices_20260604_220814.json",
        validation_evidence_paths=["output/validation/etf_eu_shadow_validation_evidence_20260604_220814.json"],
        created_at_utc="2026-06-04T22:10:00Z",
    )

    validate_manifest(path)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["status"] == "blocked_design_only"
    assert payload["delivery_enabled"] is False
    assert payload["receipt"]["receipt_status"] == "not_created"
    assert payload["authority"]["email_delivery"] is False
    assert payload["authority"]["pdf_generation"] is False
    assert payload["authority"]["production_delivery"] is False


def test_sent_manifest_without_receipt_fails(tmp_path: Path):
    payload = build_blocked_design_manifest(
        run_id="20260604_220814",
        report_date="2026-06-04",
        dutch_report_path="output/weekly_etf_eu_review_nl_260604.md",
        english_report_path="output/weekly_etf_eu_review_260604.md",
        valuation_artifact_path="output/pricing/ucits_valuation_prices_20260604_220814.json",
        created_at_utc="2026-06-04T22:10:00Z",
    )
    payload["status"] = "sent"
    payload["delivery_enabled"] = True
    payload["gates"]["receipt_path_exists"] = False
    payload["receipt"]["receipt_status"] = "not_created"
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(RuntimeError, match="sent requires all gates true"):
        validate_manifest(manifest)


def test_blocked_design_manifest_cannot_enable_delivery(tmp_path: Path):
    payload = build_blocked_design_manifest(
        run_id="20260604_220814",
        report_date="2026-06-04",
        dutch_report_path="output/weekly_etf_eu_review_nl_260604.md",
        english_report_path="output/weekly_etf_eu_review_260604.md",
        valuation_artifact_path="output/pricing/ucits_valuation_prices_20260604_220814.json",
        created_at_utc="2026-06-04T22:10:00Z",
    )
    payload["delivery_enabled"] = True
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(RuntimeError, match="blocked_design_only requires delivery_enabled=false"):
        validate_manifest(manifest)
