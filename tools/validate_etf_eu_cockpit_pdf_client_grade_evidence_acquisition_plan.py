from __future__ import annotations

import json
from pathlib import Path
from typing import Any

GAP_AUDIT = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_evidence_gap_audit_20260703_000000.json")
READINESS_GATE = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_readiness_gate_v2_20260703_000000.json")
SOURCE_CLOSEOUT = Path("output/client_surface/etf_eu_cockpit_pdf_visual_review_closeout_20260703_000000.json")
SOURCE_PDF_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.json")
SOURCE_PDF = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf")
PLAN = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_evidence_acquisition_plan_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_evidence_acquisition_plan_notes_20260703_000000.md")

PLAN_GROUPS = [
    "decision_framework_evidence_plan",
    "product_data_evidence_plan",
    "pricing_freshness_evidence_plan",
    "investability_evidence_plan",
    "output_quality_evidence_plan",
    "valuation_reconciliation_evidence_plan",
    "delivery_preflight_evidence_plan",
]
PLAN_FIELDS = [
    "gap_id",
    "source_gap",
    "layer",
    "evidence_domain",
    "priority",
    "evidence_to_acquire",
    "authoritative_source_type",
    "candidate_source_paths_or_urls",
    "validation_method",
    "target_artifact_path",
    "required_before_client_grade",
    "required_before_delivery_preflight",
    "execution_allowed_in_wp15af",
    "recommended_work_package",
    "status",
    "rationale",
]
VALID_PRIORITIES = {"P0", "P1", "P2", "P3"}
VALID_STATUSES = {"planned_not_started", "blocked_until_authorized", "not_applicable"}
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
    "evidence_acquired",
]
NOTE_MARKERS = [
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
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _all_items(plan: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for group in PLAN_GROUPS:
        value = plan.get(group)
        _require(isinstance(value, list) and value, f"missing or empty group: {group}")
        items.extend(value)
    return items


def validate() -> dict[str, Any]:
    for path in [GAP_AUDIT, READINESS_GATE, SOURCE_CLOSEOUT, SOURCE_PDF_ARTIFACT, SOURCE_PDF, PLAN, NOTES]:
        _require(path.exists(), f"missing file: {path}")

    gap_audit = _load(GAP_AUDIT)
    readiness = _load(READINESS_GATE)
    closeout = _load(SOURCE_CLOSEOUT)
    pdf_artifact = _load(SOURCE_PDF_ARTIFACT)
    plan = _load(PLAN)
    notes = NOTES.read_text(encoding="utf-8")

    _require(gap_audit.get("work_package_id") == "ETF-EU-WP15AE", "source gap audit mismatch")
    _require(readiness.get("work_package_id") == "ETF-EU-WP15AD", "source readiness mismatch")
    _require(closeout.get("work_package_id") == "ETF-EU-WP15AC", "source closeout mismatch")
    _require(pdf_artifact.get("work_package_id") == "ETF-EU-WP15AB", "source PDF artifact mismatch")

    _require(plan.get("work_package_id") == "ETF-EU-WP15AF", "wrong work package")
    _require(plan.get("source_work_package") == "ETF-EU-WP15AE", "wrong source package")
    _require(plan.get("evidence_acquisition_plan_created") is True, "plan not created")
    _require(plan.get("readiness_gate_status") == "plan_created_not_executed", "wrong readiness status")
    _require(plan.get("accepted_review_only_foundation") is True, "review-only foundation not accepted")
    _require(plan.get("pdf_exists") is True, "pdf_exists must be true")
    _require(plan.get("pdf_page_count") == 4, "page count mismatch")
    _require(plan.get("successful_rows_count") == 2, "successful row count mismatch")
    _require(plan.get("failed_rows_count") == 0, "failed row count mismatch")
    _require(plan.get("skipped_rows_count") == 1, "skipped row count mismatch")
    _require(plan.get("first_successful_symbol") == "SXR8.DE", "SXR8 symbol mismatch")
    _require(plan.get("first_successful_close_date") == "2026-07-03", "SXR8 date mismatch")
    _require(plan.get("first_successful_close") == 706.119995, "SXR8 close mismatch")
    _require(plan.get("second_successful_symbol") == "CSPX.L", "CSPX symbol mismatch")
    _require(plan.get("second_successful_close_date") == "2026-07-03", "CSPX date mismatch")
    _require(plan.get("second_successful_close") == 807.859985, "CSPX close mismatch")
    _require(plan.get("smh_status") == "skipped_pending_registry_status", "SMH status mismatch")

    items = _all_items(plan)
    _require(items, "no plan items")
    for item in items:
        for field in PLAN_FIELDS:
            _require(field in item, f"plan item missing {field}")
        _require(item["priority"] in VALID_PRIORITIES, f"invalid priority: {item['priority']}")
        _require(item["status"] in VALID_STATUSES, f"invalid status: {item['status']}")
        _require(item["execution_allowed_in_wp15af"] is False, f"execution allowed for {item['gap_id']}")

    _require(plan.get("planned_client_grade_items_count", 0) >= 12, "client-grade plan count too low")
    _require(plan.get("planned_delivery_preflight_items_count", 0) >= 8, "delivery-preflight plan count too low")
    _require(plan.get("p0_items"), "p0_items missing")
    _require(plan.get("p1_items"), "p1_items missing")
    _require(plan.get("recommended_package_sequence"), "recommended package sequence missing")
    _require(plan.get("selected_next_package") == "ETF-EU-WP15AG", "wrong next package")

    for key in REQUIRED_FALSE:
        _require(plan.get(key) is False, f"expected false for {key}")
    for marker in NOTE_MARKERS:
        _require(marker in notes, f"notes missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": "ETF-EU-WP15AF",
        "readiness_gate_status": plan["readiness_gate_status"],
        "planned_client_grade_items_count": plan["planned_client_grade_items_count"],
        "planned_delivery_preflight_items_count": plan["planned_delivery_preflight_items_count"],
        "evidence_acquired": plan["evidence_acquired"],
        "selected_next_package": plan["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
