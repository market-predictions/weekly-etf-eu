# Handover — Weekly ETF EU Roadmap After M1 Pricing Spine Integration

Date: 2026-06-03  
Repository: `market-predictions/weekly-etf-eu`  
Purpose: fresh-chat handover and roadmap for further development of the Weekly ETF EU / Dutch-client UCITS ETF report.

---

## Fresh-chat start instruction

Continue in `market-predictions/weekly-etf-eu`.

Read from GitHub in this exact order before doing meaningful work:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/PARALLEL_WORKSTREAM_PLAN_20260603.md`
5. this handover file:
   - `control/handovers/HANDOVER_WEEKLY_ETF_EU_ROADMAP_AFTER_M1_PRICING_SPINE_20260603.md`
6. then the minimum relevant work-package or execution files.

Important: GitHub is the source of truth. The control files are slightly stale after the M1 pricing-spine merges. This handover records the latest integration state and should be used to update the control files first in the next chat.

---

## Executive status

The parallel M1 pricing-spine worker phase is complete and merged.

Merged into `main`:

```text
PR #3 — M1 common pricing interface
PR #4 — M1 Stooq pricing adapter
PR #5 — M1 Börse Frankfurt / Xetra pricing adapter
PR #6 — M1 Yahoo fallback pricing adapter
PR #7 — M1 issuer NAV reference adapter
```

Merge commits:

```text
PR #3  0c21629aa315f18a0ebceb0a301841d457d2a554
PR #4  c92cff7a973f27f152b4c866515d7c84e28135d6
PR #5  34d6c909e87015de49e31ed3fc25294084faad16
PR #6  9138efd0d5613527bd6ab6f44313596e6cb6907f
PR #7  7b74a36de88b8fdb5b4a4f8709312df533c27a9d
```

Current pricing-spine result:

```text
common PriceSource / PriceResult interface exists
Stooq adapter exists
Börse Frankfurt / Xetra adapter exists
Yahoo fallback adapter exists
Issuer NAV reference adapter exists
```

Current authority result:

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

This means: the repo now has a typed multi-source pricing evidence spine, but no valuation-grade pricing pipeline yet.

---

## Current issue

The repo has successfully moved from ad-hoc/non-authoritative pricing preflight toward a typed pricing evidence spine.

However, the following remain incomplete:

```text
source metadata policy integration
agreement gate
valuation artifact wiring to agreement output
report pricing surface integration
fundability / candidate promotion contract
production-grade Dutch-first report
PDF/email/delivery enablement
```

Also, `control/CURRENT_STATE.md`, `control/NEXT_ACTIONS.md`, and `control/CHANGELOG.md` have not yet been fully consolidated after PRs #3–#7. The fresh chat should perform that consolidation before new architecture work.

---

## Four-layer separation to preserve

Every next change must keep these layers separate.

### 1. Decision framework

Purpose: decide which UCITS ETFs available to Dutch/EU investors deserve capital.

Current state:

- no candidate is funded;
- `core_us_equity_cspx` is the only verified candidate seed;
- other candidates remain placeholders / requires-verification / policy-blocked;
- no pricing result is allowed to promote a candidate to `fundable`.

Next work in this layer:

- define fundability / promotion contract later;
- include UCITS status, PRIIPs/KID, liquidity, spread, role, risk, concentration, and pricing authority.

### 2. Input/state contract

Purpose: define where authoritative instrument, pricing, portfolio and investability facts come from.

Current state:

- UCITS registry and investability validators exist;
- typed `PriceSource` / `PriceResult` interface exists;
- adapters now produce typed evidence or typed unresolved results;
- no source evidence is valuation-grade by itself.

Next work in this layer:

- integrate source metadata policy;
- implement agreement gate;
- then wire agreement-gate output into valuation artifacts.

### 3. Output contract

Purpose: ensure Dutch-first EU client reports distinguish investable UCITS ETFs from U.S. research proxies and candidate evidence.

Current state:

- Dutch-first and English companion skeleton reports exist;
- reports show cash-only state and candidate rows;
- candidate rows are not portfolio holdings and not buy recommendations.

Next work in this layer:

- after agreement gate, display priced candidate rows without implying funded positions;
- later convert to full production Dutch/EU UCITS report.

### 4. Operational runbook

Purpose: define deterministic GitHub Actions / scripts behavior without accidentally using U.S. ETF holdings as EU truth.

Current state:

- inherited U.S. delivery path is disabled;
- EU bootstrap validation exists;
- no production PDF/email/delivery is enabled;
- GitHub run verification should be done by ChatGPT when tool access allows.

Next work in this layer:

- only after agreement-gate integration, wire controlled validation into workflow;
- do not enable production delivery until EU validators and delivery receipt/manifest path are ready.

---

## Integrated pricing spine details

### Common interface

Integrated files:

```text
pricing/README.md
pricing/price_result_schema.py
pricing/source_selection.py
pricing/sources/__init__.py
pricing/sources/base.py
tests/fixtures/pricing/fake_price_rows.json
tests/test_pricing_interface.py
```

Contract:

```text
PriceSource.fetch_eod_close(request: PriceRequest) -> PriceResult
```

Key shared concepts:

```text
PriceIdentity
PriceRequest
PriceResult
SourceLineage
status constants
license_class constants
authority_tier constants
```

### Stooq adapter

Integrated files:

```text
pricing/sources/stooq.py
config/source_symbol_overrides/stooq.yml
tests/test_stooq_adapter.py
tests/fixtures/pricing/stooq/cspx_daily.csv
tests/fixtures/pricing/stooq/no_data.csv
```

Role:

```text
provisional / cross-check source
license_class=provider_free_personal
authority_tier=diagnostic_candidate_source
```

Important uncertainty:

```text
CSPX London USD -> cspx.uk
SXR8 Xetra EUR -> sxr8.de
```

These Stooq mappings remain provisional and require provider coverage verification before valuation use.

### Börse Frankfurt / Xetra adapter

Integrated files:

```text
config/source_symbol_overrides/boerse_frankfurt.yml
pricing/sources/boerse_frankfurt.py
tests/fixtures/pricing/boerse_frankfurt/currency_uncertain.json
tests/fixtures/pricing/boerse_frankfurt/no_close.json
tests/fixtures/pricing/boerse_frankfurt/resolved_close.json
tests/test_boerse_frankfurt_adapter.py
```

Role:

```text
exchange-candidate evidence only
license_class=unknown
license_note=undocumented_free_source_pending_license_review
authority_tier=diagnostic_candidate_source
authority_note=exchange_candidate_evidence_only_not_valuation_authority
```

Important uncertainty:

The endpoint is undocumented/free and pending source/license review. It must not become valuation authority by itself.

### Yahoo adapter

Integrated files:

```text
pricing/sources/yahoo.py
tests/test_yahoo_adapter.py
tests/fixtures/pricing/yahoo/cspx_history.json
tests/fixtures/pricing/yahoo/empty_history.json
tests/fixtures/pricing/yahoo/missing_close_history.json
```

Role:

```text
fallback / provisional evidence only
source_id=yahoo_yfinance
license_class=provider_free_personal
authority_tier=non_authoritative_connectivity_only
```

Important rule:

Yahoo/yfinance must not be the only path to valuation-grade UCITS pricing.

### Issuer NAV adapter

Integrated files:

```text
pricing/sources/issuer_nav.py
tests/test_issuer_nav_adapter.py
tests/fixtures/pricing/issuer_nav/valid_cspx_nav.json
tests/fixtures/pricing/issuer_nav/missing_currency_nav.json
```

Role:

```text
reference / stale-check evidence only
value_type=issuer_nav_reference
not_exchange_trading_line_close=true
license_class=issuer_public
authority_tier=diagnostic_candidate_source
```

Important rule:

Issuer NAV is not an exchange EOD close adapter and must not count as an independent market-close source for valuation-grade agreement.

---

## Immediate next step: control-file consolidation

Before new feature work, update repo control files so they reflect the M1 pricing-spine completion.

Recommended branch:

```text
workstream/control-consolidation-after-m1-pricing-spine
```

Files to update:

```text
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/CHANGELOG.md
control/DECISION_LOG.md   # if needed
```

Required updates:

1. In `CURRENT_STATE.md`, move these from incomplete to complete:

```text
common PriceSource / PriceResult interface integration
at least two fixture-backed provider adapters returning typed resolved or unresolved rows
pricing spine integration
```

2. In `CURRENT_STATE.md`, add the integrated PRs and merge commits:

```text
PR #3 — common pricing interface — 0c21629aa315f18a0ebceb0a301841d457d2a554
PR #4 — Stooq adapter — c92cff7a973f27f152b4c866515d7c84e28135d6
PR #5 — Börse Frankfurt / Xetra adapter — 34d6c909e87015de49e31ed3fc25294084faad16
PR #6 — Yahoo adapter — 9138efd0d5613527bd6ab6f44313596e6cb6907f
PR #7 — Issuer NAV reference adapter — 7b74a36de88b8fdb5b4a4f8709312df533c27a9d
```

3. In `CURRENT_STATE.md`, keep these still incomplete:

```text
source metadata policy integration
agreement gate integration
valuation artifact consumption of agreement output
valuation_grade true rows
candidate promotion to fundable
funded EU model portfolio
production Dutch-first report
PDF/email/delivery enablement
```

4. In `NEXT_ACTIONS.md`, mark actions 35 and 36 as done:

```text
35. Integrate common pricing interface — done
36. Integrate provider adapters after interface — done
```

5. In `NEXT_ACTIONS.md`, make source metadata policy the next immediate work item:

```text
37. Integrate source metadata policy — next
38. Integrate agreement gate — queued after source metadata policy / now technically unblocked by adapter availability
39. First report pricing surface — blocked until agreement gate exists
```

6. In `CHANGELOG.md`, add integration entries for PRs #3–#7. The current changelog is stale and still emphasizes earlier draft review state.

7. In `DECISION_LOG.md`, record stable architecture decisions if not already present:

```text
Yahoo is fallback/provisional, not sole valuation authority.
Issuer NAV is reference/stale-check only, not market-close agreement source.
Valuation-grade requires source policy + agreement gate.
Pricing adapters return evidence; they do not mutate portfolio state, promote candidates, render reports, or deliver email.
```

Definition of done for control consolidation:

```text
control files reflect PRs #3-#7 merged
roadmap points to source metadata and agreement gate as next work
no execution code changes
no output/state/workflow/delivery changes
```

---

## Next development roadmap

### Phase A — Source metadata policy

Use existing work package:

```text
control/work_packages/WP_M5_SOURCE_METADATA_POLICY_20260603.md
```

Recommended branch:

```text
workstream/source-metadata-policy
```

Owned files from the work package:

```text
control/DATA_SOURCE_METADATA.md
control/CHANGELOG.md
pricing/source_metadata_policy.py
tests/test_source_metadata_policy.py
```

Goal:

Create a deterministic source metadata register and helper so sources are selected and filtered by declared policy rather than hardcoded assumptions.

Required categories should align with `PriceResult` / `SourceLineage`:

```text
source_id
provider_name
source_type
usage_mode
license_class
authority_tier
review_status
valuation_grade_eligible_default
agreement_gate_role
known_limitations
```

Important policy decisions:

```text
Stooq: provisional / cross-check candidate; provider coverage still requires verification.
Börse Frankfurt: exchange-candidate evidence; undocumented/free endpoint pending license review.
Yahoo: non-authoritative fallback/provisional only.
Issuer NAV: reference/stale-check only; not a market-close agreement source.
```

Do not edit workflows, output files, portfolio state, valuation builder, or delivery behavior in this phase.

### Phase B — Agreement gate

Use existing work package:

```text
control/work_packages/WP_M1_AGREEMENT_GATE_INTEGRATION_20260603.md
```

Recommended branch:

```text
workstream/agreement-gate-integration
```

Owned files from the work package:

```text
pricing/price_agreement_gate.py
tools/validate_price_agreement_gate.py
tests/test_price_agreement_gate.py
tests/fixtures/pricing/agreement_gate/*
```

Goal:

Implement a deterministic agreement gate that classifies pricing evidence for the same ISIN/trading line as:

```text
valuation_grade
provisional
blocked
```

Core gate rules:

1. One resolved source alone is provisional, not valuation-grade.
2. Two compatible independent market-close sources may become valuation-grade if policy allows.
3. Currency mismatch blocks or marks provisional with reason.
4. Date mismatch / stale source blocks or marks provisional with reason.
5. Price disagreement beyond tolerance blocks.
6. Yahoo cannot be sole route to valuation-grade.
7. Issuer NAV cannot count as an independent exchange-close agreement source.
8. Any gate result must keep:

```text
funding_authority=false
portfolio_mutation=false
production_delivery=false
```

Suggested default tolerance:

```text
absolute tolerance: explicit config or fixture default
relative tolerance: explicit config or fixture default
```

Do not wire into valuation builder during first pass unless doing a final integration PR after tests are stable.

### Phase C — Valuation artifact integration

Only after the agreement gate exists and passes tests.

Likely files:

```text
pricing/build_ucits_valuation_prices.py
tools/validate_ucits_valuation_prices.py
config/ucits_pricing_source_policy.yml
```

Goal:

Allow `output/pricing/ucits_valuation_prices_*.json` to consume agreement-gate output.

Rules:

```text
valuation_grade rows require gate=valuation_grade
provisional rows remain non-authoritative
blocked rows must explain reason
valuation artifact still cannot mutate portfolio state
funding_authority remains false
production_delivery remains false
```

### Phase D — First report pricing surface

Use existing work package:

```text
control/work_packages/WP_M2_FIRST_REPORT_INTEGRATION_20260603.md
```

Recommended branch:

```text
workstream/first-report-integration
```

Goal:

Display priced UCITS candidate evidence in the Dutch-first report without presenting candidates as funded holdings or buy recommendations.

Rules:

```text
priced candidate != funded holding
valuation_grade != funding authority
U.S. proxies remain research-only
cash-only portfolio state remains unchanged
no PDF/email/delivery
```

### Phase E — Fundability / candidate promotion contract

Only after valuation-grade pricing exists.

Goal:

Define when a candidate can move from:

```text
verified_candidate_not_funded
```

to:

```text
fundable
```

Required gates should include:

```text
UCITS status
PRIIPs/KID availability
trading line verified
valuation-grade price available
liquidity/spread checks
portfolio role
risk/concentration limits
manual or automated approval rule
```

No portfolio mutation should occur until this contract exists and is validated.

### Phase F — Production Dutch-first report

Only after valuation-grade pricing and fundability rules exist.

Goal:

Move from candidate skeleton to a client-native Dutch/EU weekly ETF report.

Rules:

```text
Dutch report is primary
English report is companion/operator-facing
not a translation of U.S. report
uses EU-specific state files
does not treat U.S. ETFs as investable holdings
```

### Phase G — Delivery enablement

Last phase only.

Goal:

Enable PDF/email/delivery after all EU validators pass and after delivery receipt/manifest semantics are explicit.

Rules:

```text
never claim delivery succeeded without receipt/manifest
do not rely on inherited U.S. sender behavior
Gmail inbox receipt checking is deferred; sent-manifest is enough for first delivery phase
```

---

## Open risks and unresolved questions

### Source licensing and authority

- Börse Frankfurt endpoint is undocumented/free and pending source/license review.
- Stooq symbol coverage for UCITS trading lines is provisional.
- Yahoo/yfinance remains non-authoritative and free/personal-use style fallback.
- Issuer NAV is reference only.
- Future paid data providers may be needed for robust valuation-grade pricing.

### Source agreement semantics

Need exact agreement policy for:

```text
same observed_date required vs allowed adjacent completed sessions
same trading currency required
absolute/relative close tolerance
source independence weighting
issuer NAV stale-check role
```

### Registry completeness

The UCITS registry is still a seed registry. Only CSPX is verified enough for current preflight. Other candidate rows require verification before pricing/funding.

### Stale control files

`CURRENT_STATE.md`, `NEXT_ACTIONS.md`, and `CHANGELOG.md` lag behind the actual merged PR state. Consolidation is the first recommended fresh-chat task.

### Legacy artifacts

U.S. clone artifacts still exist and must remain non-authoritative. M0 documented quarantine policy, but not all inherited artifacts have been moved.

---

## Recommended first fresh-chat task

Use this as the first user prompt in the fresh chat:

```text
Continue in market-predictions/weekly-etf-eu.

Read:
1. control/SYSTEM_INDEX.md
2. control/CURRENT_STATE.md
3. control/NEXT_ACTIONS.md
4. control/PARALLEL_WORKSTREAM_PLAN_20260603.md
5. control/handovers/HANDOVER_WEEKLY_ETF_EU_ROADMAP_AFTER_M1_PRICING_SPINE_20260603.md

Then perform control-file consolidation only:
- update CURRENT_STATE.md so PRs #3-#7 are reflected as merged;
- update NEXT_ACTIONS.md so pricing interface and adapter integration are marked done;
- update CHANGELOG.md with PRs #3-#7;
- update DECISION_LOG.md only for stable architecture decisions if not already present.

Do not edit pricing execution code, workflows, output files, portfolio state, report renderer, PDF/email, or delivery behavior.
```

After that, start `WP_M5_SOURCE_METADATA_POLICY_20260603.md`, then `WP_M1_AGREEMENT_GATE_INTEGRATION_20260603.md`.

---

## Session-close summary

Completed in this session:

```text
M1 pricing interface merged
Stooq adapter merged
Börse Frankfurt / Xetra adapter merged
Yahoo fallback adapter merged
Issuer NAV reference adapter merged
```

Next durable roadmap:

```text
control consolidation
source metadata policy
agreement gate
valuation artifact integration
first report pricing surface
fundability contract
production Dutch-first report
delivery enablement
```

Standing authority rule:

```text
No pricing evidence creates funding authority, portfolio mutation, production delivery, PDF generation or email delivery until the relevant later contracts and validators explicitly allow it.
```
