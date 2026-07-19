# Decision — ETF EU additive cockpit front-page preview

Date: 2026-07-19
Repository: `market-predictions/weekly-etf-eu`
Status: accepted preview architecture / production enablement pending

## Decision

The selected Weekly ETF EU client hierarchy is:

```text
EU/UCITS cockpit front page
→ investor report
→ analyst report
```

The cockpit is additive. It does not replace the existing funded-aware investor and analyst evidence body.

## Donor relationship

The architecture adapts the mature `market-predictions/weekly-etf` front-page pattern:

- current normalized state as input authority;
- exactly one additive page;
- explicit feature gate;
- unchanged classic fallback;
- separate inline/table email surface;
- implementation and production enablement as separate decisions.

EU-specific authority remains:

```text
Dutch-primary
English companion
ISIN-first
UCITS-first
EUR model portfolio
no U.S. holdings authority
```

## Feature contract

```text
MRKT_RPRTS_ETF_EU_COCKPIT_FRONT_PAGE=disabled|enabled
missing value=disabled
invalid value=classic fallback
render failure=classic fallback
rollback=disabled
```

## Duplicate-surface rule

After successful cockpit injection, the compact investor summary strip is hidden with inline styling. The investor hero and section 1 remain because they provide document identity and detailed decision rationale.

## Acceptance evidence

```text
WP32_pull_request=61
WP32_merge_commit=348c324d911b142f0871e9a67f875b76b3450447
final_validation_run=29667194382
NL_page_delta=1
EN_page_delta=1
classic_sections_preserved=15
primary_visual_review_passed=true
secondary_adversarial_review_passed=true
protected_inputs_unchanged=true
blockers=0
```

## Authority boundaries

This decision grants preview output-contract authority only. It does not grant or change:

```text
pricing authority
macro authority
portfolio-action authority
funding authority
portfolio mutation
trade-ledger mutation
real broker execution
production delivery authority
cockpit production enablement
```

## Consequence

WP33 must perform an exact-current, non-delivery replay and prove the rollback path before production enablement may be recorded. A future report run remains separately governed.