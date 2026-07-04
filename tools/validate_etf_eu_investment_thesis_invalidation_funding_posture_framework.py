from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCE_INVESTABILITY = Path("output/client_surface/etf_eu_priips_kid_liquidity_spread_evidence_20260703_000000.json")
SOURCE_POLICY = Path("output/client_surface/etf_eu_pricing_freshness_valuation_policy_20260703_000000.json")
SOURCE_PRODUCT_FACTS = Path("output/client_surface/etf_eu_product_facts_evidence_20260703_000000.json")
SOURCE_PRICING = Path("output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json")
SOURCE_REGISTRY = Path("config/ucits_symbol_registry.yml")
SOURCE_PDF = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf")
FRAMEWORK = Path("control/ETF_EU_INVESTMENT_THESIS_INVALIDATION_FUNDING_POSTURE_FRAMEWORK_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_investment_thesis_invalidation_funding_posture_framework_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_investment_thesis_invalidation_funding_posture_framework_notes_20260703_000000.md")

REQUIRED_FUND_FIELDS = {
    "isin",
    "fund_name",
    "issuer",
    "review_only_candidate_status",
    "investment_thesis_summary",
    "investment_thesis_evidence_dependencies",
    "invalidation_criteria",
    "funding_posture_status",
    "funding_posture_framework",
    "funding_preconditions",
    "client_grade_limitation",
    "valuation_grade_limitation",
    "delivery_preflight_limitation",
}

REQUIRED_LINE_FIELDS = {
    "symbol",
    "isin",
    "exchange",
    "trading_currency",
    "line_status",
    "freshness_policy_status",
    "liquidity_evidence_status",
    "spread_evidence_status",
    "review_only_line_role",
    "line_selection_status",
    "line_selection_limitation",
    "client_grade_limitation",
    "valuation_grade_limitation",
    "funding_limitation",
}

REQUIRED_INVALIDATION_CATEGORIES = {
    "source_authority_invalidation",
    "pricing_freshness_invalidation",
    "liquidity_spread_invalidation",
    "product_fact_invalidation",
    "client_language_invalidation",
    "funding_authority_invalidation",
    "delivery_preflight_invalidation",
}

REQUIRED_RESOLVED_GAPS = {
    "investment_thesis_for_proposed_funded_positions",
    "invalidation_criteria_for_proposed_funded_positions",
    "funding_decision_or_cash_posture",
}

REQUIRED_FALSE = [
    "client_grade_claim",
    "client_grade_enough_for_delivery_preflight_discussion",
    "delivery_ready",
    "delivery_preflight_allowed",
    "outbound_path_enabled",
    "production_delivery",
    "portfolio_mutation",
    "candidate_promotion",
    "funding_authority",
    "valuation_grade",
    "pricing_evidence_for_client_grade",
    "pricing_evidence_for_delivery_preflight",
    "receipt_artifact_created",
    "production_manifest_created",
    "recipient_config_changed",
    "smtp_or_secret_config_changed",
    "fake_price_used",
    "us_proxy_price_used",
    "live_price_fetch_performed",
    "live_data_fetch_performed",
    "pricing_evidence_changed",
    "recommendation_logic_changed",
    "source_pdf_replaced",
    "new_pdf_created",
    "renderer_changed",
]

VALID_SOURCE_TYPES = {"internal_artifact", "internal_policy", "decision_framework"}
VALID_AUTHORITY_LEVELS = {"internal_artifact", "internal_policy", "decision_framework"}
VALID_LINE_SELECTION_STATUS = {"review_only_line_candidate", "needs_cross_check", "not_selected_for_funding"}
VALID_INVALIDATION_STATUS = {"active_review_only", "not_triggered_in_committed_artifact", "needs_future_validation"}
VALID_INVALIDATION_EFFECT = {"remain_review_only", "block_client_grade", "block_delivery_preflight", "block_funding_discussion"}
FORBIDDEN_UNQUALIFIED_TERMS = ["buy", "sell", "hold", "fund now", "allocate now", "delivery-ready", "client-grade ready", "valuation-grade ready"]

FRAMEWORK_MARKERS = [
    "# ETF EU investment thesis, invalidation criteria, and funding posture framework v1",
    "## Purpose",
    "## Scope",
    "## Authority boundary",
    "## Review-only thesis framework",
    "## Evidence dependency rules",
    "## Invalidation criteria framework",
    "## Funding posture framework",
    "## Candidate-not-funded rule",
    "## What this framework does not authorize",
    "## Remaining client-grade blocker",
    "## Delivery-preflight limitation",
    "## Validation requirements",
]

NOTE_MARKERS = [
    "# ETF-EU-WP15AJ investment thesis, invalidation criteria, and funding posture framework",
    "## Scope",
    "## Source artifacts",
    "## Framework document",
    "## Fund-level decision framework",
    "## Line-level decision framework",
    "## Invalidation criteria framework",
    "## Funding posture framework",
    "## Resolved decision-framework gaps",
    "## Remaining client-grade blockers",
    "## Remaining delivery-preflight blockers",
    "## Boundary checks",
    "## Decision",
    "## Next package",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _require_fields(obj: dict[str, Any], fields: set[str], label: str) -> None:
    for field in fields:
        _require(field in obj, f"{label} missing field: {field}")
        _require(obj[field] not in (None, "", []), f"{label} empty field: {field}")


def _require_false_flags(data: dict[str, Any]) -> None:
    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")


def validate() -> dict[str, Any]:
    for path in [SOURCE_INVESTABILITY, SOURCE_POLICY, SOURCE_PRODUCT_FACTS, SOURCE_PRICING, SOURCE_REGISTRY, SOURCE_PDF, FRAMEWORK, ARTIFACT, NOTES]:
        _require(path.exists(), f"missing file: {path}")

    investability = _load(SOURCE_INVESTABILITY)
    policy = _load(SOURCE_POLICY)
    product_facts = _load(SOURCE_PRODUCT_FACTS)
    data = _load(ARTIFACT)
    framework_text = FRAMEWORK.read_text(encoding="utf-8")
    notes_text = NOTES.read_text(encoding="utf-8")

    _require(investability.get("work_package_id") == "ETF-EU-WP15AI", "source investability mismatch")
    _require(policy.get("work_package_id") == "ETF-EU-WP15AH", "source policy mismatch")
    _require(product_facts.get("work_package_id") == "ETF-EU-WP15AG", "source product facts mismatch")

    _require(data.get("work_package_id") == "ETF-EU-WP15AJ", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-WP15AI", "wrong source work package")
    _require(data.get("source_investability_evidence_artifact") == str(SOURCE_INVESTABILITY), "investability path mismatch")
    _require(data.get("source_policy_artifact") == str(SOURCE_POLICY), "policy path mismatch")
    _require(data.get("source_product_facts_artifact") == str(SOURCE_PRODUCT_FACTS), "product facts path mismatch")
    _require(data.get("source_pricing_artifact") == str(SOURCE_PRICING), "pricing path mismatch")
    _require(data.get("source_registry") == str(SOURCE_REGISTRY), "registry path mismatch")
    _require(data.get("source_review_only_pdf") == str(SOURCE_PDF), "PDF path mismatch")
    _require(data.get("framework_path") == str(FRAMEWORK), "framework path mismatch")

    _require(data.get("investment_thesis_framework_created") is True, "thesis framework not created")
    _require(data.get("invalidation_criteria_framework_created") is True, "invalidation framework not created")
    _require(data.get("funding_posture_framework_created") is True, "funding posture framework not created")
    _require(data.get("decision_framework_validated") is True, "decision framework not validated")
    _require(data.get("readiness_gate_status") == "decision_framework_defined_not_client_grade", "wrong readiness gate status")
    _require(data.get("accepted_review_only_foundation") is True, "review-only foundation not accepted")
    _require(data.get("delivery_authorization_decision") == "remain_blocked", "delivery authorization must remain blocked")
    _require(data.get("review_only") is True, "review_only must be true")

    _require(data.get("pdf_exists") is True, "pdf_exists must be true")
    _require(data.get("pdf_page_count") == 4, "PDF page count mismatch")
    _require(data.get("successful_rows_count") == 2, "successful rows mismatch")
    _require(data.get("failed_rows_count") == 0, "failed rows mismatch")
    _require(data.get("skipped_rows_count") == 1, "skipped rows mismatch")
    _require(data.get("first_successful_symbol") == "SXR8.DE", "SXR8 symbol mismatch")
    _require(data.get("first_successful_close_date") == "2026-07-03", "SXR8 date mismatch")
    _require(data.get("first_successful_close") == 706.119995, "SXR8 close mismatch")
    _require(data.get("second_successful_symbol") == "CSPX.L", "CSPX symbol mismatch")
    _require(data.get("second_successful_close_date") == "2026-07-03", "CSPX date mismatch")
    _require(data.get("second_successful_close") == 807.859985, "CSPX close mismatch")
    _require(data.get("smh_status") == "skipped_pending_registry_status", "SMH status mismatch")

    fund = data.get("fund_level_decision_framework")
    _require(isinstance(fund, dict), "fund-level decision framework missing")
    _require_fields(fund, REQUIRED_FUND_FIELDS, "fund-level decision framework")
    _require(fund["isin"] == "IE00B5BMR087", "fund ISIN mismatch")
    _require(fund["fund_name"] == "iShares Core S&P 500 UCITS ETF USD (Acc)", "fund name mismatch")
    _require(fund["issuer"] == "iShares / BlackRock", "issuer mismatch")
    _require(fund["review_only_candidate_status"] == "review_only_candidate_not_funded", "candidate status mismatch")
    _require(fund["funding_posture_status"] == "not_funded_framework_only", "funding posture status mismatch")
    _require(fund["cash_posture_status"] == "not_set", "cash posture status mismatch")
    _require(fund["portfolio_action_status"] == "no_portfolio_action", "portfolio action status mismatch")
    _require(fund["funding_decision_status"] == "no_funding_decision", "funding decision status mismatch")

    lines = data.get("line_level_decision_framework")
    _require(isinstance(lines, list) and lines, "line-level framework missing")
    by_symbol = {line.get("symbol"): line for line in lines}
    _require(set(by_symbol) == {"SXR8.DE", "CSPX.L"}, "line framework must include only SXR8.DE and CSPX.L")
    for symbol, line in by_symbol.items():
        _require_fields(line, REQUIRED_LINE_FIELDS, f"{symbol} line framework")
        _require(line["isin"] == "IE00B5BMR087", f"{symbol} ISIN mismatch")
        _require(line["line_status"] == "success", f"{symbol} line status mismatch")
        _require(line["freshness_policy_status"] == "current_completed_session", f"{symbol} freshness mismatch")
        _require(line["line_selection_status"] in VALID_LINE_SELECTION_STATUS, f"{symbol} invalid selection status")
    _require(by_symbol["SXR8.DE"]["line_selection_status"] == "needs_cross_check", "SXR8 posture mismatch")
    _require(by_symbol["CSPX.L"]["line_selection_status"] == "review_only_line_candidate", "CSPX posture mismatch")

    criteria = data.get("invalidation_criteria_framework")
    _require(isinstance(criteria, list) and criteria, "invalidation criteria missing")
    criteria_ids = {criterion.get("criterion_id") for criterion in criteria}
    _require(criteria_ids == REQUIRED_INVALIDATION_CATEGORIES, "invalidation categories mismatch")
    for criterion in criteria:
        _require(criterion.get("status") in VALID_INVALIDATION_STATUS, "invalid invalidation status")
        _require(criterion.get("effect_if_triggered") in VALID_INVALIDATION_EFFECT, "invalid invalidation effect")

    posture = data.get("funding_posture_framework")
    _require(isinstance(posture, dict), "funding posture framework missing")
    _require(posture.get("funding_posture_status") == "not_funded_framework_only", "funding posture mismatch")
    _require(posture.get("cash_posture_status") == "not_set", "cash posture mismatch")
    _require(posture.get("portfolio_action_status") == "no_portfolio_action", "portfolio action mismatch")
    _require(posture.get("funding_decision_status") == "no_funding_decision", "funding decision mismatch")

    _require(set(data.get("resolved_decision_framework_gaps", [])) == REQUIRED_RESOLVED_GAPS, "resolved gaps mismatch")
    _require("client_language_quality_gate" in data.get("remaining_client_grade_blockers", []), "client language blocker missing")
    _require(data.get("remaining_delivery_preflight_blockers"), "delivery blockers missing")

    manifest = data.get("source_manifest")
    _require(isinstance(manifest, list) and manifest, "source manifest missing")
    used_fields = " ".join(" ".join(source.get("used_for_fields", [])) for source in manifest)
    _require("investment thesis framework" in used_fields, "thesis source support missing")
    _require("invalidation criteria framework" in used_fields, "invalidation source support missing")
    _require("funding posture framework" in used_fields, "funding posture source support missing")
    for source in manifest:
        _require(source.get("source_type") in VALID_SOURCE_TYPES, "invalid source type")
        _require(source.get("authority_level") in VALID_AUTHORITY_LEVELS, "invalid authority level")
        _require(source.get("source_reference"), "source reference missing")

    _require_false_flags(data)
    _require(data.get("selected_next_package") in {"ETF-EU-WP15AK", "ETF-EU-WP15AJ-FIX"}, "invalid next package")

    artifact_text = json.dumps(data).lower()
    for term in FORBIDDEN_UNQUALIFIED_TERMS:
        _require(term not in artifact_text, f"unauthorized action language found in artifact: {term}")

    for marker in FRAMEWORK_MARKERS:
        _require(marker in framework_text, f"framework missing marker: {marker}")
    for marker in NOTE_MARKERS:
        _require(marker in notes_text, f"notes missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "readiness_gate_status": data["readiness_gate_status"],
        "investment_thesis_framework_created": data["investment_thesis_framework_created"],
        "invalidation_criteria_framework_created": data["invalidation_criteria_framework_created"],
        "funding_posture_framework_created": data["funding_posture_framework_created"],
        "decision_framework_validated": data["decision_framework_validated"],
        "resolved_decision_framework_gaps_count": len(data["resolved_decision_framework_gaps"]),
        "remaining_client_grade_blockers_count": len(data["remaining_client_grade_blockers"]),
        "remaining_delivery_preflight_blockers_count": len(data["remaining_delivery_preflight_blockers"]),
        "client_grade_claim": data["client_grade_claim"],
        "delivery_preflight_allowed": data["delivery_preflight_allowed"],
        "valuation_grade": data["valuation_grade"],
        "funding_authority": data["funding_authority"],
        "portfolio_mutation": data["portfolio_mutation"],
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
