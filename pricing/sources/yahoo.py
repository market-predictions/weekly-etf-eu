from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from pricing.price_result_schema import (
    AUTHORITY_NON_AUTHORITATIVE_CONNECTIVITY_ONLY,
    LICENSE_PROVIDER_FREE_PERSONAL,
    STATUS_UNRESOLVED_DEPENDENCY_MISSING,
    STATUS_UNRESOLVED_NO_DATA,
    STATUS_UNRESOLVED_NOT_CONFIGURED,
    STATUS_UNRESOLVED_PROVIDER_ERROR,
    PriceResult,
    SourceLineage,
)
from pricing.sources.base import PriceRequest, PriceSource

SOURCE_ID = "yahoo_yfinance"
PROVIDER_NAME = "Yahoo Finance / yfinance"
DEFAULT_PERIOD = "10d"


class YahooPriceSource(PriceSource):
    """Yahoo/yfinance fallback adapter for non-authoritative UCITS close evidence.

    This adapter intentionally returns a normal typed PriceResult but marks its
    lineage as non_authoritative_connectivity_only. Valuation-grade promotion
    must happen outside this adapter through the source-policy/agreement gate.
    """

    source_id = SOURCE_ID
    provider_name = PROVIDER_NAME
    license_class = LICENSE_PROVIDER_FREE_PERSONAL
    authority_tier = AUTHORITY_NON_AUTHORITATIVE_CONNECTIVITY_ONLY

    def __init__(
        self,
        *,
        history_fetcher: Callable[[str, str], Any] | None = None,
        period: str = DEFAULT_PERIOD,
        raw_evidence_path: str | None = None,
    ) -> None:
        self._history_fetcher = history_fetcher or _fetch_yfinance_history
        self._period = period
        self._raw_evidence_path = raw_evidence_path

    def fetch_eod_close(self, request: PriceRequest) -> PriceResult:
        identity = request.identity
        provider_config = request.provider_config or {}
        provider_symbol = _clean(identity.provider_symbol)
        period = _clean(provider_config.get("period")) or self._period
        raw_evidence_path = _clean(provider_config.get("raw_evidence_path")) or self._raw_evidence_path

        if not provider_symbol:
            return self._unresolved(
                request,
                status=STATUS_UNRESOLVED_NOT_CONFIGURED,
                errors=["missing_provider_symbol"],
                raw_evidence_path=raw_evidence_path,
                raw_evidence={"source_role": "fallback_provisional"},
            )

        try:
            history = self._history_fetcher(provider_symbol, period)
        except ModuleNotFoundError as exc:
            if exc.name == "yfinance":
                return self._unresolved(
                    request,
                    status=STATUS_UNRESOLVED_DEPENDENCY_MISSING,
                    errors=[f"yfinance_dependency_missing:{exc}"],
                    raw_evidence_path=raw_evidence_path,
                    raw_evidence={"provider_symbol": provider_symbol, "period": period},
                )
            return self._unresolved(
                request,
                status=STATUS_UNRESOLVED_PROVIDER_ERROR,
                errors=[f"provider_exception:{exc}"],
                raw_evidence_path=raw_evidence_path,
                raw_evidence={"provider_symbol": provider_symbol, "period": period},
            )
        except ImportError as exc:
            return self._unresolved(
                request,
                status=STATUS_UNRESOLVED_DEPENDENCY_MISSING,
                errors=[f"yfinance_import_failed:{exc}"],
                raw_evidence_path=raw_evidence_path,
                raw_evidence={"provider_symbol": provider_symbol, "period": period},
            )
        except Exception as exc:  # pragma: no cover - live provider behavior
            return self._unresolved(
                request,
                status=STATUS_UNRESOLVED_PROVIDER_ERROR,
                errors=[f"provider_exception:{exc}"],
                raw_evidence_path=raw_evidence_path,
                raw_evidence={"provider_symbol": provider_symbol, "period": period},
            )

        rows = _normalize_history_rows(history)
        if not rows:
            return self._unresolved(
                request,
                status=STATUS_UNRESOLVED_NO_DATA,
                errors=["missing_history"],
                raw_evidence_path=raw_evidence_path,
                raw_evidence={"provider_symbol": provider_symbol, "period": period, "row_count": 0},
            )

        row = _select_row(rows, request.requested_date)
        if row is None:
            return self._unresolved(
                request,
                status=STATUS_UNRESOLVED_NO_DATA,
                errors=[f"requested_date_not_found:{request.requested_date}"],
                raw_evidence_path=raw_evidence_path,
                raw_evidence={"provider_symbol": provider_symbol, "period": period, "available_dates": [r.get("date") for r in rows]},
            )

        observed_date = _clean(row.get("date"))
        if not observed_date:
            return self._unresolved(
                request,
                status=STATUS_UNRESOLVED_NO_DATA,
                errors=["missing_observed_date"],
                raw_evidence_path=raw_evidence_path,
                raw_evidence=_row_evidence(provider_symbol, period, row),
            )

        close = _decimal_or_none(row.get("close"))
        if close is None:
            return self._unresolved(
                request,
                status=STATUS_UNRESOLVED_NO_DATA,
                errors=[f"missing_close:{observed_date}"],
                raw_evidence_path=raw_evidence_path,
                raw_evidence=_row_evidence(provider_symbol, period, row),
            )

        currency = _clean(row.get("currency")) or _clean(identity.trading_currency)
        if not currency:
            return self._unresolved(
                request,
                status=STATUS_UNRESOLVED_NO_DATA,
                errors=[f"missing_currency:{observed_date}"],
                raw_evidence_path=raw_evidence_path,
                raw_evidence=_row_evidence(provider_symbol, period, row),
            )

        lineage = SourceLineage.now(
            source_id=self.source_id,
            provider_name=self.provider_name,
            license_class=self.license_class,
            authority_tier=self.authority_tier,
            raw_evidence_path=raw_evidence_path,
            raw_evidence={
                **_row_evidence(provider_symbol, period, row),
                "source_role": "fallback_provisional",
                "valuation_grade_eligible": False,
                "currency_source": "provider_history" if _clean(row.get("currency")) else "request_identity_trading_currency",
                "completed_session_basis": "daily_history_row",
            },
        )
        return PriceResult.observed(
            identity=identity,
            lineage=lineage,
            observed_date=observed_date,
            close=close,
            currency=currency.upper(),
        )

    def _unresolved(
        self,
        request: PriceRequest,
        *,
        status: str,
        errors: list[str],
        raw_evidence_path: str | None,
        raw_evidence: dict[str, Any],
    ) -> PriceResult:
        lineage = SourceLineage.now(
            source_id=self.source_id,
            provider_name=self.provider_name,
            license_class=self.license_class,
            authority_tier=self.authority_tier,
            raw_evidence_path=raw_evidence_path,
            raw_evidence={
                **raw_evidence,
                "source_role": "fallback_provisional",
                "valuation_grade_eligible": False,
            },
        )
        return PriceResult.unresolved(
            identity=request.identity,
            lineage=lineage,
            status=status,
            errors=errors,
        )


def _fetch_yfinance_history(symbol: str, period: str) -> Any:
    import yfinance as yf

    return yf.Ticker(symbol).history(period=period, auto_adjust=False)


def _normalize_history_rows(history: Any) -> list[dict[str, Any]]:
    if history is None:
        return []

    if isinstance(history, dict):
        rows = history.get("rows") or history.get("history") or history.get("prices") or []
        if isinstance(rows, dict):
            rows = rows.values()
        return [_normalize_mapping_row(row) for row in rows if row is not None]

    # pandas DataFrame-like object returned by yfinance.
    if hasattr(history, "empty") and hasattr(history, "dropna") and hasattr(history, "tail"):
        if bool(history.empty):
            return []
        frame = history.dropna(how="all")
        if bool(frame.empty):
            return []
        rows: list[dict[str, Any]] = []
        for idx, row in frame.iterrows():
            row_dict = row.to_dict()
            rows.append(
                {
                    "date": _date_to_iso(idx),
                    "close": row_dict.get("Close") if "Close" in row_dict else row_dict.get("close"),
                    "currency": row_dict.get("Currency") or row_dict.get("currency"),
                    "raw": _json_safe(row_dict),
                }
            )
        return rows

    if isinstance(history, Iterable) and not isinstance(history, (str, bytes)):
        return [_normalize_mapping_row(row) for row in history if row is not None]

    return []


def _normalize_mapping_row(row: Any) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {}
    observed_date = row.get("date") or row.get("Date") or row.get("datetime") or row.get("Datetime")
    close = row.get("close") if "close" in row else row.get("Close")
    currency = row.get("currency") or row.get("Currency")
    return {
        "date": _date_to_iso(observed_date),
        "close": close,
        "currency": currency,
        "raw": _json_safe(row),
    }


def _select_row(rows: list[dict[str, Any]], requested_date: str | None) -> dict[str, Any] | None:
    cleaned = [row for row in rows if _clean(row.get("date"))]
    if not cleaned:
        return rows[-1] if rows else None
    sorted_rows = sorted(cleaned, key=lambda row: _clean(row.get("date")))
    if requested_date:
        requested = _date_to_iso(requested_date)
        matches = [row for row in sorted_rows if row.get("date") == requested]
        return matches[-1] if matches else None
    return sorted_rows[-1]


def _date_to_iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if hasattr(value, "date"):
        try:
            return value.date().isoformat()
        except Exception:
            pass
    text = _clean(value)
    if not text:
        return None
    if " " in text:
        text = text.split(" ", 1)[0]
    if "T" in text:
        text = text.split("T", 1)[0]
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        return text[:10]


def _decimal_or_none(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    if not amount.is_finite():
        return None
    return amount


def _row_evidence(provider_symbol: str, period: str, row: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider_symbol": provider_symbol,
        "period": period,
        "observed_date": row.get("date"),
        "raw_row": row.get("raw", {}),
    }


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "item"):
        try:
            return _json_safe(value.item())
        except Exception:
            pass
    return str(value)


def _clean(value: Any) -> str:
    return str(value or "").strip()
