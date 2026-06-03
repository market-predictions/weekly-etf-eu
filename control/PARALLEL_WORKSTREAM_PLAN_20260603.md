# Weekly ETF EU — Parallel Workstream Plan

Date: 2026-06-03  
Repository: `market-predictions/weekly-etf-eu`

## Purpose

This file coordinates parallel development workstreams for the Weekly ETF EU UCITS pricing/reporting system.

The goal is to avoid a slow fully serial path while preserving determinism, clean authority boundaries, and safe GitHub integration.

## Source decision

The previous handover proposed promoting Yahoo/yfinance as a temporary UCITS valuation fallback. After review, the better architectural decision is:

```text
Do not make Yahoo-only prices valuation-grade by themselves.
Build a PriceSource / PriceResult pricing spine first.
Use Yahoo as a tertiary/provisional fallback.
Mark valuation_grade=true only after source policy and agreement gates pass.
```

## Non-negotiable authority boundaries

All workstreams must preserve:

```text
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
no delivery receipt
no candidate promotion to fundable without a separate promotion contract
```

## Required start sequence for every workstream chat

Every fresh chat must read from GitHub in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/PARALLEL_WORKSTREAM_PLAN_20260603.md`
5. the specific workstream file listed below
6. only then the minimum relevant execution files

## Branch and write discipline

Preferred branch names:

| Workstream | Branch |
|---|---|
| Coordinator | `workstream/coordinator-pricing-spine` |
| M0 cleanup | `workstream/m0-ground-clearing` |
| Pricing interface | `workstream/pricing-interface` |
| Stooq adapter | `workstream/stooq-adapter` |
| Börse Frankfurt/Xetra adapter | `workstream/boerse-frankfurt-adapter` |
| Yahoo adapter | `workstream/yahoo-adapter` |
| Issuer NAV adapter | `workstream/issuer-nav-adapter` |
| Source metadata policy | `workstream/source-metadata-policy` |
| Agreement gate integration | `workstream/agreement-gate-integration` |
| First report integration | `workstream/first-report-integration` |

Rules:

- Do not push feature work directly to `main` unless acting as the coordinator and explicitly integrating.
- Prefer one workstream branch per chat.
- If branch creation is unavailable, write a patch/handover file instead of changing shared execution files.
- Each workstream owns its listed files and must avoid forbidden files.
- Coordinator owns final merge order and conflict resolution.

## Workstream instruction files

| Chat | File | Parallel status |
|---|---|---|
| Coordinator | `control/work_packages/WP_COORDINATOR_PARALLEL_PRICING_SPINE_20260603.md` | start now |
| M0 cleanup | `control/work_packages/WP_M0_GROUND_CLEARING_20260603.md` | start now |
| Pricing interface | `control/work_packages/WP_M1_PRICING_INTERFACE_20260603.md` | start now; early dependency |
| Stooq adapter | `control/work_packages/WP_M1_STOOQ_ADAPTER_20260603.md` | start after interface skeleton exists, or draft against expected interface |
| Börse Frankfurt/Xetra adapter | `control/work_packages/WP_M1_BOERSE_FRANKFURT_ADAPTER_20260603.md` | start after interface skeleton exists, or draft against expected interface |
| Yahoo adapter | `control/work_packages/WP_M1_YAHOO_ADAPTER_20260603.md` | start after interface skeleton exists, or draft against expected interface |
| Issuer NAV adapter | `control/work_packages/WP_M1_ISSUER_NAV_ADAPTER_20260603.md` | start after interface skeleton exists, or draft against expected interface |
| Source metadata policy | `control/work_packages/WP_M5_SOURCE_METADATA_POLICY_20260603.md` | start now |
| Agreement gate | `control/work_packages/WP_M1_AGREEMENT_GATE_INTEGRATION_20260603.md` | do not implement until at least two adapters exist |
| First report | `control/work_packages/WP_M2_FIRST_REPORT_INTEGRATION_20260603.md` | do not implement until agreement gate exists |

## Merge order

Recommended integration order:

1. Pricing interface
2. Stooq adapter
3. Börse Frankfurt/Xetra adapter
4. Yahoo adapter
5. Issuer NAV adapter
6. Source metadata policy
7. M0 cleanup, if it does not conflict with active files
8. Agreement gate integration
9. First report integration
10. Client-facing report rewrite later

## Coordinator checklist

Before merging any workstream:

- confirm no forbidden authority flags became true;
- confirm no workflow now sends email or renders PDFs;
- confirm branch diff touches only owned or explicitly allowed files;
- run relevant validators or inspect the GitHub Actions run;
- record outcome in `control/CHANGELOG.md` or a coordinator handover;
- update `control/CURRENT_STATE.md` and `control/NEXT_ACTIONS.md` only after integration, not after every draft branch.

## Final integration definition of done

The parallel workstream phase is successful when:

```text
- PriceSource / PriceResult exists and is documented.
- At least two free/personal EOD sources return typed PriceResult rows or typed unresolved rows.
- Agreement gate can mark rows valuation_grade, provisional, or blocked.
- Yahoo is no longer the only path to valuation-grade status.
- Source lineage includes source_id, observed_date, close, currency, license_class, authority_tier and raw evidence path.
- No pricing action creates funding authority, portfolio mutation or production delivery.
```
