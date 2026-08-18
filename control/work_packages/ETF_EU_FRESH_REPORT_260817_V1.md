# ETF EU Fresh Report 2026-08-17 — V1

## Identity
```text
workpackage_id=ETF-EU-FRESH-REPORT-260817-V1
claim_id=ETF-EU-FRESH-REPORT-260817-V1
issue=109
repository=market-predictions/weekly-etf-eu
branch=agent/etf-eu-fresh-260817-v1
base_main_sha=0ea61c349b99dcd23f61fed1e72b46326d516914
owner_role=implementation_operations
status=ACTIVE
opened_at=2026-08-18T15:17:09+02:00
report_date=2026-08-17
report_suffix=260817
run_id=20260817_151400
principal_decision_required=false
```

## Current issue
Generate one genuinely fresh Weekly ETF EU candidate after the closed 2026-08-14 cycle and the subsequently merged email-equity parity repair.

## Decision framework
- perform a full current portfolio re-underwrite;
- use broad Weekly ETF donor discovery as research input only;
- require EU-local UCITS mapping/fundability before any candidate is described as investable;
- no hard ticker-count target;
- no retired 50/35/15 allocation controls;
- 75% remains pricing-coverage context only;
- routine generation is valuation/recommendation only absent separate current allocation authority.

## Input/state contract
- protected portfolio: `output/etf_eu_portfolio_state.json`;
- trade ledger: `output/etf_eu_trade_ledger.csv`;
- valuation history: `output/etf_eu_valuation_history.csv`;
- recommendation scorecard: `output/etf_eu_recommendation_scorecard.csv`;
- UCITS identity registry and proxy map remain project-local authority;
- predecessor routine manifest: `output/run_manifests/etf_eu_routine_run_manifest_2026-08-14_20260814_235900.json`;
- predecessor delivery closeout: `output/run_manifests/etf_eu_delivery_closeout_manifest_20260818_061712.json`;
- requested report date is 2026-08-17, but provider evidence must prove it as the same valid completed close for funded lines or the run fails closed.

## Output contract
Produce one normalized-state bilingual candidate package:
- NL Markdown / HTML / PDF;
- EN Markdown / HTML / PDF;
- fresh pricing evidence;
- donor provenance and discovery bridge;
- current re-underwriting and recommendation memory;
- machine/client-grade validation artifacts;
- rendered PDF review pages;
- routine manifest and frozen Actions artifact.

The active donor-aligned graph contract must apply: deterministic PNG before SMTP; final standalone HTML contains embedded PNG; PDF is generated from the same final HTML. Candidate generation has no SMTP authority.

## Operational runbook
1. Create candidate-only request for run `20260817_151400`.
2. Validate request/preflight.
3. Run canonical `.github/workflows/run-weekly-etf-eu-routine.yml` on this branch only.
4. Require funded exact-line same-date pricing consensus.
5. Build broad donor discovery bridge and current full re-underwriting.
6. Generate NL/EN client surfaces.
7. Run strict machine and PDF visual gates.
8. Persist candidate output to this branch and Actions artifact only.
9. Freeze exact candidate head and prepare independent assurance handover.
10. Do not merge or send within implementation authority.

## Protected boundaries
```text
delivery_authority=false
smtp_send=false
report_delivery=false
real_broker_execution=false
portfolio_mutation_without_explicit_current_allocation_authority=false
self_assurance=false
merge_before_independent_PASS=false
```

## Definition of done for this work package phase
`ASSURANCE_READY`: fresh candidate artifacts exist on one exact frozen head with all required implementation gates green and no delivery action executed.
