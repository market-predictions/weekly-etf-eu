from __future__ import annotations

from datetime import date

from pricing.provider_close_price_engine import latest_completed, normalize_date, usable_close


def test_usable_close_rejects_invalid_values() -> None:
    assert usable_close(None) is None
    assert usable_close(0) is None
    assert usable_close(-1) is None
    assert usable_close("nan") is None
    assert usable_close("12.34") == 12.34


def test_normalize_date_supports_iso_and_epoch() -> None:
    assert normalize_date("2026-07-31T00:00:00Z") == date(2026, 7, 31)
    assert normalize_date(1753920000) is not None


def test_latest_completed_respects_cutoff() -> None:
    rows = [
        (date(2026, 7, 30), 10.0),
        (date(2026, 7, 31), 11.0),
        (date(2026, 8, 1), 12.0),
    ]
    assert latest_completed(rows, date(2026, 7, 31)) == (date(2026, 7, 31), 11.0)
