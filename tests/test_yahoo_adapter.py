from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from pricing.price_result_schema import (
    AUTHORITY_NON_AUTHORITATIVE_CONNECTIVITY_ONLY,
    LICENSE_PROVIDER_FREE_PERSONAL,
    STATUS_OBSERVED,
    STATUS_UNRESOLVED_DEPENDENCY_MISSING,
    STATUS_UNRESOLVED_NO_DATA,
    STATUS_UNRESOLVED_NOT_CONFIGURED,
    STATUS_UNRESOLVED_PROVIDER_ERROR,
    PriceIdentity,
)
from pricing.sources.base import PriceRequest
from pricing.sources.yahoo import SOURCE_ID, YahooPriceSource

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "pricing" / "yahoo"


def _identity(**overrides: str) -> PriceIdentity:
    values = {
        "registry_id": "core_us_equity_cspx",
        "isin": "IE00B5BMR087",
        "exchange": "LSE",
        "exchange_ticker": "CSPX",
        "trading_currency": "USD",
        "provider_symbol": "CSPX.L",
    }
    values.update(overrides)
    return PriceIdentity(**values)


def _fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_yahoo_adapter_returns_non_authoritative_observed_result_from_fixture() -> None:
    payload = _fixture("cspx_history.json")
    source = YahooPriceSource(
        history_fetcher=lambda symbol, period: payload,
        raw_evidence_path="tests/fixtures/pricing/yahoo/cspx_history.json",
    )

    result = source.fetch_eod_close(PriceRequest(identity=_identity()))

    assert result.status == STATUS_OBSERVED
    assert result.is_resolved
    assert result.observed_date == "2026-06-02"
    assert result.close == Decimal("613.25")
    assert result.currency == "USD"
    assert result.lineage.source_id == SOURCE_ID
    assert result.lineage.license_class == LICENSE_PROVIDER_FREE_PERSONAL
    assert result.lineage.authority_tier == AUTHORITY_NON_AUTHORITATIVE_CONNECTIVITY_ONLY
    assert result.lineage.raw_evidence["valuation_grade_eligible"] is False
    assert result.lineage.raw_evidence["source_role"] == "fallback_provisional"
    assert result.lineage.raw_evidence["currency_source"] == "request_identity_trading_currency"

    as_dict = result.as_dict()
    assert as_dict["portfolio_mutation"] is False
    assert as_dict["production_delivery"] is False
    assert as_dict["funding_authority"] is False


def test_yahoo_adapter_honours_requested_date_when_present() -> None:
    payload = _fixture("cspx_history.json")
    source = YahooPriceSource(history_fetcher=lambda symbol, period: payload)

    result = source.fetch_eod_close(PriceRequest(identity=_identity(), requested_date="2026-05-29"))

    assert result.is_resolved
    assert result.observed_date == "2026-05-29"
    assert result.close == Decimal("611.20")


def test_yahoo_adapter_returns_unresolved_for_empty_history() -> None:
    payload = _fixture("empty_history.json")
    source = YahooPriceSource(history_fetcher=lambda symbol, period: payload)

    result = source.fetch_eod_close(PriceRequest(identity=_identity()))

    assert result.is_unresolved
    assert result.status == STATUS_UNRESOLVED_NO_DATA
    assert "missing_history" in result.errors


def test_yahoo_adapter_returns_unresolved_for_missing_close() -> None:
    payload = _fixture("missing_close_history.json")
    source = YahooPriceSource(history_fetcher=lambda symbol, period: payload)

    result = source.fetch_eod_close(PriceRequest(identity=_identity()))

    assert result.is_unresolved
    assert result.status == STATUS_UNRESOLVED_NO_DATA
    assert "missing_close:2026-06-02" in result.errors


def test_yahoo_adapter_returns_unresolved_for_missing_currency() -> None:
    payload = _fixture("cspx_history.json")
    source = YahooPriceSource(history_fetcher=lambda symbol, period: payload)

    result = source.fetch_eod_close(PriceRequest(identity=_identity(trading_currency="")))

    assert result.is_unresolved
    assert result.status == STATUS_UNRESOLVED_NO_DATA
    assert "missing_currency:2026-06-02" in result.errors


def test_yahoo_adapter_returns_unresolved_for_missing_provider_symbol() -> None:
    source = YahooPriceSource(history_fetcher=lambda symbol, period: _fixture("cspx_history.json"))

    result = source.fetch_eod_close(PriceRequest(identity=_identity(provider_symbol="")))

    assert result.is_unresolved
    assert result.status == STATUS_UNRESOLVED_NOT_CONFIGURED
    assert "missing_provider_symbol" in result.errors


def test_yahoo_adapter_maps_yfinance_import_failure_to_dependency_missing() -> None:
    def raise_missing_yfinance(symbol: str, period: str) -> None:
        raise ModuleNotFoundError("No module named 'yfinance'", name="yfinance")

    source = YahooPriceSource(history_fetcher=raise_missing_yfinance)

    result = source.fetch_eod_close(PriceRequest(identity=_identity()))

    assert result.is_unresolved
    assert result.status == STATUS_UNRESOLVED_DEPENDENCY_MISSING
    assert result.errors[0].startswith("yfinance_dependency_missing:")


def test_yahoo_adapter_maps_other_provider_exception_to_provider_error() -> None:
    def raise_provider_error(symbol: str, period: str) -> None:
        raise RuntimeError("temporary provider failure")

    source = YahooPriceSource(history_fetcher=raise_provider_error)

    result = source.fetch_eod_close(PriceRequest(identity=_identity()))

    assert result.is_unresolved
    assert result.status == STATUS_UNRESOLVED_PROVIDER_ERROR
    assert result.errors == ("provider_exception:temporary provider failure",)
