from __future__ import annotations

from pathlib import Path

from pricing.price_result_schema import (
    AUTHORITY_DIAGNOSTIC_CANDIDATE_SOURCE,
    LICENSE_PROVIDER_FREE_PERSONAL,
    STATUS_OBSERVED,
    STATUS_UNRESOLVED_NO_DATA,
    STATUS_UNRESOLVED_NOT_CONFIGURED,
    PriceIdentity,
    PriceResult,
)
from pricing.sources.base import PriceRequest, PriceSource
from pricing.sources.stooq import StooqEodAdapter


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "pricing" / "stooq"
OVERRIDES_PATH = Path("config/source_symbol_overrides/stooq.yml")


def _identity(provider_symbol: str = "") -> PriceIdentity:
    return PriceIdentity(
        registry_id="core_us_equity_cspx",
        isin="IE00B5BMR087",
        exchange="London Stock Exchange",
        exchange_ticker="CSPX",
        trading_currency="USD",
        provider_symbol=provider_symbol,
    )


def test_stooq_adapter_resolves_latest_fixture_close_without_network() -> None:
    calls: list[str] = []

    def fake_http_get(url: str) -> str:
        calls.append(url)
        return (FIXTURE_DIR / "cspx_daily.csv").read_text(encoding="utf-8")

    adapter: PriceSource = StooqEodAdapter(overrides_path=OVERRIDES_PATH, http_get=fake_http_get)
    result = adapter.fetch_eod_close(PriceRequest(identity=_identity()))

    assert isinstance(result, PriceResult)
    assert result.status == STATUS_OBSERVED
    assert result.is_resolved is True
    assert result.identity.provider_symbol == "cspx.uk"
    assert result.observed_date == "2026-06-01"
    assert str(result.close) == "678.11"
    assert result.currency == "USD"
    assert result.completed_session is True
    assert result.lineage.source_id == "stooq"
    assert result.lineage.license_class == LICENSE_PROVIDER_FREE_PERSONAL
    assert result.lineage.authority_tier == AUTHORITY_DIAGNOSTIC_CANDIDATE_SOURCE
    assert calls and "s=cspx.uk" in calls[0]
    assert result.lineage.raw_evidence["row"]["Close"] == "678.11"

    result_dict = result.as_dict()
    assert result_dict["portfolio_mutation"] is False
    assert result_dict["production_delivery"] is False
    assert result_dict["funding_authority"] is False


def test_stooq_adapter_returns_unresolved_for_missing_mapping() -> None:
    adapter = StooqEodAdapter(overrides_path=OVERRIDES_PATH, http_get=lambda _url: "should not be called")
    result = adapter.fetch_eod_close(
        PriceRequest(
            identity=PriceIdentity(
                registry_id="unknown_candidate",
                isin="IE0000000000",
                exchange="Xetra",
                exchange_ticker="MISS",
                trading_currency="EUR",
                provider_symbol="",
            )
        )
    )

    assert isinstance(result, PriceResult)
    assert result.status == STATUS_UNRESOLVED_NOT_CONFIGURED
    assert result.is_unresolved is True
    assert result.close is None
    assert result.observed_date is None
    assert result.completed_session is False
    assert result.errors == ("no_explicit_stooq_symbol_mapping_for_trading_line",)

    result_dict = result.as_dict()
    assert result_dict["portfolio_mutation"] is False
    assert result_dict["production_delivery"] is False
    assert result_dict["funding_authority"] is False


def test_stooq_adapter_returns_unresolved_for_no_data_fixture() -> None:
    def fake_http_get(_url: str) -> str:
        return (FIXTURE_DIR / "no_data.csv").read_text(encoding="utf-8")

    adapter = StooqEodAdapter(overrides_path=OVERRIDES_PATH, http_get=fake_http_get)
    result = adapter.fetch_eod_close(PriceRequest(identity=_identity()))

    assert isinstance(result, PriceResult)
    assert result.status == STATUS_UNRESOLVED_NO_DATA
    assert result.is_unresolved is True
    assert result.close is None
    assert result.observed_date is None
    assert result.identity.provider_symbol == "cspx.uk"
    assert result.errors == ("stooq_no_data",)
    assert result.as_dict()["funding_authority"] is False
