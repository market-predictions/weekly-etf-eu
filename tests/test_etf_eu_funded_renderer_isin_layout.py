from __future__ import annotations

from runtime.render_etf_eu_client_grade_v2_funded import ISIN_TOKEN_CSS, _analyst_sections


def test_funded_and_pricing_isins_render_as_nonwrapping_tokens() -> None:
    isin = "IE00B5BMR087"
    state = {
        "portfolio": {
            "positions": [{"ticker": "CSPX", "isin": isin}],
            "cash_eur": 0.0,
            "nav_eur": 1.0,
            "derived_valuation": {"lines": []},
        },
        "pricing": {"rows": [{"ticker": "CSPX", "isin": isin}]},
        "verification_funnel": {},
        "next_run_input": {},
    }

    rendered = _analyst_sections(state, "en")
    token = f'<span class="isin-token">{isin}</span>'

    assert rendered.count(token) == 2
    assert "white-space: nowrap;" in ISIN_TOKEN_CSS
    assert "overflow-wrap: normal;" in ISIN_TOKEN_CSS
