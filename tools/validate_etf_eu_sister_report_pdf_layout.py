from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pypdf import PdfReader


MIN_PAGE_TEXT_CHARS = 80
BASE_MAX_EXPECTED_PAGES = 8
ALLOCATOR_V2_MAX_EXPECTED_PAGES = 9
POLICY_ALLOCATOR_V3_MAX_EXPECTED_PAGES = 10


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Sister-report manifest must be a JSON object")
    return payload


def _maximum_expected_pages(manifest: dict[str, Any]) -> int:
    surface = manifest.get("target_allocator_surface") if isinstance(manifest.get("target_allocator_surface"), dict) else {}
    boundaries = (
        surface.get("applied") is True
        and surface.get("portfolio_mutation") is False
        and surface.get("funding_authority") is False
        and surface.get("execution_authority") is False
    )
    if boundaries and surface.get("preferred_variant") == "staged_policy_driven_v1" and surface.get("policy_driven") is True:
        return POLICY_ALLOCATOR_V3_MAX_EXPECTED_PAGES
    if boundaries and surface.get("preferred_variant") == "staged_cash_first_50pct":
        return ALLOCATOR_V2_MAX_EXPECTED_PAGES
    return BASE_MAX_EXPECTED_PAGES


def validate(manifest: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    languages = manifest.get("languages") if isinstance(manifest.get("languages"), dict) else {}
    page_counts: dict[str, int] = {}
    max_expected_pages = _maximum_expected_pages(manifest)

    for language in ("nl", "en"):
        files = languages.get(language) if isinstance(languages.get(language), dict) else {}
        pdf_path = Path(str(files.get("pdf") or ""))
        if not pdf_path.is_file() or pdf_path.stat().st_size <= 0:
            blockers.append(f"{language} PDF is missing or empty: {pdf_path}")
            continue
        reader = PdfReader(str(pdf_path))
        page_counts[language] = len(reader.pages)
        if len(reader.pages) > max_expected_pages:
            blockers.append(
                f"{language} PDF has {len(reader.pages)} pages; expected at most {max_expected_pages} for this report surface"
            )
        for index, page in enumerate(reader.pages, start=1):
            text = " ".join((page.extract_text() or "").split())
            if len(text) < MIN_PAGE_TEXT_CHARS:
                blockers.append(
                    f"{language} PDF page {index} has only {len(text)} extracted characters and may be blank"
                )

    if set(page_counts) == {"nl", "en"} and page_counts["nl"] != page_counts["en"]:
        blockers.append(
            f"bilingual PDF page counts differ: nl={page_counts['nl']} en={page_counts['en']}"
        )

    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ETF EU sister-report PDF layout")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    manifest = _load(args.manifest)
    blockers = validate(manifest)
    languages = manifest.get("languages") if isinstance(manifest.get("languages"), dict) else {}
    page_counts: dict[str, int | None] = {}
    for language in ("nl", "en"):
        files = languages.get(language) if isinstance(languages.get(language), dict) else {}
        pdf_path = Path(str(files.get("pdf") or ""))
        page_counts[language] = len(PdfReader(str(pdf_path)).pages) if pdf_path.is_file() else None
    print(json.dumps({
        "artifact_type": "etf_eu_sister_report_pdf_layout_validation",
        "valid": not blockers,
        "blockers": blockers,
        "page_counts": page_counts,
        "minimum_page_text_characters": MIN_PAGE_TEXT_CHARS,
        "maximum_expected_pages": _maximum_expected_pages(manifest),
    }, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
