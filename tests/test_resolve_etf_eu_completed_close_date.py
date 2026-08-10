from datetime import datetime, timezone

from tools.resolve_etf_eu_completed_close_date import plausible_completed_close


def test_monday_afternoon_uses_previous_friday() -> None:
    now = datetime(2026, 8, 10, 14, 0, tzinfo=timezone.utc)  # 16:00 Amsterdam
    assert str(plausible_completed_close(now)) == "2026-08-07"


def test_monday_evening_may_use_monday_subject_to_provider_gate() -> None:
    now = datetime(2026, 8, 10, 17, 30, tzinfo=timezone.utc)  # 19:30 Amsterdam
    assert str(plausible_completed_close(now)) == "2026-08-10"


def test_weekend_uses_friday() -> None:
    now = datetime(2026, 8, 9, 12, 0, tzinfo=timezone.utc)
    assert str(plausible_completed_close(now)) == "2026-08-07"
