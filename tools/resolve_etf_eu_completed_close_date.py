from __future__ import annotations

import argparse
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

AMSTERDAM = ZoneInfo("Europe/Amsterdam")


def previous_weekday(day: date) -> date:
    candidate = day - timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate -= timedelta(days=1)
    return candidate


def plausible_completed_close(now: datetime) -> date:
    """Return a conservative European completed-close candidate.

    Provider evidence remains final authority. On weekdays the current date is used
    only after 18:00 Europe/Amsterdam, otherwise the previous weekday is selected.
    Exchange holidays are resolved later by the pricing same-date evidence gate.
    """
    local = now.astimezone(AMSTERDAM)
    day = local.date()
    if day.weekday() >= 5:
        while day.weekday() >= 5:
            day -= timedelta(days=1)
        return day
    if local.time() >= time(18, 0):
        return day
    return previous_weekday(day)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--requested-date")
    parser.add_argument("--now-utc")
    args = parser.parse_args()
    if args.requested_date:
        print(date.fromisoformat(args.requested_date))
        return
    now = datetime.fromisoformat(args.now_utc.replace("Z", "+00:00")) if args.now_utc else datetime.now(timezone.utc)
    print(plausible_completed_close(now))


if __name__ == "__main__":
    main()
