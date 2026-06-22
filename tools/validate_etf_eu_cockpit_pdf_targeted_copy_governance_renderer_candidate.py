from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.build_etf_eu_cockpit_pdf_targeted_copy_governance_renderer_candidate import OUTPUT as PDF_CANDIDATE
from runtime.build_etf_eu_cockpit_pdf_targeted_copy_governance_renderer_candidate import main as build_pdf_candidate

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_targeted_copy_governance_renderer_candidate_20260618_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_targeted_copy_governance_renderer_candidate_notes_20260618_000000.md")
SOURCE_REVIEW = Path("output/client_surface/etf_eu_cockpit_pdf_targeted_copy_governance_refinement_review_checkpoint_20260618_000000.json")
SOURCE_IMPL = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_implementation_20260618_000000.json")
PREMIUM_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf")
MIN_PDF_SIZE_BYTES = 1000


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


def validate_renderer_candidate(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise ValidationError(f"unexpected renderer candidate artifact path: {path}")

    # Hard build requirement: validation produces/checks the review-only PDF candidate.
    build_pdf_candidate()

    for file_path, label in [
        (ARTIFACT, "renderer candidate artifact"),
        (NOTES, "renderer candidate notes"),
        (PDF_CANDIDATE, "review-only PDF candidate"),
        (SOURCE_REVIEW, "source review checkpoint artifact"),
        (SOURCE_IMPL, "source implementation artifact"),
        (PREMIUM_PDF, "premium PDF baseline"),
    ]:
        _need(file_path, label)

    pdf = PDF_CANDIDATE.read_bytes()
    if not pdf.startswith(b"%PDF") or len(pdf) <= MIN_PDF_SIZE_BYTES:
        raise ValidationError("review-only PDF candidate header/size check failed")
    if b"review-only" not in pdf or b"delivery_authorization_decision=remain_blocked" not in pdf:
        raise ValidationError("review-only PDF candidate missing required visible governance markers")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    expected = {
        "schema_version": "etf_eu_cockpit_pdf_targeted_copy_governance_renderer_candidate_v1",
        "run_id": "20260618_000000",
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15M",
        "legacy_work_package_id": "WP15M",
        "source_work_package": "ETF-EU-WP15L",
        "pdf_candidate_path": str(PDF_CANDIDATE),
        "pdf_candidate_builder": "runtime/build_etf_eu_cockpit_pdf_targeted_copy_governance_renderer_candidate.py",
        "source_review_checkpoint_artifact": str(SOURCE_REVIEW),
        "source_implementation_artifact": str(SOURCE_IMPL),
        "premium_pdf_baseline_path": str(PREMIUM_PDF),
        "premium_pdf_baseline_commit": "fb7751026a70db355385946ee3882c68f9ec0e71",
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "ETF-EU-WP15N",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise ValidationError(f"unexpected {key}: {data.get(key)!r}")

    for key in [
        "review_only_pdf_candidate_required",
        "review_only_pdf_candidate_created",
        "pdf_candidate_is_review_only",
        "premium_pdf_baseline_preserved",
        "validator_marker_preservation",
        "ucits_proxy_separation_preserved",
        "review_only_status_preserved",
        "delivery_authority_preserved_as_blocked",
        "new_pdf_created",
        "renderer_changed",
    ]:
        _true(data, key)

    for key in [
        "pdf_candidate_is_delivery",
        "pdf_candidate_is_production_delivery",
        "premium_pdf_replaced",
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

    if not data.get("renderer_candidate_scope"):
        raise ValidationError("renderer_candidate_scope must not be empty")
    if not data.get("changed_source_paths"):
        raise ValidationError("changed_source_paths must not be empty when renderer_changed=true")

    notes = NOTES.read_text(encoding="utf-8")
    for marker in [
        "work_package_id=ETF-EU-WP15M",
        "review_only_pdf_candidate_required=true",
        "review_only_pdf_candidate_created=true",
        "pdf_candidate_is_delivery=false",
        "pdf_candidate_is_review_only=true",
        "new_pdf_created=true",
        "renderer_changed=true",
        "premium_pdf_replaced=false",
        "production_delivery=false",
        "client_distribution_claimed=false",
        "receipt_artifact_created=false",
        "production_manifest_created=false",
        "ETF-EU-WP15N",
    ]:
        if marker not in notes:
            raise ValidationError(f"notes missing marker: {marker}")

    print(
        "ETF_EU_COCKPIT_PDF_TARGETED_COPY_GOVERNANCE_RENDERER_CANDIDATE_OK "
        f"| artifact={ARTIFACT} | pdf={PDF_CANDIDATE} | selected_next_package=ETF-EU-WP15N"
    )
    return {"status": "valid", "artifact": str(ARTIFACT), "pdf": str(PDF_CANDIDATE), "selected_next_package": "ETF-EU-WP15N"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    validate_renderer_candidate(Path(parser.parse_args().artifact))


if __name__ == "__main__":
    main()
