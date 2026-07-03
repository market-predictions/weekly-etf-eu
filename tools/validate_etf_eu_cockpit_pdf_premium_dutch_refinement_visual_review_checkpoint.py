from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.build_etf_eu_cockpit_pdf_premium_dutch_refinement_candidate import OUTPUT as SOURCE_PDF
from runtime.build_etf_eu_cockpit_pdf_premium_dutch_refinement_candidate import main as build_source_pdf

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_visual_review_checkpoint_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_visual_review_checkpoint_notes_20260703_000000.md")
SOURCE_BUILD_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_build_20260703_000000.json")
SOURCE_BUILD_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_build_notes_20260703_000000.md")


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


def _contains_all_text(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise ValidationError(f"{label} missing marker: {marker}")


def _contains_all_bytes(data: bytes, markers: list[bytes], label: str) -> None:
    for marker in markers:
        if marker not in data:
            raise ValidationError(f"{label} missing marker: {marker!r}")


def validate_premium_dutch_refinement_visual_review_checkpoint(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise ValidationError(f"unexpected WP15U artifact path: {path}")

    build_source_pdf()

    for file_path, label in [
        (ARTIFACT, "WP15U visual review artifact"),
        (NOTES, "WP15U visual review notes"),
        (SOURCE_BUILD_ARTIFACT, "source WP15T build artifact"),
        (SOURCE_BUILD_NOTES, "source WP15T build notes"),
        (SOURCE_PDF, "source WP15T refined PDF candidate"),
    ]:
        _need(file_path, label)

    pdf = SOURCE_PDF.read_bytes()
    if not pdf.startswith(b"%PDF"):
        raise ValidationError("source PDF does not start with %PDF")
    _contains_all_bytes(
        pdf,
        [
            b"ETF EU Cockpit",
            b"Beslissing nu",
            b"Actiekaart",
            b"Kwaliteitsbadges",
            b"UCITS-kandidaten",
            b"Bewijs en versheid",
            b"Proxy-disclosure",
            b"Niet oplossen in WP15T",
            b"Klantgrade status",
            b"Governance footer",
            b"Runbook voor review",
            b"REVIEW-ONLY",
            b"NIET GELEVERD",
            b"Geen e-mail of klantdistributie",
            b"geen receipt",
            b"geen productie-manifest",
        ],
        "source PDF",
    )

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    expected = {
        "schema_version": "etf_eu_cockpit_pdf_premium_dutch_refinement_visual_review_checkpoint_v1",
        "run_id": "20260703_000000",
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15U",
        "legacy_work_package_id": "WP15U",
        "status": "completed_after_premium_dutch_refinement_visual_review_checkpoint_validation",
        "source_work_package": "ETF-EU-WP15T",
        "source_pdf_candidate_path": str(SOURCE_PDF),
        "source_pdf_candidate_builder": "runtime/build_etf_eu_cockpit_pdf_premium_dutch_refinement_candidate.py",
        "source_build_artifact": str(SOURCE_BUILD_ARTIFACT),
        "source_build_notes": str(SOURCE_BUILD_NOTES),
        "visual_review_checkpoint_artifact": str(ARTIFACT),
        "visual_review_checkpoint_notes": str(NOTES),
        "visual_review_checkpoint_validator": "tools/validate_etf_eu_cockpit_pdf_premium_dutch_refinement_visual_review_checkpoint.py",
        "visual_review_checkpoint_tests": "tests/test_etf_eu_cockpit_pdf_premium_dutch_refinement_visual_review_checkpoint.py",
        "visual_review_decision": "accept_as_review_only_premium_dutch_cockpit_foundation_not_delivery_grade",
        "client_grade_status_after_wp15u": "not_yet_client_grade_review_only_foundation_accepted_for_readiness_contract",
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "ETF-EU-WP15V",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise ValidationError(f"unexpected {key}: {data.get(key)!r}")

    for key in [
        "source_pdf_candidate_reviewed",
        "actual_render_review_performed",
        "visual_review_checkpoint_created",
        "dutch_first_language_reviewed",
        "cards_and_tables_reviewed",
        "evidence_badges_reviewed",
        "proxy_disclosure_reviewed",
        "delivery_boundary_markers_reviewed",
        "no_us_etf_as_eu_holding",
        "validator_created",
        "tests_created",
    ]:
        _true(data, key)

    for key in [
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

    if data.get("review_page_count") != 4:
        raise ValidationError("review_page_count must be 4")
    if len(data.get("render_review_observations", [])) < 8:
        raise ValidationError("not enough render review observations")
    if len(data.get("required_before_client_grade_or_delivery_preflight", [])) < 5:
        raise ValidationError("not enough required readiness items")

    notes = NOTES.read_text(encoding="utf-8")
    _contains_all_text(
        notes,
        [
            "work_package_id=ETF-EU-WP15U",
            "visual_review_decision=accept_as_review_only_premium_dutch_cockpit_foundation_not_delivery_grade",
            "client_grade_claim=false",
            "production_delivery=false",
            "valuation_grade=false",
            "source_pdf_replaced=false",
            "ETF-EU-WP15V",
        ],
        "notes",
    )

    print(
        "ETF_EU_COCKPIT_PDF_PREMIUM_DUTCH_REFINEMENT_VISUAL_REVIEW_CHECKPOINT_OK "
        f"| artifact={ARTIFACT} | source_pdf={SOURCE_PDF} | selected_next_package=ETF-EU-WP15V"
    )
    return {"status": "valid", "artifact": str(ARTIFACT), "source_pdf": str(SOURCE_PDF), "selected_next_package": "ETF-EU-WP15V"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    validate_premium_dutch_refinement_visual_review_checkpoint(Path(parser.parse_args().artifact))


if __name__ == "__main__":
    main()
