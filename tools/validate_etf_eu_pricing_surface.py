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


def validate_pricing_surface(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.replace("**", "").split())
    lowered = normalized.lower()
    required = REQUIRED_NL if "_nl_" in path.name else REQUIRED_EN
    missing = [item for item in required if item not in normalized]
    if missing:
        raise RuntimeError(f"EU pricing surface validation failed: missing {', '.join(missing)}")
    for phrase in FORBIDDEN:
        if phrase.lower() in lowered:
            raise RuntimeError(f"EU pricing surface validation failed: forbidden phrase present: {phrase}")
    if "funded ucits holding" in lowered and "not a funded ucits holding" not in lowered:
        raise RuntimeError("EU pricing surface validation failed: positive funded UCITS holding claim present")
    print(f"ETF_EU_PRICING_SURFACE_OK | report={path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    validate_pricing_surface(Path(args.path))


if __name__ == "__main__":
    main()
