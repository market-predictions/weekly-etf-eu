from __future__ import annotations

import json
from pathlib import Path
from typing import Any

READINESS_GATE = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_readiness_gate_v2_20260703_000000.json")
READINESS_CONTRACT = Path("control/ETF_EU_COCKPIT_PDF_CLIENT_GRADE_READINESS_GATE_V2.md")
SOURCE_CLOSEOUT = Path("output/client_surface/etf_eu_cockpit_pdf_visual_review_closeout_20260703_000000.json")
SOURCE_PDF_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.json")
SOURCE_PDF = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf")
AUDIT = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_evidence_gap_audit_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_evidence_gap_audit_notes_20260703_000000.md")

AUDIT_GROUPS = [
    "decision_framework_gap_audit",
    "input_state_contract_gap_audit",
    "output_contract_gap_audit",
    "operational_runbook_gap_audit",
]
AUDIT_FIELDS = [
    "gate_id",
    "layer",
    "gate_status_from_wp15ad",
    "audit_status",
    "current_evidence",
    "missing_evidence",
    "gap_severity",
    "blocks_client_grade",
    "blocks_delivery_preflight",
    "recommended_resolution_package",
    "rationale",
]
VALID_AUDIT_STATUSES = {"pass", "fail", "blocked", "not_applicable"}
VALID_GAP_SEVERITIES = {"none", "minor", "major", "blocking"}
REQUIRED_FALSE = [
    "client_grade_claim",
    "client_grade_enough_for_delivery_preflight_discussion",
    "delivery_ready",
    "delivery_preflight_allowed",
    "valuation_grade",
    "pricing_evidence_for_client_grade",
    "pricing_evidence_for_delivery_preflight",
    "production_delivery",
    "portfolio_mutation",
    "candidate_promotion",
    "funding_authority",
    "receipt_artifact_created",
    "production_manifest_created",
    "fake_price_used",
    "us_proxy_price_used",
    "live_data_fetch_performed",
    "pricing_evidence_changed",
    "recommendation_logic_changed",
    "source_pdf_replaced",
    "new_pdf_created",
    "renderer_changed",
]
NOTE_MARKERS = [
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
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _all_rows(audit: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group in AUDIT_GROUPS:
        value = audit.get(group)
        _require(isinstance(value, list) and value, f"missing or empty group: {group}")
        rows.extend(value)
    return rows


def validate() -> dict[str, Any]:
    for path in [READINESS_GATE, READINESS_CONTRACT, SOURCE_CLOSEOUT, SOURCE_PDF_ARTIFACT, SOURCE_PDF, AUDIT, NOTES]:
        _require(path.exists(), f"missing file: {path}")

    readiness = _load(READINESS_GATE)
    closeout = _load(SOURCE_CLOSEOUT)
    pdf_artifact = _load(SOURCE_PDF_ARTIFACT)
    audit = _load(AUDIT)
    notes = NOTES.read_text(encoding="utf-8")

    _require(readiness.get("work_package_id") == "ETF-EU-WP15AD", "source readiness gate mismatch")
    _require(closeout.get("work_package_id") == "ETF-EU-WP15AC", "source closeout mismatch")
    _require(pdf_artifact.get("work_package_id") == "ETF-EU-WP15AB", "source PDF artifact mismatch")
    _require(audit.get("work_package_id") == "ETF-EU-WP15AE", "wrong work package")
    _require(audit.get("source_work_package") == "ETF-EU-WP15AD", "wrong source package")
    _require(audit.get("evidence_gap_audit_created") is True, "audit not created")
    _require(audit.get("readiness_gate_status") == "audited_not_passed", "wrong readiness status")
    _require(audit.get("accepted_review_only_foundation") is True, "review-only foundation not accepted")
    _require(audit.get("pdf_exists") is True, "pdf_exists must be true")
    _require(audit.get("pdf_page_count") == 4, "page count mismatch")
    _require(audit.get("successful_rows_count") == 2, "successful row count mismatch")
    _require(audit.get("failed_rows_count") == 0, "failed row count mismatch")
    _require(audit.get("skipped_rows_count") == 1, "skipped row count mismatch")
    _require(audit.get("first_successful_symbol") == "SXR8.DE", "SXR8 symbol mismatch")
    _require(audit.get("first_successful_close_date") == "2026-07-03", "SXR8 date mismatch")
    _require(audit.get("first_successful_close") == 706.119995, "SXR8 close mismatch")
    _require(audit.get("second_successful_symbol") == "CSPX.L", "CSPX symbol mismatch")
    _require(audit.get("second_successful_close_date") == "2026-07-03", "CSPX date mismatch")
    _require(audit.get("second_successful_close") == 807.859985, "CSPX close mismatch")
    _require(audit.get("smh_status") == "skipped_pending_registry_status", "SMH status mismatch")

    rows = _all_rows(audit)
    _require(rows, "no audit rows")
    for row in rows:
        for field in AUDIT_FIELDS:
            _require(field in row, f"audit row missing {field}")
        _require(row["audit_status"] in VALID_AUDIT_STATUSES, f"invalid audit status: {row['audit_status']}")
        _require(row["gap_severity"] in VALID_GAP_SEVERITIES, f"invalid gap severity: {row['gap_severity']}")
        if row["audit_status"] in {"blocked", "fail"}:
            _require(bool(row["missing_evidence"]), f"missing evidence empty for {row['gate_id']}")
            _require(bool(row["recommended_resolution_package"]), f"recommended package empty for {row['gate_id']}")

    _require(audit.get("blocking_gaps_before_client_grade"), "client-grade blockers missing")
    _require(audit.get("blocking_gaps_before_delivery_preflight"), "delivery-preflight blockers missing")
    _require(audit.get("client_grade_blocking_gap_count", 0) > 0, "client-grade blocking count must be positive")
    _require(audit.get("delivery_preflight_blocking_gap_count", 0) > 0, "delivery-preflight blocking count must be positive")
    _require(audit.get("selected_next_package") == "ETF-EU-WP15AF", "wrong next package")

    for key in REQUIRED_FALSE:
        _require(audit.get(key) is False, f"expected false for {key}")
    for marker in NOTE_MARKERS:
        _require(marker in notes, f"notes missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": "ETF-EU-WP15AE",
        "readiness_gate_status": audit["readiness_gate_status"],
        "client_grade_blocking_gap_count": audit["client_grade_blocking_gap_count"],
        "delivery_preflight_blocking_gap_count": audit["delivery_preflight_blocking_gap_count"],
        "selected_next_package": audit["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
