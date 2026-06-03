from __future__ import annotations

import json
from pathlib import Path

import pytest

from pricing.price_result_schema import (
    AUTHORITY_CANDIDATE_VALUATION_SOURCE,
    LICENSE_PROVIDER_FREE_PERSONAL,
    PriceIdentity,
    PriceResult,
    SourceLineage,
    STATUS_UNRESOLVED_NO_DATA,
)
from pricing.source_selection import SourceSelection, first_resolved_or_last_unresolved, select_sources
from pricing.sources import PriceRequest, StaticPriceSource


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "pricing" / "fake_price_rows.json"


def _identity(symbol: str = "CSPX.L") -> PriceIdentity:
    return PriceIdentity(
        registry_id="core_us_equity_cspx",
        isin="IE00B5BMR087",
        exchange="LSE",
        exchange_ticker="CSPX",
        trading_currency="USD",
        provider_symbol=symbol,
    )


def _lineage() -> SourceLineage:
    return SourceLineage.now(
        source_id="fake_provider",
        provider_name="Fake Provider",
        license_class=LICENSE_PROVIDER_FREE_PERSONAL,
        authority_tier=AUTHORITY_CANDIDATE_VALUATION_SOURCE,
        raw_evidence_path=str(FIXTURE_PATH),
    )


def test_price_result_observed_serializes_without_authority_flags() -> None:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    fixture = payload["CSPX.L"]
    result = PriceResult.observed(
        identity=_identity(),
        lineage=_lineage(),
        observed_date=fixture["observed_date"],
        close=fixture["close"],
        currency=fixture["currency"],
    )

    data = result.as_dict()

    assert result.is_resolved is True
    assert data["status"] == "observed"
    assert data["close"] == "650.25"
    assert data["currency"] == "USD"
    assert data["completed_session"] is True
    assert data["portfolio_mutation"] is False
    assert data["production_delivery"] is False
    assert data["funding_authority"] is False


def test_unresolved_result_rejects_close_value() -> None:
    with pytest.raises(ValueError, match="unresolved PriceResult must not include close"):
        PriceResult(
            identity=_identity("MISSING"),
            lineage=_lineage(),
            status=STATUS_UNRESOLVED_NO_DATA,
            close="1.0",  # type: ignore[arg-type]
        )


def test_static_fake_provider_returns_typed_unresolved_for_missing_symbol() -> None:
    source = StaticPriceSource(
        source_id="fake_provider",
        provider_name="Fake Provider",
        license_class=LICENSE_PROVIDER_FREE_PERSONAL,
        authority_tier=AUTHORITY_CANDIDATE_VALUATION_SOURCE,
        rows={},
    )

    result = source.fetch_eod_close(request=PriceRequest(identity=_identity("MISSING")))

    assert result.is_unresolved is True
    assert result.status == STATUS_UNRESOLVED_NO_DATA
    assert "no_static_price_for_provider_symbol:MISSING" in result.errors


def test_config_driven_selection_returns_first_resolved_result() -> None:
    observed = PriceResult.observed(
        identity=_identity(),
        lineage=_lineage(),
        observed_date="2026-06-02",
        close="650.25",
        currency="USD",
    )
    first = StaticPriceSource(
        source_id="missing_first",
        provider_name="Missing First",
        license_class=LICENSE_PROVIDER_FREE_PERSONAL,
        authority_tier=AUTHORITY_CANDIDATE_VALUATION_SOURCE,
        rows={},
    )
    second = StaticPriceSource(
        source_id="fake_provider",
        provider_name="Fake Provider",
        license_class=LICENSE_PROVIDER_FREE_PERSONAL,
        authority_tier=AUTHORITY_CANDIDATE_VALUATION_SOURCE,
        rows={"CSPX.L": observed},
    )
    selection = SourceSelection.from_policy_row({"source_order": [{"source_id": "missing_first"}, {"source_id": "fake_provider"}]})
    sources = select_sources(selection, {"missing_first": first, "fake_provider": second})

    result = first_resolved_or_last_unresolved(_identity(), sources)

    assert result.is_resolved is True
    assert result.close == observed.close
    assert result.lineage.source_id == "fake_provider"


def test_config_driven_selection_returns_not_configured_when_no_sources_available() -> None:
    result = first_resolved_or_last_unresolved(_identity(), [])

    assert result.is_unresolved is True
    assert result.status == "unresolved_not_configured"
    assert "no_price_sources_supplied" in result.errors
