from datetime import date

from pricing.build_current_session_close_results import resolve_previous_session_close_date


def test_same_day_after_session_is_accepted() -> None:
    resolved, mode = resolve_previous_session_close_date(
        report_date=date(2026, 8, 5),
        last_trade_date=date(2026, 8, 5),
        observed_after_report_session=True,
    )
    assert resolved == date(2026, 8, 5)
    assert mode == "same_session_completed_close"


def test_next_session_rollover_is_accepted() -> None:
    resolved, mode = resolve_previous_session_close_date(
        report_date=date(2026, 8, 5),
        last_trade_date=date(2026, 8, 6),
        observed_after_report_session=True,
    )
    assert resolved == date(2026, 8, 5)
    assert mode == "next_session_previous_close_rollover"


def test_weekend_rollover_is_accepted() -> None:
    resolved, mode = resolve_previous_session_close_date(
        report_date=date(2026, 8, 7),
        last_trade_date=date(2026, 8, 10),
        observed_after_report_session=True,
    )
    assert resolved == date(2026, 8, 7)
    assert mode == "next_session_previous_close_rollover"


def test_stale_previous_close_is_rejected() -> None:
    resolved, mode = resolve_previous_session_close_date(
        report_date=date(2026, 8, 4),
        last_trade_date=date(2026, 8, 6),
        observed_after_report_session=True,
    )
    assert resolved is None
    assert mode is None


def test_same_day_before_session_end_is_rejected() -> None:
    resolved, mode = resolve_previous_session_close_date(
        report_date=date(2026, 8, 5),
        last_trade_date=date(2026, 8, 5),
        observed_after_report_session=False,
    )
    assert resolved is None
    assert mode is None
