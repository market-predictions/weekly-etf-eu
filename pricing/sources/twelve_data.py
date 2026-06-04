from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from pricing.price_result_schema import (
    AUTHORITY_DIAGNOSTIC_CANDIDATE_SOURCE,
    LICENSE_PROVIDER_PAID,
    STATUS_UNRESOLVED_DEPENDENCY_MISSING,
    STATUS_UNRESOLVED_NO_DATA,
    STATUS_UNRESOLVED_NOT_CONFIGURED,
    STATUS_UNRESOLVED_PROVIDER_ERROR,
    PriceIdentity,
    PriceResult,
    SourceLineage,
)
from pricing.sources.base import PriceRequest, PriceSource

SOURCE_ID = "twelve_data"
SOURCE_NAME = "Twelve Data"
LICENSE_CLASS = LICENSE_PROVIDER_PAID
AUTHORITY_TIER = AUTHORITY_DIAGNOSTIC_CANDIDATE_SOURCE
DEFAULT_BASE_URL = "https://api.twelvedata.com"
DEFAULT_INTERVAL = "1day"
DEFAULT_OUTPUTSIZE = 5

ERROR_POLICY_REVIEW_REQUIRED = "paid_source_policy_review_required"
ERROR_MISSING_API_KEY = "missing_twelve_data_api_key"
ERROR_MISSING_SYMBOL = "missing_twelve_data_symbol"
ERROR_PROVIDER_ERROR = "provider_error"
ERROR_PROVIDER_EXCEPTION = "provider_exception"
ERROR_NO_VALUES = "no_time_series_values"
ERROR_MISSING_CLOSE = "missing_close"
ERROR_MISSING_DATE = "missing_datetime"
ERROR_CURRENCY_MISMATCH = "currency_mismatch"
ERROR_CURRENCY_UNVERIFIED = "currency_unverified"


def _text(value: Any) -> str:
    return str(value or "").strip()


def _decimal(value: Any) -> Decimal | None:
    text = _text(value).replace(",", "")
    if not text:
        return None
    try:
        result = Decimal(text)
    except (InvalidOperation, ValueError):
        return None
    return result if result > 0 else None


def _api_key(provider_config: dict[str, Any]) -> str | None:
    configured = _text(provider_config.get("api_key"))
    return configured or os.environ.get("TWELVE_DATA_API_KEY") or os.environ.get("TWELVEDATA_API_KEY")


def _query(params: dict[str, Any]) -> str:
    return urllib.parse.urlencode({key: value for key, value in params.items() if value not in (None, "")})


def _redacted_url(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urllib.parse.urlsplit(url)
    pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    redacted = [(key, "REDACTED" if key.lower() == "apikey" else value) for key, value in pairs]
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(redacted), parsed.fragment))


def _http_get_json(url: str, timeout: int = 20) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 weekly-etf-eu pricing evidence"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:  # noqa: S310 - provider URL assembled by adapter
            text = response.read().decode("utf-8", errors="replace")
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body) if body else {}
        except json.JSONDecodeError:
            parsed = {"message": body[:300]}
        if isinstance(parsed, dict):
            parsed.setdefault("http_status", exc.code)
            return parsed
        return {"status": "error", "code": exc.code, "message": body[:300]}


def _provider_error(payload: dict[str, Any]) -> str | None:
    if str(payload.get("status") or "").lower() == "error":
        return _text(payload.get("message") or payload.get("code") or ERROR_PROVIDER_ERROR)
    if payload.get("code") and payload.get("message") and not payload.get("values"):
        return _text(payload.get("message"))
    return None


class TwelveDataPriceSource(PriceSource):
    """Twelve Data paid/provider-reviewed EOD close adapter.

    This adapter is a typed evidence path only. It does not update portfolio
    state, render reports, send output or promote candidates. Current policy
    must explicitly pass provider_config["paid_source_policy_reviewed"] = True
    before live use.
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
        if provider_config.get("paid_source_policy_reviewed") is not True:
            return self._unresolved(identity, None, STATUS_UNRESOLVED_NOT_CONFIGURED, [ERROR_POLICY_REVIEW_REQUIRED])

        symbol = _text(provider_config.get("symbol"))
        if not symbol:
            return self._unresolved(identity, None, STATUS_UNRESOLVED_NOT_CONFIGURED, [ERROR_MISSING_SYMBOL])

        api_key = _api_key(provider_config)
        if not api_key:
            return self._unresolved(identity, None, STATUS_UNRESOLVED_DEPENDENCY_MISSING, [ERROR_MISSING_API_KEY])

        exchange = _text(provider_config.get("exchange")) or None
        interval = _text(provider_config.get("interval")) or DEFAULT_INTERVAL
        outputsize = provider_config.get("outputsize") or DEFAULT_OUTPUTSIZE
        endpoint = f"{self.base_url}/time_series?" + _query(
            {
                "symbol": symbol,
                "exchange": exchange,
                "interval": interval,
                "outputsize": outputsize,
                "format": "JSON",
                "apikey": api_key,
            }
        )

        try:
            payload = _http_get_json(endpoint)
        except Exception as exc:  # pragma: no cover - fixture tests monkeypatch _http_get_json
            return self._unresolved(identity, _redacted_url(endpoint), STATUS_UNRESOLVED_PROVIDER_ERROR, [ERROR_PROVIDER_EXCEPTION, str(exc)])

        raw_path = self._write_raw_evidence(identity, symbol, payload)
        lineage = self._lineage(identity, _redacted_url(endpoint), symbol, exchange, raw_path, payload)

        provider_error = _provider_error(payload)
        if provider_error:
            return PriceResult.unresolved(
                identity=identity,
                lineage=lineage,
                status=STATUS_UNRESOLVED_PROVIDER_ERROR,
                errors=[ERROR_PROVIDER_ERROR, provider_error],
            )

        values = payload.get("values") if isinstance(payload.get("values"), list) else []
        if not values or not isinstance(values[0], dict):
            return PriceResult.unresolved(identity=identity, lineage=lineage, status=STATUS_UNRESOLVED_NO_DATA, errors=[ERROR_NO_VALUES])

        latest = values[0]
        close = _decimal(latest.get("close"))
        observed_date = _text(latest.get("datetime"))[:10] or None
        if close is None:
            return PriceResult.unresolved(identity=identity, lineage=lineage, status=STATUS_UNRESOLVED_NO_DATA, errors=[ERROR_MISSING_CLOSE])
        if not observed_date:
            return PriceResult.unresolved(identity=identity, lineage=lineage, status=STATUS_UNRESOLVED_NO_DATA, errors=[ERROR_MISSING_DATE])

        meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
        currency = _text(meta.get("currency") or provider_config.get("expected_currency") or identity.trading_currency).upper()
        expected_currency = _text(provider_config.get("expected_currency") or identity.trading_currency).upper()
        if expected_currency and currency and currency != expected_currency:
            return PriceResult.unresolved(
                identity=identity,
                lineage=lineage,
                status=STATUS_UNRESOLVED_NO_DATA,
                errors=[ERROR_CURRENCY_MISMATCH, f"expected_currency:{expected_currency}", f"provider_currency:{currency}"],
            )
        if not currency:
            return PriceResult.unresolved(identity=identity, lineage=lineage, status=STATUS_UNRESOLVED_NO_DATA, errors=[ERROR_CURRENCY_UNVERIFIED])

        return PriceResult.observed(identity=identity, lineage=lineage, observed_date=observed_date, close=close, currency=currency)

    def _unresolved(self, identity: PriceIdentity, endpoint: str | None, status: str, errors: list[str]) -> PriceResult:
        return PriceResult.unresolved(identity=identity, lineage=self._lineage(identity, endpoint, None, None, None, {}), status=status, errors=errors)

    def _lineage(
        self,
        identity: PriceIdentity,
        endpoint: str | None,
        symbol: str | None,
        exchange: str | None,
        raw_evidence_path: str | None,
        payload: dict[str, Any],
    ) -> SourceLineage:
        meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
        return SourceLineage.now(
            source_id=self.source_id,
            provider_name=self.provider_name,
            license_class=self.license_class,
            authority_tier=self.authority_tier,
            raw_evidence_path=raw_evidence_path,
            raw_evidence={
                "endpoint": endpoint,
                "query_mode": "time_series_symbol_exchange",
                "symbol": symbol,
                "exchange": exchange,
                "isin": identity.isin,
                "provider_status": payload.get("status"),
                "provider_code": payload.get("code"),
                "meta": meta,
                "paid_source_policy_reviewed_required": True,
                "valuation_grade_by_adapter": False,
                "portfolio_mutation": False,
                "production_delivery": False,
                "funding_authority": False,
            },
        )

    def _write_raw_evidence(self, identity: PriceIdentity, symbol: str, payload: dict[str, Any]) -> str | None:
        if self.raw_evidence_dir is None:
            return None
        self.raw_evidence_dir.mkdir(parents=True, exist_ok=True)
        safe_isin = "".join(ch for ch in identity.isin if ch.isalnum()) or "unknown"
        safe_symbol = "".join(ch for ch in symbol if ch.isalnum()) or "unknown"
        path = self.raw_evidence_dir / f"twelve_data_{safe_isin}_{safe_symbol}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return str(path)


def fetch_eod_close(request: PriceRequest, *, base_url: str = DEFAULT_BASE_URL, raw_evidence_dir: Path | None = None) -> PriceResult:
    return TwelveDataPriceSource(base_url=base_url, raw_evidence_dir=raw_evidence_dir).fetch_eod_close(request)
