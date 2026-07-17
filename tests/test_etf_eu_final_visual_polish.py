from __future__ import annotations

from runtime.inject_etf_eu_funded_identity_strip import inject_funded_identity_strip


def _funded_rows(status: str) -> str:
    return (
        "<tr><td>VWCE</td><td>Vanguard</td><td>IE00BK5BQT80</td><td>151</td><td>€ 165.32</td><td>2026-07-16</td><td>€ 24,963.32</td><td>24.96%</td><td>25.00%</td><td>" + status + "</td></tr>"
        "<tr><td>EUNA</td><td>iShares Bonds</td><td>IE00BDBRDM35</td><td>1,526</td><td>€ 4.91</td><td>2026-07-14</td><td>€ 7,497.24</td><td>7.50%</td><td>7.50%</td><td>" + status + "</td></tr>"
        "<tr><td>SXR8</td><td>iShares S&amp;P 500</td><td>IE00B5BMR087</td><td>10</td><td>€ 711.66</td><td>2026-07-16</td><td>€ 7,116.60</td><td>7.12%</td><td>7.50%</td><td>" + status + "</td></tr>"
    )


def test_english_funded_headers_are_visually_separated() -> None:
    headers = (
        "<thead><tr><th>Trading line</th><th>Fund</th><th>ISIN</th><th>Shares</th>"
        "<th>Price</th><th>Pricing date</th><th>Market value</th><th>Weight</th>"
        "<th>Phase target</th><th>Status</th></tr></thead>"
    )
    html = (
        '<html><head></head><body><section><span>Current-position review</span>'
        '<div class="note-box">Model</div><table class="data-table">'
        + headers
        + "<tbody>"
        + _funded_rows("Model position · no brokerage order")
        + "</tbody></table></section></body></html>"
    )
    output = inject_funded_identity_strip(html, language="en")
    assert "<th>Phase target</th>" not in output
    assert "<th>Target</th><th>Status</th>" in output
    assert ".funded-position-table th:nth-child(2) { width: 20%; }" in output
    assert ".funded-position-table th:nth-child(9) { width: 8%; }" in output
    assert ".funded-position-table th:nth-child(10) { width: 11%; }" in output


def test_next_run_panel_starts_on_a_new_page_without_breaking_idempotence() -> None:
    rows = _funded_rows("Modelpositie · geen brokerorder")
    html = (
        '<html><head></head><body>'
        '<section><span>Review huidige posities</span><div class="note-box">Model</div>'
        '<table class="data-table"><tbody>' + rows + "</tbody></table></section>"
        '<section class="panel "><div class="section-head"><span class="badge">14</span>'
        '<span class="section-title">Input voor de volgende run</span></div><ul><li>State</li></ul></section>'
        "</body></html>"
    )
    output = inject_funded_identity_strip(html, language="nl")
    assert 'class="panel next-run-panel"' in output
    assert ".next-run-panel { break-before: page; page-break-before: always; }" in output
    assert inject_funded_identity_strip(output, language="nl") == output
