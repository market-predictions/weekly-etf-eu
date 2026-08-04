from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Any
from zoneinfo import ZoneInfo

BERLIN = ZoneInfo("Europe/Berlin")


def positive_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def report_date_regular_market_close(
    meta: dict[str, Any],
    *,
    report_date: date,
    observed_at_utc: datetime,
) -> dict[str, Any] | None:
    """Return a completed Yahoo regular-session close when daily bars lag.

    Yahoo's German daily-history array can remain one session behind after the
    Xetra close, while chart metadata already exposes regularMarketPrice and
    regularMarketTime for the completed report-date session. The currentTradingPeriod
    block can roll to the next session after midnight, so completion is proven by:

    1. regularMarketTime resolves to the requested report date in Europe/Berlin;
    2. regularMarketPrice is positive;
    3. either the observation is on a later Berlin calendar date, or the
       observation is after the report-date regular-session end supplied by
       currentTradingPeriod.

    The caller still validates symbol, venue and currency metadata and still
    compares the result with an independent provider.
    """

    try:
        regular_timestamp = int(meta.get("regularMarketTime"))
    except (TypeError, ValueError):
        return None
    regular_datetime = datetime.fromtimestamp(regular_timestamp, tz=timezone.utc).astimezone(BERLIN)
    if regular_datetime.date() != report_date:
        return None
    regular_price = positive_float(meta.get("regularMarketPrice"))
    if regular_price is None:
        return None

    observed_local = observed_at_utc.astimezone(BERLIN)
    completed = observed_local.date() > report_date
    completion_mode = "observed_on_later_berlin_date"

    if not completed:
        current_period = meta.get("currentTradingPeriod") if isinstance(meta.get("currentTradingPeriod"), dict) else {}
        regular_period = current_period.get("regular") if isinstance(current_period.get("regular"), dict) else {}
        try:
            regular_end = datetime.fromtimestamp(int(regular_period.get("end")), tz=timezone.utc)
        except (TypeError, ValueError, OSError):
            regular_end = None
        if regular_end is not None and regular_end.astimezone(BERLIN).date() == report_date:
            completed = observed_at_utc >= regular_end
            completion_mode = "observed_after_report_date_regular_period_end"

    if not completed:
        return None

    return {
        "close_date": report_date.isoformat(),
        "close_price": regular_price,
        "regular_market_timestamp": regular_timestamp,
        "regular_market_time_berlin": regular_datetime.isoformat(),
        "observed_at_utc": observed_at_utc.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "completion_mode": completion_mode,
        "source_field": "meta.regularMarketPrice",
        "timestamp_field": "meta.regularMarketTime",
    }
