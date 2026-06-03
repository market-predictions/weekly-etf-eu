from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any


STATUS_OBSERVED = "observed"
STATUS_UNRESOLVED_NO_DATA = "unresolved_no_data"
STATUS_UNRESOLVED_PROVIDER_ERROR = "unresolved_provider_error"
STATUS_UNRESOLVED_DEPENDENCY_MISSING = "unresolved_dependency_missing"
STATUS_UNRESOLVED_NOT_CONFIGURED = "unresolved_not_configured"

RESOLVED_STATUSES = {STATUS_OBSERVED}
UNRESOLVED_STATUSES = {
    STATUS_UNRESOLVED_NO_DATA,
    STATUS_UNRESOLVED_PROVIDER_ERROR,
    STATUS_UNRESOLVED_DEPENDENCY_MISSING,
    STATUS_UNRESOLVED_NOT_CONFIGURED,
}
ALLOWED_STATUSES = RESOLVED_STATUSES | UNRESOLVED_STATUSES

LICENSE_EXCHANGE_PUBLIC = "exchange_public"
LICENSE_PROVIDER_FREE_PERSONAL = "provider_free_personal"
LICENSE_PROVIDER_PAID = "provider_paid"
LICENSE_ISSUER_PUBLIC = "issuer_public"
LICENSE_UNKNOWN = "unknown"

ALLOWED_LICENSE_CLASSES = {
    LICENSE_EXCHANGE_PUBLIC,
    LICENSE_PROVIDER_FREE_PERSONAL,
    LICENSE_PROVIDER_PAID,
    LICENSE_ISSUER_PUBLIC,
    LICENSE_UNKNOWN,
}

AUTHORITY_EXCHANGE_OFFICIAL = "exchange_official"
AUTHORITY_CANDIDATE_VALUATION_SOURCE = "candidate_valuation_source"
AUTHORITY_DIAGNOSTIC_CANDIDATE_SOURCE = "diagnostic_candidate_source"
AUTHORITY_NON_AUTHORITATIVE_CONNECTIVITY_ONLY = "non_authoritative_connectivity_only"
AUTHORITY_UNKNOWN = "unknown"

ALLOWED_AUTHORITY_TIERS = {
    AUTHORITY_EXCHANGE_OFFICIAL,
    AUTHORITY_CANDIDATE_VALUATION_SOURCE,
    AUTHORITY_DIAGNOSTIC_CANDIDATE_SOURCE,
    AUTHORITY_NON_AUTHORITATIVE_CONNECTIVITY_ONLY,
    AUTHORITY_UNKNOWN,
}


@dataclass(frozen=True)
class PriceIdentity:
    """ISIN-first UCITS trading-line identity for one requested close."""

    registry_id: str
    isin: str
    exchange: str
    exchange_ticker: str
    trading_currency: str
    provider_symbol: str

    def as_dict(self) -> dict[str, str]:
        return {
            "registry_id": self.registry_id,
            "isin": self.isin,
            "exchange": self.exchange,
            "exchange_ticker": self.exchange_ticker,
            "trading_currency": self.trading_currency,
            "provider_symbol": self.provider_symbol,
        }


@dataclass(frozen=True)
class SourceLineage:
    """Provider and evidence metadata attached to a normalized price result."""

    source_id: str
    provider_name: str
    license_class: str
    authority_tier: str
    observed_at_utc: str
    raw_evidence_path: str | None = None
    raw_evidence: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.license_class not in ALLOWED_LICENSE_CLASSES:
            raise ValueError(f"unsupported license_class: {self.license_class}")
        if self.authority_tier not in ALLOWED_AUTHORITY_TIERS:
            raise ValueError(f"unsupported authority_tier: {self.authority_tier}")

    @classmethod
    def now(
        cls,
        *,
        source_id: str,
        provider_name: str,
        license_class: str,
        authority_tier: str,
        raw_evidence_path: str | None = None,
        raw_evidence: dict[str, Any] | None = None,
    ) -> "SourceLineage":
        return cls(
            source_id=source_id,
            provider_name=provider_name,
            license_class=license_class,
            authority_tier=authority_tier,
            observed_at_utc=datetime.now(timezone.utc).isoformat(),
            raw_evidence_path=raw_evidence_path,
            raw_evidence=raw_evidence or {},
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "provider_name": self.provider_name,
            "license_class": self.license_class,
            "authority_tier": self.authority_tier,
            "observed_at_utc": self.observed_at_utc,
            "raw_evidence_path": self.raw_evidence_path,
            "raw_evidence": self.raw_evidence,
        }


@dataclass(frozen=True)
class PriceResult:
    """Normalized provider response for one UCITS end-of-day close request."""

    identity: PriceIdentity
    status: str
    lineage: SourceLineage
    observed_date: str | None = None
    close: Decimal | None = None
    currency: str | None = None
    completed_session: bool = False
    errors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.status not in ALLOWED_STATUSES:
            raise ValueError(f"unsupported status: {self.status}")
        if self.is_resolved:
            if self.observed_date is None:
                raise ValueError("resolved PriceResult requires observed_date")
            if self.close is None:
                raise ValueError("resolved PriceResult requires close")
            if self.currency is None:
                raise ValueError("resolved PriceResult requires currency")
            if not self.completed_session:
                raise ValueError("resolved PriceResult requires completed_session=True")
            date.fromisoformat(self.observed_date)
        else:
            if self.close is not None:
                raise ValueError("unresolved PriceResult must not include close")

    @property
    def is_resolved(self) -> bool:
        return self.status in RESOLVED_STATUSES

    @property
    def is_unresolved(self) -> bool:
        return not self.is_resolved

    @classmethod
    def observed(
        cls,
        *,
        identity: PriceIdentity,
        lineage: SourceLineage,
        observed_date: str,
        close: Decimal | int | float | str,
        currency: str,
    ) -> "PriceResult":
        return cls(
            identity=identity,
            status=STATUS_OBSERVED,
            lineage=lineage,
            observed_date=observed_date,
            close=Decimal(str(close)),
            currency=currency,
            completed_session=True,
        )

    @classmethod
    def unresolved(
        cls,
        *,
        identity: PriceIdentity,
        lineage: SourceLineage,
        status: str,
        errors: list[str] | tuple[str, ...],
    ) -> "PriceResult":
        if status not in UNRESOLVED_STATUSES:
            raise ValueError(f"status is not unresolved: {status}")
        return cls(
            identity=identity,
            status=status,
            lineage=lineage,
            errors=tuple(errors),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            **self.identity.as_dict(),
            "status": self.status,
            "resolved": self.is_resolved,
            "observed_date": self.observed_date,
            "close": str(self.close) if self.close is not None else None,
            "currency": self.currency,
            "completed_session": self.completed_session,
            "source_id": self.lineage.source_id,
            "provider_name": self.lineage.provider_name,
            "license_class": self.lineage.license_class,
            "authority_tier": self.lineage.authority_tier,
            "source_lineage": self.lineage.as_dict(),
            "errors": list(self.errors),
            "portfolio_mutation": False,
            "production_delivery": False,
            "funding_authority": False,
        }
