from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from tools.validate_etf_eu_routine_pdf_client_grade_base import validate_pdf as validate_base


ISIN_RE = re.compile(r"\b[A-Z]{2}[A-Z0-9]{9}\d\b")
SEMANTIC_HEADER = {
    "nl": "| Handelslijn | ISIN | Peildatum | Slot | Valuta | Status |",
    "en": "| Trading line | ISIN | Pricing date | Close | Currency | Status |",
}
SEMANTIC_PDF_TOKEN = {"nl": "Peildatum", "en": "Pricing date"}
LEGACY_DATE_HEADERS = {"nl": "Markt", "en": "Market"}
RESIDUAL_LANGUAGE_DEFECTS = {
    "nl": [
        "Trading line",
        "broker- en bevestiging",
        "afzonderlijke afzonderlijk",
        "waarderingsautoriteit",
        "Core aandelen",
        "Core-aandelen",
    ],
    "en": [
        "not funding or valuation authority",
        "do not fund thematic or gold exposure",
        "no funding before full verification",
        "No portfolio mutation without a separate funding decision",
        "Technology/semiconductors",
    ],
}


def validate_language_contract(*, markdown_text: str, html_text: str, pdf_text: str, language: str) -> dict[str, Any]:
    if language not in {"nl", "en"}:
        raise ValueError("language must be nl or en")
    combined = "\n".join((markdown_text, html_text, pdf_text))
    residual = sorted(
        token for token in RESIDUAL_LANGUAGE_DEFECTS[language]
        if token.casefold() in combined.casefold()
    )
    semantic_header_passed = (
        SEMANTIC_HEADER[language] in markdown_text
        and SEMANTIC_PDF_TOKEN[language].casefold() in pdf_text.casefold()
    )
    blockers = [f"Residual client-language defect: {token}" for token in residual]
    if not semantic_header_passed:
        blockers.append("Pricing table header is not client-safe or does not describe the pricing-date column")
    return {
        "client_language_contract_version": "v2",
        "semantic_pricing_header_passed": semantic_header_passed,
        "residual_client_language_defects": residual,
        "client_language_contract_passed": not blockers,
        "client_language_blockers": blockers,
    }


def _upgrade_legacy_header_blockers(blockers: list[str], *, language: str) -> list[str]:
    upgraded: list[str] = []
    prefix = "Missing pricing-table headers:"
    legacy_date_header = LEGACY_DATE_HEADERS[language]
    for blocker in blockers:
        if not blocker.startswith(prefix):
            upgraded.append(blocker)
            continue
        missing = [item.strip() for item in blocker[len(prefix):].split(",") if item.strip()]
        remaining = [item for item in missing if item != legacy_date_header]
        if remaining:
            upgraded.append(prefix + " " + ", ".join(remaining))
    return upgraded


def validate_pdf(
    *,
    pdf: Path,
    html: Path,
    markdown: Path,
    language: str,
    repair_run_id: str,
    source_run_id: str,
) -> dict[str, Any]:
    result = validate_base(
        pdf=pdf,
        html=html,
        markdown=markdown,
        language=language,
        repair_run_id=repair_run_id,
        source_run_id=source_run_id,
    )
    markdown_text = markdown.read_text(encoding="utf-8")
    html_text = html.read_text(encoding="utf-8")
    pdf_text = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    language_contract = validate_language_contract(
        markdown_text=markdown_text,
        html_text=html_text,
        pdf_text=pdf_text,
        language=language,
    )

    represented_rows = len(ISIN_RE.findall(markdown_text.upper()))
    blockers = _upgrade_legacy_header_blockers(list(result.get("blockers", [])), language=language)
    if represented_rows < 8:
        blockers.append(f"Expected at least 8 represented pricing lines, found {represented_rows}")
    blockers.extend(language_contract["client_language_blockers"])
    result.update(
        {
            "schema_version": "etf_eu_routine_pdf_client_grade_v3",
            "pricing_line_count_detected": represented_rows,
            "pricing_line_count_source": "source_markdown_isin_rows",
            **language_contract,
            "blockers": blockers,
            "machine_validation_passed": not blockers,
        }
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Weekly ETF EU client-grade HTML/PDF output.")
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--html", required=True)
    parser.add_argument("--markdown", required=True)
    parser.add_argument("--language", required=True, choices=["nl", "en"])
    parser.add_argument("--repair-run-id", required=True)
    parser.add_argument("--source-run-id", required=True)
    parser.add_argument("--write-result", required=True)
    args = parser.parse_args()
    result = validate_pdf(
        pdf=Path(args.pdf),
        html=Path(args.html),
        markdown=Path(args.markdown),
        language=args.language,
        repair_run_id=args.repair_run_id,
        source_run_id=args.source_run_id,
    )
    output = Path(args.write_result)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["machine_validation_passed"] is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
