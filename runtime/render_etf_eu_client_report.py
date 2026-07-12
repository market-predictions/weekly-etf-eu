from __future__ import annotations

import argparse
import re
from pathlib import Path

import mistune
from weasyprint import HTML


MARKDOWN = mistune.create_markdown(plugins=["table"], escape=True)
CITATION_PATTERNS = [
    re.compile(r"cite.*?", flags=re.DOTALL),
    re.compile(r"filecite.*?", flags=re.DOTALL),
]


def normalize_markdown(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    for pattern in CITATION_PATTERNS:
        text = pattern.sub("", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def _report_date(markdown: str) -> str:
    match = re.search(r"\b20\d{2}-\d{2}-\d{2}\b", markdown)
    return match.group(0) if match else ""


def build_html(markdown: str, *, title: str, language: str) -> str:
    if language not in {"nl", "en"}:
        raise ValueError("language must be nl or en")
    normalized = normalize_markdown(markdown)
    rendered = MARKDOWN(normalized)
    report_date = _report_date(normalized)
    brand = "WEEKLY ETF EU"
    subtitle = "Nederlands clientrapport" if language == "nl" else "English companion report"
    footer_text = (
        "Informatief en educatief; geen persoonlijk beleggingsadvies."
        if language == "nl"
        else "For informational and educational purposes; not personal investment advice."
    )
    return f"""<!doctype html>
<html lang="{language}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    @page {{
      size: A4 landscape;
      margin: 12mm 12mm 14mm 12mm;
      @bottom-left {{
        content: "{brand} · {report_date}";
        color: #66727d;
        font-size: 8pt;
      }}
      @bottom-right {{
        content: "Page " counter(page) " of " counter(pages);
        color: #66727d;
        font-size: 8pt;
      }}
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; }}
    body {{
      background: #ffffff;
      color: #24313b;
      font-family: "Lato", "DejaVu Sans", Arial, sans-serif;
      font-size: 9.8pt;
      line-height: 1.42;
      overflow-wrap: anywhere;
    }}
    header.report-header {{
      border-bottom: 4px solid #8da0ad;
      margin: 0 0 7mm 0;
      padding: 0 0 4mm 0;
    }}
    .brand {{
      color: #314d61;
      font-size: 12pt;
      font-weight: 800;
      letter-spacing: .12em;
    }}
    .subtitle {{
      color: #66727d;
      font-size: 9pt;
      margin-top: 1mm;
    }}
    main {{ display: block; }}
    section.report-content {{ display: block; }}
    h1 {{
      color: #203746;
      font-size: 22pt;
      line-height: 1.16;
      margin: 0 0 6mm 0;
      break-after: avoid-page;
      page-break-after: avoid;
    }}
    h2 {{
      color: #314d61;
      font-size: 14pt;
      line-height: 1.2;
      margin: 7mm 0 3mm 0;
      padding-bottom: 1.5mm;
      border-bottom: .5pt solid #cbd3d9;
      break-after: avoid-page;
      page-break-after: avoid;
    }}
    h3, h4 {{
      color: #425b6c;
      break-after: avoid-page;
      page-break-after: avoid;
    }}
    p {{ margin: 0 0 3.2mm 0; orphans: 3; widows: 3; }}
    ul, ol {{ margin: 0 0 4mm 6mm; padding-left: 5mm; }}
    li {{ margin: 0 0 1.4mm 0; }}
    blockquote {{
      margin: 0 0 5mm 0;
      padding: 3mm 4mm;
      background: #f5f7f8;
      border-left: 3mm solid #8da0ad;
      color: #4d5b65;
      break-inside: avoid-page;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: auto;
      margin: 2mm 0 5mm 0;
      font-size: 8.6pt;
    }}
    thead {{ display: table-header-group; }}
    tbody {{ display: table-row-group; }}
    tr {{
      break-inside: avoid-page;
      page-break-inside: avoid;
    }}
    th, td {{
      border: .5pt solid #d6dde2;
      padding: 2mm 2.2mm;
      vertical-align: top;
      text-align: left;
      overflow-wrap: anywhere;
      word-break: normal;
    }}
    th {{
      background: #edf1f3;
      color: #24313b;
      font-weight: 700;
    }}
    tbody tr:nth-child(even) td {{ background: #fafbfb; }}
    code {{
      font-family: "DejaVu Sans Mono", "Liberation Mono", monospace;
      font-size: 8.5pt;
      background: #f4f5f6;
      padding: .2mm .8mm;
      border-radius: 1mm;
      overflow-wrap: anywhere;
    }}
    pre {{
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      background: #f4f5f6;
      border: .5pt solid #d6dde2;
      padding: 3mm;
      font-family: "DejaVu Sans Mono", "Liberation Mono", monospace;
      font-size: 8.2pt;
      line-height: 1.35;
      break-inside: avoid-page;
    }}
    pre code {{ background: transparent; padding: 0; }}
    strong {{ color: #24313b; }}
    footer.report-footer {{ display: none; }}
    a {{ color: #315f82; text-decoration: underline; }}
  </style>
</head>
<body>
  <header class="report-header">
    <div class="brand">{brand}</div>
    <div class="subtitle">{subtitle}{(" · " + report_date) if report_date else ""}</div>
  </header>
  <main>
    <section class="report-content">
      {rendered}
    </section>
  </main>
  <footer class="report-footer">{footer_text}</footer>
</body>
</html>
"""


def render_report(
    *,
    markdown_path: Path,
    html_output: Path,
    pdf_output: Path,
    language: str,
    title: str,
) -> None:
    markdown = markdown_path.read_text(encoding="utf-8")
    html = build_html(markdown, title=title, language=language)
    html_output.parent.mkdir(parents=True, exist_ok=True)
    pdf_output.parent.mkdir(parents=True, exist_ok=True)
    html_output.write_text(html, encoding="utf-8")
    HTML(string=html, base_url=str(markdown_path.parent.resolve())).write_pdf(str(pdf_output))
    if not pdf_output.exists() or pdf_output.stat().st_size <= 0:
        raise RuntimeError(f"PDF output was not created: {pdf_output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a client-grade Weekly ETF EU HTML/PDF report.")
    parser.add_argument("--markdown", required=True)
    parser.add_argument("--html-output", required=True)
    parser.add_argument("--pdf-output", required=True)
    parser.add_argument("--language", required=True, choices=["nl", "en"])
    parser.add_argument("--title", required=True)
    args = parser.parse_args()
    render_report(
        markdown_path=Path(args.markdown),
        html_output=Path(args.html_output),
        pdf_output=Path(args.pdf_output),
        language=args.language,
        title=args.title,
    )
    print(
        "ETF_EU_CLIENT_REPORT_RENDER_OK"
        f" | language={args.language}"
        f" | html={args.html_output}"
        f" | pdf={args.pdf_output}"
    )


if __name__ == "__main__":
    main()
