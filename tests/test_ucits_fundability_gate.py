import json
from pathlib import Path

import pytest

from runtime.build_ucits_fundability_gate import build_fundability_gate, write_fundability_gate
from tools.validate_ucits_fundability_promotion_contract import validate_gate_artifact


REGISTRY = """
schema_version: ucits_symbol_registry_v1
funds:
  - registry_id: core_us_equity_cspx
    role: Core U.S. equity exposure
    us_research_proxy: SPY
    isin: IE00B5BMR087
    fund_name: iShares Core S&P 500 UCITS ETF USD (Acc)
    provider: iShares / BlackRock
    instrument_type: ETF
    ucits_status: confirmed
    priips_kid_status: available
    investability_status: verified_candidate_not_funded
    fundable_status: not_funded_requires_broker_and_pricing_line_confirmation
    domicile: Ireland
    distribution_policy: accumulating
    replication_method: physical_replication
    benchmark_index: S&P 500 Index
    ter_pct: 0.07
    trading_lines:
      - exchange: Xetra
        exchange_ticker: SXR8
        trading_currency: EUR
        provider_symbol: SXR8 GY
        pricing_symbol_yahoo: SXR8.DE
        line_verification_status: issuer_verified_bloomberg_ticker
        pricing_status: pending_pipeline_test
    research_proxies:
      - us_proxy: SPY
        purpose: benchmark_reference_only
        proxy_must_not_be_funded: true
"""


VALUATION_PENDING = {
    "schema_version": "ucits_valuation_prices_v1",
    "rows": [
        {
            "registry_id": "core_us_equity_cspx",
            "valuation_grade": False,
            "valuation_status": "valuation_grade_pending",
            "non_authoritative_preflight_evidence": {
                "source_id": "yahoo_yfinance",
                "status": "priced_non_authoritative",
            },
        }
    ],
}


VALUATION_GRADE = {
    "schema_version": "ucits_valuation_prices_v1",
    "rows": [
        {
            "registry_id": "core_us_equity_cspx",
            "valuation_grade": True,
            "valuation_status": "valuation_grade",
        }
    ],
}


def _write_inputs(tmp_path: Path, valuation_payload: dict = VALUATION_PENDING) -> tuple[Path, Path]:
    registry = tmp_path / "registry.yml"
    valuation = tmp_path / "valuation.json"
    registry.write_text(REGISTRY, encoding="utf-8")
    valuation.write_text(json.dumps(valuation_payload), encoding="utf-8")
    return registry, valuation


def test_build_fundability_gate_blocks_current_bootstrap_candidate(tmp_path: Path):
    registry, valuation = _write_inputs(tmp_path)

    payload = build_fundability_gate(registry, "test_run", valuation)
    row = payload["rows"][0]

    assert payload["schema_version"] == "ucits_fundability_gate_v1"
    assert payload["candidate_promotion"] is False
    assert payload["funding_authority"] is False
    assert payload["portfolio_mutation"] is False
    assert payload["production_delivery"] is False
    assert row["fundability_gate_status"] == "not_fundable_blocked"
    assert row["candidate_promotion"] is False
    assert "pricing_quality:valuation_grade_false" in row["gate_blockers"]
    assert "tradability_liquidity:liquidity_check_missing_or_not_passed" in row["gate_blockers"]
    assert "decision:portfolio_promotion_decision_missing" in row["gate_blockers"]


def test_write_and_validate_fundability_gate_artifact(tmp_path: Path):
    registry, valuation = _write_inputs(tmp_path)
    output_dir = tmp_path / "out"

    artifact_path = write_fundability_gate(registry, output_dir, "test_run", valuation)

    validate_gate_artifact(artifact_path)
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["candidate_count"] == 1
    assert payload["not_fundable_count"] == 1
    assert payload["gate_passed_no_promotion_count"] == 0


def test_even_all_gates_pass_does_not_promote_candidate(tmp_path: Path):
    registry, valuation = _write_inputs(tmp_path, VALUATION_GRADE)
    text = registry.read_text(encoding="utf-8")
    text = text.replace(
        "    research_proxies:\n      - us_proxy: SPY\n        purpose: benchmark_reference_only\n        proxy_must_not_be_funded: true\n",
        "    liquidity_check_status: passed\n    spread_check_status: passed\n    broker_availability_status: confirmed\n    portfolio_role_review_status: approved\n    alternative_comparison_status: completed\n    risk_concentration_review_status: completed\n    promotion_decision_status: approved\n    promotion_decision_reference: control/DECISION_LOG.md#test\n    research_proxies:\n      - us_proxy: SPY\n        purpose: benchmark_reference_only\n        proxy_must_not_be_funded: true\n",
    )
    registry.write_text(text, encoding="utf-8")

    payload = build_fundability_gate(registry, "test_run", valuation)
    row = payload["rows"][0]

    assert row["fundability_gate_status"] == "gate_passed_no_promotion"
    assert row["gate_blockers"] == []
    assert row["candidate_promotion"] is False
    assert payload["candidate_promotion"] is False


def test_gate_artifact_validator_rejects_candidate_promotion(tmp_path: Path):
    registry, valuation = _write_inputs(tmp_path)
    artifact_path = write_fundability_gate(registry, tmp_path / "out", "test_run", valuation)
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    payload["candidate_promotion"] = True
    bad_path = tmp_path / "bad.json"
    bad_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(RuntimeError, match="candidate_promotion_must_be_false"):
        validate_gate_artifact(bad_path)
