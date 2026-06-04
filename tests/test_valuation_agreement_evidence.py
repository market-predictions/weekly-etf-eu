from pricing.enrich_ucits_valuation_agreement import enrich_valuation_artifact
from pricing.valuation_agreement_evidence import build_agreement_gate_evidence


CANDIDATE_ROW = {
    "registry_id": "core_us_equity_cspx",
    "isin": "IE00B5BMR087",
    "exchange": "Euronext Amsterdam",
    "exchange_ticker": "CSPX",
    "trading_currency": "EUR",
    "provider_symbol": "IE00B5BMR087-XAMS",
}


def test_yahoo_only_evidence_is_provisional_and_not_promoted():
    gate = build_agreement_gate_evidence(
        CANDIDATE_ROW,
        non_authoritative_preflight_evidence={
            "status": "priced_non_authoritative",
            "observed_date": "2026-06-02",
            "close": "100.00",
            "currency": "EUR",
        },
    )

    assert gate["status"] == "provisional"
    assert gate["valuation_artifact_action"] == "evidence_only_no_promotion"
    assert gate["valuation_grade_promoted_by_artifact"] is False
    assert gate["funding_authority"] is False
    assert gate["portfolio_mutation"] is False
    assert gate["production_delivery"] is False


def test_enrichment_adds_gate_evidence_but_keeps_authority_fields_empty():
    payload = {
        "schema_version": "ucits_valuation_prices_v1",
        "valuation_grade_row_count": 0,
        "portfolio_mutation": False,
        "production_delivery": False,
        "funding_authority": False,
        "rows": [
            {
                **CANDIDATE_ROW,
                "valuation_status": "valuation_grade_pending",
                "valuation_grade": False,
                "pricing_source": None,
                "source_authority": None,
                "observed_date": None,
                "close": None,
                "currency": None,
                "completed_session": False,
                "valuation_blockers": ["no_integrated_preferred_exchange_official_close"],
                "non_authoritative_preflight_evidence": {
                    "status": "priced_non_authoritative",
                    "observed_date": "2026-06-02",
                    "close": "100.00",
                    "currency": "EUR",
                },
            }
        ],
    }

    enriched = enrich_valuation_artifact(payload)
    row = enriched["rows"][0]

    assert enriched["valuation_grade_row_count"] == 0
    assert row["agreement_gate_evidence"]["status"] == "provisional"
    assert row["valuation_grade"] is False
    assert row["pricing_source"] is None
    assert row["source_authority"] is None
    assert row["observed_date"] is None
    assert row["close"] is None
    assert row["currency"] is None
    assert row["completed_session"] is False
    assert row["portfolio_mutation"] is False
    assert row["production_delivery"] is False
    assert row["funding_authority"] is False
    assert "agreement_gate_no_valuation_grade_agreement" in row["valuation_blockers"]
