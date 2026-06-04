from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED = [
    "Agreement-gate pricing",
    "not valuation authority",
    "not funded",
]

FORBIDDEN = [
    "funded UCITS holding",
    "valuation authority: yes",
    "waarderingsautoriteit: ja",
    "koopadvies: ja",
]


def validate_pricing_surface(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.replace("**", "").split())
    missing = [item for item in REQUIRED if item not in normalized]
    if missing:
        raise RuntimeError(f"EU pricing surface validation failed: missing {', '.join(missing)}")
    for phrase in FORBIDDEN:
        if phrase.lower() in normalized.lower():
            raise RuntimeError(f"EU pricing surface validation failed: forbidden phrase present: {phrase}")
    print(f"ETF_EU_PRICING_SURFACE_OK | report={path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    validate_pricing_surface(Path(args.path))


if __name__ == "__main__":
    main()
