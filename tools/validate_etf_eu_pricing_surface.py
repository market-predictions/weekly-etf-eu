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

PRODUCTION_MATURITY_EN = [
    "Production report maturity",
    "Dutch report is the primary client report",
    "no production delivery",
    "no delivery receipt",
    "fundability gate status visible",
    "candidate_promotion=false",
]

PRODUCTION_MATURITY_NL = [
    "Productierapport-volwassenheid",
    "Nederlandse hoofdrapportage",
    "primaire clientrapportage",
    "Engelse rapportage is companion/operator-facing",
    "geen productielevering",
    "geen delivery receipt",
    "fundability gate status zichtbaar",
    "candidate_promotion=false",
]

FORBIDDEN = [
    "valuation authority: yes",
    "waarderingsautoriteit: ja",
    "koopadvies: ja",
    "portfolio status: funded",
    "funding_authority=true",
    "portfolio_mutation=true",
    "production_delivery=true",
    "candidate_promotion=true",
    "delivery completed",
    "delivery receipt exists",
    "delivery receipt created",
    "pdf generated",
    "email sent",
    "candidate promoted to fundable",
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


def validate_pricing_surface(path: Path, *, require_production_dutch_first: bool = False) -> None:
    text = path.read_text(encoding="utf-8")
    normalized = _normalize(text)
    lowered = normalized.lower()
    is_nl = "_nl_" in path.name
    required = REQUIRED_NL if is_nl else REQUIRED_EN
    missing = [item for item in required if item not in normalized]
    if missing:
        raise RuntimeError(f"EU pricing surface validation failed: missing {', '.join(missing)}")
    if require_production_dutch_first or "Productierapport-volwassenheid" in normalized or "Production report maturity" in normalized:
        maturity_required = PRODUCTION_MATURITY_NL if is_nl else PRODUCTION_MATURITY_EN
        missing_maturity = [item for item in maturity_required if item not in normalized]
        if missing_maturity:
            raise RuntimeError(f"EU pricing surface validation failed: missing production maturity phrase(s): {', '.join(missing_maturity)}")
    for phrase in FORBIDDEN:
        if phrase.lower() in lowered:
            raise RuntimeError(f"EU pricing surface validation failed: forbidden phrase present: {phrase}")
    if _has_positive_funded_ucits_claim(text):
        raise RuntimeError("EU pricing surface validation failed: positive funded UCITS holding claim present")
    print(f"ETF_EU_PRICING_SURFACE_OK | report={path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--require-production-dutch-first", action="store_true")
    args = parser.parse_args()
    validate_pricing_surface(Path(args.path), require_production_dutch_first=args.require_production_dutch_first)


if __name__ == "__main__":
    main()
