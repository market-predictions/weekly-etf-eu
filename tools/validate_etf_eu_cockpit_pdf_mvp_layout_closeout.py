from __future__ import annotations

import argparse
import json
from pathlib import Path

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_mvp_layout_closeout_20260618_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_mvp_layout_closeout_notes_20260618_000000.md")
ORIGINAL_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf")
LAYOUT_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_mvp_layout_20260618_000000.pdf")
LAYOUT_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_mvp_layout_notes_20260618_000000.md")
LAYOUT_RENDERER = Path("tools/render_etf_eu_cockpit_pdf_mvp_layout.py")
LAYOUT_VALIDATOR = Path("tools/validate_etf_eu_cockpit_pdf_mvp_layout.py")
LAYOUT_TESTS = Path("tests/test_etf_eu_cockpit_pdf_mvp_layout.py")
MIN_LAYOUT_PDF_SIZE_BYTES = 4000


class LayoutCloseoutValidationError(RuntimeError):
    pass


def _require(path: Path, label: str) -> None:
    if not path.exists():
        raise LayoutCloseoutValidationError(f"missing {label}: {path}")


def _load_artifact(path: Path) -> dict:
    _require(path, "layout closeout artifact")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise LayoutCloseoutValidationError("layout closeout artifact must be a JSON object")
    return data


def _assert_true(data: dict, key: str) -> None:
    if data.get(key) is not True:
        raise LayoutCloseoutValidationError(f"expected true: {key}")


def _assert_false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        raise LayoutCloseoutValidationError(f"expected false: {key}")


def validate_layout_closeout(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise LayoutCloseoutValidationError(f"unexpected artifact path: {path}")

    data = _load_artifact(path)
    _require(NOTES, "layout closeout notes")
    _require(ORIGINAL_PDF, "original WP15A PDF")
    _require(LAYOUT_PDF, "improved WP15C layout PDF")
    _require(LAYOUT_NOTES, "layout notes")
    _require(LAYOUT_RENDERER, "layout renderer")
    _require(LAYOUT_VALIDATOR, "layout validator")
    _require(LAYOUT_TESTS, "layout tests")

    if not ORIGINAL_PDF.read_bytes().startswith(b"%PDF"):
        raise LayoutCloseoutValidationError("original PDF header missing")
    layout_bytes = LAYOUT_PDF.read_bytes()
    if not layout_bytes.startswith(b"%PDF"):
        raise LayoutCloseoutValidationError("layout PDF header missing")
    if len(layout_bytes) <= MIN_LAYOUT_PDF_SIZE_BYTES:
        raise LayoutCloseoutValidationError("layout PDF is too small")

    expected_values = {
        "schema_version": "etf_eu_cockpit_pdf_mvp_layout_closeout_v1",
        "run_id": "20260618_000000",
        "status": "completed",
        "work_package": "WP15D",
        "source_work_package": "WP15C",
        "original_pdf_mvp_path": str(ORIGINAL_PDF),
        "original_pdf_mvp_commit": "ce0146326d3235687aabd23d5e728b3ee34a8fe5",
        "layout_pdf_path": str(LAYOUT_PDF),
        "layout_pdf_commit": "651de79f11ded4285ca57938cfdf38d46b02e5bf",
        "layout_renderer_path": str(LAYOUT_RENDERER),
        "layout_validator_path": str(LAYOUT_VALIDATOR),
        "layout_test_path": str(LAYOUT_TESTS),
        "layout_notes_path": str(LAYOUT_NOTES),
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "WP15E",
        "selected_next_package_title": "ETF EU cockpit PDF MVP premium surface planning, no delivery",
    }
    for key, expected in expected_values.items():
        if data.get(key) != expected:
            raise LayoutCloseoutValidationError(f"unexpected {key}: {data.get(key)!r}")

    for key in ["original_pdf_mvp_preserved", "layout_pdf_created", "layout_pdf_committed", "proof_of_concept_pdf_mvp", "layout_improvements_confirmed"]:
        _assert_true(data, key)

    for key in [
        "production_delivery",
        "portfolio_mutation",
        "candidate_promotion",
        "funding_authority",
        "valuation_grade",
        "outbound_path_enabled",
        "receipt_artifact_created",
        "recipient_configuration_changed",
        "credential_configuration_changed",
        "live_data_fetch_performed",
        "pricing_evidence_changed",
        "recommendation_logic_changed",
    ]:
        _assert_false(data, key)

    improvements = data.get("layout_improvements")
    if not isinstance(improvements, list) or len(improvements) < 5:
        raise LayoutCloseoutValidationError("layout improvements not sufficiently recorded")

    print(f"ETF_EU_COCKPIT_PDF_MVP_LAYOUT_CLOSEOUT_OK | artifact={ARTIFACT} | selected_next_package=WP15E")
    return {"status": "valid", "artifact": str(ARTIFACT), "selected_next_package": "WP15E"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_layout_closeout(Path(args.artifact))


if __name__ == "__main__":
    main()
