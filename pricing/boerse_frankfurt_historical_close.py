from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Callable
from urllib.parse import urlencode

import requests

BASE_URL = "https://api.boerse-frankfurt.de"


def positive_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def select_exact_history_close(payload: Any, report_date: date) -> dict[str, Any] | None:
    """Return the exact requested-date history row or None.

    Börse Frankfurt's price-history payload is an object with a `data` array.
    Replay authority is intentionally exact-date only: a prior or later row is
    never silently substituted for the requested completed close.
    """
    if not isinstance(payload, dict):
        return None
    rows = payload.get("data")
    if not isinstance(rows, list):
        return None
    requested = report_date.isoformat()
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("date") or "") != requested:
            continue
        close = positive_float(row.get("close"))
        if close is None:
            return None
        return {
            "date": requested,
            "close": close,
            "open": positive_float(row.get("open")),
            "high": positive_float(row.get("high")),
            "low": positive_float(row.get("low")),
            "turnover_eur": positive_float(row.get("turnoverEuro")),
            "turnover_pieces": positive_float(row.get("turnoverPieces")),
        }
    return None


def fetch_exact_history_close(
    line: dict[str, Any],
    report_date: date,
    *,
    headers_factory: Callable[[str], dict[str, str]],
    timeout_seconds: int = 30,
    session: Any = requests,
) -> dict[str, Any]:
    """Fetch an exact-date historical Xetra close with sanitized provenance."""
    isin = str(line.get("isin") or "").strip().upper()
    mic = str(line.get("venue_code") or "").strip().upper()
    expected_currency = str(line.get("currency") or "").strip().upper() or None
    provider_symbol = f"{mic}:{isin}" if isin and mic else None
    result: dict[str, Any] = {
        "provider": "boerse_frankfurt_price_history",
        "configured": mic == "XETR" and bool(isin),
        "provider_symbol": provider_symbol,
        "expected_isin": isin or None,
        "expected_venue_code": mic or None,
        "expected_currency": expected_currency,
        "requested_report_date": report_date.isoformat(),
        "pricing_status": "not_configured",
        "close_date": None,
        "close_price": None,
        "close_age_days": None,
        "returned_symbol": None,
        "returned_exchange": None,
        "returned_mic": None,
        "returned_currency": None,
        "venue_match": None,
        "currency_match": None,
        "http_status": None,
        "observed_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "retrieval_mode": "historical_exact_date",
        "blockers": [],
    }
    if mic != "XETR" or not isin:
        result["blockers"] = ["boerse_frankfurt_history_xetra_only"]
        return result

    # Use a one-day bounded window and still filter the response to the exact
    # requested date. maxDate is advanced one day because the public endpoint's
    # boundary behavior has varied; exact-date selection below remains strict.
    from datetime import timedelta

    params = {
        "limit": 10,
        "offset": 0,
        "isin": isin,
        "mic": mic,
        "minDate": report_date.isoformat(),
        "maxDate": (report_date + timedelta(days=1)).isoformat(),
        "cleanSplit": "false",
        "cleanPayout": "false",
        "cleanSubscriptionRights": "false",
    }
    url = f"{BASE_URL}/v1/data/price_history?{urlencode(params)}"
    try:
        response = session.get(url, headers=headers_factory(url), timeout=timeout_seconds)
        result["http_status"] = response.status_code
        payload = response.json()
    except Exception as exc:
        result["pricing_status"] = "fetch_failed"
        result["blockers"] = [f"history_request_exception:{type(exc).__name__}"]
        return result

    if response.status_code != 200 or not isinstance(payload, dict):
        result["pricing_status"] = "fetch_failed"
        result["blockers"] = [f"history_provider_error:{response.status_code}"]
        return result

    selected = select_exact_history_close(payload, report_date)
    if selected is None:
        result["pricing_status"] = "fetch_failed"
        result["blockers"] = ["exact_report_date_history_close_unavailable"]
        return result

    result.update(
        {
            "pricing_status": "priced",
            "close_date": selected["date"],
            "close_price": round(float(selected["close"]), 8),
            "close_age_days": 0,
            "returned_symbol": provider_symbol,
            "returned_exchange": "Xetra",
            "returned_mic": mic,
            "returned_currency": None,
            # The endpoint is queried by exact ISIN+MIC. It does not need to
            # echo currency metadata; Yahoo remains the independent metadata
            # anchor required by the existing consensus policy.
            "venue_match": True,
            "currency_match": None,
            "identity_status": "exact_isin_mic_query_history_row",
            "identity_evidence": [
                {
                    "query_mode": "exact_isin_plus_mic_price_history",
                    "query_isin": isin,
                    "query_mic": mic,
                    "returned_close_date": selected["date"],
                    "source_field": "close",
                    "turnover_eur": selected.get("turnover_eur"),
                    "turnover_pieces": selected.get("turnover_pieces"),
                }
            ],
            "blockers": [],
        }
    )
    return result
