from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_html_pdf_render_dry_run_v1"
RUN_ID = "20260618_000000"
EN_MD = Path("output/weekly_etf_eu_review_260618_mature_draft.md")
NL_MD = Path("output/weekly_etf_eu_review_nl_260618_mature_draft.md")
BILINGUAL_SURFACE = Path("output/bilingual/etf_eu_bilingual_report_surface_20260618_000000.json")
PREVIOUS_DRY_RUN = Path("output/delivery/etf_eu_delivery_pdf_dry_run_20260618_000000.json")
EN_HTML = Path("output/delivery/weekly_etf_eu_review_260618_mature_dry_run.html")
NL_HTML = Path("output/delivery/weekly_etf_eu_review_nl_260618_mature_dry_run.html")
MANIFEST = Path("output/delivery/etf_eu_html_pdf_render_dry_run_20260618_000000.json")

FALSE_FLAGS = {
    "production_delivery": False,
    "recipient_activation": False,
    "send_attempted": False,
    "mail_transport_enabled": False,
    "smtp_configured": False,
    "secrets_present": False,
    "real_recipients": False,
    "real_receipt": False,
    "proof_claimed": False,
    "portfolio_mutation": False,
    "candidate_promotion": False,
    "funding_authority": False,
    "valuation_grade": False,
}

STYLE = """
<style id="etf-eu-dry-run-style">
  body { font-family: Arial, sans-serif; margin: 32px; line-height: 1.45; color: #111; }
  h1, h2, h3 { page-break-after: avoid; }
  table { border-collapse: collapse; width: 100%; margin: 14px 0; }
  th, td { border: 1px solid #ccc; padding: 6px 8px; vertical-align: top; }
  pre { background: #f6f6f6; padding: 10px; border: 1px solid #ddd; overflow-x: auto; }
  .dry-run-contract { border: 2px solid #999; padding: 12px; margin-bottom: 18px; }
  @media print {
    table { page-break-inside: auto; break-inside: auto; border-collapse: collapse; }
    thead { display: table-header-group; }
    tr, th, td { page-break-inside: avoid; break-inside: avoid; }
  }
</style>
""".strip()


def _inline(text: str) -> str:
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def _table(lines: list[str]) -> str:
    headers = [cell.strip() for cell in lines[0].strip("|").split("|")]
    body_lines = lines[2:]
    out = ["<table>", "<thead><tr>" + "".join(f"<th>{_inline(h)}</th>" for h in headers) + "</tr></thead>", "<tbody>"]
    for raw in body_lines:
        cells = [cell.strip() for cell in raw.strip("|").split("|")]
        out.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in cells) + "</tr>")
    out += ["</tbody>", "</table>"]
    return "\n".join(out)


def markdown_to_html(md_text: str) -> str:
    html: list[str] = []
    lines = md_text.splitlines()
    i = 0
    in_code = False
    code_lines: list[str] = []
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_code:
                html.append("<pre>" + escape("\n".join(code_lines)) + "</pre>")
                code_lines = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue
        if not stripped:
            i += 1
            continue
        if stripped.startswith("|") and i + 1 < len(lines) and lines[i + 1].strip().startswith("| ---"):
            table_lines = [stripped, lines[i + 1].strip()]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            html.append(_table(table_lines))
            continue
        if stripped.startswith("# "):
            html.append(f"<h1>{_inline(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            html.append(f"<h2>{_inline(stripped[3:])}</h2>")
        elif stripped.startswith("### "):
            html.append(f"<h3>{_inline(stripped[4:])}</h3>")
        elif stripped.startswith("- "):
            items: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append("<li>" + _inline(lines[i].strip()[2:]) + "</li>")
                i += 1
            html.append("<ul>" + "".join(items) + "</ul>")
            continue
        else:
            html.append(f"<p>{_inline(stripped)}</p>")
        i += 1
    return "\n".join(html)


def render_dry_run_html(markdown_path: Path, *, language: str) -> str:
    text = markdown_path.read_text(encoding="utf-8")
    title = "ETF EU dry-run render" if language == "en" else "ETF EU dry-run weergave"
    contract = "\n".join([
        "dry_run_only=true",
        "production_delivery=false",
        "recipient_activation=false",
        "send_attempted=false",
        "real_receipt=false",
    ])
    return "\n".join([
        "<!doctype html>",
        f"<html lang=\"{language}\">",
        "<head>",
        "<meta charset=\"utf-8\">",
        f"<title>{escape(title)}</title>",
        STYLE,
        "</head>",
        "<body>",
        "<section class=\"dry-run-contract\"><h2>Dry-run contract</h2><pre>" + escape(contract) + "</pre></section>",
        markdown_to_html(text),
        "</body>",
        "</html>",
        "",
    ])


def build_manifest(*, english_html_path: Path = EN_HTML, dutch_html_path: Path = NL_HTML) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": RUN_ID,
        "status": "completed",
        "created_at_utc": datetime(2026, 6, 18, 0, 0, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
        "english_markdown_report_path": str(EN_MD),
        "dutch_markdown_report_path": str(NL_MD),
        "english_html_output_path": str(english_html_path),
        "dutch_html_output_path": str(dutch_html_path),
        "bilingual_surface_artifact_path": str(BILINGUAL_SURFACE),
        "previous_delivery_dry_run_artifact_path": str(PREVIOUS_DRY_RUN),
        "dry_run_only": True,
        "html_generation_status": "generated_dry_run_html",
        "pdf_generation_status": "not_generated_manifest_only",
        **FALSE_FLAGS,
        "validators_run": [
            "tools/validate_etf_eu_ucits_closing_price_smoke.py",
            "tools/validate_etf_eu_mature_bilingual_report.py",
            "tools/validate_etf_eu_dutch_language_quality.py",
            "tools/validate_etf_eu_delivery_pdf_dry_run.py",
            "tools/validate_etf_eu_html_pdf_dry_run.py",
        ],
        "tests_expected": [
            "tests/test_etf_eu_html_pdf_dry_run.py",
            "tests/test_etf_eu_mature_bilingual_report.py",
            "tests/test_etf_eu_dutch_language_quality.py",
            "tests/test_etf_eu_delivery_pdf_dry_run.py",
        ],
        "selected_next_package": "WP14K",
        "selected_next_package_title": "ETF EU recipient/secrets policy and delivery authorization gate, no send",
    }


def build_all(*, manifest_path: Path = MANIFEST, english_html_path: Path = EN_HTML, dutch_html_path: Path = NL_HTML) -> dict[str, Path]:
    english_html_path.parent.mkdir(parents=True, exist_ok=True)
    english_html_path.write_text(render_dry_run_html(EN_MD, language="en"), encoding="utf-8")
    dutch_html_path.write_text(render_dry_run_html(NL_MD, language="nl"), encoding="utf-8")
    manifest = build_manifest(english_html_path=english_html_path, dutch_html_path=dutch_html_path)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"manifest": manifest_path, "english_html": english_html_path, "dutch_html": dutch_html_path}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(MANIFEST))
    parser.add_argument("--english-html", default=str(EN_HTML))
    parser.add_argument("--dutch-html", default=str(NL_HTML))
    args = parser.parse_args()
    paths = build_all(manifest_path=Path(args.manifest), english_html_path=Path(args.english_html), dutch_html_path=Path(args.dutch_html))
    print(f"ETF_EU_HTML_PDF_DRY_RUN_RENDERED | manifest={paths['manifest']}")


if __name__ == "__main__":
    main()
