from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.build_etf_eu_cockpit_pdf_premium_dutch_refinement_candidate import OUTPUT as REFINED_PDF
from runtime.build_etf_eu_cockpit_pdf_premium_dutch_refinement_candidate import main as build_refined_pdf

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_build_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_build_notes_20260703_000000.md")
SOURCE_REVIEW_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_visual_review_checkpoint_20260703_000000.json")
SOURCE_REVIEW_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_visual_review_checkpoint_notes_20260703_000000.md")
SOURCE_PDF = Path("output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_20260703_000000.pdf")
MIN_PDF_SIZE_BYTES = 15000


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


def _contains(data: bytes, marker: bytes, label: str) -> None:
    if marker not in data:
        raise ValidationError(f"{label} missing marker: {marker!r}")


def validate_premium_dutch_refinement_candidate_build(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise ValidationError(f"unexpected WP15T artifact path: {path}")

    build_refined_pdf()

    for file_path, label in [
        (ARTIFACT, "WP15T refinement artifact"),
        (NOTES, "WP15T refinement notes"),
        (SOURCE_REVIEW_ARTIFACT, "source WP15S visual review artifact"),
        (SOURCE_REVIEW_NOTES, "source WP15S visual review notes"),
        (SOURCE_PDF, "source WP15R PDF candidate"),
        (REFINED_PDF, "WP15T refined PDF candidate"),
    ]:
        _need(file_path, label)

    pdf = REFINED_PDF.read_bytes()
    if not pdf.startswith(b"%PDF") or len(pdf) <= MIN_PDF_SIZE_BYTES:
        raise ValidationError("refined PDF header/size check failed")

    for marker in [
        b"ETF EU Cockpit",
        b"Nederlandse reviewkandidaat",
        b"Beslissing nu",
        b"Actiekaart",
        b"Kwaliteitsbadges",
        b"UCITS-kandidaten",
        b"Bewijs en versheid",
        b"Evidence badges",
        b"Proxy-disclosure",
        b"Niet oplossen in WP15T",
        b"Klantgrade status",
        b"Governance footer",
        b"Runbook voor review",
        b"Authority statement",
        b"REVIEW-ONLY",
        b"NIET GELEVERD",
        b"Geen live prijsupdate",
        b"Geen e-mail of klantdistributie",
        b"ETF-EU-WP15U",
    ]:
        _contains(pdf, marker, "WP15T refined PDF")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    expected = {
        "schema_version": "etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_build_v1",
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15T",
        "legacy_work_package_id": "WP15T",
        "source_work_package": "ETF-EU-WP15S",
        "refined_pdf_candidate_path": str(REFINED_PDF),
        "refined_pdf_candidate_builder": "runtime/build_etf_eu_cockpit_pdf_premium_dutch_refinement_candidate.py",
        "refinement_build_artifact": str(ARTIFACT),
        "refinement_build_notes": str(NOTES),
        "refinement_validator": "tools/validate_etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_build.py",
        "refinement_tests": "tests/test_etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_build.py",
        "client_grade_status_after_wp15t": "not_yet_client_grade_refined_review_only_candidate_built",
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "ETF-EU-WP15U",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise ValidationError(f"unexpected {key}: {data.get(key)!r}")

    for key in [
        "premium_visual_refinement_candidate_created",
        "dutch_first_language_refinement_candidate_created",
        "review_only_refined_pdf_candidate_created",
        "new_pdf_created",
        "renderer_changed",
        "dutch_first_language",
        "client_facing_hierarchy_improved",
        "cards_and_tables_used",
        "evidence_badges_used",
        "sequential_flow_used",
        "validator_created",
        "tests_created",
        "render_verified_locally",
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

    if data.get("visible_page_count") != 4:
        raise ValidationError("visible_page_count must be 4")
    if len(data.get("visible_sections_present", [])) < 16:
        raise ValidationError("not enough visible sections recorded")
    if len(data.get("wp15s_gaps_addressed", [])) < 7:
        raise ValidationError("not enough WP15S gaps addressed")

    notes = NOTES.read_text(encoding="utf-8")
    for marker in ["work_package_id=ETF-EU-WP15T", "Dutch-first client language", "production_delivery=false", "valuation_grade=false", "ETF-EU-WP15U"]:
        if marker not in notes:
            raise ValidationError(f"notes missing marker: {marker}")

    print(
        "ETF_EU_COCKPIT_PDF_PREMIUM_DUTCH_REFINEMENT_CANDIDATE_BUILD_OK "
        f"| artifact={ARTIFACT} | pdf={REFINED_PDF} | selected_next_package=ETF-EU-WP15U"
    )
    return {"status": "valid", "artifact": str(ARTIFACT), "pdf": str(REFINED_PDF), "selected_next_package": "ETF-EU-WP15U"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    validate_premium_dutch_refinement_candidate_build(Path(parser.parse_args().artifact))


if __name__ == "__main__":
    main()
