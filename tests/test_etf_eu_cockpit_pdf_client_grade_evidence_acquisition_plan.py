from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_cockpit_pdf_client_grade_evidence_acquisition_plan import NOTES, PLAN, PLAN_FIELDS, PLAN_GROUPS, VALID_PRIORITIES, VALID_STATUSES, validate


def _plan() -> dict:
    return json.loads(PLAN.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert PLAN.exists()
    assert NOTES.exists()


def test_artifact_identity_and_source_paths() -> None:
    data = _plan()
    assert data["work_package_id"] == "ETF-EU-WP15AF"
    assert data["source_work_package"] == "ETF-EU-WP15AE"
    assert data["source_gap_audit_artifact"].endswith(".json")
    assert data["source_readiness_gate_artifact"].endswith(".json")
    assert data["source_review_only_pdf"].endswith(".pdf")
    assert data["readiness_gate_status"] == "plan_created_not_executed"


def test_authority_claims_remain_false() -> None:
    data = _plan()
    for key in [
        "client_grade_claim",
        "client_grade_enough_for_delivery_preflight_discussion",
        "delivery_ready",
        "delivery_preflight_allowed",
        "production_delivery",
        "receipt_artifact_created",
        "production_manifest_created",
        "valuation_grade",
        "pricing_evidence_for_client_grade",
        "pricing_evidence_for_delivery_preflight",
        "live_data_fetch_performed",
        "pricing_evidence_changed",
        "new_pdf_created",
        "renderer_changed",
        "evidence_acquired",
    ]:
        assert data[key] is False


def test_plan_groups_and_items_are_valid() -> None:
    data = _plan()
    for group in PLAN_GROUPS:
        assert group in data
        assert data[group]
        for item in data[group]:
            for field in PLAN_FIELDS:
                assert field in item
            assert item["priority"] in VALID_PRIORITIES
            assert item["status"] in VALID_STATUSES
            assert item["execution_allowed_in_wp15af"] is False


def test_counts_and_sequences_are_valid() -> None:
    data = _plan()
    assert data["planned_client_grade_items_count"] >= 12
    assert data["planned_delivery_preflight_items_count"] >= 8
    assert data["p0_items"]
    assert data["p1_items"]
    assert data["recommended_package_sequence"]
    assert data["selected_next_package"] == "ETF-EU-WP15AG"


def test_source_values_remain_fixed() -> None:
    data = _plan()
    assert data["successful_rows_count"] == 2
    assert data["failed_rows_count"] == 0
    assert data["skipped_rows_count"] == 1
    assert data["first_successful_symbol"] == "SXR8.DE"
    assert data["first_successful_close"] == 706.119995
    assert data["second_successful_symbol"] == "CSPX.L"
    assert data["second_successful_close"] == 807.859985
    assert data["smh_status"] == "skipped_pending_registry_status"


def test_notes_contain_required_sections() -> None:
    text = NOTES.read_text(encoding="utf-8")
    for marker in [
        "# ETF-EU-WP15AF client-grade evidence acquisition plan",
        "## Scope",
        "## Source artifacts",
        "## Plan summary",
        "## Decision framework evidence plan",
        "## Product data evidence plan",
        "## Pricing freshness evidence plan",
        "## Investability evidence plan",
        "## Output quality evidence plan",
        "## Valuation reconciliation evidence plan",
        "## Delivery-preflight evidence plan",
        "## Recommended package sequence",
        "## Boundary checks",
        "## Decision",
        "## Next package",
    ]:
        assert marker in text


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-WP15AF"
    assert result["readiness_gate_status"] == "plan_created_not_executed"
    assert result["planned_client_grade_items_count"] >= 12
    assert result["planned_delivery_preflight_items_count"] >= 8
    assert result["evidence_acquired"] is False
    assert result["selected_next_package"] == "ETF-EU-WP15AG"
