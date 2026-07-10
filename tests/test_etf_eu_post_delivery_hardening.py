from __future__ import annotations

import json
from pathlib import Path

WORKFLOW = Path(".github/workflows/send-weekly-etf-eu-report.yml")
CLOSEOUT_MANIFEST = Path("output/run_manifests/etf_eu_delivery_closeout_manifest_20260710_1755.json")
LATEST_POINTER = Path("output/run_manifests/latest_etf_eu_delivery_closeout_manifest_path.txt")


def test_future_guarded_sends_require_persisted_evidence_files() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert 'test -f "output/delivery/etf_eu_delivery_evidence_${ETF_EU_RUN_ID}.json"' in workflow
    assert 'test -f "output/delivery/etf_eu_transport_result_${ETF_EU_RUN_ID}.json"' in workflow
    assert 'test -f "output/delivery/etf_eu_receipt_check_${ETF_EU_RUN_ID}.json"' in workflow
    assert "git add -f" in workflow
    assert "ETF_EU_TRANSPORT_EVIDENCE_NOT_STAGED" in workflow
    assert "git ls-files --error-unmatch" in workflow


def test_future_guarded_sends_require_message_reference() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "message_id_or_receipt_reference" in workflow
    assert "ETF_EU_TRANSPORT_MISSING_MESSAGE_REFERENCE" in workflow


def test_latest_closeout_manifest_pointer_is_present() -> None:
    assert LATEST_POINTER.exists()
    assert LATEST_POINTER.read_text(encoding="utf-8").strip() == str(CLOSEOUT_MANIFEST)
    assert CLOSEOUT_MANIFEST.exists()


def test_post_delivery_closeout_adapts_upstream_pattern_without_us_authority() -> None:
    data = json.loads(CLOSEOUT_MANIFEST.read_text(encoding="utf-8"))
    assert "weekly-etf delivery manifest and run manifest closeout pattern" in data["upstream_pattern_adapted"]
    assert data["production_delivery_authority"] is False
    assert data["valuation_grade"] is False
    assert data["funding_authority"] is False
    assert data["portfolio_mutation"] is False
    assert data["next_package"] == "ETF-EU-MVP22_ROUTINE_WEEKLY_EU_REPORT_OPERATING_LOOP"
