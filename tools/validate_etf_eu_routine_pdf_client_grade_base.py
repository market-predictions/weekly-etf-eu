from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import shutil
import subprocess
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import mistune

MARKDOWN = mistune.create_markdown(plugins=["table"], escape=True)
SECTIONS = {
    "nl": [
        "1. Besluit in één oogopslag",
        "2. Portefeuille en kapitaal",
        "3. Actuele UCITS-prijssnapshot",
        "4. Dekking en besliskwaliteit",
        "5. Lane-oordeel",
        "6. Risico- en kwaliteitsgrenzen",
        "7. Volgende routineactie",
    ],
    "en": [
        "1. Decision at a glance",
        "2. Portfolio and capital",
        "3. Current UCITS pricing snapshot",
        "4. Coverage and decision quality",
        "5. Lane assessment",
        "6. Risk and quality boundaries",
        "7. Next routine action",
    ],
}
LANGUAGE_TOKENS = {
    "nl": ["Weekly ETF EU Review", "Nederlands", "Besluit in één oogopslag", "vóór", "portefeuille"],
    "en": ["Weekly ETF EU Review", "English Companion", "Decision at a glance", "Portfolio and capital"],
}
TABLE_HEADERS = {
    "nl": ["Handelslijn", "ISIN", "Markt", "Slot", "Valuta", "Status"],
    "en": ["Trading line", "ISIN", "Market", "Close", "Currency", "Status"],
}
MARKDOWN_LEAKAGE_TOKENS = ["|---|", "**", "```"]
FORBIDDEN_CLIENT_TOKENS = [
    "candidate_requires_verification",
    "verified_ucits_trading_line",
    "priced_non_authoritative",
    "fetch_failed",
    "valuation_grade=",
    "ready_for_controlled_delivery=",
    "send_executed=",
    "transport_attempted=",
    "receipt_confirmed=",
    "funding_authority=",
    "portfolio_mutation=",
    "production_delivery_authority=",
    "8. Authority flags",
    "Authority flags",
]
FORBIDDEN_NL = [
    "research candidates",
    "fundable",
    "pricing-line",
    "client-facing",
    "candidate/research",
    "Technologie/semiconductors",
]
SNAKE_CASE_RE = re.compile(r"\b[a-z]+(?:_[a-z0-9]+){1,}\b")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _require_tools() -> None:
    missing = [name for name in ("pdftotext", "pdftoppm", "pdfinfo") if not shutil.which(name)]
    if missing:
        raise RuntimeError("Missing required Poppler tools: " + ", ".join(missing))


def _run(args: list[str]) -> str:
    completed = subprocess.run(args, check=True, text=True, capture_output=True)
    return completed.stdout


def _page_count(pdf: Path) -> int:
    info = _run(["pdfinfo", str(pdf)])
    match = re.search(r"^Pages:\s+(\d+)\s*$", info, flags=re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not determine page count for {pdf}")
    return int(match.group(1))


def _pdf_text(pdf: Path) -> str:
    return _run(["pdftotext", "-layout", str(pdf), "-"])


def _visible_html_text(raw_html: str) -> str:
    raw_html = re.sub(r"<head\b.*?</head>", " ", raw_html, flags=re.IGNORECASE | re.DOTALL)
    raw_html = re.sub(r"<(style|script)\b.*?</\1>", " ", raw_html, flags=re.IGNORECASE | re.DOTALL)
    raw_html = re.sub(r"<[^>]+>", " ", raw_html)
    return re.sub(r"\s+", " ", html_lib.unescape(raw_html)).strip()


def _plain_markdown(markdown: str) -> str:
    rendered = MARKDOWN(markdown)
    rendered = re.sub(r"<[^>]+>", " ", rendered)
    return re.sub(r"\s+", " ", html_lib.unescape(rendered)).strip()


def _normalized(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _contains(haystack: str, needle: str) -> bool:
    return _normalized(needle) in _normalized(haystack)


def validate_pdf(
    *,
    pdf: Path,
    html: Path,
    markdown: Path,
    language: str,
    repair_run_id: str,
    source_run_id: str,
) -> dict[str, Any]:
    if language not in {"nl", "en"}:
        raise ValueError("language must be nl or en")
    _require_tools()
    blockers: list[str] = []
    warnings: list[str] = []

    for path in (pdf, html, markdown):
        if not path.exists():
            raise AssertionError(f"Required client artifact does not exist: {path}")

    raw_pdf = pdf.read_bytes()
    raw_html = html.read_text(encoding="utf-8")
    raw_markdown = markdown.read_text(encoding="utf-8")
    pdf_text = _pdf_text(pdf)
    html_text = _visible_html_text(raw_html)
    source_text = _plain_markdown(raw_markdown)

    pdf_header_valid = raw_pdf.startswith(b"%PDF-")
    pdf_eof_valid = b"%%EOF" in raw_pdf[-512:]
    pages = _page_count(pdf)
    text_extraction_passed = len(pdf_text.strip()) > 100
    completeness_ratio = min(1.0, len(re.sub(r"\s+", " ", pdf_text).strip()) / max(1, len(source_text)))

    missing_sections = [section for section in SECTIONS[language] if not _contains(pdf_text, section)]
    required_sections_present = not missing_sections
    final_section_token = SECTIONS[language][-1]
    final_section_index = _normalized(pdf_text).find(_normalized(final_section_token))
    final_required_section_present_near_end = final_section_index >= int(len(_normalized(pdf_text)) * 0.60)

    html_lower = raw_html.casefold()
    table_rendering_passed = (
        "<table" in html_lower
        and "<thead" in html_lower
        and "<tbody" in html_lower
        and 'class="table-row"' not in html_lower
        and "class='table-row'" not in html_lower
    )

    combined_visible = f"{raw_markdown}\n{html_text}\n{pdf_text}"
    markdown_leakage = [token for token in MARKDOWN_LEAKAGE_TOKENS if token in f"{html_text}\n{pdf_text}"]
    markdown_leakage_detected = bool(markdown_leakage)
    expected_language_tokens = LANGUAGE_TOKENS[language]
    missing_language_tokens = [token for token in expected_language_tokens if not _contains(pdf_text, token)]
    unicode_integrity_passed = "\ufffd" not in combined_visible and not missing_language_tokens

    title_line = next((line[2:].strip() for line in raw_markdown.splitlines() if line.startswith("# ")), "")
    title_count = _normalized(html_text).count(_normalized(title_line)) if title_line else 0
    duplicate_title_detected = title_count != 1
    missing_table_headers = [header for header in TABLE_HEADERS[language] if not _contains(pdf_text, header)]

    forbidden = list(FORBIDDEN_CLIENT_TOKENS)
    if language == "nl":
        forbidden.extend(FORBIDDEN_NL)
    forbidden_hits = sorted({token for token in forbidden if token.casefold() in combined_visible.casefold()})
    snake_case_hits = sorted(set(SNAKE_CASE_RE.findall(combined_visible)))
    authority_metadata_absent = not any(
        token.casefold() in combined_visible.casefold()
        for token in FORBIDDEN_CLIENT_TOKENS
        if token.endswith("=") or "Authority flags" in token
    )
    raw_status_enums_absent = not any(
        token.casefold() in combined_visible.casefold()
        for token in (
            "candidate_requires_verification",
            "verified_ucits_trading_line",
            "priced_non_authoritative",
            "fetch_failed",
        )
    )
    client_surface_clean = not forbidden_hits and not snake_case_hits and authority_metadata_absent and raw_status_enums_absent

    checks = [
        (pdf_header_valid, "PDF header is invalid"),
        (pdf_eof_valid, "PDF EOF marker is missing"),
        (2 <= pages <= 12, f"page_count must be between 2 and 12, got {pages}"),
        (text_extraction_passed, "PDF text extraction produced too little text"),
        (completeness_ratio >= 0.72, f"PDF text completeness ratio is too low: {completeness_ratio:.3f}"),
        (required_sections_present, "Missing required sections: " + ", ".join(missing_sections)),
        (final_required_section_present_near_end, "Final required section is absent from the final portion of the PDF"),
        (not missing_table_headers, "Missing pricing-table headers: " + ", ".join(missing_table_headers)),
        (not markdown_leakage_detected, "Raw Markdown leakage detected: " + ", ".join(markdown_leakage)),
        (unicode_integrity_passed, "Unicode/language tokens missing or corrupted: " + ", ".join(missing_language_tokens)),
        (table_rendering_passed, "Semantic HTML table structure is missing or legacy table-row divs remain"),
        (not duplicate_title_detected, f"Visible report title must occur exactly once, found {title_count}"),
        (client_surface_clean, "Client-surface leakage detected: " + ", ".join(forbidden_hits + snake_case_hits)),
        (authority_metadata_absent, "Authority or transport metadata is visible on the client surface"),
        (raw_status_enums_absent, "Raw status enums remain visible on the client surface"),
    ]
    for passed, message in checks:
        if not passed:
            blockers.append(message)

    machine_validation_passed = not blockers
    return {
        "schema_version": "etf_eu_routine_pdf_client_grade_base_v2",
        "artifact_type": "etf_eu_routine_pdf_client_grade",
        "generated_at_utc": _utc_now(),
        "repair_run_id": repair_run_id,
        "source_run_id": source_run_id,
        "language": language,
        "pdf": str(pdf),
        "html": str(html),
        "markdown": str(markdown),
        "page_count": pages,
        "pdf_header_valid": pdf_header_valid,
        "pdf_eof_valid": pdf_eof_valid,
        "text_extraction_passed": text_extraction_passed,
        "text_completeness_ratio": round(completeness_ratio, 4),
        "required_sections_present": required_sections_present,
        "missing_sections": missing_sections,
        "final_required_section_present_near_end": final_required_section_present_near_end,
        "table_rendering_passed": table_rendering_passed,
        "markdown_leakage_detected": markdown_leakage_detected,
        "markdown_leakage_tokens": markdown_leakage,
        "unicode_integrity_passed": unicode_integrity_passed,
        "missing_language_tokens": missing_language_tokens,
        "duplicate_title_detected": duplicate_title_detected,
        "visible_title_count": title_count,
        "client_surface_clean": client_surface_clean,
        "authority_metadata_absent": authority_metadata_absent,
        "raw_status_enums_absent": raw_status_enums_absent,
        "forbidden_client_tokens": forbidden_hits,
        "snake_case_tokens": snake_case_hits,
        "machine_validation_passed": machine_validation_passed,
        "blockers": blockers,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Base Weekly ETF EU client-grade HTML/PDF checks.")
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
