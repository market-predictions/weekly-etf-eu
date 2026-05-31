from __future__ import annotations

import argparse
import re
from pathlib import Path

REQUIRED_NL = [
    "UCITS-kandidatenregister",
    "geen portefeuille",
    "geen koopadvies",
    "geen waarderingsautoriteit",
    "niet gefinancierd; geen waarderingsautoriteit",
    "Pricing-preflight: niet-autoritatieve connectiviteitstest",
]
REQUIRED_EN = [
    "UCITS candidate registry",
    "not a portfolio",
    "not a buy recommendation",
    "not valuation authority",
    "not funded; no valuation authority",
    "Pricing preflight: non-authoritative connectivity test",
]
FORBIDDEN = [
    "funded UCITS position: CSPX",
    "funded UCITS holding: CSPX",
    "gefinancierde UCITS-positie: CSPX",
    "waarderingsautoriteit: ja",
    "valuation authority: yes",
]


def _normalize(text: str) -> str:
    text = text.replace("**", "")
    text = text.replace("`", "")
    return re.sub(r"\s+", " ", text).strip()


def _validate_one(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    normalized = _normalize(text)
    is_nl = "_nl_" in path.name
    required = REQUIRED_NL if is_nl else REQUIRED_EN
    missing = [phrase for phrase in required if phrase not in normalized]
    if missing:
        raise RuntimeError(f"EU candidate report validation failed for {path.name}: missing {', '.join(missing)}")
    for phrase in FORBIDDEN:
        if phrase.lower() in normalized.lower():
            raise RuntimeError(f"EU candidate report validation failed for {path.name}: forbidden phrase present: {phrase}")
    if "CSPX" in normalized and "not funded" not in normalized and "niet gefinancierd" not in normalized:
        raise RuntimeError(f"EU candidate report validation failed for {path.name}: CSPX appears without explicit non-funded context")
    if "priced_non_authoritative" in normalized and "no valuation authority" not in normalized and "geen waarderingsautoriteit" not in normalized:
        raise RuntimeError(f"EU candidate report validation failed for {path.name}: pricing status appears without no-valuation-authority context")
    print(f"ETF_EU_CANDIDATE_REPORT_OK | report={path.name} | language={'nl' if is_nl else 'en'}")


def validate(output_dir: Path) -> None:
    reports = sorted(output_dir.glob("weekly_etf_eu_review*.md"))
    if not reports:
        raise RuntimeError("EU candidate report validation failed: no reports found")
    has_en = any("_nl_" not in p.name for p in reports)
    has_nl = any("_nl_" in p.name for p in reports)
    if not has_en or not has_nl:
        raise RuntimeError("EU candidate report validation failed: expected Dutch and English report pair")
    for path in reports:
        _validate_one(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    validate(Path(args.output_dir))


if __name__ == "__main__":
    main()
