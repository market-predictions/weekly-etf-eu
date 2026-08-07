from __future__ import annotations

from datetime import date

from pricing import build_current_session_close_results_v2 as pricing_v2


class _FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self._payload


def _line() -> dict[str, str]:
    return {
        "ticker": "VWCE",
        "isin": "IE00BK5BQT80",
        "venue_code": "XETR",
        "currency": "EUR",
        "provider_symbol_yahoo": "VWCE.DE",
    }


def _live_later_session_result() -> dict[str, object]:
    return {
        "provider": "boerse_frankfurt_xetra",
        "configured": True,
        "pricing_status": "fetch_failed",
        "close_date": None,
        "close_price": None,
        "close_age_days": None,
        "returned_symbol": "XETR:IE00BK5BQT80",
        "returned_exchange": "Xetra",
        "returned_mic": "XETR",
        "returned_currency": "EUR",
        "venue_match": True,
        "currency_match": True,
        "identity_status": "verified_exact_isin_mic_currency",
        "identity_evidence": [{"query_mode": "exact_isin_plus_mic"}],
        "retrieval_mode": "live",
        "blockers": ["completed_report_date_session_close_unavailable"],
    }


def test_boerse_historical_replay_recovers_exact_report_date(monkeypatch) -> None:
    report_date = date(2026, 8, 5)
    monkeypatch.setattr(pricing_v2, "_original_fetch_boerse", lambda line, day: _live_later_session_result())

    def fake_get(url: str, **kwargs):
        assert "/v1/data/price_history?" in url
        assert "isin=IE00BK5BQT80" in url
        assert "mic=XETR" in url
        assert "minDate=2026-08-05" in url
        assert "maxDate=2026-08-05" in url
        return _FakeResponse(
            {
                "totalCount": 1,
                "data": [
                    {
                        "date": "2026-08-05",
                        "open": 136.1,
                        "high": 137.0,
                        "low": 135.8,
                        "close": 136.72,
                        "turnoverPieces": 1000,
                        "turnoverEuro": 136720,
                    }
                ],
            }
        )

    monkeypatch.setattr(pricing_v2.requests, "get", fake_get)
    result = pricing_v2.fetch_boerse_with_historical_replay(_line(), report_date)

    assert result["pricing_status"] == "priced"
    assert result["close_date"] == "2026-08-05"
    assert result["close_price"] == 136.72
    assert result["retrieval_mode"] == "historical_exact_isin_mic_replay"
    assert result["venue_match"] is True
    assert result["currency_match"] is True
    assert result["blockers"] == []
    assert result["identity_evidence"][-1]["endpoint"] == "boerse_frankfurt_price_history"


def test_boerse_historical_replay_remains_fail_closed_without_identity(monkeypatch) -> None:
    live_result = _live_later_session_result()
    live_result["venue_match"] = False
    live_result["identity_status"] = "identity_mismatch"
    monkeypatch.setattr(pricing_v2, "_original_fetch_boerse", lambda line, day: live_result)

    def should_not_fetch(*args, **kwargs):
        raise AssertionError("historical endpoint must not be queried without verified identity")

    monkeypatch.setattr(pricing_v2.requests, "get", should_not_fetch)
    result = pricing_v2.fetch_boerse_with_historical_replay(_line(), date(2026, 8, 5))

    assert result["pricing_status"] == "fetch_failed"
    assert "historical_replay_identity_not_verified" in result["blockers"]


def test_historical_parser_requires_exact_report_date() -> None:
    payload = {
        "totalCount": 2,
        "data": [
            {"date": "2026-08-04", "close": 135.0},
            {"date": "2026-08-06", "close": 138.0},
        ],
    }
    assert pricing_v2._historical_close_from_boerse_payload(payload, date(2026, 8, 5)) is None
