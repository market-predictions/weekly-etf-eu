from __future__ import annotations

import argparse
import json
from pathlib import Path

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_20260618_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_notes_20260618_000000.md")
PREMIUM_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf")
SOURCE_CLOSEOUT_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_closeout_20260618_000000.json")

FALSE_BOUNDARY_FLAGS = [
    "production_delivery",
    "portfolio_mutation",
    "candidate_promotion",
    "funding_authority",
    "valuation_grade",
    "live_data_fetch_performed",
    "recommendation_logic_changed",
    "renderer_changed",
    "new_pdf_created",
    "outbound_path_enabled",
    "receipt_artifact_created",
    "production_manifest_created",
    "client_distribution_claimed",
]


class PremiumSurfaceReviewCheckpointValidationError(RuntimeError):
    pass


def _require(path: Path, label: str) -> None:
    if not path.exists():
        raise PremiumSurfaceReviewCheckpointValidationError(f"missing {label}: {path}")


def _require_non_empty(value: object, key: str) -> None:
    if value in (None, "", [], {}):
        raise PremiumSurfaceReviewCheckpointValidationError(f"missing or empty {key}")


def _require_false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        raise PremiumSurfaceReviewCheckpointValidationError(f"expected false: {key}")


def validate_premium_surface_review_checkpoint(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise PremiumSurfaceReviewCheckpointValidationError(f"unexpected review checkpoint artifact path: {path}")

    _require(ARTIFACT, "premium surface review checkpoint artifact")
    _require(NOTES, "premium surface review checkpoint notes")
    _require(PREMIUM_PDF, "reviewed premium PDF")
    _require(SOURCE_CLOSEOUT_ARTIFACT, "source premium surface closeout artifact")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise PremiumSurfaceReviewCheckpointValidationError("review checkpoint artifact must be a JSON object")

    expected_values = {
        "schema_version": "etf_eu_cockpit_pdf_premium_surface_review_checkpoint_v1",
        "run_id": "20260618_000000",
        "status": "completed_accept_as_evidence_with_non_blocking_improvements",
        "work_package": "WP15H",
        "source_work_package": "WP15G",
        "reviewed_pdf_path": str(PREMIUM_PDF),
        "source_closeout_artifact": str(SOURCE_CLOSEOUT_ARTIFACT),
        "selected_next_package": "WP15I",
        "selected_next_package_title": "ETF EU cockpit PDF premium surface copy/governance refinement plan, no delivery",
    }
    for key, expected in expected_values.items():
        if data.get(key) != expected:
            raise PremiumSurfaceReviewCheckpointValidationError(f"unexpected {key}: {data.get(key)!r}")

    for key in [
        "client_readability_assessment",
        "governance_assessment",
        "product_checkpoint_assessment",
        "readability_governance_checklist",
        "delivery_enablement_blockers",
        "non_blocking_improvements",
        "boundary_flags",
    ]:
        _require_non_empty(data.get(key), key)

    if not isinstance(data.get("blocking_issues"), list):
        raise PremiumSurfaceReviewCheckpointValidationError("blocking_issues must be a list")

    boundary_flags = data["boundary_flags"]
    if not isinstance(boundary_flags, dict):
        raise PremiumSurfaceReviewCheckpointValidationError("boundary_flags must be an object")
    for key in FALSE_BOUNDARY_FLAGS:
        _require_false(boundary_flags, key)

    governance = data["governance_assessment"]
    for key in [
        "avoids_valuation_grade_authority",
        "avoids_funding_authority",
        "avoids_candidate_promotion",
        "avoids_portfolio_mutation",
        "avoids_production_delivery_authority",
        "preserves_eu_ucits_source_of_truth_boundary",
        "keeps_us_etf_information_non_authoritative",
        "avoids_suggesting_delivery_enabled",
    ]:
        if governance.get(key) is not True:
            raise PremiumSurfaceReviewCheckpointValidationError(f"governance assessment did not pass: {key}")

    readability = data["client_readability_assessment"]
    for key in [
        "first_page_understandable_for_dutch_eu_client",
        "cockpit_first_structure_clear",
        "answers_what_matters_now",
        "dutch_eu_investor_assumptions_clear_enough_for_review",
        "ucits_vs_us_proxy_relationship_clear",
    ]:
        if readability.get(key) is not True:
            raise PremiumSurfaceReviewCheckpointValidationError(f"readability assessment did not pass: {key}")

    product = data["product_checkpoint_assessment"]
    if product.get("better_than_mvp_layout_surface") is not True:
        raise PremiumSurfaceReviewCheckpointValidationError("premium surface must be better than MVP/layout surface")
    if product.get("good_enough_to_preserve_as_evidence") is not True:
        raise PremiumSurfaceReviewCheckpointValidationError("premium surface must be preserved as evidence")

    notes = NOTES.read_text(encoding="utf-8")
    for marker in [
        "work_package=WP15H",
        "selected_next_package=WP15I",
        "production_delivery=false",
        "portfolio_mutation=false",
        "candidate_promotion=false",
        "funding_authority=false",
        "valuation_grade=false",
        "renderer_changed=false",
        "new_pdf_created=false",
        "ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_REVIEW_CHECKPOINT_OK",
    ]:
        if marker not in notes:
            raise PremiumSurfaceReviewCheckpointValidationError(f"review checkpoint notes missing marker: {marker}")

    print(
        "ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_REVIEW_CHECKPOINT_OK "
        f"| artifact={ARTIFACT} | selected_next_package=WP15I"
    )
    return {"status": "valid", "artifact": str(ARTIFACT), "selected_next_package": "WP15I"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_premium_surface_review_checkpoint(Path(args.artifact))


if __name__ == "__main__":
    main()
