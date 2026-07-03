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

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_visual_review_checkpoint_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_visual_review_checkpoint_notes_20260703_000000.md")
SOURCE_BUILD_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_build_20260703_000000.json")
SOURCE_BUILD_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_build_notes_20260703_000000.md")


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


def _contains_all_text(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise ValidationError(f"{label} missing marker: {marker}")


def _contains_all_bytes(data: bytes, markers: list[bytes], label: str) -> None:
    for marker in markers:
        if marker not in data:
            raise ValidationError(f"{label} missing marker: {marker!r}")


def validate_visual_review_checkpoint(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise ValidationError(f"unexpected visual review checkpoint artifact path: {path}")

    build_content_complete_pdf()

    for file_path, label in [
        (ARTIFACT, "WP15S visual review artifact"),
        (NOTES, "WP15S visual review notes"),
        (SOURCE_BUILD_ARTIFACT, "source WP15R build artifact"),
        (SOURCE_BUILD_NOTES, "source WP15R build notes"),
        (CONTENT_COMPLETE_PDF, "source WP15R content-complete PDF candidate"),
    ]:
        _need(file_path, label)

    pdf = CONTENT_COMPLETE_PDF.read_bytes()
    if not pdf.startswith(b"%PDF"):
        raise ValidationError("source PDF does not start with %PDF")
    _contains_all_bytes(
        pdf,
        [
            b"ETF EU Cockpit Content-Complete Candidate",
            b"REVIEW-ONLY",
            b"NOT DELIVERED",
            b"NO RECEIPT",
            b"NO PRODUCTION MANIFEST",
            b"AUTHORITY BLOCKED",
            b"U.S. ETFs are not EU portfolio holdings",
            b"live pricing not fetched",
            b"selected_next_package=ETF-EU-WP15S",
        ],
        "source PDF",
    )

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    expected = {
        "schema_version": "etf_eu_cockpit_pdf_content_complete_candidate_visual_review_checkpoint_v1",
        "run_id": "20260703_000000",
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15S",
        "legacy_work_package_id": "WP15S",
        "status": "completed_after_visual_review_checkpoint_validation",
        "source_work_package": "ETF-EU-WP15R",
        "source_pdf_candidate_path": str(CONTENT_COMPLETE_PDF),
        "source_build_artifact": str(SOURCE_BUILD_ARTIFACT),
        "source_build_notes": str(SOURCE_BUILD_NOTES),
        "review_checkpoint_artifact": str(ARTIFACT),
        "review_checkpoint_notes": str(NOTES),
        "review_checkpoint_validator": "tools/validate_etf_eu_cockpit_pdf_content_complete_candidate_visual_review_checkpoint.py",
        "review_checkpoint_tests": "tests/test_etf_eu_cockpit_pdf_content_complete_candidate_visual_review_checkpoint.py",
        "visual_review_decision": "accept_as_review_only_content_complete_foundation_request_premium_visual_and_language_refinement",
        "content_completeness_status": "content_complete_for_review_only_candidate",
        "client_grade_status_after_wp15s": "not_yet_client_grade_visual_language_refinement_required",
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "ETF-EU-WP15T",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise ValidationError(f"unexpected {key}: {data.get(key)!r}")

    for key in [
        "source_pdf_candidate_reviewed",
        "actual_pdf_candidate_reviewed",
        "visual_review_checkpoint_created",
        "validator_created",
        "tests_created",
    ]:
        _true(data, key)

    for key in [
        "client_grade_claim",
        "client_grade_enough_for_delivery_preflight_discussion",
        "delivery_ready",
        "source_pdf_replaced",
        "new_pdf_created",
        "renderer_changed",
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

    _non_empty_list(data, "review_strengths", 7)
    _non_empty_list(data, "blocking_gaps_before_client_grade_or_delivery_preflight", 8)
    _non_empty_list(data, "required_before_client_grade_or_delivery_preflight", 8)

    gaps = "\n".join(data["blocking_gaps_before_client_grade_or_delivery_preflight"])
    _contains_all_text(
        gaps,
        [
            "visually dense",
            "section order",
            "pipe-delimited",
            "Dutch-first",
            "raw control labels",
            "freshness badges",
            "placeholders",
            "bilingual parity",
        ],
        "blocking gaps",
    )

    notes = NOTES.read_text(encoding="utf-8")
    _contains_all_text(
        notes,
        [
            "work_package_id=ETF-EU-WP15S",
            "source_work_package=ETF-EU-WP15R",
            "visual_review_decision=accept_as_review_only_content_complete_foundation_request_premium_visual_and_language_refinement",
            "client_grade_status_after_wp15s=not_yet_client_grade_visual_language_refinement_required",
            "production_delivery=false",
            "valuation_grade=false",
            "ETF-EU-WP15T",
        ],
        "notes",
    )

    print(
        "ETF_EU_COCKPIT_PDF_CONTENT_COMPLETE_CANDIDATE_VISUAL_REVIEW_CHECKPOINT_OK "
        f"| artifact={ARTIFACT} | source_pdf={CONTENT_COMPLETE_PDF} | selected_next_package=ETF-EU-WP15T"
    )
    return {"status": "valid", "artifact": str(ARTIFACT), "source_pdf": str(CONTENT_COMPLETE_PDF), "selected_next_package": "ETF-EU-WP15T"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    validate_visual_review_checkpoint(Path(parser.parse_args().artifact))


if __name__ == "__main__":
    main()
