from __future__ import annotations

import argparse
import json
from pathlib import Path

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_targeted_copy_governance_refinement_review_checkpoint_20260618_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_targeted_copy_governance_refinement_review_checkpoint_notes_20260618_000000.md")
SOURCE_IMPL = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_implementation_20260618_000000.json")
SOURCE_IMPL_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_implementation_notes_20260618_000000.md")
SOURCE_PLAN = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_plan_20260618_000000.json")
PREMIUM_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf")
MIN_PDF_SIZE_BYTES = 8500


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


def validate_review_checkpoint(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise ValidationError(f"unexpected review checkpoint path: {path}")
    for file_path, label in [
        (ARTIFACT, "review checkpoint artifact"),
        (NOTES, "review checkpoint notes"),
        (SOURCE_IMPL, "source implementation artifact"),
        (SOURCE_IMPL_NOTES, "source implementation notes"),
        (SOURCE_PLAN, "source plan artifact"),
        (PREMIUM_PDF, "premium PDF baseline"),
    ]:
        _need(file_path, label)

    pdf = PREMIUM_PDF.read_bytes()
    if not pdf.startswith(b"%PDF") or len(pdf) <= MIN_PDF_SIZE_BYTES:
        raise ValidationError("premium PDF baseline header/size check failed")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    expected = {
        "schema_version": "etf_eu_cockpit_pdf_targeted_copy_governance_refinement_review_checkpoint_v1",
        "run_id": "20260618_000000",
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15L",
        "legacy_work_package_id": "WP15L",
        "status": "completed",
        "source_work_package": "ETF-EU-WP15K",
        "review_checkpoint_decision": "accept_contract_refinement_and_request_scoped_renderer_pdf_candidate",
        "implementation_review_status": "accepted_as_contract_layer",
        "source_implementation_artifact": str(SOURCE_IMPL),
        "source_implementation_notes": str(SOURCE_IMPL_NOTES),
        "source_plan_artifact": str(SOURCE_PLAN),
        "premium_pdf_baseline_path": str(PREMIUM_PDF),
        "premium_pdf_baseline_commit": "fb7751026a70db355385946ee3882c68f9ec0e71",
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "ETF-EU-WP15M",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise ValidationError(f"unexpected {key}: {data.get(key)!r}")

    for key in [
        "review_checkpoint_created",
        "renderer_pdf_candidate_required",
        "premium_pdf_baseline_preserved",
        "validator_marker_preservation",
        "ucits_proxy_separation_preserved",
        "review_only_status_preserved",
        "delivery_authority_preserved_as_blocked",
    ]:
        _true(data, key)

    for key in [
        "implementation_is_delivery",
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

    for key in ["review_findings", "accepted_contract_elements", "remaining_gap"]:
        if not data.get(key):
            raise ValidationError(f"{key} must not be empty")

    notes = NOTES.read_text(encoding="utf-8")
    for marker in [
        "work_package_id=ETF-EU-WP15L",
        "source_work_package=ETF-EU-WP15K",
        "review_checkpoint_created=true",
        "renderer_pdf_candidate_required=true",
        "implementation_is_delivery=false",
        "new_pdf_created=false",
        "renderer_changed=false",
        "premium_pdf_replaced=false",
        "production_delivery=false",
        "client_distribution_claimed=false",
        "receipt_artifact_created=false",
        "production_manifest_created=false",
        "ETF-EU-WP15M",
    ]:
        if marker not in notes:
            raise ValidationError(f"notes missing marker: {marker}")

    print(
        "ETF_EU_COCKPIT_PDF_TARGETED_COPY_GOVERNANCE_REFINEMENT_REVIEW_CHECKPOINT_OK "
        f"| artifact={ARTIFACT} | selected_next_package=ETF-EU-WP15M"
    )
    return {"status": "valid", "artifact": str(ARTIFACT), "selected_next_package": "ETF-EU-WP15M"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    validate_review_checkpoint(Path(parser.parse_args().artifact))


if __name__ == "__main__":
    main()
