from __future__ import annotations

import argparse
import re
from pathlib import Path

REQUIRED_DUTCH_PHRASES = [
    "review-only",
    "geen productielevering",
    "geen ontvangers geactiveerd",
    "geen portefeuillemutatie",
    "geen financieringsautoriteit",
    "geen waarderingsautoriteit",
    "UCITS-prijsbewijs",
    "UCITS-identiteit",
    "Amerikaanse ETF's zijn alleen researchproxy's",
    "Bron- en versheidsbeperking",
]

ALLOWED_ENGLISH_TERMS = {
    "ETF",
    "UCITS",
    "ISIN",
    "Yahoo",
    "CSPX.L",
    "SXR8.DE",
    "Xetra",
    "London Stock Exchange",
    "USD",
    "EUR",
    "LSE",
    "GER",
    "SPY",
    "HTML",
    "PDF",
    "WP14J",
}

FORBIDDEN_ENGLISH_PHRASES = [
    "production delivery",
    "portfolio mutation",
    "funding authority",
    "valuation-grade authority",
    "U.S. ETF as investable holding",
    "review_only=true",
    "production_delivery=false",
    "portfolio_mutation=false",
    "funding_authority=false",
    "valuation_grade=false",
]


class EtfEuDutchLanguageQualityError(RuntimeError):
    pass


def _mask_allowed_terms(text: str) -> str:
    masked = text
    for term in sorted(ALLOWED_ENGLISH_TERMS, key=len, reverse=True):
        masked = masked.replace(term, "")
    return masked


def validate_dutch_language_quality(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    missing = [phrase for phrase in REQUIRED_DUTCH_PHRASES if phrase not in text]
    if missing:
        raise EtfEuDutchLanguageQualityError("missing Dutch phrase: " + ", ".join(missing))
    lower = text.lower()
    forbidden = [phrase for phrase in FORBIDDEN_ENGLISH_PHRASES if phrase.lower() in lower]
    if forbidden:
        raise EtfEuDutchLanguageQualityError("forbidden English or authority phrase: " + ", ".join(forbidden))
    masked = _mask_allowed_terms(text)
    leaked_heading = re.search(r"\b(Executive Summary|Research proxy separation|Authority disclaimer|Next development step)\b", masked)
    if leaked_heading:
        raise EtfEuDutchLanguageQualityError("English heading leakage: " + leaked_heading.group(0))
    print(f"ETF_EU_DUTCH_LANGUAGE_QUALITY_OK | report={path}")
    return {"status": "valid", "report": str(path)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report")
    args = parser.parse_args()
    validate_dutch_language_quality(Path(args.report))


if __name__ == "__main__":
    main()
