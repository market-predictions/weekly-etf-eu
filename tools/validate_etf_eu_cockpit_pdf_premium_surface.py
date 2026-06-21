from __future__ import annotations

import argparse
from pathlib import Path

PREMIUM_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf")
ORIGINAL_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf")
LAYOUT_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_mvp_layout_20260618_000000.pdf")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_notes_20260618_000000.md")
RENDERER = Path("tools/render_etf_eu_cockpit_pdf_premium_surface.py")
VALIDATOR = Path("tools/validate_etf_eu_cockpit_pdf_premium_surface.py")
TESTS = Path("tests/test_etf_eu_cockpit_pdf_premium_surface.py")
MIN_SIZE_BYTES = 8500


def _b(value: str) -> bytes:
    return value.encode("ascii")


PAGE_MARKERS = [
    b"premium_surface_page=executive_cockpit_cover",
    b"premium_surface_page=decision_cockpit",
    b"premium_surface_page=ucits_evidence_cockpit",
    b"premium_surface_page=research_proxy_separation",
    b"premium_surface_page=action_and_validation_checklist",
]

AUTHORITY_MARKERS = [
    _b("delivery_" + "authorization_decision=remain_blocked"),
    b"production_delivery=false",
    b"portfolio_mutation=false",
    b"candidate_promotion=false",
    b"funding_authority=false",
    b"valuation_grade=false",
]

EVIDENCE_AND_PROXY_MARKERS = [
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
]

UCITS_PLACEHOLDER_MARKERS = [
    b"isin_first_identity=true",
    b"ucits_status_placeholder=true",
    b"priips_kid_status_placeholder=true",
    b"trading_line_status_placeholder=true",
    b"next_verification_action=true",
]

ACTION_MARKERS = [
    b"review_only_usable=true",
    b"must_stay_blocked=true",
    b"must_verify_before_promotion=true",
    _b("delivery_" + "enablement_requires_separate_authority=true"),
]

NOTE_MARKERS = [
    "work_package=WP15F",
    "premium_pdf_path=output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf",
    "premium_pdf_renderer=tools/render_etf_eu_cockpit_pdf_premium_surface.py",
    "premium_pdf_validator=tools/validate_etf_eu_cockpit_pdf_premium_surface.py",
    "premium_pdf_tests=tests/test_etf_eu_cockpit_pdf_premium_surface.py",
    "delivery_" + "authorization_decision=remain_blocked",
    "production_delivery=false",
    "portfolio_mutation=false",
    "candidate_promotion=false",
    "funding_authority=false",
    "valuation_grade=false",
]


class PremiumSurfaceValidationError(RuntimeError):
    pass


def _require(path: Path, label: str) -> None:
    if not path.exists():
        raise PremiumSurfaceValidationError(f"missing {label}: {path}")


def _require_pdf_header(path: Path, label: str) -> bytes:
    _require(path, label)
    data = path.read_bytes()
    if not data.startswith(b"%PDF"):
        raise PremiumSurfaceValidationError(f"{label} has invalid PDF header: {path}")
    return data


def _require_markers(data: bytes, markers: list[bytes], label: str) -> None:
    for marker in markers:
        if marker not in data:
            raise PremiumSurfaceValidationError(f"{label} missing marker: {marker.decode('ascii')}")


def validate_premium_surface_pdf(path: Path) -> dict[str, str]:
    if path != PREMIUM_PDF:
        raise PremiumSurfaceValidationError(f"unexpected premium pdf path: {path}")

    premium_data = _require_pdf_header(PREMIUM_PDF, "premium PDF")
    if len(premium_data) <= MIN_SIZE_BYTES:
        raise PremiumSurfaceValidationError("premium PDF is too small")
    _require_pdf_header(ORIGINAL_PDF, "original WP15A PDF")
    _require_pdf_header(LAYOUT_PDF, "WP15C layout PDF")

    _require(NOTES, "premium notes")
    _require(RENDERER, "premium renderer")
    _require(VALIDATOR, "premium validator")
    _require(TESTS, "premium tests")

    _require_markers(premium_data, PAGE_MARKERS, "premium PDF")
    _require_markers(premium_data, AUTHORITY_MARKERS, "premium PDF")
    _require_markers(premium_data, EVIDENCE_AND_PROXY_MARKERS, "premium PDF")
    _require_markers(premium_data, UCITS_PLACEHOLDER_MARKERS, "premium PDF")
    _require_markers(premium_data, ACTION_MARKERS, "premium PDF")

    notes = NOTES.read_text(encoding="utf-8")
    for marker in NOTE_MARKERS:
        if marker not in notes:
            raise PremiumSurfaceValidationError(f"premium notes missing marker: {marker}")

    print(f"ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_OK | pdf={PREMIUM_PDF} | selected_next_package=WP15G")
    return {"status": "valid", "pdf": str(PREMIUM_PDF), "selected_next_package": "WP15G"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    args = parser.parse_args()
    validate_premium_surface_pdf(Path(args.pdf))


if __name__ == "__main__":
    main()
