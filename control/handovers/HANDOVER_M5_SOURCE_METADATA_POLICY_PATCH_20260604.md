# Handover — M5 Source Metadata Policy Patch

Date: 2026-06-04  
Repository: `market-predictions/weekly-etf-eu`  
Work package: `control/work_packages/WP_M5_SOURCE_METADATA_POLICY_20260603.md`

## Status

The work package was analyzed and a concrete implementation patch was prepared.

Preferred branch:

```text
workstream/source-metadata-policy
```

Branch creation through the available GitHub tool layer was blocked, and updating the non-existing branch ref failed with `Reference does not exist`. Per `control/PARALLEL_WORKSTREAM_PLAN_20260603.md`, when branch creation is unavailable, the safe fallback is to write a patch/handover file instead of changing shared execution files.

This file is that patch handover.

## Scope discipline

This patch only proposes the owned work-package files:

```text
control/DATA_SOURCE_METADATA.md
control/CHANGELOG.md
pricing/source_metadata_policy.py
tests/test_source_metadata_policy.py
```

It does not propose changes to forbidden files:

```text
pricing/build_ucits_valuation_prices.py
tools/validate_ucits_valuation_prices.py
.github/workflows/*
output/*
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
config/ucits_pricing_source_policy.yml
```

## Local validation performed

A temporary local fixture-only test harness was created using the current `pricing.price_result_schema` constants and the proposed helper/test files.

Command:

```bash
python -m pytest tests/test_source_metadata_policy.py -q
```

Result:

```text
9 passed in 0.12s
```

No network access was used.

## Metadata categories

The proposed policy introduces these metadata categories:

### source_type

```text
exchange
data_vendor
issuer
connectivity
unknown
```

### usage_mode

```text
official_close
candidate_evidence
fallback_provisional
diagnostic_cross_check
reference_stale_check
connectivity_only
```

### authority_tier

Aligned with `pricing.price_result_schema`:

```text
exchange_official
candidate_valuation_source
diagnostic_candidate_source
non_authoritative_connectivity_only
unknown
```

### review_status

```text
reviewed
provisional
pending_license_review
pending_coverage_review
reference_only
unknown
```

### policy_mode helper filters

```text
diagnostic_evidence
market_close_agreement_candidates
valuation_candidate_evidence
reference_evidence
```

Important: these filters classify declared metadata only. They do not approve prices, create valuation-grade rows, mutate portfolio state, promote candidates, render reports, generate PDFs, send email, or create delivery receipts.

## Unresolved source-review questions recorded by the patch

1. Exact license and redistribution permissions for venue-specific official/free endpoints still need review.
2. Börse Frankfurt / Xetra free endpoint remains undocumented and pending source/license review.
3. Stooq symbol mappings remain provisional and require provider coverage verification.
4. Yahoo/yfinance remains fallback/provisional evidence only and must not be the sole path to valuation-grade UCITS pricing.
5. Issuer NAV and issuer factsheets remain reference/stale-check only and must not count as market-close agreement evidence.
6. Twelve Data remains diagnostic unless plan, symbol, date, currency and completed-session evidence are explicitly reviewed later.

---

## Proposed file: `control/DATA_SOURCE_METADATA.md`

```markdown
# Weekly ETF EU — Data Source Metadata Policy

Date: 2026-06-04  
Repository: `market-predictions/weekly-etf-eu`

## Purpose

This file defines source metadata categories for the EU/UCITS pricing spine.

It is not an approval list and not a valuation-grade policy by itself. It records how pricing evidence sources are classified so later source selection and agreement-gate logic can reason from explicit metadata instead of hardcoded assumptions.

## Authority boundary

The metadata register does not:

```text
create valuation_grade=true rows
create funding authority
mutate portfolio state
promote candidates to fundable
render reports
generate PDFs
send email
create delivery receipts
```

Pricing adapters return typed evidence. A later agreement gate must decide whether evidence is valuation-grade, provisional or blocked.

## Categories

### source_type

| Value | Meaning |
|---|---|
| `exchange` | Exchange or trading venue source candidate. |
| `data_vendor` | Data provider or aggregator. |
| `issuer` | Issuer-provided product/NAV/factsheet reference. |
| `connectivity` | Connectivity/fallback source that is useful operationally but not authority by itself. |
| `unknown` | Source type not yet reviewed. |

### usage_mode

| Value | Meaning |
|---|---|
| `official_close` | Candidate source for official or venue-specific completed-session close evidence. |
| `candidate_evidence` | Candidate valuation evidence requiring agreement-gate review. |
| `fallback_provisional` | Provisional fallback evidence; not sole valuation authority. |
| `diagnostic_cross_check` | Cross-check / diagnostic evidence only. |
| `reference_stale_check` | Issuer/reference/stale-check context, not exchange close evidence. |
| `connectivity_only` | Connectivity proof only. |

### authority_tier

Authority tiers must align with `pricing.price_result_schema`:

```text
exchange_official
candidate_valuation_source
diagnostic_candidate_source
non_authoritative_connectivity_only
unknown
```

These values describe evidence quality only. They do not create `valuation_grade=true` by themselves.

### review_status

| Value | Meaning |
|---|---|
| `reviewed` | Metadata reviewed for this role. |
| `provisional` | Useful but explicitly provisional. |
| `pending_license_review` | License/source-rights review still needed. |
| `pending_coverage_review` | Provider symbol or coverage still needs verification. |
| `reference_only` | Source is reference/stale-check only. |
| `unknown` | Review status is not known. |

## Current source-role register

| source_id | source_type | usage_mode | license_class | authority_tier | review_status | counts_for_market_close_agreement | valuation_candidate_eligible | Notes |
|---|---|---|---|---|---|---:|---:|---|
| `euronext_live` | `exchange` | `official_close` | `exchange_public` | `candidate_valuation_source` | `pending_license_review` | true | true | Venue-specific official discovery candidate; license/session details still require review. |
| `deutsche_boerse_live` | `exchange` | `official_close` | `exchange_public` | `candidate_valuation_source` | `pending_license_review` | true | true | Venue-specific official discovery candidate; license/session details still require review. |
| `boerse_frankfurt` | `exchange` | `diagnostic_cross_check` | `unknown` | `diagnostic_candidate_source` | `pending_license_review` | false | false | Undocumented/free endpoint; exchange-candidate evidence only until reviewed. |
| `stooq` | `data_vendor` | `diagnostic_cross_check` | `provider_free_personal` | `diagnostic_candidate_source` | `pending_coverage_review` | false | false | Provisional/cross-check source; explicit symbol mappings require coverage verification. |
| `yahoo_yfinance` | `connectivity` | `fallback_provisional` | `provider_free_personal` | `non_authoritative_connectivity_only` | `provisional` | false | false | Fallback/provisional evidence only; not the sole path to valuation-grade UCITS pricing. |
| `issuer_nav` | `issuer` | `reference_stale_check` | `issuer_public` | `diagnostic_candidate_source` | `reference_only` | false | false | Reference/stale-check evidence only; not exchange market-close agreement evidence. |
| `blackrock_issuer_reference` | `issuer` | `reference_stale_check` | `issuer_public` | `diagnostic_candidate_source` | `reference_only` | false | false | Product facts/NAV sanity-check reference, not trading-line close authority. |
| `twelve_data` | `data_vendor` | `diagnostic_cross_check` | `provider_paid` | `diagnostic_candidate_source` | `pending_coverage_review` | false | false | Diagnostic candidate until symbol/date/currency/session evidence and plan status are reviewed. |
| `issuer_factsheet` | `issuer` | `reference_stale_check` | `issuer_public` | `diagnostic_candidate_source` | `reference_only` | false | false | Instrument facts and stale sanity checks only. |

## Policy-mode helper semantics

The helper in `pricing/source_metadata_policy.py` filters metadata rows by declared policy mode.

| policy_mode | Intended use |
|---|---|
| `diagnostic_evidence` | Return all declared source metadata rows in input order. |
| `market_close_agreement_candidates` | Return only metadata rows that are allowed to count as market-close agreement candidates. |
| `valuation_candidate_evidence` | Return only rows flagged as valuation candidate evidence. |
| `reference_evidence` | Return issuer/reference/stale-check rows only. |

This is metadata filtering only. The agreement gate must still validate dates, closes, currencies, completed-session status, source lineage, agreement conditions and authority constraints.

## Open review questions

1. Confirm license and redistribution constraints for venue-specific official/free endpoints.
2. Review whether the Börse Frankfurt / Xetra endpoint can ever move beyond diagnostic candidate evidence.
3. Verify Stooq coverage and exact symbol mappings before any stronger role.
4. Decide whether Yahoo/yfinance remains diagnostic/fallback only or can be considered as provisional evidence under a future agreement-gate rule.
5. Keep issuer NAV and factsheets reference-only unless a separate NAV-specific report surface is designed.
6. Review Twelve Data plan/source terms before any candidate valuation role.
```

---

## Proposed file: `pricing/source_metadata_policy.py`

```python
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
```

---

## Proposed file: `tests/test_source_metadata_policy.py`

```python
import pytest

from pricing.price_result_schema import ALLOWED_AUTHORITY_TIERS, ALLOWED_LICENSE_CLASSES
from pricing.source_metadata_policy import (
    DEFAULT_SOURCE_METADATA,
    POLICY_MODE_DIAGNOSTIC_EVIDENCE,
    POLICY_MODE_MARKET_CLOSE_AGREEMENT_CANDIDATES,
    POLICY_MODE_REFERENCE_EVIDENCE,
    POLICY_MODE_VALUATION_CANDIDATE_EVIDENCE,
    REVIEW_STATUS_REVIEWED,
    SOURCE_TYPE_EXCHANGE,
    USAGE_MODE_OFFICIAL_CLOSE,
    SourceMetadata,
    filter_sources_by_policy_mode,
    metadata_by_source_id,
)


def test_default_metadata_source_ids_are_unique():
    indexed = metadata_by_source_id(DEFAULT_SOURCE_METADATA)

    assert len(indexed) == len(DEFAULT_SOURCE_METADATA)
    assert "yahoo_yfinance" in indexed
    assert "issuer_nav" in indexed


def test_default_metadata_aligns_with_price_result_schema_categories():
    for row in DEFAULT_SOURCE_METADATA:
        assert row.license_class in ALLOWED_LICENSE_CLASSES
        assert row.authority_tier in ALLOWED_AUTHORITY_TIERS


def test_market_close_agreement_candidates_exclude_fallback_and_reference_sources():
    rows = filter_sources_by_policy_mode(
        DEFAULT_SOURCE_METADATA,
        policy_mode=POLICY_MODE_MARKET_CLOSE_AGREEMENT_CANDIDATES,
    )
    source_ids = {row.source_id for row in rows}

    assert "euronext_live" in source_ids
    assert "deutsche_boerse_live" in source_ids
    assert "yahoo_yfinance" not in source_ids
    assert "issuer_nav" not in source_ids
    assert all(row.counts_for_market_close_agreement for row in rows)


def test_valuation_candidate_evidence_is_metadata_only_not_authority_promotion():
    rows = filter_sources_by_policy_mode(
        DEFAULT_SOURCE_METADATA,
        policy_mode=POLICY_MODE_VALUATION_CANDIDATE_EVIDENCE,
    )

    assert {row.source_id for row in rows} == {"euronext_live", "deutsche_boerse_live"}
    assert all(row.valuation_candidate_eligible for row in rows)


def test_reference_evidence_returns_issuer_reference_sources_only():
    rows = filter_sources_by_policy_mode(
        DEFAULT_SOURCE_METADATA,
        policy_mode=POLICY_MODE_REFERENCE_EVIDENCE,
    )
    source_ids = {row.source_id for row in rows}

    assert source_ids == {"issuer_nav", "blackrock_issuer_reference", "issuer_factsheet"}
    assert all(not row.counts_for_market_close_agreement for row in rows)


def test_diagnostic_evidence_preserves_input_order_and_includes_all_metadata():
    rows = filter_sources_by_policy_mode(
        DEFAULT_SOURCE_METADATA,
        policy_mode=POLICY_MODE_DIAGNOSTIC_EVIDENCE,
    )

    assert rows == DEFAULT_SOURCE_METADATA


def test_unknown_policy_mode_fails_closed():
    with pytest.raises(ValueError, match="unsupported policy_mode"):
        filter_sources_by_policy_mode(DEFAULT_SOURCE_METADATA, policy_mode="production_delivery")


def test_duplicate_source_ids_fail_closed():
    source = SourceMetadata(
        source_id="duplicate",
        provider_name="Duplicate",
        source_type=SOURCE_TYPE_EXCHANGE,
        usage_mode=USAGE_MODE_OFFICIAL_CLOSE,
        license_class="exchange_public",
        authority_tier="exchange_official",
        review_status=REVIEW_STATUS_REVIEWED,
    )

    with pytest.raises(ValueError, match="duplicate source metadata"):
        metadata_by_source_id((source, source))


def test_reference_source_cannot_count_for_market_close_agreement():
    with pytest.raises(ValueError, match="reference/stale-check sources cannot count"):
        SourceMetadata(
            source_id="bad_reference",
            provider_name="Bad Reference",
            source_type="issuer",
            usage_mode="reference_stale_check",
            license_class="issuer_public",
            authority_tier="diagnostic_candidate_source",
            review_status="reference_only",
            counts_for_market_close_agreement=True,
        )
```

---

## Proposed `control/CHANGELOG.md` entry

Add this entry at the top of `control/CHANGELOG.md` when applying the patch:

```markdown
## 2026-06-04 — Add M5 source metadata policy workstream

Implemented the source metadata policy workstream.

Files changed:

```text
control/DATA_SOURCE_METADATA.md
pricing/source_metadata_policy.py
tests/test_source_metadata_policy.py
control/CHANGELOG.md
```

Summary:

- added source metadata categories for `source_type`, `usage_mode`, `authority_tier` and `review_status`;
- added a deterministic helper for filtering declared source metadata by policy mode;
- aligned license and authority categories with `pricing.price_result_schema`;
- recorded unresolved source-review questions without making external source claims;
- added fixture-only tests.

Validation:

```text
python -m pytest tests/test_source_metadata_policy.py -q
9 passed
```

Authority boundaries preserved:

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
no delivery receipt
no candidate promotion to fundable
```
```

## Handback

When branch tooling is available, apply the three proposed files, update `control/CHANGELOG.md` with the entry above, run:

```bash
python -m pytest tests/test_source_metadata_policy.py -q
```

Then open a PR from:

```text
workstream/source-metadata-policy
```

to:

```text
main
```

Recommended PR title:

```text
M5: Add source metadata policy
```

Recommended PR authority note:

```text
This PR classifies source metadata only. It does not create valuation-grade pricing, funding authority, portfolio mutation, report rendering, PDF/email generation, or delivery behavior.
```
