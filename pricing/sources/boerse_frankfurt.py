from __future__ import annotations

import json
import urllib.parse
import urllib.request
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from pricing.price_result_schema import (
    AUTHORITY_DIAGNOSTIC_CANDIDATE_SOURCE,
    LICENSE_UNKNOWN,
    STATUS_UNRESOLVED_NO_DATA,
    STATUS_UNRESOLVED_NOT_CONFIGURED,
    STATUS_UNRESOLVED_PROVIDER_ERROR,
    PriceIdentity,
    PriceResult,
    SourceLineage,
)
from pricing.sources.base import PriceRequest, PriceSource

SOURCE_ID = "boerse_frankfurt_xetra"
SOURCE_NAME = "Boerse Frankfurt / Xetra"
LICENSE_CLASS = LICENSE_UNKNOWN
LICENSE_NOTE = "undocumented_free_source_pending_license_review"
AUTHORITY_TIER = AUTHORITY_DIAGNOSTIC_CANDIDATE_SOURCE
AUTHORITY_NOTE = "exchange_candidate_evidence_only_not_valuation_authority"
DEFAULT_BASE_URL = "https://api.boerse-frankfurt.de/v1"
DEFAULT_MIC = "XETR"

ERROR_MISSING_ISIN = "missing_isin"
ERROR_PROVIDER_ERROR = "provider_error"
ERROR_PROVIDER_EXCEPTION = "provider_exception"
ERROR_SCHEMA_DRIFT = "schema_drift"
ERROR_MISSING_CLOSE = "missing_close"
ERROR_MISSING_DATE = "missing_date"
ERROR_CURRENCY_UNCERTAIN = "currency_uncertain"


def _as_str(value: Any) -> str:
    return str(value or "").strip()


def _decimal(value: Any) -> Decimal | None:
    text = _as_str(value).replace(",", "")
    if not text:
        return None
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        return None


def _first_present(payload: dict[str, Any], names: list[str]) -> Any:
    for name in names:
        if name in payload and payload.get(name) not in (None, ""):
            return payload.get(name)
    return None


def _walk_dicts(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        found.append(value)
        for child in value.values():
            found.extend(_walk_dicts(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_walk_dicts(child))
    return found


def _query(params: dict[str, Any]) -> str:
    return urllib.parse.urlencode({k: v for k, v in params.items() if v not in (None, "")})


def _http_get_json(url: str, timeout: int = 20) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 weekly-etf-eu pricing diagnostics",
            "Accept": "application/json,text/plain,*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - provider URL assembled by adapter
        return json.loads(resp.read().decode("utf-8"))


def _candidate_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Return likely price records across known and drifted response shapes.

    The Börse Frankfurt web API is undocumented for this use case. The adapter
    therefore avoids assuming one brittle path and searches nested dictionaries
    for close/date/currency-like fields. Schema changes become typed unresolved
    results instead of exceptions.
    """

    records: list[dict[str, Any]] = []
    for item in _walk_dicts(payload):
        close = _first_present(item, ["close", "closingPrice", "lastPrice", "price", "value"])
        date_value = _first_present(item, ["date", "tradingDate", "priceDate", "datetime", "time"])
        currency = _first_present(item, ["currency", "currencyCode", "isoCurrency"])
        if close is not None or date_value is not None or currency is not None:
            records.append(item)
    return records


def _extract_price(payload: dict[str, Any], expected_currency: str | None) -> tuple[str | None, Decimal | None, str | None, list[str]]:
    records = _candidate_records(payload)
    if not records:
        return None, None, None, [ERROR_SCHEMA_DRIFT]

    collected_errors: list[str] = []
    for record in records:
        close = _decimal(_first_present(record, ["close", "closingPrice", "lastPrice", "price", "value"]))
        observed_date = _as_str(_first_present(record, ["date", "tradingDate", "priceDate", "datetime", "time"]))[:10] or None
        currency = _as_str(_first_present(record, ["currency", "currencyCode", "isoCurrency"])).upper() or None
        if close is not None and observed_date:
            if expected_currency and currency and currency != expected_currency.upper():
                return None, None, None, [ERROR_CURRENCY_UNCERTAIN, f"expected_currency:{expected_currency}", f"provider_currency:{currency}"]
            if expected_currency and not currency:
                return None, None, None, [ERROR_CURRENCY_UNCERTAIN, f"expected_currency:{expected_currency}", "provider_currency_missing"]
            return observed_date, close, currency or expected_currency, []
        if close is None:
            collected_errors.append(ERROR_MISSING_CLOSE)
        if not observed_date:
            collected_errors.append(ERROR_MISSING_DATE)
    return None, None, None, sorted(set(collected_errors or [ERROR_SCHEMA_DRIFT]))


class BoerseFrankfurtXetraPriceSource(PriceSource):
    """ISIN-first Börse Frankfurt / Xetra EOD close adapter.

    This source returns typed PriceResult evidence only. It never creates
    valuation authority, funding authority, portfolio mutation or delivery.
    """

    source_id = SOURCE_ID
    provider_name = SOURCE_NAME
    license_class = LICENSE_CLASS
    authority_tier = AUTHORITY_TIER

    def __init__(self, base_url: str = DEFAULT_BASE_URL, raw_evidence_dir: Path | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.raw_evidence_dir = raw_evidence_dir

    def fetch_eod_close(self, request: PriceRequest) -> PriceResult:
        identity = request.identity
        provider_config = request.provider_config or {}
        mic = _as_str(provider_config.get("venue_mic") or provider_config.get("mic") or DEFAULT_MIC)

        if not _as_str(identity.isin):
            return PriceResult.unresolved(
                identity=identity,
                lineage=self._lineage(identity, mic, endpoint=None),
                status=STATUS_UNRESOLVED_NOT_CONFIGURED,
                errors=[ERROR_MISSING_ISIN],
            )

        endpoint = f"{self.base_url}/data/price_information/single?" + _query(
            {
                "isin": identity.isin,
                "mic": mic,
                "currency": identity.trading_currency,
                "symbol": identity.exchange_ticker,
            }
        )

        try:
            payload = _http_get_json(endpoint)
        except Exception as exc:  # pragma: no cover - fixture tests monkeypatch _http_get_json
            return PriceResult.unresolved(
                identity=identity,
                lineage=self._lineage(identity, mic, endpoint=endpoint),
                status=STATUS_UNRESOLVED_PROVIDER_ERROR,
                errors=[ERROR_PROVIDER_EXCEPTION, str(exc)],
            )

        raw_path = self._write_raw_evidence(identity, mic, payload)
        lineage = self._lineage(identity, mic, endpoint=endpoint, raw_evidence_path=raw_path)

        if isinstance(payload, dict) and (payload.get("error") or payload.get("message") and payload.get("status") == "error"):
            return PriceResult.unresolved(
                identity=identity,
                lineage=lineage,
                status=STATUS_UNRESOLVED_PROVIDER_ERROR,
                errors=[ERROR_PROVIDER_ERROR, _as_str(payload.get("error") or payload.get("message"))],
            )

        observed_date, close, currency, errors = _extract_price(payload, identity.trading_currency)
        if errors:
            return PriceResult.unresolved(
                identity=identity,
                lineage=lineage,
                status=STATUS_UNRESOLVED_NO_DATA,
                errors=errors,
            )

        return PriceResult.observed(
            identity=identity,
            lineage=lineage,
            observed_date=observed_date or "",
            close=close or Decimal("0"),
            currency=currency or identity.trading_currency,
        )

    def fetch_close(self, request: PriceRequest) -> PriceResult:
        """Backward-compatible alias; integration should call fetch_eod_close."""

        return self.fetch_eod_close(request)

    def _lineage(self, identity: PriceIdentity, mic: str, endpoint: str | None, raw_evidence_path: str | None = None) -> SourceLineage:
        return SourceLineage.now(
            source_id=self.source_id,
            provider_name=self.provider_name,
            license_class=self.license_class,
            authority_tier=self.authority_tier,
            raw_evidence_path=raw_evidence_path,
            raw_evidence={
                "endpoint": endpoint,
                "query_mode": "isin_plus_mic",
                "isin": identity.isin,
                "venue_mic": mic,
                "exchange_ticker": identity.exchange_ticker,
                "license_note": LICENSE_NOTE,
                "authority_note": AUTHORITY_NOTE,
                "valuation_grade_by_adapter": False,
                "portfolio_mutation": False,
                "production_delivery": False,
                "funding_authority": False,
            },
        )

    def _write_raw_evidence(self, identity: PriceIdentity, mic: str, payload: dict[str, Any]) -> str | None:
        if self.raw_evidence_dir is None:
            return None
        self.raw_evidence_dir.mkdir(parents=True, exist_ok=True)
        safe_isin = "".join(ch for ch in identity.isin if ch.isalnum()) or "unknown"
        safe_mic = "".join(ch for ch in mic if ch.isalnum()) or DEFAULT_MIC
        path = self.raw_evidence_dir / f"boerse_frankfurt_{safe_isin}_{safe_mic}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return str(path)


def fetch_eod_close(request: PriceRequest, *, base_url: str = DEFAULT_BASE_URL, raw_evidence_dir: Path | None = None) -> PriceResult:
    return BoerseFrankfurtXetraPriceSource(base_url=base_url, raw_evidence_dir=raw_evidence_dir).fetch_eod_close(request)
