from __future__ import annotations

import argparse
import json
from pathlib import Path

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_20260618_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_notes_20260618_000000.md")
PREMIUM_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf")
CLOSEOUT_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_closeout_20260618_000000.json")
CLOSEOUT_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_closeout_notes_20260618_000000.md")
PREMIUM_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_notes_20260618_000000.md")
PLAN_MD = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_plan_20260618_000000.md")
MIN_PDF_SIZE_BYTES = 8500

ACCEPTABLE = "acceptable_for_review_checkpoint"
DECISION = "keep_premium_pdf_as_current_review_artifact"


class ReviewCheckpointValidationError(RuntimeError):
    pass


def _require(path: Path, label: str) -> None:
    if not path.exists():
        raise ReviewCheckpointValidationError(f"missing {label}: {path}")


def _require_pdf(path: Path, label: str) -> bytes:
    _require(path, label)
    data = path.read_bytes()
    if not data.startswith(b"%PDF"):
        raise ReviewCheckpointValidationError(f"invalid PDF header for {label}: {path}")
    if len(data) <= MIN_PDF_SIZE_BYTES:
        raise ReviewCheckpointValidationError(f"{label} is too small: {path}")
    return data


def _assert_true(data: dict, key: str) -> None:
    if data.get(key) is not True:
        raise ReviewCheckpointValidationError(f"expected true: {key}")


def _assert_false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        raise ReviewCheckpointValidationError(f"expected false: {key}")


def validate_review_checkpoint(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise ReviewCheckpointValidationError(f"unexpected review checkpoint artifact path: {path}")

    _require(ARTIFACT, "review checkpoint artifact")
    _require(NOTES, "review checkpoint notes")
    _require_pdf(PREMIUM_PDF, "premium PDF")
    for required, label in [
        (CLOSEOUT_ARTIFACT, "WP15G closeout artifact"),
        (CLOSEOUT_NOTES, "WP15G closeout notes"),
        (PREMIUM_NOTES, "WP15F premium notes"),
        (PLAN_MD, "WP15E premium surface plan"),
    ]:
        _require(required, label)

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ReviewCheckpointValidationError("review checkpoint artifact must be a JSON object")

    expected_values = {
        "schema_version": "etf_eu_cockpit_pdf_premium_surface_review_checkpoint_v1",
        "run_id": "20260618_000000",
        "status": "completed",
        "work_package": "WP15H",
        "source_work_package": "WP15G",
        "review_checkpoint_decision": DECISION,
        "review_checkpoint_notes": str(NOTES),
        "review_checkpoint_validator": "tools/validate_etf_eu_cockpit_pdf_premium_surface_review_checkpoint.py",
        "review_checkpoint_tests": "tests/test_etf_eu_cockpit_pdf_premium_surface_review_checkpoint.py",
        "premium_pdf_path": str(PREMIUM_PDF),
        "premium_pdf_commit": "fb7751026a70db355385946ee3882c68f9ec0e71",
        "premium_surface_closeout_artifact": str(CLOSEOUT_ARTIFACT),
        "premium_surface_closeout_notes": str(CLOSEOUT_NOTES),
        "client_readability_status": ACCEPTABLE,
        "governance_clarity_status": ACCEPTABLE,
        "ucits_proxy_separation_status": ACCEPTABLE,
        "validation_traceability_status": ACCEPTABLE,
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "WP15I",
    }
    for key, expected in expected_values.items():
        if data.get(key) != expected:
            raise ReviewCheckpointValidationError(f"unexpected {key}: {data.get(key)!r}")

    _assert_true(data, "review_checkpoint_created")
    _assert_true(data, "review_only")

    for key in [
        "new_pdf_created",
        "renderer_changed",
        "premium_pdf_replaced",
        "production_delivery",
        "portfolio_mutation",
        "candidate_promotion",
        "funding_authority",
        "valuation_grade",
        "outbound_path_enabled",
        "live_data_fetch_performed",
        "pricing_evidence_changed",
        "recommendation_logic_changed",
        "client_distribution_claimed",
        "receipt_artifact_created",
        "production_manifest_created",
    ]:
        _assert_false(data, key)

    notes = NOTES.read_text(encoding="utf-8")
    for marker in [
        "work_package=WP15H",
        "review_checkpoint_decision=keep_premium_pdf_as_current_review_artifact",
        "client_readability_status=acceptable_for_review_checkpoint",
        "governance_clarity_status=acceptable_for_review_checkpoint",
        "ucits_proxy_separation_status=acceptable_for_review_checkpoint",
        "validation_traceability_status=acceptable_for_review_checkpoint",
        "production_delivery=false",
        "portfolio_mutation=false",
        "candidate_promotion=false",
        "funding_authority=false",
        "valuation_grade=false",
        "WP15I",
    ]:
        if marker not in notes:
            raise ReviewCheckpointValidationError(f"review checkpoint notes missing marker: {marker}")

    print(f"ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_REVIEW_CHECKPOINT_OK | artifact={ARTIFACT} | selected_next_package=WP15I")
    return {"status": "valid", "artifact": str(ARTIFACT), "selected_next_package": "WP15I"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_review_checkpoint(Path(args.artifact))


if __name__ == "__main__":
    main()
