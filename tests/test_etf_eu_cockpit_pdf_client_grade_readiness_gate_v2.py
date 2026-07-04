from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_cockpit_pdf_client_grade_readiness_gate_v2 import ARTIFACT, CONTRACT, GATE_FIELDS, GATE_GROUPS, NOTES, VALID_STATUSES, validate


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert CONTRACT.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()


def test_contract_contains_sections() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    for marker in [
        "# ETF EU cockpit PDF client-grade readiness gate v2",
        "## Purpose",
        "## Scope",
        "## Authority boundary",
        "## Layer 1 — Decision framework",
        "## Layer 2 — Input/state contract",
        "## Layer 3 — Output contract",
        "## Layer 4 — Operational runbook",
        "## Blocking gates before client-grade",
        "## Blocking gates before delivery-preflight",
        "## Completion semantics",
        "## Non-authorized actions",
        "review-only foundation",
        "client-grade report authority",
        "delivery-preflight authority",
        "ISIN-first",
        "UCITS",
        "PRIIPs/KID",
        "pricing freshness",
        "investment thesis",
        "invalidation criteria",
        "Dutch-first",
        "proxy disclosure",
    ]:
        assert marker in text


def test_artifact_identity_and_source_paths() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-WP15AD"
    assert data["source_work_package"] == "ETF-EU-WP15AC"
    assert data["source_pdf_artifact"].endswith(".pdf")
    assert data["source_visual_closeout_artifact"].endswith(".json")
    assert data["accepted_review_only_foundation"] is True
    assert data["readiness_gate_status"] == "gate_defined_not_passed"


def test_authority_claims_remain_false() -> None:
    data = _artifact()
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
        "recommendation_logic_changed",
        "source_pdf_replaced",
        "new_pdf_created",
        "renderer_changed",
    ]:
        assert data[key] is False


def test_gate_groups_and_rows_are_valid() -> None:
    data = _artifact()
    for group in GATE_GROUPS:
        assert group in data
        assert data[group]
        for row in data[group]:
            for field in GATE_FIELDS:
                assert field in row
            assert row["status"] in VALID_STATUSES


def test_blocking_gates_are_non_empty() -> None:
    data = _artifact()
    assert data["blocking_gates_before_client_grade"]
    assert data["blocking_gates_before_delivery_preflight"]
    assert "investment_thesis_for_proposed_funded_positions" in data["blocking_gates_before_client_grade"]
    assert "delivery_receipt_or_manifest_contract" in data["blocking_gates_before_delivery_preflight"]


def test_source_values_remain_fixed() -> None:
    data = _artifact()
    assert data["successful_rows_count"] == 2
    assert data["failed_rows_count"] == 0
    assert data["skipped_rows_count"] == 1
    assert data["first_successful_symbol"] == "SXR8.DE"
    assert data["first_successful_close"] == 706.119995
    assert data["second_successful_symbol"] == "CSPX.L"
    assert data["second_successful_close"] == 807.859985
    assert data["smh_status"] == "skipped_pending_registry_status"


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-WP15AD"
    assert result["readiness_gate_status"] == "gate_defined_not_passed"
    assert result["client_grade_claim"] is False
    assert result["delivery_preflight_allowed"] is False
