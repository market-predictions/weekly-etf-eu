from __future__ import annotations

import re

from bs4 import BeautifulSoup

from runtime.inline_etf_eu_email_report_styles import MARKER_ATTRIBUTE, inline_email_report_styles


def sample_html() -> str:
    return '''<!doctype html><html><head><style>.panel{background:red}</style></head><body><main>
<section class="etf-eu-cockpit-page" style="background:#F6F1E7"><div style="font-size:20px">Cockpit</div></section>
<header class="hero"><div class="hero-row"><div><div class="masthead">Weekly ETF EU</div><div class="hero-date">2026-07-17</div></div><div class="hero-type">Investor report</div></div></header>
<div class="hero-rule"></div>
<section class="panel"><div class="section-head"><span class="badge">1</span><span class="section-title">Decision cockpit</span></div>
<div class="note-box">Detail</div><table class="data-table"><thead><tr><th>Key</th><th>Value</th></tr></thead><tbody><tr><td>A</td><td>B</td></tr><tr><td>C</td><td>D</td></tr></tbody></table></section>
<div class="funnel-strip"><div class="funnel-card"><div class="funnel-value">3</div><div class="funnel-label">Funded</div></div></div>
<div class="funded-identity-strip"><span class="funded-identity-item">VWCE - IE00BK5BQT80</span></div>
</main></body></html>'''


def test_full_report_styles_are_inline_and_cockpit_styles_are_preserved() -> None:
    result = inline_email_report_styles(sample_html())
    soup = BeautifulSoup(result, "html.parser")
    assert soup.html[MARKER_ATTRIBUTE] == "true"
    assert "background:#F6F1E7" in soup.select_one(".etf-eu-cockpit-page").get("style", "")
    assert "background:#607887" in soup.select_one(".hero").get("style", "")
    assert "background:#FCFAF7" in soup.select_one(".panel").get("style", "")
    assert "border:1px solid #D8D5CE" in soup.select_one("th").get("style", "")
    assert "background:#FEFCF9" in soup.select("tbody tr")[1].select_one("td").get("style", "")
    assert "display:inline-block" in soup.select_one(".funnel-card").get("style", "")
    assert "white-space:nowrap" in soup.select_one(".funded-identity-item").get("style", "")


def test_head_css_removal_preserves_classic_report_hierarchy() -> None:
    result = inline_email_report_styles(sample_html())
    stripped = re.sub(r"<style\b[^>]*>.*?</style>", "", result, flags=re.IGNORECASE | re.DOTALL)
    soup = BeautifulSoup(stripped, "html.parser")
    for selector in (".hero", ".panel", ".section-head", ".badge", ".section-title", "table", "th", "td"):
        tag = soup.select_one(selector)
        assert tag is not None and tag.get("style")


def test_inliner_is_idempotent() -> None:
    first = inline_email_report_styles(sample_html())
    second = inline_email_report_styles(first)
    assert second == first
