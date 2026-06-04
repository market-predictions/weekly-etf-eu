from runtime.etf_eu_fundability_surface import fundability_surface_section


def _payload():
    return {
        "candidate_promotion": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "candidate_count": 1,
        "not_fundable_count": 1,
        "rows": [
            {
                "fund_name": "iShares Core S&P 500 UCITS ETF USD (Acc)",
                "isin": "IE00B5BMR087",
                "fundability_gate_status": "not_fundable_blocked",
                "gate_blockers": ["pricing_quality:valuation_grade_false", "decision:portfolio_promotion_decision_missing"],
                "gates": {
                    "pricing_quality": {"status": "blocked", "blockers": ["valuation_grade_false"]},
                    "decision": {"status": "blocked", "blockers": ["portfolio_promotion_decision_missing"]},
                },
            }
        ],
    }


def test_dutch_fundability_surface_shows_gate_without_promotion():
    section = fundability_surface_section(_payload(), language="nl")

    assert "Fundability gate status" in section
    assert "fundability gate status is zichtbaar" in section
    assert "not_fundable_blocked" in section
    assert "pricing_quality:valuation_grade_false" in section
    assert "candidate_promotion=false" in section
    assert "funding_authority=false" in section
    assert "portfolio_mutation=false" in section
    assert "production_delivery=false" in section
    assert "promoveert geen kandidaat naar fundable" in section
    assert "candidate_promotion=true" not in section


def test_english_fundability_surface_is_operator_companion_safe():
    section = fundability_surface_section(_payload(), language="en")

    assert "Fundability gate status" in section
    assert "does not promote any candidate to fundable" in section
    assert "candidate_promotion=false" in section
    assert "funding_authority=false" in section
    assert "portfolio_mutation=false" in section
    assert "production_delivery=false" in section
    assert "candidate_promotion=true" not in section
