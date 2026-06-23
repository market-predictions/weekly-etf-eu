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

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_visual_refinement_build_20260618_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_visual_refinement_build_notes_20260618_000000.md")
SOURCE_PDF = Path("output/client_surface/etf_eu_cockpit_pdf_targeted_copy_governance_renderer_candidate_20260618_000000.pdf")
SOURCE_REVIEW = Path("output/client_surface/etf_eu_cockpit_pdf_renderer_candidate_visual_review_checkpoint_20260618_000000.json")
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


def validate_premium_visual_refinement_build(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise ValidationError(f"unexpected build artifact path: {path}")

    build_premium_pdf()

    for file_path, label in [
        (ARTIFACT, "build artifact"),
        (NOTES, "build notes"),
        (SOURCE_PDF, "source WP15M PDF candidate"),
        (SOURCE_REVIEW, "source WP15N visual review artifact"),
        (PREMIUM_PDF, "new premium PDF candidate"),
    ]:
        _need(file_path, label)

    source_pdf = SOURCE_PDF.read_bytes()
    if not source_pdf.startswith(b"%PDF"):
        raise ValidationError("source WP15M PDF candidate does not start with %PDF")

    premium_pdf = PREMIUM_PDF.read_bytes()
    if not premium_pdf.startswith(b"%PDF") or len(premium_pdf) <= MIN_PDF_SIZE_BYTES:
        raise ValidationError("new premium PDF candidate header/size check failed")
    for marker in [
        b"review-only",
        b"not delivered",
        b"no delivery receipt",
        b"no production manifest",
        b"delivery_authorization_decision=remain_blocked",
        b"ETF EU Cockpit",
    ]:
        if marker not in premium_pdf:
            raise ValidationError(f"new premium PDF candidate missing visible marker: {marker!r}")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    expected = {
        "schema_version": "etf_eu_cockpit_pdf_premium_visual_refinement_build_v1",
        "run_id": "20260618_000000",
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15O",
        "legacy_work_package_id": "WP15O",
        "source_work_package": "ETF-EU-WP15N",
        "source_pdf_candidate_path": str(SOURCE_PDF),
        "source_pdf_candidate_commit": "92c09a8",
        "source_visual_review_artifact": str(SOURCE_REVIEW),
        "premium_pdf_candidate_path": str(PREMIUM_PDF),
        "premium_pdf_candidate_builder": "runtime/build_etf_eu_cockpit_pdf_premium_visual_refinement_candidate.py",
        "premium_visual_refinement_decision": "build_review_only_premium_candidate",
        "client_grade_target": "closer_to_client_grade_but_still_review_only",
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "ETF-EU-WP15P",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise ValidationError(f"unexpected {key}: {data.get(key)!r}")

    for key in [
        "premium_visual_refinement_build_created",
        "review_only_premium_pdf_candidate_required",
        "review_only_premium_pdf_candidate_created",
        "new_pdf_created",
        "renderer_changed",
        "premium_visual_refinement_candidate_created",
    ]:
        _true(data, key)

    for key in [
        "client_grade_claim",
        "delivery_ready",
        "prior_wp15m_pdf_replaced",
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

    for key in ["visual_improvements", "preserved_constraints"]:
        if not data.get(key):
            raise ValidationError(f"{key} must not be empty")

    notes = NOTES.read_text(encoding="utf-8")
    for marker in [
        "work_package_id=ETF-EU-WP15O",
        "review_only_premium_pdf_candidate_created=true",
        "new_pdf_created=true",
        "renderer_changed=true",
        "prior_wp15m_pdf_replaced=false",
        "production_delivery=false",
        "client_distribution_claimed=false",
        "receipt_artifact_created=false",
        "production_manifest_created=false",
        "ETF-EU-WP15P",
    ]:
        if marker not in notes:
            raise ValidationError(f"notes missing marker: {marker}")

    print(
        "ETF_EU_COCKPIT_PDF_PREMIUM_VISUAL_REFINEMENT_BUILD_OK "
        f"| artifact={ARTIFACT} | pdf={PREMIUM_PDF} | selected_next_package=ETF-EU-WP15P"
    )
    return {"status": "valid", "artifact": str(ARTIFACT), "pdf": str(PREMIUM_PDF), "selected_next_package": "ETF-EU-WP15P"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    validate_premium_visual_refinement_build(Path(parser.parse_args().artifact))


if __name__ == "__main__":
    main()
