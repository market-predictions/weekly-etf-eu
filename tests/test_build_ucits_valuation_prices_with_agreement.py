import json
from pathlib import Path

from pricing.build_ucits_valuation_prices_with_agreement import write_valuation_artifact_with_agreement


def test_agreement_wrapper_writes_enriched_artifact(tmp_path: Path):
    registry = tmp_path / "registry.yml"
    policy = tmp_path / "policy.yml"
    candidates = tmp_path / "candidates.json"
    output = tmp_path / "out"

    registry.write_text("schema_version: test_registry\n", encoding="utf-8")
    policy.write_text(
        """
schema_version: ucits_pricing_source_policy_v1
pricing_authority_mode: valuation_grade_pending
rules:
  portfolio_mutation_from_pricing: false
  production_delivery_from_pricing: false
  funding_authority_from_pricing: false
  yfinance_default_authority: non_authoritative_connectivity_only
  twelve_data_default_accept_as_valuation_grade: false
trading_line_policies:
  - registry_id: core_us_equity_cspx
    isin: IE00B5BMR087
    exchange: Euronext Amsterdam
    exchange_ticker: CSPX
    trading_currency: EUR
    provider_symbol: IE00B5BMR087-XAMS
    source_order:
      - source_id: euronext_live
        authority: preferred_official_exchange_discovery
        valuation_grade_eligible: true
        accept_as_valuation_grade: false
""",
        encoding="utf-8",
    )
    candidates.write_text(
        json.dumps(
            {
                "candidates": [
                    {
                        "registry_id": "core_us_equity_cspx",
                        "isin": "IE00B5BMR087",
                        "fund_name": "iShares Core S&P 500 UCITS ETF",
                        "provider": "iShares",
                        "instrument_type": "UCITS ETF",
                        "ucits_status": "verified_ucits",
                        "priips_kid_status": "verified_kid_available",
                        "investability_status": "verified_candidate_not_funded",
                        "fundable_status": "not_funded",
                        "exchange": "Euronext Amsterdam",
                        "exchange_ticker": "CSPX",
                        "trading_currency": "EUR",
                        "provider_symbol": "IE00B5BMR087-XAMS",
                        "pricing_symbol_yahoo": "CSPX.AS",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    artifact_path = write_valuation_artifact_with_agreement(registry, policy, candidates, output, "test_run")
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    row = payload["rows"][0]

    assert "agreement_gate_evidence" in row
    assert payload["valuation_grade_row_count"] == 0
    assert row["valuation_grade"] is False
    assert row["pricing_source"] is None
    assert row["close"] is None
    assert row["portfolio_mutation"] is False
    assert row["production_delivery"] is False
    assert row["funding_authority"] is False
