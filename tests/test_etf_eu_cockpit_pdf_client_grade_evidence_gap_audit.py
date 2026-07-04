from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_cockpit_pdf_client_grade_evidence_gap_audit import AUDIT, AUDIT_FIELDS, AUDIT_GROUPS, NOTES, VALID_AUDIT_STATUSES, VALID_GAP_SEVERITIES, validate


def _audit() -> dict:
    return json.loads(AUDIT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert AUDIT.exists()
    assert NOTES.exists()


def test_artifact_identity_and_source_paths() -> None:
    data = _audit()
    assert data["work_package_id"] == "ETF-EU-WP15AE"
    assert data["source_work_package"] == "ETF-EU-WP15AD"
    assert data["source_readiness_gate_artifact"].endswith(".json")
    assert data["source_readiness_contract"].endswith(".md")
    assert data["source_review_only_pdf"].endswith(".pdf")
    assert data["readiness_gate_status"] == "audited_not_passed"


def test_authority_claims_remain_false() -> None:
    data = _audit()
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
    ]:
        assert data[key] is False


def test_audit_groups_and_rows_are_valid() -> None:
    data = _audit()
    for group in AUDIT_GROUPS:
        assert group in data
        assert data[group]
        for row in data[group]:
            for field in AUDIT_FIELDS:
                assert field in row
            assert row["audit_status"] in VALID_AUDIT_STATUSES
            assert row["gap_severity"] in VALID_GAP_SEVERITIES
            if row["audit_status"] in {"blocked", "fail"}:
                assert row["missing_evidence"]
                assert row["recommended_resolution_package"]


def test_blockers_are_non_empty_and_counted() -> None:
    data = _audit()
    assert data["blocking_gaps_before_client_grade"]
    assert data["blocking_gaps_before_delivery_preflight"]
    assert data["client_grade_blocking_gap_count"] > 0
    assert data["delivery_preflight_blocking_gap_count"] > 0
    assert "investment_thesis_for_proposed_funded_positions" in data["blocking_gaps_before_client_grade"]
    assert "delivery_receipt_or_manifest_contract" in data["blocking_gaps_before_delivery_preflight"]


def test_source_values_remain_fixed() -> None:
    data = _audit()
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
        "# ETF-EU-WP15AE client-grade evidence gap audit",
        "## Scope",
        "## Source artifacts",
        "## Audit summary",
        "## Decision framework gap audit",
        "## Input/state contract gap audit",
        "## Output contract gap audit",
        "## Operational runbook gap audit",
        "## Blocking gaps before client-grade",
        "## Blocking gaps before delivery-preflight",
        "## Boundary checks",
        "## Decision",
        "## Next package",
    ]:
        assert marker in text


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-WP15AE"
    assert result["readiness_gate_status"] == "audited_not_passed"
    assert result["client_grade_blocking_gap_count"] > 0
    assert result["delivery_preflight_blocking_gap_count"] > 0
    assert result["selected_next_package"] == "ETF-EU-WP15AF"
