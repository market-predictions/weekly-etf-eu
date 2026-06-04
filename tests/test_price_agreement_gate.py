from decimal import Decimal

from pricing.price_agreement_gate import (
    AGREEMENT_STATUS_BLOCKED,
    AGREEMENT_STATUS_PROVISIONAL,
    AGREEMENT_STATUS_VALUATION_GRADE,
    REASON_CURRENCY_MISMATCH,
    REASON_INDEPENDENT_SOURCE_COUNT_TOO_LOW,
    REASON_ONE_RESOLVED_SOURCE_ONLY,
    REASON_PRICE_DISAGREEMENT,
    REASON_REQUESTED_DATE_MISMATCH,
    evaluate_price_agreement,
)
from pricing.price_result_schema import PriceIdentity, PriceResult, SourceLineage


IDENTITY = PriceIdentity(
    registry_id="core_us_equity_cspx",
    isin="IE00B5BMR087",
    exchange="Euronext Amsterdam",
    exchange_ticker="CSPX",
    trading_currency="EUR",
    provider_symbol="IE00B5BMR087-XAMS",
)


def price(source_id: str, close: str, *, currency: str = "EUR", observed_date: str = "2026-06-02") -> PriceResult:
    return PriceResult.observed(
        identity=IDENTITY,
        lineage=SourceLineage.now(
            source_id=source_id,
            provider_name=source_id,
            license_class="exchange_public" if source_id in {"euronext_live", "deutsche_boerse_live"} else "issuer_public",
            authority_tier="candidate_valuation_source" if source_id in {"euronext_live", "deutsche_boerse_live"} else "diagnostic_candidate_source",
        ),
        observed_date=observed_date,
        close=close,
        currency=currency,
    )


def test_two_independent_market_close_sources_can_be_valuation_grade():
    result = evaluate_price_agreement(
        [price("euronext_live", "100.00"), price("deutsche_boerse_live", "100.01")],
        requested_date="2026-06-02",
    )

    assert result.status == AGREEMENT_STATUS_VALUATION_GRADE
    assert result.reason_codes == ("agreement_passed",)
    assert result.funding_authority is False
    assert result.portfolio_mutation is False
    assert result.production_delivery is False


def test_one_source_only_is_provisional():
    result = evaluate_price_agreement([price("euronext_live", "100.00")], requested_date="2026-06-02")

    assert result.status == AGREEMENT_STATUS_PROVISIONAL
    assert REASON_ONE_RESOLVED_SOURCE_ONLY in result.reason_codes


def test_issuer_reference_does_not_count_as_market_close_agreement():
    result = evaluate_price_agreement(
        [price("euronext_live", "100.00"), price("issuer_nav", "100.00")],
        requested_date="2026-06-02",
    )

    assert result.status == AGREEMENT_STATUS_PROVISIONAL
    assert REASON_INDEPENDENT_SOURCE_COUNT_TOO_LOW in result.reason_codes
    assert result.agreement_source_ids == ("euronext_live",)
    assert result.excluded_source_ids == ("issuer_nav",)


def test_price_disagreement_is_blocked():
    result = evaluate_price_agreement(
        [price("euronext_live", "100.00"), price("deutsche_boerse_live", "101.00")],
        requested_date="2026-06-02",
    )

    assert result.status == AGREEMENT_STATUS_BLOCKED
    assert REASON_PRICE_DISAGREEMENT in result.reason_codes
    assert result.max_abs_diff == Decimal("1.00")


def test_requested_date_mismatch_is_blocked():
    result = evaluate_price_agreement(
        [price("euronext_live", "100.00", observed_date="2026-06-01"), price("deutsche_boerse_live", "100.00", observed_date="2026-06-01")],
        requested_date="2026-06-02",
    )

    assert result.status == AGREEMENT_STATUS_BLOCKED
    assert REASON_REQUESTED_DATE_MISMATCH in result.reason_codes


def test_currency_mismatch_is_blocked():
    result = evaluate_price_agreement(
        [price("euronext_live", "100.00", currency="EUR"), price("deutsche_boerse_live", "100.00", currency="USD")],
        requested_date="2026-06-02",
    )

    assert result.status == AGREEMENT_STATUS_BLOCKED
    assert REASON_CURRENCY_MISMATCH in result.reason_codes
