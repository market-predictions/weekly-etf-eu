from __future__ import annotations

import argparse
import json
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml
from zoneinfo import ZoneInfo

SCHEMA_VERSION = "yahoo_completed_session_gate_v1"
DEFAULT_SESSION_POLICY = Path("config/ucits_exchange_session_policy.yml")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def parse_date(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value or "")[:10])
    except ValueError:
        return None


def parse_hhmm(value: str) -> time:
    hour, minute = value.split(":", 1)
    return time(int(hour), int(minute))


def session_close_utc(session_date: date, venue_policy: dict[str, Any], buffer_minutes: int) -> str:
    tz = ZoneInfo(str(venue_policy["timezone"]))
    close_local = parse_hhmm(str(venue_policy["regular_close_local"]))
    local_dt = datetime.combine(session_date, close_local, tzinfo=tz) + timedelta(minutes=buffer_minutes)
    return local_dt.astimezone(timezone.utc).isoformat()


def evaluate_row(row: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    venue_name = str(row.get("exchange") or "")
    venue = (policy.get("venues") or {}).get(venue_name)
    observed_date = parse_date(row.get("observed_close_date"))
    now_utc = datetime.now(timezone.utc)
    max_staleness = int(policy.get("max_staleness_days") or 5)
    buffer_minutes = int(policy.get("post_close_buffer_minutes") or 30)
    errors: list[str] = []
    if not venue:
        errors.append("venue_policy_missing")
    if observed_date is None:
        errors.append("observed_close_date_missing")
    regular_session = False
    holiday = False
    session_complete = False
    close_ready_utc = None
    staleness_days = None
    if venue and observed_date:
        weekday_allowed = observed_date.weekday() in [int(day) for day in venue.get("regular_weekdays") or []]
        holiday = observed_date.isoformat() in set(str(day) for day in venue.get("static_holiday_dates_2026") or [])
        regular_session = bool(weekday_allowed and not holiday)
        close_ready_utc = session_close_utc(observed_date, venue, buffer_minutes)
        session_complete = bool(regular_session and now_utc >= datetime.fromisoformat(close_ready_utc))
        staleness_days = (now_utc.date() - observed_date).days
    staleness_ok = staleness_days is not None and 0 <= staleness_days <= max_staleness
    gates = {
        "venue_policy_present": venue is not None,
        "observed_close_date_present": observed_date is not None,
        "regular_session_date": regular_session,
        "session_close_time_elapsed": session_complete,
        "staleness_within_limit": staleness_ok,
    }
    passed = all(gates.values())
    failed = [key for key, value in gates.items() if value is not True]
    return {
        "registry_id": row.get("registry_id"),
        "isin": row.get("isin"),
        "exchange": row.get("exchange"),
        "exchange_ticker": row.get("exchange_ticker"),
        "trading_currency": row.get("trading_currency"),
        "provider_symbol": row.get("provider_symbol"),
        "yahoo_symbol": row.get("yahoo_symbol"),
        "observed_close_date": observed_date.isoformat() if observed_date else None,
        "observed_currency": row.get("observed_currency"),
        "venue_mic": venue.get("mic") if isinstance(venue, dict) else None,
        "venue_timezone": venue.get("timezone") if isinstance(venue, dict) else None,
        "regular_close_local": venue.get("regular_close_local") if isinstance(venue, dict) else None,
        "post_close_buffer_minutes": buffer_minutes,
        "session_close_ready_utc": close_ready_utc,
        "staleness_days": staleness_days,
        "max_staleness_days": max_staleness,
        "is_static_holiday": holiday,
        "gates": gates,
        "failed_gates": failed,
        "completed_session_validated": passed,
        "diagnostic_status": "completed_session_validated" if passed else "completed_session_blocked",
        "diagnostic_only": True,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "errors": errors,
    }


def build(fallback_gate_evaluation: Path, session_policy: Path, output_dir: Path, run_id: str) -> Path:
    source = load_json(fallback_gate_evaluation)
    policy = load_yaml(session_policy)
    rows = [evaluate_row(row, policy) for row in source.get("rows", []) if isinstance(row, dict)]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_fallback_gate_evaluation": str(fallback_gate_evaluation),
        "session_policy": str(session_policy),
        "diagnostic_only": True,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "completed_session_validated_count": sum(1 for row in rows if row.get("completed_session_validated") is True),
            "blocked_count": sum(1 for row in rows if row.get("completed_session_validated") is not True),
            "authority_note": "Completed-session validation is one Yahoo fallback gate only. It does not create valuation authority or cross-source validation.",
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"yahoo_completed_session_gate_{run_id}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"YAHOO_COMPLETED_SESSION_GATE_OK | artifact={path} | rows={len(rows)}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fallback-gate-evaluation", required=True)
    parser.add_argument("--session-policy", default=str(DEFAULT_SESSION_POLICY))
    parser.add_argument("--output-dir", default="output/pricing")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    build(Path(args.fallback_gate_evaluation), Path(args.session_policy), Path(args.output_dir), args.run_id)


if __name__ == "__main__":
    main()
