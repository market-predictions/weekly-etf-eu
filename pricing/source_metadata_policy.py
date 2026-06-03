from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from pricing.price_result_schema import ALLOWED_AUTHORITY_TIERS, ALLOWED_LICENSE_CLASSES

SOURCE_TYPE_EXCHANGE = "exchange"
SOURCE_TYPE_DATA_VENDOR = "data_vendor"
SOURCE_TYPE_ISSUER = "issuer"
SOURCE_TYPE_CONNECTIVITY = "connectivity"
SOURCE_TYPE_UNKNOWN = "unknown"

ALLOWED_SOURCE_TYPES = {
    SOURCE_TYPE_EXCHANGE,
    SOURCE_TYPE_DATA_VENDOR,
    SOURCE_TYPE_ISSUER,
    SOURCE_TYPE_CONNECTIVITY,
    SOURCE_TYPE_UNKNOWN,
}

USAGE_MODE_OFFICIAL_CLOSE = "official_close"
USAGE_MODE_CANDIDATE_EVIDENCE = "candidate_evidence"
USAGE_MODE_FALLBACK_PROVISIONAL = "fallback_provisional"
USAGE_MODE_DIAGNOSTIC_CROSS_CHECK = "diagnostic_cross_check"
USAGE_MODE_REFERENCE_STALE_CHECK = "reference_stale_check"
USAGE_MODE_CONNECTIVITY_ONLY = "connectivity_only"

ALLOWED_USAGE_MODES = {
    USAGE_MODE_OFFICIAL_CLOSE,
    USAGE_MODE_CANDIDATE_EVIDENCE,
    USAGE_MODE_FALLBACK_PROVISIONAL,
    USAGE_MODE_DIAGNOSTIC_CROSS_CHECK,
    USAGE_MODE_REFERENCE_STALE_CHECK,
    USAGE_MODE_CONNECTIVITY_ONLY,
}

REVIEW_STATUS_REVIEWED = "reviewed"
REVIEW_STATUS_PROVISIONAL = "provisional"
REVIEW_STATUS_PENDING_LICENSE_REVIEW = "pending_license_review"
REVIEW_STATUS_PENDING_COVERAGE_REVIEW = "pending_coverage_review"
REVIEW_STATUS_REFERENCE_ONLY = "reference_only"
REVIEW_STATUS_UNKNOWN = "unknown"

ALLOWED_REVIEW_STATUSES = {
    REVIEW_STATUS_REVIEWED,
    REVIEW_STATUS_PROVISIONAL,
    REVIEW_STATUS_PENDING_LICENSE_REVIEW,
    REVIEW_STATUS_PENDING_COVERAGE_REVIEW,
    REVIEW_STATUS_REFERENCE_ONLY,
    REVIEW_STATUS_UNKNOWN,
}

POLICY_MODE_DIAGNOSTIC_EVIDENCE = "diagnostic_evidence"
POLICY_MODE_MARKET_CLOSE_AGREEMENT_CANDIDATES = "market_close_agreement_candidates"
POLICY_MODE_VALUATION_CANDIDATE_EVIDENCE = "valuation_candidate_evidence"
POLICY_MODE_REFERENCE_EVIDENCE = "reference_evidence"

ALLOWED_POLICY_MODES = {
    POLICY_MODE_DIAGNOSTIC_EVIDENCE,
    POLICY_MODE_MARKET_CLOSE_AGREEMENT_CANDIDATES,
    POLICY_MODE_VALUATION_CANDIDATE_EVIDENCE,
    POLICY_MODE_REFERENCE_EVIDENCE,
}


@dataclass(frozen=True)
class SourceMetadata:
    """Declared metadata for one pricing evidence source.

    This class classifies evidence sources only. It does not approve prices,
    create valuation-grade rows, mutate portfolio state, or promote candidates.
    """

    source_id: str
    provider_name: str
    source_type: str
    usage_mode: str
    license_class: str
    authority_tier: str
    review_status: str
    counts_for_market_close_agreement: bool = False
    valuation_candidate_eligible: bool = False
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("source_id is required")
        if self.source_type not in ALLOWED_SOURCE_TYPES:
            raise ValueError(f"unsupported source_type: {self.source_type}")
        if self.usage_mode not in ALLOWED_USAGE_MODES:
            raise ValueError(f"unsupported usage_mode: {self.usage_mode}")
        if self.license_class not in ALLOWED_LICENSE_CLASSES:
            raise ValueError(f"unsupported license_class: {self.license_class}")
        if self.authority_tier not in ALLOWED_AUTHORITY_TIERS:
            raise ValueError(f"unsupported authority_tier: {self.authority_tier}")
        if self.review_status not in ALLOWED_REVIEW_STATUSES:
            raise ValueError(f"unsupported review_status: {self.review_status}")
        if self.counts_for_market_close_agreement and self.usage_mode == USAGE_MODE_REFERENCE_STALE_CHECK:
            raise ValueError("reference/stale-check sources cannot count for market-close agreement")


DEFAULT_SOURCE_METADATA: tuple[SourceMetadata, ...] = (
    SourceMetadata(
        source_id="euronext_live",
        provider_name="Euronext Live",
        source_type=SOURCE_TYPE_EXCHANGE,
        usage_mode=USAGE_MODE_OFFICIAL_CLOSE,
        license_class="exchange_public",
        authority_tier="candidate_valuation_source",
        review_status=REVIEW_STATUS_PENDING_LICENSE_REVIEW,
        counts_for_market_close_agreement=True,
        valuation_candidate_eligible=True,
        notes="Venue-specific official discovery candidate; license/session details still require review.",
    ),
    SourceMetadata(
        source_id="deutsche_boerse_live",
        provider_name="Deutsche Börse / Xetra Live",
        source_type=SOURCE_TYPE_EXCHANGE,
        usage_mode=USAGE_MODE_OFFICIAL_CLOSE,
        license_class="exchange_public",
        authority_tier="candidate_valuation_source",
        review_status=REVIEW_STATUS_PENDING_LICENSE_REVIEW,
        counts_for_market_close_agreement=True,
        valuation_candidate_eligible=True,
        notes="Venue-specific official discovery candidate; license/session details still require review.",
    ),
    SourceMetadata(
        source_id="boerse_frankfurt",
        provider_name="Börse Frankfurt / Xetra endpoint",
        source_type=SOURCE_TYPE_EXCHANGE,
        usage_mode=USAGE_MODE_DIAGNOSTIC_CROSS_CHECK,
        license_class="unknown",
        authority_tier="diagnostic_candidate_source",
        review_status=REVIEW_STATUS_PENDING_LICENSE_REVIEW,
        notes="Undocumented/free endpoint; exchange-candidate evidence only until reviewed.",
    ),
    SourceMetadata(
        source_id="stooq",
        provider_name="Stooq",
        source_type=SOURCE_TYPE_DATA_VENDOR,
        usage_mode=USAGE_MODE_DIAGNOSTIC_CROSS_CHECK,
        license_class="provider_free_personal",
        authority_tier="diagnostic_candidate_source",
        review_status=REVIEW_STATUS_PENDING_COVERAGE_REVIEW,
        notes="Provisional/cross-check source; explicit symbol mappings require coverage verification.",
    ),
    SourceMetadata(
        source_id="yahoo_yfinance",
        provider_name="Yahoo Finance via yfinance",
        source_type=SOURCE_TYPE_CONNECTIVITY,
        usage_mode=USAGE_MODE_FALLBACK_PROVISIONAL,
        license_class="provider_free_personal",
        authority_tier="non_authoritative_connectivity_only",
        review_status=REVIEW_STATUS_PROVISIONAL,
        notes="Fallback/provisional evidence only; not the sole path to valuation-grade UCITS pricing.",
    ),
    SourceMetadata(
        source_id="issuer_nav",
        provider_name="Issuer NAV reference",
        source_type=SOURCE_TYPE_ISSUER,
        usage_mode=USAGE_MODE_REFERENCE_STALE_CHECK,
        license_class="issuer_public",
        authority_tier="diagnostic_candidate_source",
        review_status=REVIEW_STATUS_REFERENCE_ONLY,
        notes="Reference/stale-check evidence only; not exchange market-close agreement evidence.",
    ),
    SourceMetadata(
        source_id="blackrock_issuer_reference",
        provider_name="BlackRock issuer reference",
        source_type=SOURCE_TYPE_ISSUER,
        usage_mode=USAGE_MODE_REFERENCE_STALE_CHECK,
        license_class="issuer_public",
        authority_tier="diagnostic_candidate_source",
        review_status=REVIEW_STATUS_REFERENCE_ONLY,
        notes="Product facts/NAV sanity-check reference, not trading-line close authority.",
    ),
    SourceMetadata(
        source_id="twelve_data",
        provider_name="Twelve Data",
        source_type=SOURCE_TYPE_DATA_VENDOR,
        usage_mode=USAGE_MODE_DIAGNOSTIC_CROSS_CHECK,
        license_class="provider_paid",
        authority_tier="diagnostic_candidate_source",
        review_status=REVIEW_STATUS_PENDING_COVERAGE_REVIEW,
        notes="Diagnostic candidate until symbol/date/currency/session evidence and plan status are reviewed.",
    ),
    SourceMetadata(
        source_id="issuer_factsheet",
        provider_name="Issuer factsheet",
        source_type=SOURCE_TYPE_ISSUER,
        usage_mode=USAGE_MODE_REFERENCE_STALE_CHECK,
        license_class="issuer_public",
        authority_tier="diagnostic_candidate_source",
        review_status=REVIEW_STATUS_REFERENCE_ONLY,
        notes="Instrument facts and stale sanity checks only.",
    ),
)


def metadata_by_source_id(metadata: Iterable[SourceMetadata] = DEFAULT_SOURCE_METADATA) -> dict[str, SourceMetadata]:
    indexed: dict[str, SourceMetadata] = {}
    for item in metadata:
        if item.source_id in indexed:
            raise ValueError(f"duplicate source metadata: {item.source_id}")
        indexed[item.source_id] = item
    return indexed


def filter_sources_by_policy_mode(
    metadata: Iterable[SourceMetadata] = DEFAULT_SOURCE_METADATA,
    *,
    policy_mode: str,
) -> tuple[SourceMetadata, ...]:
    """Return source metadata rows allowed for a declared policy mode.

    This helper filters declared metadata only. It is not an agreement gate and
    does not mark any observed price as valuation-grade.
    """

    rows = tuple(metadata)
    metadata_by_source_id(rows)

    if policy_mode not in ALLOWED_POLICY_MODES:
        raise ValueError(f"unsupported policy_mode: {policy_mode}")
    if policy_mode == POLICY_MODE_DIAGNOSTIC_EVIDENCE:
        return rows
    if policy_mode == POLICY_MODE_MARKET_CLOSE_AGREEMENT_CANDIDATES:
        return tuple(row for row in rows if row.counts_for_market_close_agreement)
    if policy_mode == POLICY_MODE_VALUATION_CANDIDATE_EVIDENCE:
        return tuple(row for row in rows if row.valuation_candidate_eligible)
    if policy_mode == POLICY_MODE_REFERENCE_EVIDENCE:
        return tuple(row for row in rows if row.usage_mode == USAGE_MODE_REFERENCE_STALE_CHECK)
    raise AssertionError("unreachable policy mode branch")
