from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED_REPORT_QUALITY_TEXT = [
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
    "Authority and delivery disclaimer",
    "WP14G",
]

FORBIDDEN_TRUE_FLAGS = [
    "production_delivery=true",
    "portfolio_mutation=true",
    "funding_authority=true",
    "valuation_grade=true",
]

FORBIDDEN_PROXY_PHRASES = [
    "SPY funded holding",
    "SMH funded holding",
    "GLD funded holding",
    "PAVE funded holding",
    "SPY EU holding",
    "SMH EU holding",
    "GLD EU holding",
    "PAVE EU holding",
]


class EtfEuReportQualityError(RuntimeError):
    pass


def validate_report_quality(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    missing = [item for item in REQUIRED_REPORT_QUALITY_TEXT if item not in text]
    if missing:
        raise EtfEuReportQualityError("missing required report quality text: " + ", ".join(missing))
    forbidden_flags = [flag for flag in FORBIDDEN_TRUE_FLAGS if flag in text]
    if forbidden_flags:
        raise EtfEuReportQualityError("forbidden authority flag: " + ", ".join(forbidden_flags))
    forbidden_proxy = [phrase for phrase in FORBIDDEN_PROXY_PHRASES if phrase in text]
    if forbidden_proxy:
        raise EtfEuReportQualityError("forbidden proxy context: " + ", ".join(forbidden_proxy))
    if "U.S. ETFs are research proxies only" not in text:
        raise EtfEuReportQualityError("research proxy separation missing")
    print(f"ETF_EU_REPORT_QUALITY_OK | report={path}")
    return {"status": "valid", "report": str(path)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report")
    args = parser.parse_args()
    validate_report_quality(Path(args.report))


if __name__ == "__main__":
    main()
