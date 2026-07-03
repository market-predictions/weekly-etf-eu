from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.build_etf_eu_cockpit_pdf_content_complete_candidate import OUTPUT as CONTENT_COMPLETE_PDF
from runtime.build_etf_eu_cockpit_pdf_content_complete_candidate import main as build_content_complete_pdf

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_build_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_build_notes_20260703_000000.md")
CONTRACT = Path("control/ETF_EU_COCKPIT_PDF_CLIENT_GRADE_CONTENT_CONTRACT_V1.md")
SOURCE_PLAN = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_content_completeness_plan_20260703_000000.json")
SOURCE_PLAN_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_content_completeness_plan_notes_20260703_000000.md")
MIN_PDF_SIZE_BYTES = 9000


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


def _contains_all_bytes(data: bytes, markers: list[bytes], label: str) -> None:
    for marker in markers:
        if marker not in data:
            raise ValidationError(f"{label} missing marker: {marker!r}")


def _contains_all_text(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise ValidationError(f"{label} missing marker: {marker}")


def validate_content_complete_candidate_build(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise ValidationError(f"unexpected content-complete candidate artifact path: {path}")

    build_content_complete_pdf()

    for file_path, label in [
        (ARTIFACT, "WP15R build artifact"),
        (NOTES, "WP15R build notes"),
        (CONTRACT, "WP15Q content contract"),
        (SOURCE_PLAN, "source WP15Q content plan"),
        (SOURCE_PLAN_NOTES, "source WP15Q content plan notes"),
        (CONTENT_COMPLETE_PDF, "WP15R content-complete PDF candidate"),
    ]:
        _need(file_path, label)

    pdf = CONTENT_COMPLETE_PDF.read_bytes()
    if not pdf.startswith(b"%PDF") or len(pdf) <= MIN_PDF_SIZE_BYTES:
        raise ValidationError("content-complete PDF candidate header/size check failed")

    _contains_all_bytes(
        pdf,
        [
            b"ETF EU Cockpit Content-Complete Candidate",
            b"content_completeness_candidate=true",
            b"REVIEW-ONLY",
            b"NOT DELIVERED",
            b"NO RECEIPT",
            b"NO PRODUCTION MANIFEST",
            b"AUTHORITY BLOCKED",
            b"1. Cockpit header with report date and authority markers",
            b"2. Executive read and action summary",
            b"3. Portfolio holdings and cash snapshot",
            b"4. Allocation and concentration summary",
            b"5. UCITS investability table",
            b"6. Pricing and freshness evidence table",
            b"7. Holding-level decision table",
            b"8. Watchlist and candidate pipeline with promotion status",
            b"9. Risk, regime and event context",
            b"10. Proxy and benchmark disclosure",
            b"11. Unresolved-data and limitation block",
            b"12. Validation and governance footer",
            b"U.S. ETFs are not EU portfolio holdings",
            b"live pricing not fetched",
            b"delivery_authorization_decision=remain_blocked",
            b"selected_next_package=ETF-EU-WP15S",
        ],
        "content-complete PDF candidate",
    )

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    expected = {
        "schema_version": "etf_eu_cockpit_pdf_content_complete_candidate_build_v1",
        "run_id": "20260703_000000",
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15R",
        "legacy_work_package_id": "WP15R",
        "status": "completed_after_content_complete_candidate_build_and_validation",
        "source_work_package": "ETF-EU-WP15Q",
        "content_contract_path": str(CONTRACT),
        "source_content_plan_artifact": str(SOURCE_PLAN),
        "source_content_plan_notes": str(SOURCE_PLAN_NOTES),
        "content_complete_pdf_candidate_path": str(CONTENT_COMPLETE_PDF),
        "content_complete_pdf_candidate_builder": "runtime/build_etf_eu_cockpit_pdf_content_complete_candidate.py",
        "content_complete_candidate_build_artifact": str(ARTIFACT),
        "content_complete_candidate_build_notes": str(NOTES),
        "content_complete_candidate_validator": "tools/validate_etf_eu_cockpit_pdf_content_complete_candidate_build.py",
        "content_complete_candidate_tests": "tests/test_etf_eu_cockpit_pdf_content_complete_candidate_build.py",
        "funded_holdings_status": "none_cash_only_review_surface",
        "pricing_surface_status": "not_refreshed_in_wp15r_unresolved_for_review_candidate",
        "portfolio_reconciliation_status": "not_applicable_no_valuation_surface_promoted_and_no_funded_holdings",
        "client_grade_status_after_wp15r": "not_yet_client_grade_review_only_candidate_built",
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "ETF-EU-WP15S",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise ValidationError(f"unexpected {key}: {data.get(key)!r}")

    for key in [
        "content_complete_pdf_candidate_created",
        "review_only_content_complete_candidate_created",
        "builder_created",
        "new_pdf_created",
        "renderer_changed",
        "content_contract_followed",
        "content_completeness_candidate",
        "cash_snapshot_included",
        "allocation_summary_included",
        "candidate_pipeline_included",
        "ucits_investability_table_included",
        "pricing_freshness_table_included",
        "proxy_disclosure_included",
        "unresolved_data_block_included",
        "governance_footer_included",
        "validator_created",
        "tests_created",
    ]:
        _true(data, key)

    for key in [
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

    if data.get("visible_page_count") != 3:
        raise ValidationError("visible_page_count must be 3")
    if data.get("funded_etf_holdings_count") != 0:
        raise ValidationError("funded_etf_holdings_count must remain 0")

    _non_empty_list(data, "visible_sections_present", 12)
    _non_empty_list(data, "minimum_visible_fields_for_funded_or_investable_rows_included", 17)
    _non_empty_list(data, "candidate_rows_represented", 4)

    section_names = set(data["visible_sections_present"])
    for section in [
        "portfolio holdings and cash snapshot",
        "UCITS investability table",
        "pricing and freshness evidence table",
        "proxy and benchmark disclosure",
        "unresolved-data and limitation block",
        "validation and governance footer",
    ]:
        if section not in section_names:
            raise ValidationError(f"visible_sections_present missing: {section}")

    visible_fields = set(data["minimum_visible_fields_for_funded_or_investable_rows_included"])
    for field in [
        "isin",
        "ucits_status",
        "priips_kid_status",
        "exchange_ticker",
        "pricing_symbol",
        "latest_close_date",
        "latest_close",
        "pricing_source",
        "pricing_freshness_status",
    ]:
        if field not in visible_fields:
            raise ValidationError(f"minimum visible field missing: {field}")

    notes = NOTES.read_text(encoding="utf-8")
    _contains_all_text(
        notes,
        [
            "work_package_id=ETF-EU-WP15R",
            "content_complete_pdf_candidate_path=output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_20260703_000000.pdf",
            "production_delivery=false",
            "valuation_grade=false",
            "live_data_fetch_performed=false",
            "pricing_evidence_changed=false",
            "ETF-EU-WP15S",
        ],
        "notes",
    )

    print(
        "ETF_EU_COCKPIT_PDF_CONTENT_COMPLETE_CANDIDATE_BUILD_OK "
        f"| artifact={ARTIFACT} | pdf={CONTENT_COMPLETE_PDF} | selected_next_package=ETF-EU-WP15S"
    )
    return {
        "status": "valid",
        "artifact": str(ARTIFACT),
        "pdf": str(CONTENT_COMPLETE_PDF),
        "selected_next_package": "ETF-EU-WP15S",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    validate_content_complete_candidate_build(Path(parser.parse_args().artifact))


if __name__ == "__main__":
    main()
