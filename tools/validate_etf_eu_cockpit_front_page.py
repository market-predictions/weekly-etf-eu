from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from runtime.additive_etf_eu_cockpit_front_page import SUPPRESSED_SUMMARY_CLASS
from runtime.render_etf_eu_cockpit_front_page import FRONT_PAGE_MARKER


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pages(path: Path) -> int:
    result = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True)
    match = re.search(r"^Pages:\s+(\d+)\s*$", result.stdout, flags=re.MULTILINE)
    if match is None:
        raise RuntimeError(f"Unable to determine PDF pages for {path}")
    return int(match.group(1))


def _front_fragment(html_text: str) -> str:
    start = html_text.find(FRONT_PAGE_MARKER)
    if start < 0:
        return ""
    root_start = html_text.rfind("<section", 0, start)
    end = html_text.find("</section>", start)
    return html_text[root_start : end + len("</section>")] if root_start >= 0 and end >= 0 else ""


def _strip_head_styles(html_text: str) -> str:
    return re.sub(r"<style\b[^>]*>.*?</style>", "", html_text, flags=re.IGNORECASE | re.DOTALL)


def validate_language(
    *,
    language: str,
    state: dict[str, Any],
    classic_html: Path,
    classic_pdf: Path,
    disabled_html: Path,
    disabled_pdf: Path,
    enabled_html: Path,
    enabled_pdf: Path,
    email_html: Path,
) -> dict[str, Any]:
    blockers: list[str] = []
    classic_text = classic_html.read_text(encoding="utf-8")
    disabled_text = disabled_html.read_text(encoding="utf-8")
    enabled_text = enabled_html.read_text(encoding="utf-8")
    email_text = email_html.read_text(encoding="utf-8")
    front = _front_fragment(enabled_text)
    email_front = _front_fragment(email_text)

    if disabled_text != classic_text:
        blockers.append("disabled HTML is not byte-identical to classic HTML")
    if _sha256(disabled_pdf) != _sha256(classic_pdf):
        blockers.append("disabled PDF is not byte-identical to classic PDF")
    if enabled_text.count(FRONT_PAGE_MARKER) != 1:
        blockers.append("enabled front-page count is not exactly one")
    if email_text.count(FRONT_PAGE_MARKER) != 1:
        blockers.append("email front-page count is not exactly one")
    if enabled_text.count(SUPPRESSED_SUMMARY_CLASS) != 1:
        blockers.append("investor summary strip is not suppressed exactly once")

    investor_token = "Beleggersrapport" if language == "nl" else "Investor report"
    analyst_token = "Analistenrapport" if language == "nl" else "Analyst report"
    front_index = enabled_text.find(FRONT_PAGE_MARKER)
    investor_index = enabled_text.find(investor_token, front_index + 1)
    analyst_index = enabled_text.find(analyst_token, investor_index + 1)
    if not (front_index >= 0 and investor_index > front_index and analyst_index > investor_index):
        blockers.append("report order is not cockpit then investor then analyst")

    for number in range(1, 16):
        if f'<span class="badge">{number}</span>' not in enabled_text:
            blockers.append(f"classic section {number} missing")

    classic_pages = _pages(classic_pdf)
    disabled_pages = _pages(disabled_pdf)
    enabled_pages = _pages(enabled_pdf)
    if disabled_pages != classic_pages:
        blockers.append("disabled PDF page count changed")
    if enabled_pages != classic_pages + 1:
        blockers.append(f"enabled PDF page delta is not +1: {classic_pages}->{enabled_pages}")

    portfolio = state.get("portfolio") or {}
    expected_values = [
        str(portfolio.get("position_count")),
        "VWCE",
        "EUNA",
        "SXR8",
        "3/3",
    ]
    for value in expected_values:
        if value not in front:
            blockers.append(f"front page missing funded-state evidence: {value}")

    forbidden_front_tokens = [
        "US ETF strategy",
        "US ETF-strategie",
        "MRKT_RPRTS",
        "preview-only",
        "promotion_status",
        "fundability authority",
        "real broker order",
    ]
    lowered_front = front.lower()
    for token in forbidden_front_tokens:
        if token.lower() in lowered_front:
            blockers.append(f"front page contains forbidden token: {token}")

    stripped_email = _strip_head_styles(email_text)
    stripped_front = _front_fragment(stripped_email)
    essential_email_tokens = [
        "style=",
        "etf-eu-cockpit-page",
        "ISIN-first",
        investor_token,
        "3/3",
    ]
    for token in essential_email_tokens:
        if token not in stripped_front:
            blockers.append(f"email-safe hierarchy missing after style stripping: {token}")
    if "<style" in email_front.lower():
        blockers.append("email-safe front page contains a style block")

    return {
        "language": language,
        "passed": not blockers,
        "blockers": blockers,
        "classic_html": str(classic_html),
        "enabled_html": str(enabled_html),
        "email_html": str(email_html),
        "classic_pdf_pages": classic_pages,
        "disabled_pdf_pages": disabled_pages,
        "enabled_pdf_pages": enabled_pages,
        "front_page_count": enabled_text.count(FRONT_PAGE_MARKER),
        "classic_section_count_preserved": sum(
            f'<span class="badge">{number}</span>' in enabled_text for number in range(1, 16)
        ),
        "disabled_html_sha256": _sha256(disabled_html),
        "classic_html_sha256": _sha256(classic_html),
        "disabled_pdf_sha256": _sha256(disabled_pdf),
        "classic_pdf_sha256": _sha256(classic_pdf),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the additive Weekly ETF EU cockpit preview contract.")
    parser.add_argument("--state", required=True)
    parser.add_argument("--classic-nl-html", required=True)
    parser.add_argument("--classic-nl-pdf", required=True)
    parser.add_argument("--classic-en-html", required=True)
    parser.add_argument("--classic-en-pdf", required=True)
    parser.add_argument("--disabled-nl-html", required=True)
    parser.add_argument("--disabled-nl-pdf", required=True)
    parser.add_argument("--disabled-en-html", required=True)
    parser.add_argument("--disabled-en-pdf", required=True)
    parser.add_argument("--enabled-nl-html", required=True)
    parser.add_argument("--enabled-nl-pdf", required=True)
    parser.add_argument("--enabled-en-html", required=True)
    parser.add_argument("--enabled-en-pdf", required=True)
    parser.add_argument("--email-nl-html", required=True)
    parser.add_argument("--email-en-html", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    state = json.loads(Path(args.state).read_text(encoding="utf-8"))
    common = {
        "state": state,
    }
    dutch = validate_language(
        language="nl",
        classic_html=Path(args.classic_nl_html),
        classic_pdf=Path(args.classic_nl_pdf),
        disabled_html=Path(args.disabled_nl_html),
        disabled_pdf=Path(args.disabled_nl_pdf),
        enabled_html=Path(args.enabled_nl_html),
        enabled_pdf=Path(args.enabled_nl_pdf),
        email_html=Path(args.email_nl_html),
        **common,
    )
    english = validate_language(
        language="en",
        classic_html=Path(args.classic_en_html),
        classic_pdf=Path(args.classic_en_pdf),
        disabled_html=Path(args.disabled_en_html),
        disabled_pdf=Path(args.disabled_en_pdf),
        enabled_html=Path(args.enabled_en_html),
        enabled_pdf=Path(args.enabled_en_pdf),
        email_html=Path(args.email_en_html),
        **common,
    )
    blockers = [f"NL: {item}" for item in dutch["blockers"]] + [f"EN: {item}" for item in english["blockers"]]
    payload = {
        "schema_version": "etf_eu_cockpit_front_page_validation_v1",
        "artifact_type": "etf_eu_cockpit_front_page_validation",
        "passed": not blockers,
        "blockers": blockers,
        "dutch": dutch,
        "english": english,
        "portfolio_mutation": false if False else False,
        "production_enablement": False,
    }
    # Keep JSON booleans explicit without relying on truthy strings.
    payload["portfolio_mutation"] = False
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
