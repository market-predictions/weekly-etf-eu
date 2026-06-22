from __future__ import annotations

import argparse
import json
from pathlib import Path

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_improvement_decision_20260618_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_improvement_decision_notes_20260618_000000.md")
PREMIUM_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf")
REVIEW_CHECKPOINT_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_20260618_000000.json")
REVIEW_CHECKPOINT_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_notes_20260618_000000.md")
CLOSEOUT_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_closeout_20260618_000000.json")
PREMIUM_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_notes_20260618_000000.md")
PLAN_MD = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_plan_20260618_000000.md")

DECISION = "targeted_copy_governance_refinement_before_delivery_preflight"
SELECTED_NEXT_PACKAGE = "WP15J"
MIN_PDF_SIZE_BYTES = 8500


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


def _load_json(path: Path) -> dict:
    _require(path, "JSON artifact")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ImprovementDecisionValidationError(f"expected JSON object: {path}")
    return data


def _assert_true(data: dict, key: str) -> None:
    if data.get(key) is not True:
        raise ImprovementDecisionValidationError(f"expected true: {key}")


def _assert_false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        raise ImprovementDecisionValidationError(f"expected false: {key}")


def validate_improvement_decision(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise ImprovementDecisionValidationError(f"unexpected improvement decision artifact path: {path}")

    _require(ARTIFACT, "WP15I decision artifact")
    _require(NOTES, "WP15I decision notes")
    _require_pdf(PREMIUM_PDF, "premium PDF")

    for required, label in [
        (REVIEW_CHECKPOINT_ARTIFACT, "WP15H review checkpoint artifact"),
        (REVIEW_CHECKPOINT_NOTES, "WP15H review checkpoint notes"),
        (CLOSEOUT_ARTIFACT, "WP15G closeout artifact"),
        (PREMIUM_NOTES, "WP15F premium notes"),
        (PLAN_MD, "WP15E premium surface plan"),
    ]:
        _require(required, label)

    data = _load_json(ARTIFACT)
    review_checkpoint = _load_json(REVIEW_CHECKPOINT_ARTIFACT)

    expected_values = {
        "schema_version": "etf_eu_cockpit_pdf_premium_surface_improvement_decision_v1",
        "run_id": "20260618_000000",
        "status": "completed",
        "work_package": "WP15I",
        "source_work_package": "WP15H",
        "reviewed_pdf_path": str(PREMIUM_PDF),
        "reviewed_pdf_commit": "fb7751026a70db355385946ee3882c68f9ec0e71",
        "source_review_checkpoint_artifact": str(REVIEW_CHECKPOINT_ARTIFACT),
        "source_review_checkpoint_notes": str(REVIEW_CHECKPOINT_NOTES),
        "decision_artifact_notes": str(NOTES),
        "decision_validator": "tools/validate_etf_eu_cockpit_pdf_premium_surface_improvement_decision.py",
        "decision_tests": "tests/test_etf_eu_cockpit_pdf_premium_surface_improvement_decision.py",
        "decision": DECISION,
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": SELECTED_NEXT_PACKAGE,
        "selected_next_package_title": "ETF EU cockpit PDF premium surface targeted copy/governance refinement plan, no delivery",
    }
    for key, expected in expected_values.items():
        if data.get(key) != expected:
            raise ImprovementDecisionValidationError(f"unexpected {key}: {data.get(key)!r}")

    _assert_true(data, "decision_questions_answered")
    _assert_true(data, "keep_as_current_review_artifact")
    _assert_true(data, "targeted_improvement_needed")

    for key in [
        "delivery_preflight_allowed",
        "production_delivery",
        "portfolio_mutation",
        "candidate_promotion",
        "funding_authority",
        "valuation_grade",
        "live_data_fetch_performed",
        "recommendation_logic_changed",
        "renderer_changed",
        "new_pdf_created",
        "premium_pdf_replaced",
        "outbound_path_enabled",
        "receipt_artifact_created",
        "production_manifest_created",
        "client_distribution_claimed",
    ]:
        _assert_false(data, key)

    if review_checkpoint.get("work_package") != "WP15H":
        raise ImprovementDecisionValidationError("source review checkpoint must be WP15H")
    if review_checkpoint.get("selected_next_package") != "WP15I":
        raise ImprovementDecisionValidationError("source review checkpoint must select WP15I")
    if review_checkpoint.get("review_checkpoint_decision") != "keep_premium_pdf_as_current_review_artifact":
        raise ImprovementDecisionValidationError("source review checkpoint decision mismatch")
    if review_checkpoint.get("premium_pdf_path") != str(PREMIUM_PDF):
        raise ImprovementDecisionValidationError("review checkpoint premium PDF path mismatch")

    for key in [
        "production_delivery",
        "portfolio_mutation",
        "candidate_promotion",
        "funding_authority",
        "valuation_grade",
        "new_pdf_created",
        "renderer_changed",
        "premium_pdf_replaced",
        "outbound_path_enabled",
        "client_distribution_claimed",
        "receipt_artifact_created",
        "production_manifest_created",
    ]:
        if review_checkpoint.get(key) is not False:
            raise ImprovementDecisionValidationError(f"source review checkpoint boundary mismatch: {key}")

    notes = NOTES.read_text(encoding="utf-8")
    for marker in [
        "work_package=WP15I",
        f"decision={DECISION}",
        "keep_as_current_review_artifact=true",
        "targeted_improvement_needed=true",
        "delivery_preflight_allowed=false",
        "selected_next_package=WP15J",
        "production_delivery=false",
        "portfolio_mutation=false",
        "candidate_promotion=false",
        "funding_authority=false",
        "valuation_grade=false",
        "renderer_changed=false",
        "new_pdf_created=false",
        "premium_pdf_replaced=false",
        "delivery_authorization_decision=remain_blocked",
    ]:
        if marker not in notes:
            raise ImprovementDecisionValidationError(f"decision notes missing marker: {marker}")

    print(
        "ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_IMPROVEMENT_DECISION_OK "
        f"| artifact={ARTIFACT} | selected_next_package={SELECTED_NEXT_PACKAGE}"
    )
    return {"status": "valid", "artifact": str(ARTIFACT), "selected_next_package": SELECTED_NEXT_PACKAGE}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_improvement_decision(Path(args.artifact))


if __name__ == "__main__":
    main()
