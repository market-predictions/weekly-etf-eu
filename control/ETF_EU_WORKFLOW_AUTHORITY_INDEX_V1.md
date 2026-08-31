# Weekly ETF EU Workflow Authority Index V1

**Status:** ACTIVE CURRENT STANDARD  
**Product:** `weekly_etf_eu`  
**Authority scope:** operational workflow topology only

## Purpose

This file defines the complete current GitHub Actions topology for Weekly ETF EU. Anything not listed here is not a current production/supporting workflow merely because it exists in Git history or archive.

## Canonical lifecycle

```text
non-main candidate generation
→ machine validation
→ independent exact-head assurance
→ governed integration
→ exact-main validation
→ separately authorized guarded transport
→ receipt evidence
```

Machine validation never substitutes for independent assurance. SMTP transport never substitutes for receipt evidence.

## Current executable workflows

`.github/workflows/` contains exactly six current/current-supporting workflows.

### 1. Candidate build

`/.github/workflows/run-weekly-etf-eu-routine.yml`

May:
- build a candidate on a non-`main` branch;
- obtain current EU/UCITS evidence;
- construct the Thin Current Kernel semantic state and pure client artifacts;
- run machine validation;
- persist candidate evidence to the same candidate branch;
- upload review evidence.

May not:
- push candidate semantics to `main`;
- self-assure;
- merge;
- create delivery authority;
- send email;
- execute broker actions;
- mutate protected portfolio/trade-ledger authority without separate explicit current allocation authority.

### 2. Guarded delivery

`/.github/workflows/send-weekly-etf-eu-controlled-transport.yml`

This is the only workflow authorized to invoke real ETF EU transport. It is main-only and requires exact guarded-delivery authority, exact assured/integrated lineage, double send confirmation, frozen Thin Current Kernel manifest binding and exact artifact hashes. It may persist post-transport delivery/receipt evidence to `main`; this narrow post-delivery evidence write is the only direct-main-write exception.

It may not re-render or change approved semantic facts.

### 3. Current-kernel regression gate

`/.github/workflows/validate-etf-eu-current-kernel.yml`

Validates:
- `runtime/current/`;
- frozen-state and pure-render contracts;
- guarded-delivery authority/package binding;
- product/repository/workflow boundaries;
- execution reachability;
- canonical runtime namespace.

### 4. Close-price provider engine gate

`/.github/workflows/validate-etf-eu-price-provider-engine.yml`

Validates provider, identity, cache, redaction, capacity and qualification infrastructure. It supplies pricing evidence only; it has no report, funding, allocation, portfolio or delivery authority.

### 5. Release-evidence preflight gate

`/.github/workflows/validate-etf-eu-release-assurance.yml`

Validates machine-readable release-evidence preflight. It explicitly does **not** create independent assurance.

### 6. Repository/product boundary gate

`/.github/workflows/validate-etf-eu-repository-boundary.yml`

Validates the Weekly ETF EU product boundary and rejects donor/U.S. product leakage or prohibited executor reachability.

No additional active workflow is authorized without an explicit governed architecture change and corresponding update to this index plus boundary tests.

## Canonical runtime namespace

Current top-level runtime authority is deliberately limited to:

```text
runtime/__init__.py
runtime/adapt_weekly_etf_macro_for_eu.py
runtime/current/
runtime/send_etf_eu_controlled_report.py
runtime/write_etf_eu_delivery_evidence.py
runtime/check_etf_eu_delivery_receipt.py
```

All investment/client semantics after evidence acquisition live in `runtime/current/`.

`tools/validate_etf_eu_current_reachability.py` fails closed if an additional top-level runtime executor or subdirectory appears. Git history is the default provenance for retired code; historical executable code must not remain beside current production code merely for convenience.

## Current per-run output contract

The Thin Current Kernel writes the current candidate package under:

```text
output/current/
```

with immutable per-run copies under:

```text
output/history/<report_date>/<run_id>/
output/evidence/<run_id>/
```

The frozen review state is the semantic source. NL/EN Markdown/HTML/PDF are projections from that state. Delivery binds to the exact current manifest plus artifact hashes and may not silently select different files.

## Independent assurance

Independent assurance is performed by a separate `governance_release_assurance` worker on one exact candidate head and returns `PASS | FAIL | INDETERMINATE`.

Rules:
- implementation worker may not self-assure;
- assurance worker may not repair the candidate under review;
- semantic candidate changes invalidate prior assurance;
- machine checks are supporting evidence only.

## Retired workflow disposition

There is no `.yml.disabled` category in `.github/workflows/`.

Retired workflows leave the active namespace. Git history is the default provenance. Only incident-relevant forensic artifacts explicitly documented under `archive/workflows/` may remain non-executable.

The retained 2026-08-10 donor-boundary forensic artifacts carry no current authority.

## Donor/product-boundary rule

`market-predictions/weekly-etf` is donor evidence/code only. It never supplies EU holdings, recipients, workflow state, protected portfolio state, delivery authority or allocation authority.

Active ETF EU workflows may not invoke donor U.S. product surfaces such as:
- `output/etf_portfolio_state.json` as EU state;
- `weekly_analysis_pro_*` as EU report authority;
- root `send_report.py` as EU delivery/render authority;
- `etf.txt` / `etf-pro.txt` as current execution authority.

## Authority hierarchy

For operational routing:

```text
this index + current runbook
> six canonical/current-supporting workflows
> Thin Current Kernel/runtime namespace
> explicit forensic archive
> Git history
```

For funding/allocation authority, defer to protected state and `control/ETF_EU_ALLOCATION_AUTHORITY_V1.md`. This index never creates investment authority.
