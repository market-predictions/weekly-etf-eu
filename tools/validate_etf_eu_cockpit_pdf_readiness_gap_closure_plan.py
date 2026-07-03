from __future__ import annotations

import argparse
import json
from pathlib import Path

PLAN = Path("control/ETF_EU_COCKPIT_PDF_READINESS_GAP_CLOSURE_PLAN_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_readiness_gap_closure_plan_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_readiness_gap_closure_plan_notes_20260703_000000.md")
SOURCE_AUDIT_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_readiness_gate_implementation_audit_20260703_000000.json")
SOURCE_AUDIT_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_readiness_gate_implementation_audit_notes_20260703_000000.md")
READINESS_CONTRACT = Path("control/ETF_EU_COCKPIT_PDF_CLIENT_GRADE_READINESS_CONTRACT_V1.md")

PRIMARY_GAPS = {
    "thesis_and_invalidation_present_for_funded_holdings_or_proposed_candidates",
    "isin_first_identity_present",
    "trading_currency_present",
    "pricing_symbol_present",
    "latest_close_date_present",
    "latest_close_present",
    "pricing_source_present",
    "ter_or_cost_status_present",
    "replication_method_present_or_explicitly_unknown",
    "distribution_policy_present_or_explicitly_unknown",
    "hedged_unhedged_status_present_or_explicitly_unknown",
    "liquidity_spread_evidence_present_or_review_needed",
}
ALLOWED_STATUS = {"fail", "blocked", "not_started"}
ALLOWED_LAYERS = {"decision_framework", "input_state_contract", "output_contract", "operational_runbook"}
ALLOWED_PACKAGE_TYPES = {"data_contract", "evidence_collection", "validator_implementation", "pdf_surface_update", "policy_decision", "manual_review"}
ALLOWED_AUTHORITY = {"none_for_planning", "explicit_later_authority_required"}
DATA_DEPENDENT_GAPS = PRIMARY_GAPS


class ValidationError(RuntimeError):
    pass


def _need(path: Path, label: str) -> None:
    if not path.exists():
        raise ValidationError(f"missing {label}: {path}")


def _true(data: dict, key: str) -> None:
    if data.get(key) is not True:
        raise ValidationError(f"expected true: {key}")


def _false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        raise ValidationError(f"expected false: {key}")


def _all_gap_rows(data: dict) -> list[dict]:
    rows: list[dict] = []
    for group in ["decision_framework_gap_closure_plan", "input_state_contract_gap_closure_plan"]:
        group_rows = data.get(group)
        if not isinstance(group_rows, list) or not group_rows:
            raise ValidationError(f"missing gap group: {group}")
        rows.extend(group_rows)
    return rows


def _validate_gap_row(row: dict) -> None:
    required = [
        "gap_id",
        "layer",
        "current_status",
        "why_it_blocks_client_grade",
        "required_evidence",
        "expected_source_contract_or_file",
        "future_validator_expectation",
        "future_package_type",
        "execution_authority_required",
        "closure_sequence",
        "risk_if_skipped",
    ]
    for key in required:
        if key not in row or row[key] in (None, "", []):
            raise ValidationError(f"missing required gap field {key}: {row}")
    if row["current_status"] not in ALLOWED_STATUS:
        raise ValidationError(f"invalid current_status: {row['current_status']}")
    if row["layer"] not in ALLOWED_LAYERS:
        raise ValidationError(f"invalid layer: {row['layer']}")
    if row["future_package_type"] not in ALLOWED_PACKAGE_TYPES:
        raise ValidationError(f"invalid future_package_type: {row['future_package_type']}")
    if row["execution_authority_required"] not in ALLOWED_AUTHORITY:
        raise ValidationError(f"invalid execution_authority_required: {row['execution_authority_required']}")
    if row["gap_id"] in DATA_DEPENDENT_GAPS and row["execution_authority_required"] == "none_for_planning":
        raise ValidationError(f"data/valuation/delivery dependent gap cannot have none_for_planning: {row['gap_id']}")


def validate_gap_closure_plan(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise ValidationError(f"unexpected WP15X artifact path: {path}")

    for file_path, label in [
        (PLAN, "gap closure plan"),
        (ARTIFACT, "gap closure artifact"),
        (NOTES, "gap closure notes"),
        (SOURCE_AUDIT_ARTIFACT, "source WP15W audit artifact"),
        (SOURCE_AUDIT_NOTES, "source WP15W audit notes"),
        (READINESS_CONTRACT, "source WP15V readiness contract"),
    ]:
        _need(file_path, label)

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    expected = {
        "schema_version": "etf_eu_cockpit_pdf_readiness_gap_closure_plan_v1",
        "run_id": "20260703_000000",
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15X",
        "legacy_work_package_id": "WP15X",
        "status": "completed_after_non_executing_readiness_gap_closure_plan",
        "source_work_package": "ETF-EU-WP15W",
        "source_readiness_audit_artifact": str(SOURCE_AUDIT_ARTIFACT),
        "source_readiness_audit_notes": str(SOURCE_AUDIT_NOTES),
        "readiness_contract_path": str(READINESS_CONTRACT),
        "gap_closure_plan_path": str(PLAN),
        "gap_closure_artifact": str(ARTIFACT),
        "gap_closure_notes": str(NOTES),
        "gap_closure_validator": "tools/validate_etf_eu_cockpit_pdf_readiness_gap_closure_plan.py",
        "gap_closure_tests": "tests/test_etf_eu_cockpit_pdf_readiness_gap_closure_plan.py",
        "gap_closure_plan_status": "non_executing_plan_created",
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "ETF-EU-WP15Y",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise ValidationError(f"unexpected {key}: {data.get(key)!r}")

    _true(data, "gap_closure_plan_created")
    _true(data, "validator_created")
    _true(data, "tests_created")

    for key in [
        "execution_performed",
        "client_grade_claim",
        "client_grade_enough_for_delivery_preflight_discussion",
        "delivery_ready",
        "production_delivery",
        "portfolio_mutation",
        "candidate_promotion",
        "funding_authority",
        "valuation_grade",
        "delivery_preflight_allowed",
        "outbound_path_enabled",
        "live_data_fetch_performed",
        "pricing_evidence_changed",
        "recommendation_logic_changed",
        "client_distribution_claimed",
        "receipt_artifact_created",
        "production_manifest_created",
        "source_pdf_replaced",
        "new_pdf_created",
        "renderer_changed",
    ]:
        _false(data, key)

    rows = _all_gap_rows(data)
    represented = {row.get("gap_id") for row in rows}
    if represented != PRIMARY_GAPS:
        raise ValidationError(f"primary gaps mismatch: {sorted(represented)}")
    for row in rows:
        _validate_gap_row(row)

    blocked = set(data.get("blocked_until_later_authority", []))
    if not PRIMARY_GAPS.issubset(blocked):
        raise ValidationError("blocked_until_later_authority does not contain all primary gaps")

    output_plan = data.get("output_contract_gap_closure_plan")
    if not isinstance(output_plan, dict) or output_plan.get("no_output_contract_gap_requiring_closure") is not True:
        raise ValidationError("output contract no-gap flag missing")
    runbook_plan = data.get("operational_runbook_gap_closure_plan")
    if not isinstance(runbook_plan, dict) or runbook_plan.get("no_operational_runbook_gap_requiring_closure") is not True:
        raise ValidationError("operational runbook no-gap flag missing")

    summary = data.get("non_executing_plan_summary")
    if not isinstance(summary, dict) or summary.get("primary_gap_count") != 12:
        raise ValidationError("invalid non_executing_plan_summary")
    for key in ["evidence_collected", "recommendation_changed", "pdf_changed"]:
        if summary.get(key) is not False:
            raise ValidationError(f"summary expected false: {key}")

    notes = NOTES.read_text(encoding="utf-8")
    for marker in [
        "work_package_id=ETF-EU-WP15X",
        "gap_closure_plan_status=non_executing_plan_created",
        "execution_performed=false",
        "production_delivery=false",
        "valuation_grade=false",
        "ETF-EU-WP15Y",
    ]:
        if marker not in notes:
            raise ValidationError(f"notes missing marker: {marker}")

    print(
        "ETF_EU_COCKPIT_PDF_READINESS_GAP_CLOSURE_PLAN_OK "
        f"| artifact={ARTIFACT} | selected_next_package=ETF-EU-WP15Y"
    )
    return {"status": "valid", "artifact": str(ARTIFACT), "selected_next_package": "ETF-EU-WP15Y"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    validate_gap_closure_plan(Path(parser.parse_args().artifact))


if __name__ == "__main__":
    main()
