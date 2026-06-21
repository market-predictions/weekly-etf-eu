from __future__ import annotations

import argparse
from pathlib import Path

LAYOUT_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_mvp_layout_20260618_000000.pdf")
ORIGINAL_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_mvp_layout_notes_20260618_000000.md")
RENDERER = Path("tools/render_etf_eu_cockpit_pdf_mvp_layout.py")
VALIDATOR = Path("tools/validate_etf_eu_cockpit_pdf_mvp_layout.py")
TESTS = Path("tests/test_etf_eu_cockpit_pdf_mvp_layout.py")
MIN_SIZE_BYTES = 4000

REQUIRED_PDF_MARKERS = [
    b"ETF EU Cockpit",
    b"proof-of-concept",
    b"review-only",
    b"delivery_authorization_decision=remain_blocked",
    b"production_delivery=false",
    b"portfolio_mutation=false",
    b"candidate_promotion=false",
    b"funding_authority=false",
    b"valuation_grade=false",
    b"IE00B5BMR087",
    b"CSPX.L",
    b"SXR8.DE",
    b"usable_for_review_only",
    b"pricing_symbol_ambiguous",
    b"policy_blocked",
    b"identity_incomplete",
    b"SPY=research_proxy_only",
    b"SMH=research_proxy_only_and_ambiguous_as_pricing_symbol",
    b"GLD=research_proxy_only_not_eu_holding",
    b"PAVE=research_proxy_only_not_eu_holding",
    b"selected_next_package=WP15D",
]

REQUIRED_NOTE_MARKERS = [
    "WP15C",
    "selected_next_package=WP15D",
    "delivery_authorization_decision=remain_blocked",
    "production_delivery=false",
    "portfolio_mutation=false",
    "candidate_promotion=false",
    "funding_authority=false",
    "valuation_grade=false",
]


class PdfMvpLayoutValidationError(RuntimeError):
    pass


def _require(path: Path, label: str) -> None:
    if not path.exists():
        raise PdfMvpLayoutValidationError(f"missing {label}: {path}")


def validate_layout_pdf(path: Path) -> dict[str, str]:
    if path != LAYOUT_PDF:
        raise PdfMvpLayoutValidationError(f"unexpected layout pdf path: {path}")
    _require(LAYOUT_PDF, "layout PDF")
    _require(ORIGINAL_PDF, "original WP15A PDF")
    _require(NOTES, "layout notes")
    _require(RENDERER, "layout renderer")
    _require(VALIDATOR, "layout validator")
    _require(TESTS, "layout tests")

    pdf_bytes = LAYOUT_PDF.read_bytes()
    if not pdf_bytes.startswith(b"%PDF"):
        raise PdfMvpLayoutValidationError("layout PDF header missing")
    if len(pdf_bytes) <= MIN_SIZE_BYTES:
        raise PdfMvpLayoutValidationError("layout PDF is too small")
    for marker in REQUIRED_PDF_MARKERS:
        if marker not in pdf_bytes:
            raise PdfMvpLayoutValidationError(f"layout PDF missing marker: {marker.decode('ascii')}")

    notes = NOTES.read_text(encoding="utf-8")
    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in notes:
            raise PdfMvpLayoutValidationError(f"layout notes missing marker: {marker}")

    print(f"ETF_EU_COCKPIT_PDF_MVP_LAYOUT_OK | pdf={LAYOUT_PDF} | selected_next_package=WP15D")
    return {"status": "valid", "pdf": str(LAYOUT_PDF), "selected_next_package": "WP15D"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    args = parser.parse_args()
    validate_layout_pdf(Path(args.pdf))


if __name__ == "__main__":
    main()
