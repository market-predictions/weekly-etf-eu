from __future__ import annotations

from pathlib import Path

from pricing.price_result_schema import (
    AUTHORITY_DIAGNOSTIC_CANDIDATE_SOURCE,
    LICENSE_ISSUER_PUBLIC,
    STATUS_OBSERVED,
    STATUS_UNRESOLVED_NO_DATA,
    STATUS_UNRESOLVED_NOT_CONFIGURED,
    PriceIdentity,
)
from pricing.sources.base import PriceRequest
from pricing.sources.issuer_nav import IssuerNavSource


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "pricing" / "issuer_nav"


def cspx_identity() -> PriceIdentity:
    return PriceIdentity(
        registry_id="core_us_equity_cspx",
        isin="IE00B5BMR087",
        exchange="LSE",
        exchange_ticker="CSPX",
        trading_currency="USD",
        provider_symbol="CSPX.L",
    )


def test_issuer_nav_source_returns_reference_result_without_market_close_authority() -> None:
    source = IssuerNavSource()
    result = source.fetch_eod_close(
        PriceRequest(
            identity=cspx_identity(),
            provider_config={"issuer_nav_path": str(FIXTURE_DIR / "valid_cspx_nav.json")},
        )
    )

    assert result.status == STATUS_OBSERVED
    assert result.is_resolved
    assert result.observed_date == "2026-06-02"
    assert str(result.close) == "645.12"
    assert result.currency == "USD"
    assert result.lineage.license_class == LICENSE_ISSUER_PUBLIC
    assert result.lineage.authority_tier == AUTHORITY_DIAGNOSTIC_CANDIDATE_SOURCE
    assert result.lineage.raw_evidence["value_type"] == "issuer_nav_reference"
    assert result.lineage.raw_evidence["not_exchange_trading_line_close"] is True
    assert result.as_dict()["funding_authority"] is False
    assert result.as_dict()["portfolio_mutation"] is False
    assert result.as_dict()["production_delivery"] is False


def test_issuer_nav_source_returns_unresolved_for_missing_currency() -> None:
    source = IssuerNavSource()
    result = source.fetch_eod_close(
        PriceRequest(
            identity=cspx_identity(),
            provider_config={"issuer_nav_path": str(FIXTURE_DIR / "missing_currency_nav.json")},
        )
    )

    assert result.status == STATUS_UNRESOLVED_NO_DATA
    assert result.is_unresolved
    assert "issuer_nav_missing_currency" in result.errors
    assert result.close is None
    assert result.lineage.raw_evidence["value_type"] == "issuer_nav_reference"


def test_issuer_nav_source_returns_unresolved_for_missing_input() -> None:
    source = IssuerNavSource()
    result = source.fetch_eod_close(PriceRequest(identity=cspx_identity()))

    assert result.status == STATUS_UNRESOLVED_NOT_CONFIGURED
    assert result.is_unresolved
    assert "missing_issuer_nav_input" in result.errors


def test_issuer_nav_source_can_use_inline_fixture_data() -> None:
    source = IssuerNavSource()
    result = source.fetch_eod_close(
        PriceRequest(
            identity=cspx_identity(),
            provider_config={
                "issuer_nav_data": {
                    "rows": [
                        {
                            "isin": "IE00B5BMR087",
                            "exchange_ticker": "CSPX",
                            "nav_date": "2026-06-01",
                            "nav": "644.10",
                            "currency": "USD",
                        }
                    ]
                }
            },
        )
    )

    assert result.status == STATUS_OBSERVED
    assert result.observed_date == "2026-06-01"
    assert str(result.close) == "644.10"
