from __future__ import annotations

import json
from pathlib import Path

from pricing.price_result_schema import PriceIdentity, STATUS_OBSERVED, STATUS_UNRESOLVED_NO_DATA, STATUS_UNRESOLVED_NOT_CONFIGURED
from pricing.sources import boerse_frankfurt
from pricing.sources.base import PriceRequest, PriceSource
from pricing.sources.boerse_frankfurt import (
    BoerseFrankfurtXetraPriceSource,
    ERROR_CURRENCY_UNCERTAIN,
    ERROR_MISSING_CLOSE,
    ERROR_MISSING_ISIN,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "pricing" / "boerse_frankfurt"


def _fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _request(isin: str = "IE00B5BMR087") -> PriceRequest:
    return PriceRequest(
        identity=PriceIdentity(
            registry_id="core_us_equity_cspx",
            isin=isin,
            exchange="Xetra",
            exchange_ticker="SXR8",
            trading_currency="EUR",
            provider_symbol="IE00B5BMR087.XETR",
        ),
        provider_config={"venue_mic": "XETR"},
    )


def test_boerse_frankfurt_resolved_close_from_fixture(monkeypatch, tmp_path):
    monkeypatch.setattr(boerse_frankfurt, "_http_get_json", lambda url: _fixture("resolved_close.json"))

    source = BoerseFrankfurtXetraPriceSource(base_url="https://fixture.invalid", raw_evidence_dir=tmp_path)
    result = source.fetch_eod_close(_request())
    row = result.as_dict()

    assert isinstance(source, PriceSource)
    assert row["resolved"] is True
    assert row["status"] == STATUS_OBSERVED
    assert row["source_id"] == "boerse_frankfurt_xetra"
    assert row["isin"] == "IE00B5BMR087"
    assert row["exchange_ticker"] == "SXR8"
    assert row["observed_date"] == "2026-06-02"
    assert row["close"] == "632.40"
    assert row["currency"] == "EUR"
    assert row["completed_session"] is True
    assert row["license_class"] == "unknown"
    assert row["authority_tier"] == "diagnostic_candidate_source"
    assert row["portfolio_mutation"] is False
    assert row["production_delivery"] is False
    assert row["funding_authority"] is False
    assert row["source_lineage"]["raw_evidence_path"] is not None
    assert Path(row["source_lineage"]["raw_evidence_path"]).exists()
    raw_evidence = row["source_lineage"]["raw_evidence"]
    assert raw_evidence["query_mode"] == "isin_plus_mic"
    assert raw_evidence["venue_mic"] == "XETR"
    assert raw_evidence["license_note"] == "undocumented_free_source_pending_license_review"
    assert raw_evidence["authority_note"] == "exchange_candidate_evidence_only_not_valuation_authority"
    assert raw_evidence["valuation_grade_by_adapter"] is False


def test_boerse_frankfurt_missing_close_is_typed_unresolved(monkeypatch):
    monkeypatch.setattr(boerse_frankfurt, "_http_get_json", lambda url: _fixture("no_close.json"))

    result = BoerseFrankfurtXetraPriceSource(base_url="https://fixture.invalid").fetch_eod_close(_request())
    row = result.as_dict()

    assert row["resolved"] is False
    assert row["status"] == STATUS_UNRESOLVED_NO_DATA
    assert ERROR_MISSING_CLOSE in row["errors"]
    assert row["close"] is None
    assert row["completed_session"] is False
    assert row["portfolio_mutation"] is False
    assert row["production_delivery"] is False
    assert row["funding_authority"] is False


def test_boerse_frankfurt_missing_currency_is_typed_unresolved(monkeypatch):
    monkeypatch.setattr(boerse_frankfurt, "_http_get_json", lambda url: _fixture("currency_uncertain.json"))

    result = BoerseFrankfurtXetraPriceSource(base_url="https://fixture.invalid").fetch_eod_close(_request())
    row = result.as_dict()

    assert row["resolved"] is False
    assert row["status"] == STATUS_UNRESOLVED_NO_DATA
    assert ERROR_CURRENCY_UNCERTAIN in row["errors"]
    assert row["close"] is None
    assert row["observed_date"] is None
    assert row["completed_session"] is False


def test_boerse_frankfurt_requires_isin():
    result = BoerseFrankfurtXetraPriceSource(base_url="https://fixture.invalid").fetch_eod_close(_request(isin=""))
    row = result.as_dict()

    assert row["resolved"] is False
    assert row["status"] == STATUS_UNRESOLVED_NOT_CONFIGURED
    assert ERROR_MISSING_ISIN in row["errors"]
    assert row["portfolio_mutation"] is False
    assert row["production_delivery"] is False
    assert row["funding_authority"] is False
