# Handover — Weekly ETF EU WP-SYNC-10 production convergence

**Date:** 2026-08-03  
**Repository:** `market-predictions/weekly-etf-eu`  
**Branch:** `sync/wp10-production-engine-convergence`  
**Pull request:** #69  
**Status:** implementation complete, machine-green, visual review passed

## Session result

WP-SYNC-10 closes the report-engine split between the legacy premium EU production renderer and the merged donor-synchronized sister-report architecture.

The new path rebuilds donor, mapping, allocator and official EU state into a normalized production-convergence state, then generates a Dutch-primary and English-companion premium client package.

## Four-layer handover

### 1. Decision framework

- Current official portfolio: VWCE, EUNA and SXR8.
- Current promoted donor exposures: six.
- Exact UCITS mappings: six of six.
- Frozen Stage-1 review continuity: VVSM and L0CK.
- VVSM is not currently promoted.
- L0CK is currently promoted but remains blocked.
- No new position is actionable.
- Blocked capacity remains official cash.

### 2. Input/state contract

Pinned donor evidence:

```text
repository=market-predictions/weekly-etf
commit=52f13e190a9f6b0045df175973fdf8d0f6f5f30d
report_date=2026-07-29
```

Official EU state:

```text
portfolio_state=output/etf_eu_portfolio_state.json
trade_ledger=output/etf_eu_trade_ledger.csv
portfolio_state_sha256=6642334558818e630f0b22a2500ef44b2489ff237aacca638e81f184c165aa6f
trade_ledger_sha256=718f0681fe0d1162f9a91c34aa90489eb8566aecb06c12a1a2d9ad251be3e87c
```

Accepted evidence boundary:

`control/evidence/etf_eu_wp09_fresh_cutover_evidence_30501245612_1.json`

New current mappings:

```text
water_infrastructure=XMLC / IE00BK5BC891
water_utilities=IQQQ / IE00B1TXK627
```

### 3. Output contract

Generated client package:

```text
output/production_convergence/client_report/weekly_etf_eu_review_nl_260729_converged.html
output/production_convergence/client_report/weekly_etf_eu_review_nl_260729_converged.pdf
output/production_convergence/client_report/weekly_etf_eu_review_260729_converged.html
output/production_convergence/client_report/weekly_etf_eu_review_260729_converged.pdf
```

Contract result:

```text
nl_sections=19
nl_pages=11
en_sections=19
en_pages=11
funded_position_count=3
promoted_exposure_count=6
client_internal_language_absent=true
stale_simulated_trade_content_absent=true
cash_target_matches_official_state=true
stage_1_actionable_target=0
```

Visual review:

```text
reviewed_pages=22
blank_pages=0
clipping=false
overlap=false
orphaned_rows=false
footer_client_safe=true
visual_review_passed=true
```

### 4. Operational runbook

Workflow:

`.github/workflows/validate-etf-eu-production-convergence.yml`

The workflow:

1. checks out the pinned Weekly ETF donor evidence;
2. rebuilds shared donor strategy and target artifacts;
3. validates and merges all UCITS registry additions;
4. rebuilds synchronization and policy allocator context;
5. renders the synchronized bilingual source report;
6. builds and validates the convergence state;
7. rebuilds client-safe executive sections;
8. promotes and validates premium HTML/PDF;
9. proves official portfolio and ledger hashes are unchanged;
10. uploads artifacts only.

It does not send email or mutate state.

## Validation evidence

```text
head_sha=0997545ad0cf670d805536414d05abde17ff89f2
strategy_sync_run=30810262285 success
allocator_run=30810262293 success
allocator_report_run=30810262292 success
production_convergence_run=30810262300 success
job_id=91675081232
artifact_id=8854509533
artifact_digest=sha256:19a5bfcc2db4f813bebc3588946e4843c587ff17aa021d0150835bde58208d65
```

## Key implementation files

```text
config/ucits_symbol_registry_sync_additions_wp10.yml
config/shared_exposure_ucits_map.yml
runtime/merge_etf_eu_sync_registries.py
runtime/build_etf_eu_production_convergence_state.py
runtime/finalize_etf_eu_wp10_source_language.py
runtime/prepare_etf_eu_wp10_client_executive_surface.py
runtime/promote_etf_eu_sister_report_to_production_candidate.py
tools/validate_etf_eu_production_convergence_state.py
tools/validate_etf_eu_production_converged_report.py
.github/workflows/validate-etf-eu-production-convergence.yml
```

## Important defects resolved

- two promoted water sleeves were unmapped;
- the Dutch water lane names were introduced after the earlier localization pass;
- VVSM was incorrectly assumed to remain currently promoted;
- current opportunity surfaces and frozen Stage-1 continuity were conflated;
- client pages retained development terminology and machine tokens;
- the executive summary rendered regime metadata instead of its label;
- the footer retained development wording;
- the cash row showed the analytical scenario rather than official cash;
- official positions displayed analytical rather than no-change targets;
- the stale `VVSM/SMH` cross-market label remained visible.

## Authority boundary

```text
portfolio_mutation=false
ledger_write=false
funding_authority=false
execution_authority=false
activation_authority=false
production_delivery_authority=false
executable_trade_intents=[]
```

## Recommended next work package

`ETF-EU-WP-SYNC-11_ROUTINE_PRODUCTION_PROMOTION_AND_GUARDED_DELIVERY`

Scope:

- integrate the converged engine into the routine production package builder and runbook;
- use a fresh dated run identity and latest accepted donor/state evidence;
- preserve fail-closed allocation behavior;
- validate receiving-mail HTML against the PDF/client package;
- create a guarded send package;
- claim delivery only after SMTP evidence and independent inbox receipt;
- keep portfolio mutation in a separate package unless activation gates independently pass.
