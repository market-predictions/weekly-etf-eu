from __future__ import annotations

from pricing.canonical_pricing_authority import (
    CANONICAL_PRICING_AUTHORITY_STATUSES,
    NO_PRICING_AUTHORITY,
    canonical_pricing_authority,
)
from runtime.build_etf_eu_client_grade_report_state_v2 import _canonical_pricing_rows
from runtime.build_etf_eu_donor_discovery_bridge import _pricing_authorized


def _row(status: str, *, valuation_grade: bool = True) -> dict:
    return {
        "ticker": "VWCE",
        "isin": "IE00BK5BQT80",
        "fund_name": "Vanguard FTSE All-World UCITS ETF",
        "exchange": "Xetra",
        "currency": "EUR",
        "close_date": "2026-09-18",
        "close_price": 142.5,
        "pricing_status": "priced_non_authoritative",
        "source_agreement_status": status,
        "valuation_grade": valuation_grade,
        "completed_close_on_requested_report_date": True,
        "static_identity_binding": True,
        "static_primary_provider_symbol_binding": True,
        "primary_provider": "provider_a",
        "verification_providers": ["provider_b"] if status == "fresh_exact_verified" else [],
        "same_date_provider_count": 2 if status == "fresh_exact_verified" else 1,
        "blockers": [],
    }


def test_authorized_rows_preserve_only_canonical_authority_statuses() -> None:
    for status in ("fresh_exact_verified", "fresh_exact_unverified"):
        canonical, blockers = canonical_pricing_authority(_row(status))
        assert canonical == status
        assert blockers == []
        assert canonical in CANONICAL_PRICING_AUTHORITY_STATUSES


def test_provider_failure_status_collapses_to_no_authority_with_explicit_blockers() -> None:
    row = _row("provider_disagreement", valuation_grade=False)
    canonical, blockers = canonical_pricing_authority(row)

    assert canonical == NO_PRICING_AUTHORITY
    assert "source_authority_status:provider_disagreement" in blockers
    assert "not_valuation_grade" in blockers
    assert _pricing_authorized(row) is False


def test_normalized_report_rows_do_not_expose_second_business_status_vocabulary() -> None:
    rows = _canonical_pricing_rows(
        {
            "rows": [
                _row("fresh_exact_verified"),
                _row("provider_disagreement", valuation_grade=False),
            ]
        }
    )

    statuses = {row["authority_status"] for row in rows}
    assert statuses == {"fresh_exact_verified", NO_PRICING_AUTHORITY}
    assert all(status in CANONICAL_PRICING_AUTHORITY_STATUSES for status in statuses)
    assert all("pricing_status" not in row for row in rows)

    blocked = next(row for row in rows if row["authority_status"] == NO_PRICING_AUTHORITY)
    assert blocked["authorized"] is False
    assert blocked["valuation_grade"] is False
    assert blocked["blockers"]
