from __future__ import annotations

import argparse
import json
from pathlib import Path

TARGET = Path("output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf")
CLOSEOUT = Path("output/client_surface/etf_eu_cockpit_poc_coordinator_closeout_20260618_000000.json")
POC_PACKAGE = Path("output/client_surface/etf_eu_cockpit_poc_package_20260618_000000.json")
DUTCH_MD = Path("output/client_surface/weekly_etf_eu_review_nl_260618_cockpit_pricing_integrated.md")
ENGLISH_MD = Path("output/client_surface/weekly_etf_eu_review_260618_cockpit_pricing_integrated.md")
MIN_SIZE_BYTES = 2500
REQUIRED_PDF_MARKERS = [
    b"ETF EU Cockpit PDF MVP",
    b"proof_of_concept_pdf_mvp",
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
]


class EtfEuCockpitPdfMvpError(RuntimeError):
    pass


def _load_json(path: Path) -> dict:
    if not path.exists():
        raise EtfEuCockpitPdfMvpError(f"missing source: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise EtfEuCockpitPdfMvpError(f"source must be object: {path}")
    return data


def _require(path: Path, label: str) -> None:
    if not path.exists():
        raise EtfEuCockpitPdfMvpError(f"missing {label}: {path}")


def validate_pdf_mvp(path: Path) -> dict[str, str]:
    if path != TARGET:
        raise EtfEuCockpitPdfMvpError(f"unexpected pdf path: {path}")
    _require(TARGET, "pdf")
    _require(CLOSEOUT, "source closeout artifact")
    _require(POC_PACKAGE, "source POC package")
    _require(DUTCH_MD, "Dutch markdown source")
    _require(ENGLISH_MD, "English markdown source")

    closeout = _load_json(CLOSEOUT)
    package = _load_json(POC_PACKAGE)

    if closeout.get("delivery_authorization_decision") != "remain_blocked":
        raise EtfEuCockpitPdfMvpError("delivery boundary changed")
    for key in ["production_delivery", "portfolio_mutation", "candidate_promotion", "funding_authority", "valuation_grade"]:
        if closeout.get(key) is not False:
            raise EtfEuCockpitPdfMvpError(f"closeout boundary changed: {key}")
        if package.get(key) is not False:
            raise EtfEuCockpitPdfMvpError(f"package boundary changed: {key}")
    if package.get("current_pricing_baseline", {}).get("review_only") is not True:
        raise EtfEuCockpitPdfMvpError("pricing baseline review_only flag changed")

    pdf_bytes = TARGET.read_bytes()
    if not pdf_bytes.startswith(b"%PDF"):
        raise EtfEuCockpitPdfMvpError("missing PDF header")
    if len(pdf_bytes) <= MIN_SIZE_BYTES:
        raise EtfEuCockpitPdfMvpError("PDF size too small")
    for marker in REQUIRED_PDF_MARKERS:
        if marker not in pdf_bytes:
            raise EtfEuCockpitPdfMvpError(f"PDF missing marker: {marker.decode('ascii')}")
    if b"delivery_receipt_created=true" in pdf_bytes:
        raise EtfEuCockpitPdfMvpError("forbidden positive receipt marker")
    print(f"ETF_EU_COCKPIT_PDF_MVP_OK | pdf={TARGET}")
    return {"status": "valid", "pdf": str(TARGET)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    args = parser.parse_args()
    validate_pdf_mvp(Path(args.pdf))


if __name__ == "__main__":
    main()
