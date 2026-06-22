from __future__ import annotations

import argparse
import json
from pathlib import Path

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_improvement_decision_20260618_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_improvement_decision_notes_20260618_000000.md")
PREMIUM_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf")
REVIEW_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_20260618_000000.json")
REVIEW_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_notes_20260618_000000.md")
CLOSEOUT_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_closeout_20260618_000000.json")
MIN_PDF_SIZE_BYTES = 8500

REPOSITORY = "market-predictions/weekly-etf-eu"
WORK_PACKAGE_ID = "ETF-EU-WP15I-RECONCILE"
LEGACY_WORK_PACKAGE_ID = "WP15I"
CREATE_TARGETED = "create_targeted_improvement_package"
TARGETED_PACKAGE = "ETF-EU-WP15J"
DECISION = "targeted_copy_governance_refinement_before_delivery_preflight"


class ImprovementDecisionValidationError(RuntimeError):
    pass


def _require(path: Path, label: str) -> None:
    if not path.exists():
        raise ImprovementDecisionValidationError(f"missing {label}: {path}")


def _require_pdf(path: Path, label: str) -> bytes:
    _require(path, label)
    data = path.read_bytes()
    if not data.startswith(b"%PDF"):
        raise ImprovementDecisionValidationError(f"invalid PDF header for {label}: {path}")
    if len(data) <= MIN_PDF_SIZE_BYTES:
        raise ImprovementDecisionValidationError(f"{label} is too small: {path}")
    return data


def _assert_false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        raise ImprovementDecisionValidationError(f"expected false: {key}")


def _assert_true(data: dict, key: str) -> None:
    if data.get(key) is not True:
        raise ImprovementDecisionValidationError(f"expected true: {key}")


def validate_improvement_decision(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise ImprovementDecisionValidationError(f"unexpected decision artifact path: {path}")

    _require(ARTIFACT, "improvement decision artifact")
    _require(NOTES, "improvement decision notes")
    _require_pdf(PREMIUM_PDF, "premium PDF")
    for required, label in [
        (REVIEW_ARTIFACT, "WP15H review checkpoint artifact"),
        (REVIEW_NOTES, "WP15H review checkpoint notes"),
        (CLOSEOUT_ARTIFACT, "WP15G closeout artifact"),
    ]:
        _require(required, label)

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ImprovementDecisionValidationError("decision artifact must be a JSON object")

    expected_values = {
        "schema_version": "etf_eu_cockpit_pdf_premium_surface_improvement_decision_v1",
        "run_id": "20260618_000000",
        "repository": REPOSITORY,
        "work_package_id": WORK_PACKAGE_ID,
        "legacy_work_package_id": LEGACY_WORK_PACKAGE_ID,
        "status": "completed",
        "work_package": "WP15I",
        "source_work_package": "WP15H",
        "reconciles_work_package": "ETF-EU-WP15I",
        "improvement_decision": CREATE_TARGETED,
        "decision": DECISION,
        "premium_pdf_path": str(PREMIUM_PDF),
        "premium_pdf_commit": "fb7751026a70db355385946ee3882c68f9ec0e71",
        "review_checkpoint_artifact": str(REVIEW_ARTIFACT),
        "review_checkpoint_notes": str(REVIEW_NOTES),
        "premium_surface_closeout_artifact": str(CLOSEOUT_ARTIFACT),
        "delivery_authorization_decision": "remain_blocked",
        "targeted_improvement_package": TARGETED_PACKAGE,
        "selected_next_package": TARGETED_PACKAGE,
        "selected_next_package_title": "ETF EU cockpit PDF premium surface targeted copy/governance refinement plan, no delivery",
    }
    for key, expected in expected_values.items():
        if data.get(key) != expected:
            raise ImprovementDecisionValidationError(f"unexpected {key}: {data.get(key)!r}")

    for key in [
        "improvement_decision_created",
        "keep_as_current_review_artifact",
        "targeted_improvement_needed",
        "targeted_improvement_package_required",
    ]:
        _assert_true(data, key)

    if not data.get("recommended_improvement_scope"):
        raise ImprovementDecisionValidationError("recommended_improvement_scope must not be empty")
    if not data.get("rejected_scopes"):
        raise ImprovementDecisionValidationError("rejected_scopes must not be empty")

    for key in [
        "delivery_preflight_allowed",
        "production_delivery",
        "portfolio_mutation",
        "candidate_promotion",
        "funding_authority",
        "valuation_grade",
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
        _assert_false(data, key)

    notes = NOTES.read_text(encoding="utf-8")
    for marker in [
        "repository=market-predictions/weekly-etf-eu",
        "work_package_id=ETF-EU-WP15I-RECONCILE",
        "legacy_work_package_id=WP15I",
        "improvement_decision=create_targeted_improvement_package",
        "decision=targeted_copy_governance_refinement_before_delivery_preflight",
        "keep_as_current_review_artifact=true",
        "targeted_improvement_needed=true",
        "targeted_improvement_package_required=true",
        "targeted_improvement_package=ETF-EU-WP15J",
        "delivery_preflight_allowed=false",
        "production_delivery=false",
        "portfolio_mutation=false",
        "candidate_promotion=false",
        "funding_authority=false",
        "valuation_grade=false",
        "new_pdf_created=false",
        "renderer_changed=false",
        "premium_pdf_replaced=false",
        "ETF-EU-WP15J",
    ]:
        if marker not in notes:
            raise ImprovementDecisionValidationError(f"decision notes missing marker: {marker}")

    print(
        "ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_IMPROVEMENT_DECISION_OK "
        f"| artifact={ARTIFACT} | selected_next_package={TARGETED_PACKAGE}"
    )
    return {"status": "valid", "artifact": str(ARTIFACT), "selected_next_package": TARGETED_PACKAGE}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_improvement_decision(Path(args.artifact))


if __name__ == "__main__":
    main()
