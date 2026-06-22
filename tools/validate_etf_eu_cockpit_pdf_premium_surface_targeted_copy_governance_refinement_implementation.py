from __future__ import annotations

import argparse
import json
from pathlib import Path

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_implementation_20260618_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_implementation_notes_20260618_000000.md")
SOURCE_PLAN = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_plan_20260618_000000.json")
SOURCE_PLAN_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_plan_notes_20260618_000000.md")
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


def validate_targeted_refinement_implementation(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise ValidationError(f"unexpected implementation artifact path: {path}")

    _need(ARTIFACT, "implementation artifact")
    _need(NOTES, "implementation notes")
    _need(SOURCE_PLAN, "source WP15J plan artifact")
    _need(SOURCE_PLAN_NOTES, "source WP15J plan notes")
    _need(PREMIUM_PDF, "premium PDF baseline")

    pdf = PREMIUM_PDF.read_bytes()
    if not pdf.startswith(b"%PDF") or len(pdf) <= MIN_PDF_SIZE_BYTES:
        raise ValidationError("premium PDF baseline header/size check failed")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    expected = {
        "schema_version": "etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_implementation_v1",
        "run_id": "20260618_000000",
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15K",
        "legacy_work_package_id": "WP15K",
        "status": "completed",
        "source_work_package": "ETF-EU-WP15J",
        "implementation_decision": "implement_narrow_copy_governance_refinement",
        "implementation_scope": "narrow_copy_governance_refinement",
        "implementation_mode": "copy_governance_contract_artifact_only",
        "source_plan_artifact": str(SOURCE_PLAN),
        "source_plan_notes": str(SOURCE_PLAN_NOTES),
        "premium_pdf_baseline_path": str(PREMIUM_PDF),
        "premium_pdf_baseline_commit": "fb7751026a70db355385946ee3882c68f9ec0e71",
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "ETF-EU-WP15L",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise ValidationError(f"unexpected {key}: {data.get(key)!r}")

    for key in [
        "implementation_created",
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

    if not data.get("refinement_implemented"):
        raise ValidationError("refinement_implemented must not be empty")
    if not data.get("client_facing_copy_contract"):
        raise ValidationError("client_facing_copy_contract must not be empty")
    if not data.get("governance_badge_contract"):
        raise ValidationError("governance_badge_contract must not be empty")
    if data.get("renderer_changed") is True and not data.get("changed_source_paths"):
        raise ValidationError("renderer_changed=true requires changed_source_paths")
    if data.get("new_pdf_created") is True:
        raise ValidationError("new_pdf_created=true is not expected for ETF-EU-WP15K")

    notes = NOTES.read_text(encoding="utf-8")
    for marker in [
        "work_package_id=ETF-EU-WP15K",
        "source_work_package=ETF-EU-WP15J",
        "implementation_created=true",
        "implementation_is_delivery=false",
        "new_pdf_created=false",
        "renderer_changed=false",
        "premium_pdf_replaced=false",
        "production_delivery=false",
        "client_distribution_claimed=false",
        "receipt_artifact_created=false",
        "production_manifest_created=false",
        "ETF-EU-WP15L",
    ]:
        if marker not in notes:
            raise ValidationError(f"notes missing marker: {marker}")

    print(
        "ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_TARGETED_COPY_GOVERNANCE_REFINEMENT_IMPLEMENTATION_OK "
        f"| artifact={ARTIFACT} | selected_next_package=ETF-EU-WP15L"
    )
    return {"status": "valid", "artifact": str(ARTIFACT), "selected_next_package": "ETF-EU-WP15L"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    validate_targeted_refinement_implementation(Path(parser.parse_args().artifact))


if __name__ == "__main__":
    main()
