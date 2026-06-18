from __future__ import annotations

import argparse
from pathlib import Path


class DraftReportSurfaceError(RuntimeError):
    pass


REQUIRED_TEXT = [
    "ETF EU Review",
    "review_only=true",
    "production_delivery=false",
    "portfolio_mutation=false",
    "funding_authority=false",
    "valuation_grade=false",
    "UCITS pricing evidence used",
    "Instrument identity table",
    "Research proxy separation",
    "Source/freshness disclosure",
    "CSPX.L",
    "SXR8.DE",
    "IE00B5BMR087",
    "This report is review-only.",
    "No production delivery occurred.",
    "No email was sent.",
    "No PDF production delivery was generated.",
    "No recipient was activated.",
    "No portfolio mutation occurred.",
    "No candidate was promoted to fundable.",
    "Yahoo chart pricing is source evidence only and not valuation-grade authority by itself.",
]

FORBIDDEN_AUTHORITY_FLAGS = [
    "production_delivery=true",
    "portfolio_mutation=true",
    "funding_authority=true",
    "valuation_grade=true",
    "recipient_activation=true",
]

FORBIDDEN_PROXY_CONTEXT = [
    "SPY funded holding",
    "SMH funded holding",
    "GLD funded holding",
    "PAVE funded holding",
]


def validate_draft_report_surface(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    missing = [item for item in REQUIRED_TEXT if item not in text]
    if missing:
        raise DraftReportSurfaceError("missing required report surface text: " + ", ".join(missing))
    for flag in FORBIDDEN_AUTHORITY_FLAGS:
        if flag in text:
            raise DraftReportSurfaceError("forbidden authority flag: " + flag)
    for phrase in FORBIDDEN_PROXY_CONTEXT:
        if phrase in text:
            raise DraftReportSurfaceError("forbidden proxy context: " + phrase)
    print(f"ETF_EU_DRAFT_REPORT_SURFACE_OK | report={path}")
    return {"status": "valid", "report": str(path)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report")
    args = parser.parse_args()
    validate_draft_report_surface(Path(args.report))


if __name__ == "__main__":
    main()
