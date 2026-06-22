from __future__ import annotations

import argparse
import json
from pathlib import Path

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_renderer_candidate_visual_review_checkpoint_20260618_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_renderer_candidate_visual_review_checkpoint_notes_20260618_000000.md")
PDF_CANDIDATE = Path("output/client_surface/etf_eu_cockpit_pdf_targeted_copy_governance_renderer_candidate_20260618_000000.pdf")
SOURCE_RENDERER_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_targeted_copy_governance_renderer_candidate_20260618_000000.json")
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


def validate_visual_review_checkpoint(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise ValidationError(f"unexpected visual review artifact path: {path}")

    for file_path, label in [
        (ARTIFACT, "visual review artifact"),
        (NOTES, "visual review notes"),
        (PDF_CANDIDATE, "source PDF candidate"),
        (SOURCE_RENDERER_ARTIFACT, "source renderer candidate artifact"),
    ]:
        _need(file_path, label)

    pdf = PDF_CANDIDATE.read_bytes()
    if not pdf.startswith(b"%PDF") or len(pdf) <= MIN_PDF_SIZE_BYTES:
        raise ValidationError("source PDF candidate header/size check failed")
    for marker in [b"Review-only PDF Candidate", b"not delivered", b"delivery_authorization_decision=remain_blocked"]:
        if marker not in pdf:
            raise ValidationError(f"source PDF candidate missing visible marker: {marker!r}")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    expected = {
        "schema_version": "etf_eu_cockpit_pdf_renderer_candidate_visual_review_checkpoint_v1",
        "run_id": "20260618_000000",
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15N",
        "legacy_work_package_id": "WP15N",
        "status": "completed",
        "source_work_package": "ETF-EU-WP15M",
        "pdf_candidate_path": str(PDF_CANDIDATE),
        "pdf_candidate_commit": "92c09a8",
        "visual_review_decision": "request_concrete_visual_refinement_build_package",
        "client_grade_status": "not_yet_client_grade",
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "ETF-EU-WP15O",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise ValidationError(f"unexpected {key}: {data.get(key)!r}")

    for key in [
        "visual_review_checkpoint_created",
        "actual_pdf_candidate_reviewed",
        "pdf_candidate_exists",
        "pdf_candidate_is_review_only",
        "visual_refinement_required",
    ]:
        _true(data, key)

    for key in [
        "new_pdf_created",
        "renderer_changed",
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

    for key in ["review_findings", "accepted_elements", "required_refinements"]:
        if not data.get(key):
            raise ValidationError(f"{key} must not be empty")

    notes = NOTES.read_text(encoding="utf-8")
    for marker in [
        "work_package_id=ETF-EU-WP15N",
        "actual_pdf_candidate_reviewed=true",
        "visual_review_decision=request_concrete_visual_refinement_build_package",
        "client_grade_status=not_yet_client_grade",
        "visual_refinement_required=true",
        "new_pdf_created=false",
        "renderer_changed=false",
        "production_delivery=false",
        "client_distribution_claimed=false",
        "receipt_artifact_created=false",
        "production_manifest_created=false",
        "ETF-EU-WP15O",
    ]:
        if marker not in notes:
            raise ValidationError(f"notes missing marker: {marker}")

    print(
        "ETF_EU_COCKPIT_PDF_RENDERER_CANDIDATE_VISUAL_REVIEW_CHECKPOINT_OK "
        f"| artifact={ARTIFACT} | selected_next_package=ETF-EU-WP15O"
    )
    return {"status": "valid", "artifact": str(ARTIFACT), "selected_next_package": "ETF-EU-WP15O"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    validate_visual_review_checkpoint(Path(parser.parse_args().artifact))


if __name__ == "__main__":
    main()
