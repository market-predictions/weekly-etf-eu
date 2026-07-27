from __future__ import annotations

import argparse
import json
from pathlib import Path

from weasyprint import HTML


STYLE = """
<style id="policy-operational-appendix-pagination">
@media print {
  #section-15 { break-before: page; page-break-before: always; }
  #section-15, #section-16 { break-inside: avoid; page-break-inside: avoid; }
}
</style>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Place holdings and continuity on a stable operational appendix page")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    for language, files in (manifest.get("languages") or {}).items():
        if language not in {"nl", "en"} or not isinstance(files, dict):
            continue
        html_path = Path(str(files.get("html") or ""))
        pdf_path = Path(str(files.get("pdf") or ""))
        text = html_path.read_text(encoding="utf-8")
        if 'id="policy-operational-appendix-pagination"' not in text:
            if "</head>" not in text:
                raise RuntimeError(f"HTML head boundary missing for {language}")
            text = text.replace("</head>", STYLE + "</head>", 1)
        html_path.write_text(text, encoding="utf-8")
        HTML(string=text, base_url=str(html_path.parent.resolve())).write_pdf(pdf_path)
        files["policy_report_pagination"] = "holdings_and_continuity_appendix_page_v1"
    manifest["policy_report_pagination"] = {
        "applied": True,
        "page_break_before_section": "15",
        "appendix_sections": ["15", "16"],
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
    }
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.manifest)


if __name__ == "__main__":
    main()
