from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONTRACT = Path("control/ETF_EU_COCKPIT_PDF_CLIENT_GRADE_READINESS_GATE_V2.md")
ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_readiness_gate_v2_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_readiness_gate_v2_notes_20260703_000000.md")
SOURCE_CLOSEOUT = Path("output/client_surface/etf_eu_cockpit_pdf_visual_review_closeout_20260703_000000.json")
SOURCE_PDF_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.json")
SOURCE_PDF = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf")

GATE_GROUPS = [
    "decision_framework_gates",
    "input_state_contract_gates",
    "output_contract_gates",
    "operational_runbook_gates",
]
GATE_FIELDS = [
    "gate_id",
    "layer",
    "status",
    "current_evidence",
    "missing_evidence",
    "rationale",
    "required_before_client_grade",
    "required_before_delivery_preflight",
    "future_package_hint",
]
VALID_STATUSES = {"pass", "fail", "blocked", "not_applicable"}
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
CONTRACT_SECTIONS = [
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
]
CONTRACT_TERMS = [
    "review-only foundation",
    "client-grade report authority",
    "delivery-preflight authority",
    "delivery receipt",
    "production manifest",
    "ISIN-first",
    "UCITS",
    "PRIIPs/KID",
    "pricing freshness",
    "TER / ongoing charge",
    "replication method",
    "distribution policy",
    "hedged/unhedged status",
    "liquidity/spread",
    "investment thesis",
    "invalidation criteria",
    "Dutch-first",
    "proxy disclosure",
    "SMTP/secrets/recipients",
]
NOTES_SECTIONS = [
    "# ETF-EU-WP15AD client-grade readiness gate notes",
    "## Scope",
    "## Source artifacts",
    "## Gate summary",
    "## Decision framework",
    "## Input/state contract",
    "## Output contract",
    "## Operational runbook",
    "## Blocking gates before client-grade",
    "## Blocking gates before delivery-preflight",
    "## Decision",
    "## Next package",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _all_gates(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group in GATE_GROUPS:
        value = artifact.get(group)
        _require(isinstance(value, list) and value, f"missing or empty gate group: {group}")
        rows.extend(value)
    return rows


def validate() -> dict[str, Any]:
    for path in [CONTRACT, ARTIFACT, NOTES, SOURCE_CLOSEOUT, SOURCE_PDF_ARTIFACT, SOURCE_PDF]:
        _require(path.exists(), f"missing file: {path}")

    artifact = _load(ARTIFACT)
    closeout = _load(SOURCE_CLOSEOUT)
    pdf_artifact = _load(SOURCE_PDF_ARTIFACT)
    contract = CONTRACT.read_text(encoding="utf-8")
    notes = NOTES.read_text(encoding="utf-8")

    _require(artifact.get("work_package_id") == "ETF-EU-WP15AD", "wrong work package")
    _require(artifact.get("source_work_package") == "ETF-EU-WP15AC", "wrong source package")
    _require(artifact.get("client_grade_readiness_gate_created") is True, "readiness gate not created")
    _require(artifact.get("readiness_gate_status") == "gate_defined_not_passed", "wrong gate status")
    _require(artifact.get("accepted_review_only_foundation") is True, "review-only foundation not accepted")
    _require(closeout.get("accepted_for_review_only_foundation") is True, "source closeout not accepted")
    _require(pdf_artifact.get("pdf_created") is True, "source PDF artifact not created")
    _require(artifact.get("pdf_exists") is True, "pdf_exists must be true")
    _require(artifact.get("pdf_page_count") == 4, "PDF page count mismatch")
    _require(artifact.get("successful_rows_count") == 2, "successful row count mismatch")
    _require(artifact.get("skipped_rows_count") == 1, "skipped row count mismatch")
    _require(artifact.get("first_successful_symbol") == "SXR8.DE", "SXR8 symbol mismatch")
    _require(artifact.get("first_successful_close_date") == "2026-07-03", "SXR8 date mismatch")
    _require(artifact.get("first_successful_close") == 706.119995, "SXR8 close mismatch")
    _require(artifact.get("second_successful_symbol") == "CSPX.L", "CSPX symbol mismatch")
    _require(artifact.get("second_successful_close_date") == "2026-07-03", "CSPX date mismatch")
    _require(artifact.get("second_successful_close") == 807.859985, "CSPX close mismatch")
    _require(artifact.get("smh_status") == "skipped_pending_registry_status", "SMH status mismatch")
    _require(artifact.get("blocking_gates_before_client_grade"), "missing client-grade blockers")
    _require(artifact.get("blocking_gates_before_delivery_preflight"), "missing delivery-preflight blockers")

    for row in _all_gates(artifact):
        for field in GATE_FIELDS:
            _require(field in row, f"gate row missing {field}")
        _require(row["status"] in VALID_STATUSES, f"invalid gate status: {row['status']}")

    for key in REQUIRED_FALSE:
        _require(artifact.get(key) is False, f"expected false for {key}")

    for section in CONTRACT_SECTIONS:
        _require(section in contract, f"contract missing section: {section}")
    for term in CONTRACT_TERMS:
        _require(term in contract, f"contract missing term: {term}")
    for section in NOTES_SECTIONS:
        _require(section in notes, f"notes missing section: {section}")

    _require(artifact.get("selected_next_package"), "selected_next_package missing")

    return {
        "status": "valid",
        "work_package_id": "ETF-EU-WP15AD",
        "readiness_gate_status": artifact["readiness_gate_status"],
        "client_grade_claim": artifact["client_grade_claim"],
        "delivery_preflight_allowed": artifact["delivery_preflight_allowed"],
        "selected_next_package": artifact["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
