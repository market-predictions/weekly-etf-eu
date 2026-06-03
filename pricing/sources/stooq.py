from __future__ import annotations

import csv
import io
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("PyYAML is required for Stooq pricing overrides") from exc

from pricing.price_result_schema import (
    AUTHORITY_DIAGNOSTIC_CANDIDATE_SOURCE,
    LICENSE_PROVIDER_FREE_PERSONAL,
    STATUS_UNRESOLVED_NO_DATA,
    STATUS_UNRESOLVED_NOT_CONFIGURED,
    STATUS_UNRESOLVED_PROVIDER_ERROR,
    PriceIdentity,
    PriceResult,
    SourceLineage,
)
from pricing.sources.base import PriceRequest, PriceSource


STOOQ_SOURCE_ID = "stooq"
STOOQ_PROVIDER_NAME = "Stooq EOD"
STOOQ_LICENSE_CLASS = LICENSE_PROVIDER_FREE_PERSONAL
STOOQ_AUTHORITY_TIER = AUTHORITY_DIAGNOSTIC_CANDIDATE_SOURCE
DEFAULT_OVERRIDES_PATH = Path("config/source_symbol_overrides/stooq.yml")
DEFAULT_STOOQ_DAILY_URL = "https://stooq.com/q/d/l/"


def _as_str(value: object) -> str:
    return str(value or "").strip()


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _mapping_key(*, registry_id: str, isin: str, exchange: str, exchange_ticker: str, trading_currency: str) -> str:
    return "|".join([registry_id, isin, exchange, exchange_ticker, trading_currency])


def _identity_key(identity: PriceIdentity) -> str:
    return _mapping_key(
        registry_id=identity.registry_id,
        isin=identity.isin,
        exchange=identity.exchange,
        exchange_ticker=identity.exchange_ticker,
        trading_currency=identity.trading_currency,
    )


def _load_symbol_overrides(path: Path) -> dict[str, dict]:
    payload = _load_yaml(path)
    mappings: dict[str, dict] = {}
    for row in payload.get("symbols") or []:
        key = _mapping_key(
            registry_id=_as_str(row.get("registry_id")),
            isin=_as_str(row.get("isin")),
            exchange=_as_str(row.get("exchange")),
            exchange_ticker=_as_str(row.get("exchange_ticker")),
            trading_currency=_as_str(row.get("trading_currency")),
        )
        if all(key.split("|")):
            mappings[key] = row
    return mappings


def _query_url(symbol: str, base_url: str = DEFAULT_STOOQ_DAILY_URL) -> str:
    query = urllib.parse.urlencode({"s": symbol.lower(), "i": "d"})
    return f"{base_url}?{query}"


def _default_http_get(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - fixed provider endpoint
        return resp.read().decode("utf-8")


def _parse_latest_close(csv_text: str) -> dict:
    if not csv_text.strip() or csv_text.strip().lower().startswith("no data"):
        raise ValueError("stooq_no_data")

    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    rows = [row for row in reader if _as_str(row.get("Date")) and _as_str(row.get("Close"))]
    if not rows:
        raise ValueError("stooq_no_rows")

    latest = rows[-1]
    observed_date = _as_str(latest.get("Date"))[:10]
    close_raw = _as_str(latest.get("Close"))
    if not observed_date or not close_raw:
        raise ValueError("stooq_missing_date_or_close")

    return {
        "observed_date": observed_date,
        "close": close_raw,
        "raw_row": latest,
    }


class StooqEodAdapter(PriceSource):
    """Stooq end-of-day close adapter using explicit configured symbols only."""

    source_id = STOOQ_SOURCE_ID
    provider_name = STOOQ_PROVIDER_NAME
    license_class = STOOQ_LICENSE_CLASS
    authority_tier = STOOQ_AUTHORITY_TIER

    def __init__(
        self,
        overrides_path: Path | str = DEFAULT_OVERRIDES_PATH,
        http_get: Callable[[str], str] | None = None,
        base_url: str = DEFAULT_STOOQ_DAILY_URL,
    ) -> None:
        self.overrides_path = Path(overrides_path)
        self._symbol_overrides = _load_symbol_overrides(self.overrides_path)
        self.http_get = http_get or _default_http_get
        self.base_url = base_url

    def fetch_eod_close(self, request: PriceRequest) -> PriceResult:
        mapping = self._symbol_overrides.get(_identity_key(request.identity))
        if not mapping:
            return self._unresolved(
                request.identity,
                status=STATUS_UNRESOLVED_NOT_CONFIGURED,
                errors=["no_explicit_stooq_symbol_mapping_for_trading_line"],
            )

        source_symbol = _as_str(mapping.get("source_symbol"))
        if not source_symbol:
            return self._unresolved(
                request.identity,
                status=STATUS_UNRESOLVED_NOT_CONFIGURED,
                errors=["configured_stooq_mapping_missing_source_symbol"],
                source_symbol=source_symbol,
            )

        identity = PriceIdentity(
            registry_id=request.identity.registry_id,
            isin=request.identity.isin,
            exchange=request.identity.exchange,
            exchange_ticker=request.identity.exchange_ticker,
            trading_currency=request.identity.trading_currency,
            provider_symbol=source_symbol,
        )
        url = _query_url(source_symbol, self.base_url)

        try:
            csv_text = self.http_get(url)
        except Exception as exc:  # pragma: no cover - exercised through injected test callable in downstream branches
            return self._unresolved(
                identity,
                status=STATUS_UNRESOLVED_PROVIDER_ERROR,
                errors=[f"stooq_provider_error:{exc}"],
                source_symbol=source_symbol,
                raw_evidence={"url": url},
            )

        try:
            parsed = _parse_latest_close(csv_text)
        except ValueError as exc:
            return self._unresolved(
                identity,
                status=STATUS_UNRESOLVED_NO_DATA,
                errors=[str(exc)],
                source_symbol=source_symbol,
                raw_evidence={"url": url},
            )

        expected_currency = _as_str(mapping.get("expected_currency")) or request.identity.trading_currency
        lineage = self._lineage(
            source_symbol=source_symbol,
            raw_evidence={
                "endpoint": "daily_csv",
                "url": url,
                "row": parsed.get("raw_row"),
                "mapping_status": mapping.get("mapping_status"),
            },
        )
        return PriceResult.observed(
            identity=identity,
            lineage=lineage,
            observed_date=parsed["observed_date"],
            close=parsed["close"],
            currency=expected_currency,
        )

    def _lineage(self, *, source_symbol: str | None = None, raw_evidence: dict | None = None) -> SourceLineage:
        evidence = {"source_symbol": source_symbol} if source_symbol else {}
        if raw_evidence:
            evidence.update(raw_evidence)
        return SourceLineage.now(
            source_id=self.source_id,
            provider_name=self.provider_name,
            license_class=self.license_class,
            authority_tier=self.authority_tier,
            raw_evidence=evidence,
        )

    def _unresolved(
        self,
        identity: PriceIdentity,
        *,
        status: str,
        errors: list[str],
        source_symbol: str | None = None,
        raw_evidence: dict | None = None,
    ) -> PriceResult:
        lineage = self._lineage(source_symbol=source_symbol, raw_evidence=raw_evidence)
        return PriceResult.unresolved(
            identity=identity,
            lineage=lineage,
            status=status,
            errors=errors,
        )


__all__ = [
    "StooqEodAdapter",
    "STOOQ_SOURCE_ID",
    "STOOQ_PROVIDER_NAME",
    "STOOQ_LICENSE_CLASS",
    "STOOQ_AUTHORITY_TIER",
]
