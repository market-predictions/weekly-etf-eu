from __future__ import annotations

import html
import re


ISIN_PATTERN = re.compile(r"[A-Z]{2}[A-Z0-9]{9}\d")
NL_HISTORY_REPLACEMENTS = {
    "Three-position funded-aware non-delivery preview": "Preview zonder levering met drie gefinancierde posities",
}


def _pairs(section_html: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    pattern = re.compile(
        r"<tr>\s*<td>(?P<ticker>[^<]+)</td>\s*<td>.*?</td>\s*<td>(?P<isin>[A-Z]{2}[A-Z0-9]{9}\d)</td>",
        flags=re.DOTALL,
    )
    for match in pattern.finditer(section_html):
        pair = (html.unescape(match.group("ticker")).strip(), match.group("isin").upper())
        if pair[0] and ISIN_PATTERN.fullmatch(pair[1]) and pair not in pairs:
            pairs.append(pair)
    return pairs


def _localize_history_comments(html_text: str, *, language: str) -> str:
    if language != "nl":
        return html_text
    for source, target in NL_HISTORY_REPLACEMENTS.items():
        html_text = html_text.replace(source, target)
    return html_text


def _mark_next_run_panel(html_text: str) -> str:
    return html_text.replace(
        '<section class="panel "><div class="section-head"><span class="badge">14</span>',
        '<section class="panel next-run-panel"><div class="section-head"><span class="badge">14</span>',
        1,
    )


def inject_funded_identity_strip(html_text: str, *, language: str) -> str:
    html_text = _localize_history_comments(html_text, language=language)
    html_text = _mark_next_run_panel(html_text)
    if 'class="funded-identity-strip"' in html_text:
        return html_text

    title = "Review huidige posities" if language == "nl" else "Current-position review"
    title_index = html_text.find(title)
    if title_index < 0:
        return html_text
    section_start = html_text.rfind("<section", 0, title_index)
    section_end = html_text.find("</section>", title_index)
    if section_start < 0 or section_end < 0:
        return html_text
    section_end += len("</section>")
    section_html = html_text[section_start:section_end]
    pairs = _pairs(section_html)
    if not pairs:
        return html_text

    label = "Gefinancierde ISIN-identiteiten" if language == "nl" else "Funded ISIN identities"
    items = " · ".join(
        f'<span class="funded-identity-item"><strong>{html.escape(ticker)}</strong> — {html.escape(isin)}</span>'
        for ticker, isin in pairs
    )
    strip = f'<div class="funded-identity-strip"><strong>{html.escape(label)}:</strong> {items}</div>'
    insertion = section_html.find('<div class="note-box">')
    if insertion < 0:
        insertion = section_html.find("</div>") + len("</div>")
    section_html = section_html[:insertion] + strip + section_html[insertion:]
    section_html = section_html.replace(
        '<table class="data-table">',
        '<table class="data-table funded-position-table">',
        1,
    )
    if language == "nl":
        section_html = section_html.replace("Modelpositie · geen brokerorder", "Model · geen brokerorder")
    else:
        section_html = section_html.replace("Model position · no brokerage order", "Model only · no broker order")
        section_html = section_html.replace("<th>Phase target</th>", "<th>Target</th>")

    css = """
<style id="etf-eu-funded-identity-polish">
  .next-run-panel { break-before: page; page-break-before: always; }
  .funded-identity-strip { margin: 0 0 8px; padding: 7px 9px; border: 1px solid #C9D2D8; border-radius: 7px; background: #F4F7F8; font-size: 8.5pt; line-height: 1.35; }
  .funded-identity-item { white-space: nowrap; }

  .funded-position-table { table-layout: fixed; font-size: 6.25pt; }
  .funded-position-table th, .funded-position-table td { padding: 3px; overflow-wrap: normal; word-break: normal; hyphens: auto; }
  .funded-position-table th:nth-child(1) { width: 6%; }
  .funded-position-table th:nth-child(2) { width: 20%; }
  .funded-position-table th:nth-child(3) { width: 13%; }
  .funded-position-table th:nth-child(4) { width: 6%; }
  .funded-position-table th:nth-child(5) { width: 8%; }
  .funded-position-table th:nth-child(6) { width: 11%; }
  .funded-position-table th:nth-child(7) { width: 10%; }
  .funded-position-table th:nth-child(8) { width: 7%; }
  .funded-position-table th:nth-child(9) { width: 8%; }
  .funded-position-table th:nth-child(10) { width: 11%; }
  .funded-position-table th:nth-child(1), .funded-position-table td:nth-child(1),
  .funded-position-table th:nth-child(3), .funded-position-table td:nth-child(3),
  .funded-position-table th:nth-child(4), .funded-position-table td:nth-child(4),
  .funded-position-table th:nth-child(5), .funded-position-table td:nth-child(5),
  .funded-position-table th:nth-child(6), .funded-position-table td:nth-child(6),
  .funded-position-table th:nth-child(7), .funded-position-table td:nth-child(7),
  .funded-position-table th:nth-child(8), .funded-position-table td:nth-child(8),
  .funded-position-table th:nth-child(9), .funded-position-table td:nth-child(9) { white-space: nowrap; }

  .wide-table th, .wide-table td { overflow-wrap: normal; word-break: normal; hyphens: auto; }
  .pricing-table { table-layout: fixed; font-size: 5.95pt; }
  .pricing-table th:nth-child(1) { width: 6%; }
  .pricing-table th:nth-child(2) { width: 22%; }
  .pricing-table th:nth-child(3) { width: 13%; }
  .pricing-table th:nth-child(4) { width: 11%; }
  .pricing-table th:nth-child(5) { width: 9%; }
  .pricing-table th:nth-child(6) { width: 7%; }
  .pricing-table th:nth-child(7) { width: 6%; }
  .pricing-table th:nth-child(8) { width: 14%; }
  .pricing-table th:nth-child(9) { width: 12%; }
  .pricing-table th:nth-child(1), .pricing-table td:nth-child(1),
  .pricing-table th:nth-child(3), .pricing-table td:nth-child(3),
  .pricing-table th:nth-child(5), .pricing-table td:nth-child(5),
  .pricing-table th:nth-child(6), .pricing-table td:nth-child(6),
  .pricing-table th:nth-child(7), .pricing-table td:nth-child(7) { white-space: nowrap; }
</style>
"""
    result = html_text[:section_start] + section_html + html_text[section_end:]
    return result.replace("</head>", css + "</head>", 1)
