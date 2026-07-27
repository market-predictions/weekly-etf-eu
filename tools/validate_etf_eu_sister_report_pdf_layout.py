from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pypdf import PdfReader


MIN_PAGE_TEXT_CHARS = 80
MAX_EXPECTED_PAGES = 8


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Sister-report manifest must be a JSON object")
    return payload


def validate(manifest: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    languages = manifest.get("languages") if isinstance(manifest.get("languages"), dict) else {}
    page_counts: dict[str, int] = {}

    for language in ("nl", "en"):
        files = languages.get(language) if isinstance(languages.get(language), dict) else {}
        pdf_path = Path(str(files.get("pdf") or ""))
        if not pdf_path.is_file() or pdf_path.stat().st_size <= 0:
            blockers.append(f"{language} PDF is missing or empty: {pdf_path}")
            continue
        reader = PdfReader(str(pdf_path))
        page_counts[language] = len(reader.pages)
        if len(reader.pages) > MAX_EXPECTED_PAGES:
            blockers.append(
                f"{language} PDF has {len(reader.pages)} pages; expected at most {MAX_EXPECTED_PAGES} after blank-page removal"
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
        "maximum_expected_pages": MAX_EXPECTED_PAGES,
    }, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
