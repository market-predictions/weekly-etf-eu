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
status=BLOCKED
opened_at=2026-08-18T15:17:09+02:00
blocked_at=2026-08-18T15:34:00+02:00
report_date=2026-08-17
report_suffix=260817
run_id=20260817_151400
candidate_workflow_run=32141729593
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

## Current blocker — external second-provider freshness lag
Canonical candidate workflow run `32141729593` passed request validation, donor breadth selection, quota-aware candidate selection and routine preflight, then failed closed at funded completed-close pricing.

Exact funded result for report date `2026-08-17`:
```text
funded_lines=6
funded_consensus=0/6
funded_identity_anchors=0/6
pricing_gate=false
```

A separate non-authoritative diagnostic replay using the same candidate code and provider configuration proved the cause for every funded line:
- Alpha Vantage returned a valid `2026-08-17` exact configured-line close;
- Yahoo Chart returned only `2026-08-14` for the same line;
- therefore same-date provider count is 1, not 2;
- no ticker/ISIN/venue/currency mismatch was observed in Yahoo metadata;
- `stale_registry_funded_flags_overridden=[dfen_xetra_eur,iqqq_xetra_eur,l0ck_xetra_eur]` is normal protected-portfolio reconciliation and was also present in the prior successful 2026-08-14 qualification; it is not the cause.

Non-secret provider-availability evidence additionally proves:
```text
alpha_vantage_configured=true
yahoo_chart_configured=true
leeway_configured=false
eodhd_configured=false
marketstack_configured=false
```

The repository's Börse Frankfurt/Xetra adapter is explicitly `diagnostic_candidate_source` with unknown license status and no valuation/funding authority, so it is not promoted as an emergency second provider.

### Consequence
No client-grade 2026-08-17 report may be generated until either:
1. Yahoo Chart publishes the 2026-08-17 close for the funded lines and the existing two-provider gate passes on retry; or
2. a separately governed already-qualified second provider becomes configured and passes the same exact-line/same-date/identity contract.

Using Alpha alone, reusing 2026-08-14 closes, or promoting a diagnostic-only source would weaken the current authority contract and is prohibited.

## Operational runbook
1. Keep the current candidate branch/request intact.
2. Treat workflow run `32141729593` as a valid fail-closed attempt, not a report candidate.
3. On external provider freshness recovery, rerun the canonical candidate workflow with the same report-date contract if `2026-08-17` remains the correct completed close.
4. If later evidence establishes a different latest common completed close, create a new run identity rather than relabel stale prices.
5. After pricing passes, continue macro/discovery/re-underwriting, NL/EN generation, strict machine and PDF visual gates.
6. Persist candidate output to this branch and Actions artifact only.
7. Freeze exact candidate head and prepare independent assurance handover.
8. Do not merge or send within implementation authority.

## Protected boundaries
```text
delivery_authority=false
smtp_send=false
report_delivery=false
real_broker_execution=false
portfolio_mutation_without_explicit_current_allocation_authority=false
self_assurance=false
merge_before_independent_PASS=false
single_provider_fallback=false
stale_close_reuse=false
diagnostic_source_promotion=false
```

## Current status
`IMPLEMENTATION_BLOCKED` — external Yahoo completed-close freshness lag. No client report was generated and no delivery action occurred.
