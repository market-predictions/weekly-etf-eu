from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from weasyprint import HTML


OVERRIDE_CSS = r"""
/* Narrow output-contract fix: presentation only, no recommendation or valuation changes. */
table { table-layout: fixed; width: 100%; }
th, td { overflow-wrap: anywhere; word-break: normal; hyphens: auto; }
tr { break-inside: avoid; page-break-inside: avoid; }
.status { white-space: normal; line-height: 1.15; }
.wide-table { font-size: 6.45pt; }
/* The renderer's zero-height divider produced an empty physical page. Hide the
   marker and place the page break on the first analyst section itself. */
.analyst-divider { display: none !important; break-before: auto !important; page-break-before: auto !important; }
#section-8 { break-before: page; page-break-before: always; }
#section-13 table { font-size: 5.45pt; }
#section-13 th, #section-13 td { padding: 3px 3px; }
#section-13 tr { break-inside: avoid; page-break-inside: avoid; }
#section-14 table { font-size: 6.0pt; }
#section-14 th, #section-14 td { padding: 4px 4px; }
#section-15 table { font-size: 6.6pt; }
#section-16 { break-inside: auto; padding-top: 9px; padding-bottom: 9px; }
#section-16 .continuity-box { padding: 8px 10px; }
#section-16 ul { margin-top: 4px; margin-bottom: 2px; }
""".strip()


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Sister-report manifest must be a JSON object")
    return payload


def fix_layout(manifest_path: Path) -> None:
    manifest = _load(manifest_path)
    languages = manifest.get("languages") if isinstance(manifest.get("languages"), dict) else {}
    for language, files in languages.items():
        if not isinstance(files, dict):
            raise RuntimeError(f"Invalid language entry: {language}")
        html_path = Path(str(files.get("html") or ""))
        pdf_path = Path(str(files.get("pdf") or ""))
        if not html_path.is_file():
            raise RuntimeError(f"Missing HTML for {language}: {html_path}")
        text = html_path.read_text(encoding="utf-8")
        marker = "/* Narrow output-contract fix: presentation only"
        if marker not in text:
            if "</head>" not in text:
                raise RuntimeError(f"HTML head terminator missing for {language}")
            text = text.replace("</head>", f"<style>{OVERRIDE_CSS}</style></head>", 1)
            html_path.write_text(text, encoding="utf-8")
        HTML(string=text, base_url=str(html_path.parent.resolve())).write_pdf(pdf_path)
        files["layout_fix_applied"] = True
        files["layout_fix_scope"] = "wide_table_wrapping_row_integrity_and_analyst_page_break"

    manifest["layout_fix"] = {
        "applied": True,
        "scope": "wide_table_wrapping_row_integrity_and_analyst_page_break",
        "portfolio_mutation": False,
        "recommendation_change": False,
        "valuation_change": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply presentation-only fixes to ETF EU sister-report shadow")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    fix_layout(args.manifest)
    print(args.manifest)


if __name__ == "__main__":
    main()
