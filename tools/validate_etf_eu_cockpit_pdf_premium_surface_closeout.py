from __future__ import annotations

import argparse
import json
from pathlib import Path

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_closeout_20260618_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_closeout_notes_20260618_000000.md")
PREMIUM_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf")
ORIGINAL_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf")
LAYOUT_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_mvp_layout_20260618_000000.pdf")
PLAN_MD = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_plan_20260618_000000.md")
PLAN_JSON = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_plan_20260618_000000.json")
PREMIUM_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_notes_20260618_000000.md")
RENDERER = Path("tools/render_etf_eu_cockpit_pdf_premium_surface.py")
PREMIUM_VALIDATOR = Path("tools/validate_etf_eu_cockpit_pdf_premium_surface.py")
PREMIUM_TESTS = Path("tests/test_etf_eu_cockpit_pdf_premium_surface.py")
MIN_PDF_SIZE_BYTES = 8500


class PremiumSurfaceCloseoutValidationError(RuntimeError):
    pass


def _require(path: Path, label: str) -> None:
    if not path.exists():
        raise PremiumSurfaceCloseoutValidationError(f"missing {label}: {path}")


def _require_pdf(path: Path, label: str) -> bytes:
    _require(path, label)
    data = path.read_bytes()
    if not data.startswith(b"%PDF"):
        raise PremiumSurfaceCloseoutValidationError(f"invalid PDF header for {label}: {path}")
    return data


def _assert_true(data: dict, key: str) -> None:
    if data.get(key) is not True:
        raise PremiumSurfaceCloseoutValidationError(f"expected true: {key}")


def _assert_false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        raise PremiumSurfaceCloseoutValidationError(f"expected false: {key}")


def validate_premium_surface_closeout(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise PremiumSurfaceCloseoutValidationError(f"unexpected closeout artifact path: {path}")

    _require(ARTIFACT, "premium surface closeout artifact")
    _require(NOTES, "premium surface closeout notes")
    premium_bytes = _require_pdf(PREMIUM_PDF, "premium PDF")
    if len(premium_bytes) <= MIN_PDF_SIZE_BYTES:
        raise PremiumSurfaceCloseoutValidationError("premium PDF is too small")
    _require_pdf(ORIGINAL_PDF, "original WP15A PDF")
    _require_pdf(LAYOUT_PDF, "WP15C layout PDF")
    for required, label in [
        (PLAN_MD, "WP15E premium surface plan"),
        (PLAN_JSON, "WP15E premium surface JSON plan"),
        (PREMIUM_NOTES, "WP15F premium notes"),
        (RENDERER, "WP15F premium renderer"),
        (PREMIUM_VALIDATOR, "WP15F premium validator"),
        (PREMIUM_TESTS, "WP15F premium tests"),
    ]:
        _require(required, label)

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise PremiumSurfaceCloseoutValidationError("closeout artifact must be a JSON object")

    expected_values = {
        "schema_version": "etf_eu_cockpit_pdf_premium_surface_closeout_v1",
        "run_id": "20260618_000000",
        "status": "completed",
        "work_package": "WP15G",
        "source_work_package": "WP15F",
        "premium_pdf_path": str(PREMIUM_PDF),
        "premium_pdf_commit": "fb7751026a70db355385946ee3882c68f9ec0e71",
        "premium_pdf_renderer": str(RENDERER),
        "premium_pdf_validator": str(PREMIUM_VALIDATOR),
        "premium_pdf_tests": str(PREMIUM_TESTS),
        "premium_pdf_notes": str(PREMIUM_NOTES),
        "original_pdf_mvp_path": str(ORIGINAL_PDF),
        "layout_pdf_path": str(LAYOUT_PDF),
        "premium_surface_plan_path": str(PLAN_MD),
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "WP15H",
    }
    for key, expected in expected_values.items():
        if data.get(key) != expected:
            raise PremiumSurfaceCloseoutValidationError(f"unexpected {key}: {data.get(key)!r}")

    for key in [
        "premium_pdf_surface_created",
        "premium_pdf_committed",
        "original_pdf_mvp_preserved",
        "layout_pdf_preserved",
        "premium_surface_plan_preserved",
        "closeout_only",
    ]:
        _assert_true(data, key)

    for key in [
        "new_pdf_created",
        "renderer_changed",
        "production_delivery",
        "portfolio_mutation",
        "candidate_promotion",
        "funding_authority",
        "valuation_grade",
        "outbound_path_enabled",
        "live_data_fetch_performed",
        "pricing_evidence_changed",
        "recommendation_logic_changed",
        "receipt_artifact_created",
        "production_manifest_created",
        "client_distribution_claimed",
    ]:
        _assert_false(data, key)

    notes = NOTES.read_text(encoding="utf-8")
    for marker in [
        "work_package=WP15G",
        "premium_pdf_commit=fb7751026a70db355385946ee3882c68f9ec0e71",
        "original_pdf_mvp_preserved=true",
        "layout_pdf_preserved=true",
        "premium_surface_plan_preserved=true",
        "delivery_authorization_decision=remain_blocked",
        "production_delivery=false",
        "portfolio_mutation=false",
        "candidate_promotion=false",
        "funding_authority=false",
        "valuation_grade=false",
        "WP15H",
    ]:
        if marker not in notes:
            raise PremiumSurfaceCloseoutValidationError(f"closeout notes missing marker: {marker}")

    print(f"ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_CLOSEOUT_OK | artifact={ARTIFACT} | selected_next_package=WP15H")
    return {"status": "valid", "artifact": str(ARTIFACT), "selected_next_package": "WP15H"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_premium_surface_closeout(Path(args.artifact))


if __name__ == "__main__":
    main()
