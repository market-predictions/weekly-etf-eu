from runtime.additive_etf_eu_cockpit_front_page import SUPPRESSED_SUMMARY_CLASS, inject
from runtime.render_etf_eu_cockpit_front_page import FRONT_PAGE_MARKER


def sample_state():
    return {
        "state_valid": True,
        "report_date": "2026-07-17",
        "portfolio": {
            "starting_capital_eur": 100000.0,
            "nav_eur": 100016.6,
            "cash_eur": 60439.44,
            "position_count": 3,
            "positions": [
                {"ticker": "VWCE", "isin": "IE00BK5BQT80", "shares": 151, "shares_delta_this_run": 151, "current_weight_pct": 24.959177, "verification_status": "verified_ucits_trading_line"},
                {"ticker": "EUNA", "isin": "IE00BDBRDM35", "shares": 1526, "shares_delta_this_run": 1526, "current_weight_pct": 7.495996, "verification_status": "verified_ucits_trading_line"},
                {"ticker": "SXR8", "isin": "IE00B5BMR087", "shares": 10, "shares_delta_this_run": 0, "current_weight_pct": 7.115419, "verification_status": "verified_ucits_trading_line"},
            ],
        },
        "pricing": {"as_of": "2026-07-17"},
        "macro": {"regime": "Risk-on growth", "regime_nl": "Risk-on groei", "confidence_pct": 66},
        "equity_curve": {"points": [{"date": "2026-05-30", "nav_eur": 100000.0}, {"date": "2026-07-17", "nav_eur": 100016.6}]},
    }


def classic(language):
    investor = "Beleggersrapport" if language == "nl" else "Investor report"
    analyst = "Analistenrapport" if language == "nl" else "Analyst report"
    sections = "".join(f'<span class="badge">{n}</span>' for n in range(1, 16))
    return f'<!doctype html><html><head></head><body><main><div>{investor}</div><div class="summary-strip">summary</div>{sections}<div>{analyst}</div></main></body></html>'


def test_disabled_and_invalid_preserve_classic_html():
    source = classic("nl")
    assert inject(source, state=sample_state(), language="nl", feature_value="disabled").html == source
    assert inject(source, state=sample_state(), language="nl", feature_value="yes").html == source


def test_enabled_browser_preserves_order_and_sections():
    result = inject(classic("nl"), state=sample_state(), language="nl", feature_value="enabled", render_mode="browser")
    assert result.status == "enabled"
    assert result.html.count(FRONT_PAGE_MARKER) == 1
    assert result.html.count(SUPPRESSED_SUMMARY_CLASS) == 1
    assert result.html.index(FRONT_PAGE_MARKER) < result.html.index("Beleggersrapport") < result.html.index("Analistenrapport")
    assert all(f'<span class="badge">{n}</span>' in result.html for n in range(1, 16))
    assert "3/3" in result.html


def test_email_surface_uses_inline_presentation():
    result = inject(classic("en"), state=sample_state(), language="en", feature_value="enabled", render_mode="email")
    front = result.html[result.html.index(FRONT_PAGE_MARKER):result.html.index("</section>")]
    assert "style=" in front
    assert "<style" not in front.lower()
    assert "Funded ISINs" in front and "3/3" in front
