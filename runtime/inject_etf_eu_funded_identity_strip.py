from __future__ import annotations

import html
import re


ISIN_PATTERN = re.compile(r"[A-Z]{2}[A-Z0-9]{9}\d")


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


def inject_funded_identity_strip(html_text: str, *, language: str) -> str:
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

    css = """
<style id="etf-eu-funded-identity-polish">
  .funded-identity-strip { margin: 0 0 8px; padding: 7px 9px; border: 1px solid #C9D2D8; border-radius: 7px; background: #F4F7F8; font-size: 8.5pt; line-height: 1.35; }
  .funded-identity-item { white-space: nowrap; }
</style>
"""
    result = html_text[:section_start] + section_html + html_text[section_end:]
    return result.replace("</head>", css + "</head>", 1)
