from __future__ import annotations

import argparse
import re
from pathlib import Path

SNAKE_CASE_RE = re.compile(r"\b[a-z]+(?:_[a-z0-9]+){1,}\b")
EN_NEGATIVE_RE = re.compile(r"(\breduce\s+(?:\[[^\]]+\]\([^\)]+\)|[A-Z][A-Z0-9.-]*)\s+by\s+)-(\d+(?:\.\d+)?%)", re.IGNORECASE)
NL_NEGATIVE_RE = re.compile(r"(\bverlaag\s+(?:\[[^\]]+\]\([^\)]+\)|[A-Z][A-Z0-9.-]*)\s+met\s+)-(\d+(?:\.\d+)?%)", re.IGNORECASE)

EXACT_REPLACEMENTS = {
    "rotation_decisions, target_weights and trade_intents": "the portfolio rotation plan, target allocations and proposed trade intents",
    "trade_intents": "proposed trade intents",
    "target_weights": "target allocations",
    "rotation_decisions": "rotation decisions",
    "churn_budget_used": "rotation budget already used",
    "etf_valuation_history": "ETF valuation history",
    "Reason codes": "Decision rationale",
    "Redencodes": "Toelichting",
    "fresh_cash_smaller_or_review": "fresh capital only after review or at smaller size",
    "failed_fresh_cash_test": "position does not pass the fresh-capital test",
    "replaceable_status": "position is under replacement review",
    "review_age_ge_2": "review has persisted for multiple report cycles",
    "review_age_ge_3": "review has persisted for several report cycles",
}

PHRASE_REPLACEMENTS = {
    "Notes: Section 7 uses `output/ETF valuation history.csv` plus the current runtime NAV; Section 15 is rendered from the same normalized runtime state.":
        "Notes: Section 7 uses the validated valuation history plus the current portfolio NAV; Section 15 is rendered from the same reconciled portfolio state.",
    "Notes: Section 7 uses `output/etf valuation history.csv` plus the current runtime NAV; Section 15 is rendered from the same normalized runtime state.":
        "Notes: Section 7 uses the validated valuation history plus the current portfolio NAV; Section 15 is rendered from the same reconciled portfolio state.",
    "Notes: Section 7 uses `output/etf_valuation_history.csv` plus the current runtime NAV; Section 15 is rendered from the same normalized runtime state.":
        "Notes: Section 7 uses the validated valuation history plus the current portfolio NAV; Section 15 is rendered from the same reconciled portfolio state.",
    "Rotation plan artifact is active; Sections 12-14 are rendered from the portfolio rotation plan, target allocations and proposed trade intents.":
        "Rotation plan artifact is active; Sections 12-14 are rendered from the portfolio rotation plan, target allocations and proposed trade intents.",
    "override rotation budget already used": "override: rotation budget already used",
}


def _clean_snake_token(match: re.Match[str]) -> str:
    token = match.group(0)
    replacement = EXACT_REPLACEMENTS.get(token)
    if replacement:
        return replacement
    return token.replace("_", " ")


def scrub_text(text: str) -> str:
    text = EN_NEGATIVE_RE.sub(r"\1\2", text)
    text = NL_NEGATIVE_RE.sub(r"\1\2", text)
    for source, target in EXACT_REPLACEMENTS.items():
        text = text.replace(source, target)
    for source, target in PHRASE_REPLACEMENTS.items():
        text = text.replace(source, target)
    text = SNAKE_CASE_RE.sub(_clean_snake_token, text)
    for source, target in PHRASE_REPLACEMENTS.items():
        text = text.replace(source, target)
    return text


def scrub(output_dir: Path) -> None:
    count = 0
    for path in sorted(output_dir.glob("weekly_analysis_pro*.md")):
        if path.is_dir():
            continue
        original = path.read_text(encoding="utf-8")
        cleaned = scrub_text(original)
        if cleaned != original:
            path.write_text(cleaned, encoding="utf-8")
            count += 1
            print(f"ETF_CLIENT_SURFACE_SCRUBBED | report={path.name}")
    print(f"ETF_CLIENT_SURFACE_SCRUB_OK | changed={count}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    scrub(Path(args.output_dir))


if __name__ == "__main__":
    main()
