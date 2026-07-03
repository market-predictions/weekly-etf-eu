from __future__ import annotations

import argparse
import json
from pathlib import Path

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_content_completeness_plan_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_content_completeness_plan_notes_20260703_000000.md")
CONTRACT = Path("control/ETF_EU_COCKPIT_PDF_CLIENT_GRADE_CONTENT_CONTRACT_V1.md")
SOURCE_REVIEW_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_visual_refinement_review_checkpoint_20260618_000000.json")
SOURCE_REVIEW_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_visual_refinement_review_checkpoint_notes_20260618_000000.md")
SOURCE_PDF = Path("output/client_surface/etf_eu_cockpit_pdf_premium_visual_refinement_candidate_20260618_000000.pdf")


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


def _non_empty_list(data: dict, key: str, minimum: int = 1) -> None:
    value = data.get(key)
    if not isinstance(value, list) or len(value) < minimum:
        raise ValidationError(f"expected list with at least {minimum} entries: {key}")


def _contains_all(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise ValidationError(f"{label} missing marker: {marker}")


def validate_client_grade_content_completeness_plan(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise ValidationError(f"unexpected content plan artifact path: {path}")

    for file_path, label in [
        (ARTIFACT, "WP15Q content plan artifact"),
        (NOTES, "WP15Q content plan notes"),
        (CONTRACT, "WP15Q content contract"),
        (SOURCE_REVIEW_ARTIFACT, "source WP15P review artifact"),
        (SOURCE_REVIEW_NOTES, "source WP15P review notes"),
        (SOURCE_PDF, "source WP15O premium PDF candidate"),
    ]:
        _need(file_path, label)

    pdf = SOURCE_PDF.read_bytes()
    if not pdf.startswith(b"%PDF"):
        raise ValidationError("source premium PDF candidate does not start with %PDF")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    expected = {
        "schema_version": "etf_eu_cockpit_pdf_client_grade_content_completeness_plan_v1",
        "run_id": "20260703_000000",
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15Q",
        "legacy_work_package_id": "WP15Q",
        "status": "completed_after_content_completeness_contract_validation",
        "source_work_package": "ETF-EU-WP15P",
        "source_review_checkpoint_artifact": str(SOURCE_REVIEW_ARTIFACT),
        "source_review_checkpoint_notes": str(SOURCE_REVIEW_NOTES),
        "source_premium_pdf_candidate_path": str(SOURCE_PDF),
        "content_contract_path": str(CONTRACT),
        "content_plan_artifact": str(ARTIFACT),
        "content_plan_notes": str(NOTES),
        "content_plan_validator": "tools/validate_etf_eu_cockpit_pdf_client_grade_content_completeness_plan.py",
        "content_plan_tests": "tests/test_etf_eu_cockpit_pdf_client_grade_content_completeness_plan.py",
        "plan_decision": "define_minimum_client_grade_content_contract_before_any_delivery_preflight_discussion",
        "client_grade_status_after_wp15q": "not_yet_client_grade_contract_defined_only",
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "ETF-EU-WP15R",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise ValidationError(f"unexpected {key}: {data.get(key)!r}")

    for key in [
        "client_grade_content_contract_created",
        "content_completeness_plan_created",
        "content_completeness_validation_required",
        "actual_pdf_candidate_reviewed_in_source_package",
        "validator_created",
        "tests_created",
    ]:
        _true(data, key)

    for key in [
        "new_pdf_created",
        "renderer_changed",
        "source_pdf_replaced",
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
    ]:
        _false(data, key)

    _non_empty_list(data, "required_decision_framework_sections", 7)
    _non_empty_list(data, "required_input_state_sections", 10)
    _non_empty_list(data, "required_output_sections", 12)
    _non_empty_list(data, "required_operational_validators", 10)
    _non_empty_list(data, "minimum_visible_fields_for_funded_or_investable_rows", 17)
    _non_empty_list(data, "not_authorized_in_wp15q", 13)

    required_fields = set(data["minimum_visible_fields_for_funded_or_investable_rows"])
    for field in ["isin", "ucits_status", "priips_kid_status", "exchange_ticker", "latest_close_date", "pricing_source", "pricing_freshness_status"]:
        if field not in required_fields:
            raise ValidationError(f"minimum visible fields missing: {field}")

    validators = set(data["required_operational_validators"])
    for validator in ["no_us_etf_as_eu_holding", "isin_first_holdings", "pricing_source_and_freshness_present", "delivery_boundary_markers_present"]:
        if validator not in validators:
            raise ValidationError(f"required validator missing: {validator}")

    contract = CONTRACT.read_text(encoding="utf-8")
    _contains_all(
        contract,
        [
            "Decision framework layer",
            "Input/state contract layer",
            "Output contract layer",
            "Operational runbook layer",
            "UCITS ETFs available to Dutch/EU investors",
            "U.S.-listed ETFs may appear only as research proxies",
            "production_delivery=false",
            "ETF-EU-WP15R",
        ],
        "contract",
    )

    notes = NOTES.read_text(encoding="utf-8")
    _contains_all(
        notes,
        [
            "work_package_id=ETF-EU-WP15Q",
            "source_work_package=ETF-EU-WP15P",
            "content_contract_path=control/ETF_EU_COCKPIT_PDF_CLIENT_GRADE_CONTENT_CONTRACT_V1.md",
            "production_delivery=false",
            "valuation_grade=false",
            "new_pdf_created=false",
            "ETF-EU-WP15R",
        ],
        "notes",
    )

    print(
        "ETF_EU_COCKPIT_PDF_CLIENT_GRADE_CONTENT_COMPLETENESS_PLAN_OK "
        f"| artifact={ARTIFACT} | contract={CONTRACT} | selected_next_package=ETF-EU-WP15R"
    )
    return {"status": "valid", "artifact": str(ARTIFACT), "contract": str(CONTRACT), "selected_next_package": "ETF-EU-WP15R"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    validate_client_grade_content_completeness_plan(Path(parser.parse_args().artifact))


if __name__ == "__main__":
    main()
