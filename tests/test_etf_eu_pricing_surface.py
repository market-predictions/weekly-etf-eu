from runtime.etf_eu_pricing_surface import pricing_surface_section


def test_pricing_surface_shows_agreement_gate_evidence_without_authority():
    payload = {
        "rows": [
            {
                "fund_name": "iShares Core S&P 500 UCITS ETF",
                "isin": "IE00B5BMR087",
                "exchange_ticker": "CSPX",
                "trading_currency": "EUR",
                "exchange": "Euronext Amsterdam",
                "agreement_gate_evidence": {
                    "status": "provisional",
                    "agreed_observed_date": "2026-06-02",
                    "agreed_close": None,
                    "agreed_currency": None,
                    "agreement_source_ids": [],
                },
            }
        ]
    }

    section = pricing_surface_section(payload, language="en")

    assert "Agreement-gate pricing surface" in section
    assert "CSPX / EUR / Euronext Amsterdam" in section
    assert "status=provisional" in section
    assert "not funded; no valuation authority" in section
    assert "buy recommendation" in section


def test_pricing_surface_dutch_is_client_safe():
    payload = {"rows": []}

    section = pricing_surface_section(payload, language="nl")

    assert "Agreement-gate pricing oppervlak" in section
    assert "geen koopadvies" in section
    assert "geen waarderingsautoriteit" in section
    assert "niet gefinancierd" in section
