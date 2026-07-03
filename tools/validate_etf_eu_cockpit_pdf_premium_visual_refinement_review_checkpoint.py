from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.build_etf_eu_cockpit_pdf_premium_visual_refinement_candidate import OUTPUT as PREMIUM_PDF
from runtime.build_etf_eu_cockpit_pdf_premium_visual_refinement_candidate import main as build_premium_pdf

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_visual_refinement_review_checkpoint_20260618_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_visual_refinement_review_checkpoint_notes_20260618_000000.md")
SOURCE_BUILD_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_visual_refinement_build_20260618_000000.json")
SOURCE_BUILD_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_visual_refinement_build_notes_20260618_000000.md")
MIN_PDF_SIZE_BYTES = 1800


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


def _non_empty_list(data: dict, key: str) -> None:
    if not isinstance(data.get(key), list) or not data.get(key):
        raise ValidationError(f"expected non-empty list: {key}")


def validate_premium_visual_refinement_review_checkpoint(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise ValidationError(f"unexpected review checkpoint artifact path: {path}")

    build_premium_pdf()

    for file_path, label in [
        (PREMIUM_PDF, "source premium PDF candidate"),
        (SOURCE_BUILD_ARTIFACT, "source WP15O build artifact"),
        (SOURCE_BUILD_NOTES, "source WP15O build notes"),
        (ARTIFACT, "WP15P review checkpoint artifact"),
        (NOTES, "WP15P review checkpoint notes"),
    ]:
        _need(file_path, label)

    premium_pdf = PREMIUM_PDF.read_bytes()
    if not premium_pdf.startswith(b"%PDF") or len(premium_pdf) <= MIN_PDF_SIZE_BYTES:
        raise ValidationError("source premium PDF candidate header/size check failed")
    for marker in [
        b"ETF EU Cockpit",
        b"review-only",
        b"NOT DELIVERED",
        b"NO RECEIPT",
        b"AUTHORITY BLOCKED",
        b"delivery_authorization_decision=remain_blocked",
    ]:
        if marker not in premium_pdf:
            raise ValidationError(f"source premium PDF candidate missing visible marker: {marker!r}")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    expected = {
        "schema_version": "etf_eu_cockpit_pdf_premium_visual_refinement_review_checkpoint_v1",
        "run_id": "20260618_000000",
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15P",
        "legacy_work_package_id": "WP15P",
        "status": "completed_after_visual_review_checkpoint_validation",
        "source_work_package": "ETF-EU-WP15O",
        "source_premium_pdf_candidate_path": str(PREMIUM_PDF),
        "source_premium_pdf_candidate_commit": "88c2a75",
        "source_premium_build_artifact": str(SOURCE_BUILD_ARTIFACT),
        "source_premium_build_notes": str(SOURCE_BUILD_NOTES),
        "review_checkpoint_artifact": str(ARTIFACT),
        "review_checkpoint_notes": str(NOTES),
        "review_checkpoint_validator": "tools/validate_etf_eu_cockpit_pdf_premium_visual_refinement_review_checkpoint.py",
        "review_checkpoint_tests": "tests/test_etf_eu_cockpit_pdf_premium_visual_refinement_review_checkpoint.py",
        "visual_review_decision": "accept_as_review_only_cockpit_surface_foundation_not_delivery_grade",
        "client_grade_status": "not_yet_client_grade",
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "ETF-EU-WP15Q",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise ValidationError(f"unexpected {key}: {data.get(key)!r}")

    for key in [
        "visual_review_checkpoint_created",
        "actual_pdf_candidate_reviewed",
        "source_premium_pdf_candidate_reviewed",
        "review_only_status_confirmed",
        "no_delivery_boundary_confirmed",
        "validator_created",
        "tests_created",
    ]:
        _true(data, key)

    for key in [
        "client_grade_enough_for_delivery_preflight_discussion",
        "client_grade_claim",
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

    for key in [
        "premium_surface_strengths",
        "blocking_gaps_before_client_grade_or_delivery_preflight",
        "required_before_delivery_preflight_discussion",
    ]:
        _non_empty_list(data, key)

    notes = NOTES.read_text(encoding="utf-8")
    for marker in [
        "work_package_id=ETF-EU-WP15P",
        "source_work_package=ETF-EU-WP15O",
        "visual_review_checkpoint_created=true",
        "actual_pdf_candidate_reviewed=true",
        "visual_review_decision=accept_as_review_only_cockpit_surface_foundation_not_delivery_grade",
        "client_grade_status=not_yet_client_grade",
        "client_grade_enough_for_delivery_preflight_discussion=false",
        "production_delivery=false",
        "delivery_preflight_allowed=false",
        "receipt_artifact_created=false",
        "production_manifest_created=false",
        "selected_next_package",
        "ETF-EU-WP15Q",
    ]:
        if marker not in notes:
            raise ValidationError(f"notes missing marker: {marker}")

    print(
        "ETF_EU_COCKPIT_PDF_PREMIUM_VISUAL_REFINEMENT_REVIEW_CHECKPOINT_OK "
        f"| artifact={ARTIFACT} | source_pdf={PREMIUM_PDF} | selected_next_package=ETF-EU-WP15Q"
    )
    return {"status": "valid", "artifact": str(ARTIFACT), "source_pdf": str(PREMIUM_PDF), "selected_next_package": "ETF-EU-WP15Q"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    validate_premium_visual_refinement_review_checkpoint(Path(parser.parse_args().artifact))


if __name__ == "__main__":
    main()
