from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED_EN = [
    "Agreement-gate pricing",
    "not valuation authority",
    "not funded",
]

REQUIRED_NL = [
    "Agreement-gate pricing",
    "geen waarderingsautoriteit",
    "niet gefinancierd",
]

FORBIDDEN = [
    "valuation authority: yes",
    "waarderingsautoriteit: ja",
    "koopadvies: ja",
    "portfolio status: funded",
    "funding_authority=true",
    "portfolio_mutation=true",
    "production_delivery=true",
]

FUNDED_UCITS_TOKENS = [
    "funded ucits holding",
    "funded ucits holdings",
]

SAFE_FUNDED_UCITS_NEGATIONS = [
    "funded ucits holdings: none",
    "funded ucits holding: none",
    "funded ucits holdings:** none",
    "funded ucits holding:** none",
    "no funded ucits holding",
    "no funded ucits holdings",
    "not a funded ucits holding",
    "not funded",
]


def _normalize(text: str) -> str:
    return " ".join(text.replace("**", "").replace("__", "").split())


def _has_positive_funded_ucits_claim(text: str) -> bool:
    """Block positive funded-UCITS claims while allowing explicit safe negations.

    The base EU report deliberately contains safe lines such as
    "Funded UCITS holdings: none". A whole-document substring check makes that
    look positive, so evaluate the claim line by line and allow only clear
    negated/cash-only formulations.
    """

    for raw_line in text.splitlines():
        line = _normalize(raw_line).lower()
        if not any(token in line for token in FUNDED_UCITS_TOKENS):
            continue
        if any(negation in line for negation in SAFE_FUNDED_UCITS_NEGATIONS):
            continue
        return True
    return False


def validate_pricing_surface(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    normalized = _normalize(text)
    lowered = normalized.lower()
    required = REQUIRED_NL if "_nl_" in path.name else REQUIRED_EN
    missing = [item for item in required if item not in normalized]
    if missing:
        raise RuntimeError(f"EU pricing surface validation failed: missing {', '.join(missing)}")
    for phrase in FORBIDDEN:
        if phrase.lower() in lowered:
            raise RuntimeError(f"EU pricing surface validation failed: forbidden phrase present: {phrase}")
    if _has_positive_funded_ucits_claim(text):
        raise RuntimeError("EU pricing surface validation failed: positive funded UCITS holding claim present")
    print(f"ETF_EU_PRICING_SURFACE_OK | report={path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    validate_pricing_surface(Path(args.path))


if __name__ == "__main__":
    main()
