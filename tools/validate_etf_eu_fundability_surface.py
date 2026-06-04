from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED_EN = [
    "Fundability gate status",
    "candidate_promotion=false",
    "funding_authority=false",
    "portfolio_mutation=false",
    "production_delivery=false",
    "does not promote any candidate to fundable",
]

REQUIRED_NL = [
    "Fundability gate status",
    "fundability gate status is zichtbaar",
    "candidate_promotion=false",
    "funding_authority=false",
    "portfolio_mutation=false",
    "production_delivery=false",
    "promoveert geen kandidaat naar fundable",
]

FORBIDDEN = [
    "candidate_promotion=true",
    "funding_authority=true",
    "portfolio_mutation=true",
    "production_delivery=true",
    "candidate promoted to fundable",
    "candidate is fundable",
    "valuation authority: yes",
    "delivery completed",
]

SAFE_FUNDED_NEGATIONS = [
    "funded ucits holdings: none",
    "no funded ucits holdings",
    "not a funded ucits holding",
    "not funded",
]


def _normalize(text: str) -> str:
    return " ".join(text.replace("**", "").replace("__", "").split())


def _has_positive_funded_claim(text: str) -> bool:
    for raw_line in text.splitlines():
        line = _normalize(raw_line).lower()
        if "funded ucits holding" not in line:
            continue
        if any(negation in line for negation in SAFE_FUNDED_NEGATIONS):
            continue
        return True
    return False


def validate_fundability_surface(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    normalized = _normalize(text)
    lowered = normalized.lower()
    is_nl = "_nl_" in path.name
    required = REQUIRED_NL if is_nl else REQUIRED_EN
    missing = [phrase for phrase in required if phrase not in normalized]
    if missing:
        raise RuntimeError(f"EU fundability surface validation failed: missing {', '.join(missing)}")
    for phrase in FORBIDDEN:
        if phrase.lower() in lowered:
            raise RuntimeError(f"EU fundability surface validation failed: forbidden phrase present: {phrase}")
    if _has_positive_funded_claim(text):
        raise RuntimeError("EU fundability surface validation failed: positive funded UCITS holding claim present")
    print(f"ETF_EU_FUNDABILITY_SURFACE_OK | report={path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    validate_fundability_surface(Path(args.path))


if __name__ == "__main__":
    main()
