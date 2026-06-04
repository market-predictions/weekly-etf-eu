from __future__ import annotations

import json
from pathlib import Path

from pricing.price_result_schema import PriceIdentity, STATUS_OBSERVED, STATUS_UNRESOLVED_NOT_CONFIGURED, STATUS_UNRESOLVED_PROVIDER_ERROR
from pricing.sources import twelve_data
from pricing.sources.base import PriceRequest, PriceSource
from pricing.sources.twelve_data import ERROR_POLICY_REVIEW_REQUIRED, ERROR_PROVIDER_ERROR, TwelveDataPriceSource

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "pricing" / "twelve_data"


def _fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _request(provider_config: dict | None = None) -> PriceRequest:
    return PriceRequest(
        identity=PriceIdentity(
            registry_id="core_us_equity_cspx",
            isin="IE00B5BMR087",
            exchange="Xetra",
            exchange_ticker="SXR8",
            trading_currency="EUR",
            provider_symbol="SXR8 GY",
        ),
        provider_config=provider_config or {
            "paid_source_policy_reviewed": True,
            "symbol": "SXR8",
            "exchange": "XETR",
            "expected_currency": "EUR",
            "api_key": "fixture-token",
        },
    )


def test_twelve_data_resolved_close_from_fixture(monkeypatch, tmp_path):
    monkeypatch.setattr(twelve_data, "_http_get_json", lambda url: _fixture("resolved_time_series.json"))

    source = TwelveDataPriceSource(base_url="https://fixture.invalid", raw_evidence_dir=tmp_path)
    result = source.fetch_eod_close(_request())
    row = result.as_dict()

    assert isinstance(source, PriceSource)
    assert row["resolved"] is True
    assert row["status"] == STATUS_OBSERVED
    assert row["source_id"] == "twelve_data"
    assert row["license_class"] == "provider_paid"
    assert row["authority_tier"] == "diagnostic_candidate_source"
    assert row["observed_date"] == "2026-06-02"
    assert row["close"] == "632.40"
    assert row["currency"] == "EUR"
    assert row["completed_session"] is True
    assert row["portfolio_mutation"] is False
    assert row["production_delivery"] is False
    assert row["funding_authority"] is False
    assert Path(row["source_lineage"]["raw_evidence_path"]).exists()
    assert row["source_lineage"]["raw_evidence"]["valuation_grade_by_adapter"] is False


def test_twelve_data_requires_policy_review():
    result = TwelveDataPriceSource(base_url="https://fixture.invalid").fetch_eod_close(
        _request({"symbol": "SXR8", "api_key": "fixture-token"})
    )
    row = result.as_dict()

    assert row["resolved"] is False
    assert row["status"] == STATUS_UNRESOLVED_NOT_CONFIGURED
    assert ERROR_POLICY_REVIEW_REQUIRED in row["errors"]


def test_twelve_data_provider_error_is_typed(monkeypatch):
    monkeypatch.setattr(twelve_data, "_http_get_json", lambda url: _fixture("provider_error.json"))

    result = TwelveDataPriceSource(base_url="https://fixture.invalid").fetch_eod_close(_request())
    row = result.as_dict()

    assert row["resolved"] is False
    assert row["status"] == STATUS_UNRESOLVED_PROVIDER_ERROR
    assert ERROR_PROVIDER_ERROR in row["errors"]
    assert row["close"] is None
    assert row["completed_session"] is False
