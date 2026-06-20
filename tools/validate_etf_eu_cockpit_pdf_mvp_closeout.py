from __future__ import annotations

import argparse
import json
from pathlib import Path

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_mvp_closeout_20260618_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_mvp_review_notes_20260618_000000.md")
PDF = Path("output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf")
RENDERER = Path("tools/render_etf_eu_cockpit_pdf_mvp.py")
PDF_VALIDATOR = Path("tools/validate_etf_eu_cockpit_pdf_mvp.py")
PDF_TESTS = Path("tests/test_etf_eu_cockpit_pdf_mvp.py")
EXPECTED_COMMIT = "ce0146326d3235687aabd23d5e728b3ee34a8fe5"
MIN_PDF_SIZE_BYTES = 2500


class PdfMvpCloseoutValidationError(RuntimeError):
    pass


def _require(path: Path, label: str) -> None:
    if not path.exists():
        raise PdfMvpCloseoutValidationError(f"missing {label}: {path}")


def _load_artifact(path: Path) -> dict:
    _require(path, "closeout artifact")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise PdfMvpCloseoutValidationError("closeout artifact must be a JSON object")
    return data


def _assert_false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        raise PdfMvpCloseoutValidationError(f"expected false: {key}")


def _assert_true(data: dict, key: str) -> None:
    if data.get(key) is not True:
        raise PdfMvpCloseoutValidationError(f"expected true: {key}")


def validate_closeout(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise PdfMvpCloseoutValidationError(f"unexpected artifact path: {path}")

    data = _load_artifact(path)
    _require(NOTES, "review notes")
    _require(PDF, "committed PDF MVP")
    _require(RENDERER, "PDF MVP renderer")
    _require(PDF_VALIDATOR, "PDF MVP validator")
    _require(PDF_TESTS, "PDF MVP tests")

    pdf_bytes = PDF.read_bytes()
    if not pdf_bytes.startswith(b"%PDF"):
        raise PdfMvpCloseoutValidationError("PDF header missing")
    if len(pdf_bytes) <= MIN_PDF_SIZE_BYTES:
        raise PdfMvpCloseoutValidationError("PDF is too small")

    expected_values = {
        "schema_version": "etf_eu_cockpit_pdf_mvp_closeout_v1",
        "run_id": "20260618_000000",
        "status": "completed",
        "work_package": "WP15B",
        "source_work_package": "WP15A",
        "pdf_mvp_path": str(PDF),
        "pdf_mvp_commit": EXPECTED_COMMIT,
        "renderer_path": str(RENDERER),
        "validator_path": str(PDF_VALIDATOR),
        "test_path": str(PDF_TESTS),
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "WP15C",
        "selected_next_package_title": "ETF EU cockpit PDF MVP layout and readability iteration, no delivery",
    }
    for key, expected in expected_values.items():
        if data.get(key) != expected:
            raise PdfMvpCloseoutValidationError(f"unexpected {key}: {data.get(key)!r}")

    for key in [
        "pdf_mvp_created",
        "pdf_mvp_committed",
        "proof_of_concept_pdf_mvp",
        "no_email_send",
        "no_delivery_receipt_created",
        "no_recipient_config_changed",
        "no_secrets_changed",
        "no_live_data_fetch",
        "no_pricing_evidence_update",
        "no_recommendation_logic_change",
    ]:
        _assert_true(data, key)

    for key in [
        "production_delivery",
        "portfolio_mutation",
        "candidate_promotion",
        "funding_authority",
        "valuation_grade",
    ]:
        _assert_false(data, key)

    print(f"ETF_EU_COCKPIT_PDF_MVP_CLOSEOUT_OK | artifact={ARTIFACT} | selected_next_package=WP15C")
    return {"status": "valid", "artifact": str(ARTIFACT), "selected_next_package": "WP15C"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_closeout(Path(args.artifact))


if __name__ == "__main__":
    main()
