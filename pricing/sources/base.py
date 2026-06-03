from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from pricing.price_result_schema import PriceIdentity, PriceResult


@dataclass(frozen=True)
class PriceRequest:
    """One provider-agnostic request for a completed-session EOD close."""

    identity: PriceIdentity
    requested_date: str | None = None
    provider_config: dict[str, Any] | None = None


class PriceSource(ABC):
    """Common interface implemented by all pricing providers.

    Implementations must be deterministic, must not mutate portfolio state,
    and must return a typed PriceResult for both success and failure.
    """

    source_id: str
    provider_name: str
    license_class: str
    authority_tier: str

    @abstractmethod
    def fetch_eod_close(self, request: PriceRequest) -> PriceResult:
        """Return a normalized completed-session close or a typed unresolved result."""


class StaticPriceSource(PriceSource):
    """Small fake/test source backed by prebuilt PriceResult rows."""

    def __init__(self, *, source_id: str, provider_name: str, license_class: str, authority_tier: str, rows: dict[str, PriceResult]) -> None:
        self.source_id = source_id
        self.provider_name = provider_name
        self.license_class = license_class
        self.authority_tier = authority_tier
        self._rows = rows

    def fetch_eod_close(self, request: PriceRequest) -> PriceResult:
        key = request.identity.provider_symbol
        if key not in self._rows:
            from pricing.price_result_schema import STATUS_UNRESOLVED_NO_DATA, SourceLineage

            return PriceResult.unresolved(
                identity=request.identity,
                lineage=SourceLineage.now(
                    source_id=self.source_id,
                    provider_name=self.provider_name,
                    license_class=self.license_class,
                    authority_tier=self.authority_tier,
                ),
                status=STATUS_UNRESOLVED_NO_DATA,
                errors=[f"no_static_price_for_provider_symbol:{key}"],
            )
        return self._rows[key]
