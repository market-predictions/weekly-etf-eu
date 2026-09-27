# ETF EU Routine Weekly Production Runbook V3

Date: 2026-09-27  
Repository: `market-predictions/weekly-etf-eu`  
Status: CANONICAL

This runbook governs the single current Weekly ETF EU generation path. Generation/validation and delivery are separate authority domains.

## Read first

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/GOLDEN_PATH_PROOF_RULES.md`
5. `control/ETF_EU_ALLOCATION_AUTHORITY_V1.md`
6. `control/ETF_EU_DISCOVERY_FUNDABILITY_CONTRACT_V1.md`
7. `control/UCITS_INVESTABILITY_RULES.md`
8. `control/PRICING_AUTHORITY_CURRENT.md`

## Canonical lifecycle

```text
clean exact source checkout
→ fresh NO EMAIL request
→ completed-close pricing + donor/EU fundability
→ current-position re-underwrite + allocation boundary
→ one normalized NL/EN package
→ strict machine/client-quality gates
→ PRE_SEND_READY
→ frozen Actions evidence
→ independent exact-head assurance
→ governed integration / exact-main validation
→ separately authorized controlled transport
→ independent receipt/attachment confirmation
```

The generation workflow has no SMTP/send, delivery, broker-execution, funding or portfolio-mutation authority.

## Automation topology

Canonical generation workflow:

```text
.github/workflows/run-weekly-etf-eu-routine.yml
```

It has two legitimate uses:

- candidate/manual proof on a non-`main` branch;
- native scheduled generation on `main` each Wednesday at `18:30 UTC` (`19:30 CET` / `20:30 CEST`).

The schedule is intentionally after the European completed-close threshold used by `tools/resolve_etf_eu_completed_close_date.py`. It generates and validates only; it never invokes controlled transport.

Canonical controlled transport workflow:

```text
.github/workflows/send-weekly-etf-eu-controlled-transport.yml
```

Transport remains main-only and requires its existing independent-assurance and explicit human confirmation boundaries.

## Phase 1 — Clean exact source

The generation job checks out exact `github.sha` with full history. Before creating run-scoped files it must prove:

```text
HEAD == GITHUB_SHA
git status --porcelain == empty
manual_repair_applied=false
```

A dirty or wrong checkout fails closed.

## Phase 2 — Resolve run identity

For a fresh generated request:

1. resolve the latest plausible completed European close using `tools/resolve_etf_eu_completed_close_date.py`;
2. derive `report_suffix` from that date;
3. create a fresh run ID whose date prefix equals the report date;
4. bind the previous routine manifest and previous delivery closeout from the canonical pointer files;
5. set `execution_mode=generate_validate_candidate` and `delivery_authority=false`.

A prepared v2 request may be supplied for a manual non-main proof. Historical repair dates must never be hard-coded into the canonical routine.

## Phase 3 — Donor research and EU fundability

`market-predictions/weekly-etf` is a research/behavior donor only. The WEEU workflow may read donor artifacts but may not execute US portfolio, pricing, report or send paths.

The EU path:

1. selects donor breadth evidence on or before the report date;
2. records donor source SHA/provenance;
3. maps research proxies through the EU UCITS proxy map;
4. applies EU identity/KID/fundability rules;
5. carries no funding authority from the donor.

## Phase 4 — Current pricing

Pricing authority is defined by `control/PRICING_AUTHORITY_CURRENT.md` and the current executable pricing contract. The routine must use exact trading-line identity and current completed-close evidence and fail closed on the contract's blocking conditions.

Pricing confidence is valuation evidence, never an allocation or broker-execution instruction.

## Phase 5 — Current-position re-underwriting and allocation boundary

Every funded holding is re-underwritten from current evidence. Missing evidence is unresolved, never fabricated.

The routine remains valuation/recommendation only unless a separate explicit allocation decision exists. It may not mutate protected shares, cash or trade ledger and may not execute at a broker.

## Phase 6 — One normalized NL/EN package

Build one run-scoped normalized state and render:

- Dutch primary Markdown/HTML/PDF;
- English companion Markdown/HTML/PDF;
- pricing, macro and donor provenance;
- funded-position identity including exact ISIN/trading line;
- recommendation and allocation-boundary state.

NL and EN are two renderings of one normalized state, not independent research runs.

## Phase 7 — Deterministic quality gates

Required automated gates include:

```text
funded_position_set_matches_protected_state=true
funded_state_consistency_passed=true
nl_en_numeric_state_parity=true
client_grade_v2_passed=true
markdown_delivery_validation_passed=true
pdf_client_grade_passed=true
client_surface_clean=true
authority_metadata_absent=true
raw_status_enums_absent=true
```

All NL/EN PDF pages are also rendered into review pages and frozen in the evidence bundle for independent review.

## Phase 8 — PRE_SEND_READY finalization

Only after the strict NL/EN, Markdown and routine machine gates pass, `tools/write_etf_eu_routine_v2_machine_gate.py` invokes the minimal finalizer `tools/finalize_etf_eu_pre_send_ready.py`.

It updates the existing package manifest, readiness artifact and routine manifest to one terminal generation truth:

```text
pre_send_ready=true
full_generation_status=PRE_SEND_READY
next_action=INDEPENDENT_RELEASE_ASSURANCE
```

The same artifacts must still prove:

```text
ready_for_controlled_delivery=false
delivery_authorized=false
production_delivery_authority=false
send_executed=false
transport_attempted=false
funding_authority=false
portfolio_mutation=false
```

`PRE_SEND_READY` therefore means “generation and deterministic quality validation completed”; it is not delivery authority.

## Phase 9 — Exact-head and immutable evidence

Before success, the workflow re-checks:

```text
git rev-parse HEAD == GITHUB_SHA
live source branch SHA == GITHUB_SHA
```

A moved branch fails closed as `ETF_EU_PROOF_STALE_CANDIDATE`.

Generated report files, machine gates, PRE_SEND_READY artifacts, pricing/provenance and review pages are uploaded as one GitHub Actions artifact. They are evidence, not repository source. The generation workflow never commits or pushes proof output.

## Phase 10 — Independent assurance

A separate `governance_release_assurance` review reconstructs the frozen exact candidate and returns:

```text
PASS | FAIL | INDETERMINATE
```

Implementation may not certify itself. A repair changes the SHA and requires fresh affected proof and assurance.

## Phase 11 — Integration

After unchanged exact-head PASS and governed integration authority:

1. merge;
2. verify exact `main` where required;
3. reconcile current-state/next-action records;
4. allow the native weekly schedule to operate from default branch.

A scheduled workflow in GitHub Actions runs from the default branch. Therefore the first genuine cron-triggered proof can only exist after the scheduled workflow has been integrated into `main`; a manual dispatch is not substituted for that evidence.

## Phase 12 — Controlled transport

Delivery is a separate operation. It requires the existing guarded-delivery authority, independent assurance binding and explicit human confirmation. Generation success, `PRE_SEND_READY`, a successful schedule or SMTP no-exception does not prove delivery.

A delivered weekly run is complete only after positive independent receipt/attachment evidence.

## Retired routes

Transition allocators, dated repair/preview workflows, old send workflows, candidate branch persistence of generated output and US donor execution paths are historical/diagnostic evidence only. They are not current production routes.

Git history is the archive; active workflow topology represents current truth.

## Completion definitions

A generation cycle is complete when its exact source SHA reaches `PRE_SEND_READY` and its immutable evidence bundle exists.

A release candidate is assurance-ready only after that exact generation evidence is frozen for independent review.

A delivered weekly report is complete only after independent PASS, governed integration, separately authorized transport and independent receipt/attachment confirmation.
