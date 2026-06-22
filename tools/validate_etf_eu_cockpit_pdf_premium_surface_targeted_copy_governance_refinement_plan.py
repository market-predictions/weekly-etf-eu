from __future__ import annotations

import argparse
import json
from pathlib import Path

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_plan_20260618_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_plan_notes_20260618_000000.md")
PREMIUM_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf")
SOURCE_DECISION = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_improvement_decision_20260618_000000.json")
MIN_PDF_SIZE_BYTES = 8500


class ValidationError(RuntimeError):
    pass


def _need(path: Path, label: str) -> None:
    if not path.exists():
        raise ValidationError(f"missing {label}: {path}")


def _false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        raise ValidationError(f"expected false: {key}")


def _true(data: dict, key: str) -> None:
    if data.get(key) is not True:
        raise ValidationError(f"expected true: {key}")


def validate_targeted_refinement_plan(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise ValidationError(f"unexpected plan artifact path: {path}")
    _need(ARTIFACT, "plan artifact")
    _need(NOTES, "plan notes")
    _need(SOURCE_DECISION, "source decision artifact")
    _need(PREMIUM_PDF, "premium PDF")
    pdf = PREMIUM_PDF.read_bytes()
    if not pdf.startswith(b"%PDF") or len(pdf) <= MIN_PDF_SIZE_BYTES:
        raise ValidationError("premium PDF header/size check failed")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    expected = {
        "schema_version": "etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_plan_v1",
        "run_id": "20260618_000000",
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15J",
        "legacy_work_package_id": "WP15J",
        "status": "completed",
        "source_work_package": "ETF-EU-WP15I-RECONCILE",
        "targeted_refinement_plan_decision": "plan_future_copy_governance_refinement",
        "premium_pdf_path": str(PREMIUM_PDF),
        "premium_pdf_commit": "fb7751026a70db355385946ee3882c68f9ec0e71",
        "improvement_decision_artifact": str(SOURCE_DECISION),
        "improvement_decision": "create_targeted_improvement_package",
        "targeted_improvement_package": "ETF-EU-WP15J",
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "ETF-EU-WP15K",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise ValidationError(f"unexpected {key}: {data.get(key)!r}")

    for key in [
        "targeted_refinement_plan_created",
        "premium_pdf_preserved",
        "keep_as_current_review_artifact",
        "targeted_improvement_needed",
        "targeted_improvement_package_required",
    ]:
        _true(data, key)

    for key in [
        "implementation_in_this_package",
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
        "new_pdf_created",
        "renderer_changed",
        "premium_pdf_replaced",
        "client_distribution_claimed",
        "receipt_artifact_created",
        "production_manifest_created",
    ]:
        _false(data, key)

    if not data.get("refinement_scope"):
        raise ValidationError("refinement_scope must not be empty")
    if not data.get("out_of_scope"):
        raise ValidationError("out_of_scope must not be empty")

    notes = NOTES.read_text(encoding="utf-8")
    for marker in [
        "work_package_id=ETF-EU-WP15J",
        "source_work_package=ETF-EU-WP15I-RECONCILE",
        "targeted_refinement_plan_created=true",
        "implementation_in_this_package=false",
        "premium_pdf_preserved=true",
        "targeted_improvement_package=ETF-EU-WP15J",
        "delivery_preflight_allowed=false",
        "new_pdf_created=false",
        "renderer_changed=false",
        "premium_pdf_replaced=false",
        "ETF-EU-WP15K",
    ]:
        if marker not in notes:
            raise ValidationError(f"notes missing marker: {marker}")

    print(
        "ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_TARGETED_COPY_GOVERNANCE_REFINEMENT_PLAN_OK "
        f"| artifact={ARTIFACT} | selected_next_package=ETF-EU-WP15K"
    )
    return {"status": "valid", "artifact": str(ARTIFACT), "selected_next_package": "ETF-EU-WP15K"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    validate_targeted_refinement_plan(Path(parser.parse_args().artifact))


if __name__ == "__main__":
    main()
