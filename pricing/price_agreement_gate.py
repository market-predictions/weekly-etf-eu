from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from pricing.price_result_schema import PriceIdentity, PriceResult
from pricing.source_metadata_policy import DEFAULT_SOURCE_METADATA, SourceMetadata, metadata_by_source_id

AGREEMENT_STATUS_VALUATION_GRADE = "valuation_grade"
AGREEMENT_STATUS_PROVISIONAL = "provisional"
AGREEMENT_STATUS_BLOCKED = "blocked"

REASON_AGREEMENT_PASSED = "agreement_passed"
REASON_NO_RESULTS = "no_price_results_supplied"
REASON_NO_RESOLVED_RESULTS = "no_resolved_price_results"
REASON_ONE_RESOLVED_SOURCE_ONLY = "one_resolved_source_only"
REASON_INDEPENDENT_SOURCE_COUNT_TOO_LOW = "independent_source_count_too_low"
REASON_IDENTITY_MISMATCH = "identity_mismatch"
REASON_CURRENCY_MISMATCH = "currency_mismatch"
REASON_OBSERVED_DATE_MISMATCH = "observed_date_mismatch"
REASON_REQUESTED_DATE_MISMATCH = "requested_date_mismatch"
REASON_PRICE_DISAGREEMENT = "price_disagreement_exceeds_tolerance"


@dataclass(frozen=True)
class AgreementGateConfig:
    max_abs_diff: Decimal = Decimal("0.01")
    max_bps_diff: Decimal = Decimal("5")
    min_independent_sources: int = 2


@dataclass(frozen=True)
class AgreementGateResult:
    status: str
    identity: PriceIdentity | None
    reason_codes: tuple[str, ...]
    agreed_observed_date: str | None = None
    agreed_currency: str | None = None
    agreed_close: Decimal | None = None
    max_abs_diff: Decimal | None = None
    max_bps_diff: Decimal | None = None
    resolved_source_ids: tuple[str, ...] = ()
    agreement_source_ids: tuple[str, ...] = ()
    excluded_source_ids: tuple[str, ...] = ()
    evidence_count: int = 0
    funding_authority: bool = False
    portfolio_mutation: bool = False
    production_delivery: bool = False

    @property
    def is_valuation_grade(self) -> bool:
        return self.status == AGREEMENT_STATUS_VALUATION_GRADE

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "reason_codes": list(self.reason_codes),
            "agreed_observed_date": self.agreed_observed_date,
            "agreed_currency": self.agreed_currency,
            "agreed_close": str(self.agreed_close) if self.agreed_close is not None else None,
            "max_abs_diff": str(self.max_abs_diff) if self.max_abs_diff is not None else None,
            "max_bps_diff": str(self.max_bps_diff) if self.max_bps_diff is not None else None,
            "resolved_source_ids": list(self.resolved_source_ids),
            "agreement_source_ids": list(self.agreement_source_ids),
            "excluded_source_ids": list(self.excluded_source_ids),
            "evidence_count": self.evidence_count,
            "funding_authority": False,
            "portfolio_mutation": False,
            "production_delivery": False,
            "identity": self.identity.as_dict() if self.identity is not None else None,
        }


def _make(status: str, identity: PriceIdentity | None, reasons: tuple[str, ...], rows: tuple[PriceResult, ...], agree: tuple[PriceResult, ...] = (), excluded: tuple[PriceResult, ...] = (), **extra: object) -> AgreementGateResult:
    return AgreementGateResult(
        status=status,
        identity=identity,
        reason_codes=reasons,
        resolved_source_ids=tuple(r.lineage.source_id for r in rows if r.is_resolved),
        agreement_source_ids=tuple(r.lineage.source_id for r in agree),
        excluded_source_ids=tuple(r.lineage.source_id for r in excluded),
        evidence_count=len(rows),
        **extra,
    )


def evaluate_price_agreement(results: Iterable[PriceResult], *, requested_date: str | None = None, config: AgreementGateConfig | None = None, metadata: Iterable[SourceMetadata] = DEFAULT_SOURCE_METADATA) -> AgreementGateResult:
    config = config or AgreementGateConfig()
    rows = tuple(results)
    if not rows:
        return _make(AGREEMENT_STATUS_PROVISIONAL, None, (REASON_NO_RESULTS,), rows)

    identity = rows[0].identity
    if any(r.identity != identity for r in rows):
        return _make(AGREEMENT_STATUS_BLOCKED, identity, (REASON_IDENTITY_MISMATCH,), rows)

    resolved = tuple(r for r in rows if r.is_resolved)
    if not resolved:
        return _make(AGREEMENT_STATUS_PROVISIONAL, identity, (REASON_NO_RESOLVED_RESULTS,), rows)

    meta = metadata_by_source_id(metadata)
    agree = tuple(r for r in resolved if meta.get(r.lineage.source_id) and meta[r.lineage.source_id].counts_for_market_close_agreement)
    agree_ids = {r.lineage.source_id for r in agree}
    excluded = tuple(r for r in resolved if r.lineage.source_id not in agree_ids)

    if len(resolved) == 1:
        r = resolved[0]
        return _make(AGREEMENT_STATUS_PROVISIONAL, identity, (REASON_ONE_RESOLVED_SOURCE_ONLY,), rows, agree, excluded, agreed_observed_date=r.observed_date, agreed_currency=r.currency, agreed_close=r.close)
    if len(agree_ids) < config.min_independent_sources:
        r = resolved[0]
        return _make(AGREEMENT_STATUS_PROVISIONAL, identity, (REASON_INDEPENDENT_SOURCE_COUNT_TOO_LOW,), rows, agree, excluded, agreed_observed_date=r.observed_date, agreed_currency=r.currency, agreed_close=r.close)
    if len({r.currency for r in agree}) != 1:
        return _make(AGREEMENT_STATUS_BLOCKED, identity, (REASON_CURRENCY_MISMATCH,), rows, agree, excluded)
    if len({r.observed_date for r in agree}) != 1:
        return _make(AGREEMENT_STATUS_BLOCKED, identity, (REASON_OBSERVED_DATE_MISMATCH,), rows, agree, excluded, agreed_currency=agree[0].currency)

    observed_date = agree[0].observed_date
    if requested_date and observed_date != requested_date:
        return _make(AGREEMENT_STATUS_BLOCKED, identity, (REASON_REQUESTED_DATE_MISMATCH,), rows, agree, excluded, agreed_observed_date=observed_date, agreed_currency=agree[0].currency)

    closes = tuple(r.close for r in agree if r.close is not None)
    abs_diff = max(closes) - min(closes)
    reference = min(closes) if min(closes) != 0 else max(closes)
    bps_diff = Decimal("0") if reference == 0 else (abs_diff / reference) * Decimal("10000")
    if abs_diff > config.max_abs_diff or bps_diff > config.max_bps_diff:
        return _make(AGREEMENT_STATUS_BLOCKED, identity, (REASON_PRICE_DISAGREEMENT,), rows, agree, excluded, agreed_observed_date=observed_date, agreed_currency=agree[0].currency, max_abs_diff=abs_diff, max_bps_diff=bps_diff)

    return _make(AGREEMENT_STATUS_VALUATION_GRADE, identity, (REASON_AGREEMENT_PASSED,), rows, agree, excluded, agreed_observed_date=observed_date, agreed_currency=agree[0].currency, agreed_close=agree[0].close, max_abs_diff=abs_diff, max_bps_diff=bps_diff)
