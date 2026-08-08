from __future__ import annotations

from datetime import date

from pricing.boerse_frankfurt_historical_close import fetch_exact_history_close, select_exact_history_close


REPORT_DATE = date(2026, 8, 5)
LINE = {
    "isin": "IE00BK5BQT80",
    "venue_code": "XETR",
    "currency": "EUR",
    "ticker": "VWCE",
}


class FakeResponse:
    def __init__(self, payload: object, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> object:
        return self._payload


class FakeSession:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.urls: list[str] = []

    def get(self, url: str, **_: object) -> FakeResponse:
        self.urls.append(url)
        return self.response


def headers(_: str) -> dict[str, str]:
    return {"Accept": "application/json"}


def test_exact_date_row_is_selected() -> None:
    payload = {
        "totalCount": 2,
        "data": [
            {"date": "2026-08-06", "close": 166.0},
            {"date": "2026-08-05", "open": 164.0, "high": 166.0, "low": 163.5, "close": 165.1, "turnoverEuro": 12345, "turnoverPieces": 75},
        ],
    }
    selected = select_exact_history_close(payload, REPORT_DATE)
    assert selected is not None
    assert selected["date"] == "2026-08-05"
    assert selected["close"] == 165.1
    assert selected["turnover_eur"] == 12345.0


def test_iso_timestamp_date_is_normalized() -> None:
    payload = {"totalCount": 1, "data": [{"date": "2026-08-05T00:00:00Z", "close": 165.1}]}
    selected = select_exact_history_close(payload, REPORT_DATE)
    assert selected is not None
    assert selected["date"] == "2026-08-05"


def test_prior_row_is_not_silently_substituted() -> None:
    payload = {"totalCount": 1, "data": [{"date": "2026-08-04", "close": 164.2}]}
    assert select_exact_history_close(payload, REPORT_DATE) is None


def test_non_positive_exact_close_is_rejected() -> None:
    payload = {"totalCount": 1, "data": [{"date": "2026-08-05", "close": 0}]}
    assert select_exact_history_close(payload, REPORT_DATE) is None


def test_fetch_binds_exact_isin_mic_and_date() -> None:
    session = FakeSession(FakeResponse({"totalCount": 1, "data": [{"date": "2026-08-05", "close": 165.1}]}))
    result = fetch_exact_history_close(
        LINE,
        REPORT_DATE,
        headers_factory=headers,
        session=session,
    )
    assert result["pricing_status"] == "priced"
    assert result["provider"] == "boerse_frankfurt_price_history"
    assert result["close_date"] == "2026-08-05"
    assert result["close_price"] == 165.1
    assert result["retrieval_mode"] == "historical_exact_date"
    assert result["provider_symbol"] == "XETR:IE00BK5BQT80"
    assert result["venue_match"] is True
    assert result["currency_match"] is None
    assert "isin=IE00BK5BQT80" in session.urls[0]
    assert "mic=XETR" in session.urls[0]
    assert "minDate=2026-07-29" in session.urls[0]
    assert "maxDate=2026-08-06" in session.urls[0]


def test_fetch_missing_exact_date_fails_closed_with_sanitized_diagnostics() -> None:
    session = FakeSession(FakeResponse({"totalCount": 1, "data": [{"date": "2026-08-04", "close": 164.2}]}))
    result = fetch_exact_history_close(
        LINE,
        REPORT_DATE,
        headers_factory=headers,
        session=session,
    )
    assert result["pricing_status"] == "fetch_failed"
    assert result["close_price"] is None
    assert result["blockers"] == ["exact_report_date_history_close_unavailable"]
    assert result["history_diagnostics"]["returned_dates"] == ["2026-08-04"]


def test_fetch_http_200_with_null_data_fails_closed_without_live_substitution() -> None:
    """Freeze the public Börse response shape observed during 2026-08-05 replay."""
    session = FakeSession(FakeResponse({"totalCount": 0, "data": None}, status_code=200))
    result = fetch_exact_history_close(
        LINE,
        REPORT_DATE,
        headers_factory=headers,
        session=session,
    )
    assert result["http_status"] == 200
    assert result["pricing_status"] == "fetch_failed"
    assert result["close_date"] is None
    assert result["close_price"] is None
    assert result["retrieval_mode"] == "historical_exact_date"
    assert result["blockers"] == ["exact_report_date_history_close_unavailable"]
    assert result["history_diagnostics"]["data_type"] == "NoneType"
    assert result["history_diagnostics"]["total_count"] == 0
