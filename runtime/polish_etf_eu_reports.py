from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

EU_DECISION_COCKPIT = """### EU decision cockpit

- **Draft status:** review-only; no production delivery or portfolio mutation.
- **Pricing basis:** UCITS exchange-line close evidence from the committed smoke artifact.
- **Main active boundary:** U.S. ETFs remain research proxies only, not EU investable holdings.
- **Next action trigger:** expand the EU report runtime and bilingual quality gates before any delivery dry run.
"""

EU_AUTHORITY_LABELS = {
    "production_delivery=false": "production_delivery=false",
    "portfolio_mutation=false": "portfolio_mutation=false",
    "funding_authority=false": "funding_authority=false",
    "valuation_grade=false": "valuation_grade=false",
}

TEXT_CLEANUP = {
    "under review": "review-only",
    "Under review": "Review-only",
    "production-ready": "not production-ready",
    "valuation-grade confirmed": "valuation-grade not confirmed",
}


def _insert_after_section(text: str, section_heading: str, insertion: str) -> str:
    if insertion.strip() in text:
        return text
    start = text.find(section_heading)
    if start == -1:
        return insertion.strip() + "\n\n" + text
    next_heading = text.find("\n## ", start + len(section_heading))
    if next_heading == -1:
        return text.rstrip() + "\n\n" + insertion.strip() + "\n"
    return text[:next_heading].rstrip() + "\n\n" + insertion.strip() + "\n" + text[next_heading:]


def cleanup_client_surface(text: str) -> str:
    for old, new in TEXT_CLEANUP.items():
        text = text.replace(old, new)
    return text


def ensure_authority_labels(text: str) -> str:
    if all(label in text for label in EU_AUTHORITY_LABELS):
        return text
    labels = "\n".join(EU_AUTHORITY_LABELS.values())
    return text.rstrip() + "\n\n```text\n" + labels + "\n```\n"


def polish_english(text: str, runtime_state: dict[str, Any] | None = None) -> str:
    del runtime_state
    text = cleanup_client_surface(text)
    text = ensure_authority_labels(text)
    return _insert_after_section(text, "## 2. Executive summary", EU_DECISION_COCKPIT)


def bilingual_readiness_payload(*, english_report_path: Path, planned_dutch_report_path: Path | None = None) -> dict[str, Any]:
    return {
        "schema_version": "etf_eu_bilingual_surface_readiness_v1",
        "status": "minimal_readiness",
        "english_source_report": str(english_report_path),
        "planned_dutch_companion_report": str(planned_dutch_report_path or ""),
        "review_only": True,
        "derived_from_english_eu_source_artifact": True,
        "dutch_companion_independent_research_pass": False,
        "production_delivery": False,
        "portfolio_mutation": False,
        "funding_authority": False,
        "valuation_grade": False,
    }


def write_bilingual_readiness(output_path: Path, *, english_report_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    import json

    output_path.write_text(
        json.dumps(bilingual_readiness_payload(english_report_path=english_report_path), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path


def polish_file(input_path: Path, output_path: Path) -> Path:
    text = input_path.read_text(encoding="utf-8")
    polished = polish_english(text, runtime_state={})
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(polished, encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = polish_file(Path(args.input), Path(args.output))
    print(f"ETF_EU_REPORT_POLISH_OK | output={output}")


if __name__ == "__main__":
    main()
