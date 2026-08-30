# Weekly ETF EU Workflow Authority Index V1

**Status:** ACTIVE CURRENT STANDARD  
**Product:** `weekly_etf_eu`  
**Authority scope:** operational workflow topology only

## Purpose

This file defines which GitHub Actions routes may participate in the current Weekly ETF EU lifecycle. It prevents activation, preview, repair, donor-runtime and delivery history from silently becoming parallel production authority.

## Canonical topology

### Candidate build route

Canonical workflow:

`/.github/workflows/run-weekly-etf-eu-routine.yml`

Authority:
- build a candidate on a non-`main` branch;
- obtain current EU/UCITS evidence;
- construct the current semantic state and client artifacts;
- run machine validation;
- persist candidate evidence to the same candidate branch;
- upload review evidence where configured.

Explicitly not authorized:
- pushing candidate output directly to `main`;
- granting independent assurance;
- merging the candidate;
- creating delivery authority;
- sending email;
- mutating protected portfolio/trade-ledger authority without separate current allocation authority;
- real broker execution.

A v2 routine request must declare:

```text
execution_mode=generate_validate_candidate
delivery_authority=false
```

Retained donor primitives are evidence/discovery inputs only and never create EU runtime or state authority.

### Independent assurance route

Independent assurance is not produced by the candidate workflow. A separate `governance_release_assurance` worker reviews one exact frozen candidate head and returns `PASS | FAIL | INDETERMINATE`. Machine checks are supporting evidence only. Any semantic candidate change invalidates the verdict.

### Merge / exact-main route

A semantic candidate may be merged only after the required independent exact-head PASS and unchanged-head verification. Exact-main validation must then prove the approved candidate is present without unreviewed semantic drift.

### Guarded delivery route

Canonical workflow:

`/.github/workflows/send-weekly-etf-eu-controlled-transport.yml`

This is the only current workflow authorized to invoke real ETF EU transport. It is `main`-only, requires exact guarded-delivery authority, validates exact artifact hashes, does not re-render, sends exact approved artifacts, records transport evidence separately and may not claim inbox delivery without positive receipt evidence.

## Active supporting workflows

EU-scoped diagnostic, pricing, lab, probe and validation workflows may remain active only when they are non-authoritative and genuinely support the current product boundary. They must not:
- create funding or portfolio-mutation authority;
- invoke real delivery outside the canonical controlled-transport route;
- create independent assurance;
- turn report text into portfolio state;
- render a parallel client-like production report from historical/shadow state;
- execute retained donor U.S. pricing/report runtime as ETF EU authority.

Architecture V2 requires these supporting workflows to trend down as permanent current-kernel regressions absorb their useful checks.

## Retired workflow disposition

There is no longer an indefinite `.yml.disabled` category inside `.github/workflows/`.

On the Revision V2 realization line, all retired `.disabled` workflows were removed from the executable workflow namespace. Git history is the default provenance source.

Only three incident-relevant workflows are retained as explicit non-executable forensic artifacts under `archive/workflows/`:
- `archive/workflows/persist-etf-pricing-audit.yml`;
- `archive/workflows/validate-etf-runtime.yml`;
- `archive/workflows/validate-etf-lane-breadth.yml`.

They document the 2026-08-10 donor/U.S. product-boundary leakage incident and carry **no current authority**. `archive/README.md` defines the archive policy.

## Post-merge donor-leak incident rule

PR #91 was independently PASSed and merged, after which a still-active legacy pricing-audit path wrote U.S. holdings/pricing artifacts into ETF EU. A subsequent boundary scan also found an active donor-report breadth validator anchored to `weekly_analysis_pro_*`.

Stable lesson:

> Green CI does not create product identity. An active ETF EU workflow may not invoke retained U.S. Weekly ETF donor execution surfaces as product authority.

Prohibited active-workflow execution tokens include at minimum:
- `pricing.run_pricing_pass` when used as donor U.S. pricing authority rather than an explicitly bounded retained primitive;
- `output/etf_portfolio_state.json`;
- `weekly_analysis_pro_`;
- `send_report.py` / `import send_report` as donor client renderer/delivery authority;
- `etf.txt`;
- `etf-pro.txt`.

Historical appearances under `archive/` are allowed only as forensic evidence.

## Current-kernel boundary

Architecture V2 adds a stronger requirement:

- one current candidate entrypoint;
- one current transport entrypoint;
- one per-run semantic `review_state` after freeze;
- no archived path imported/called by current production;
- no retired workflow under `.github/workflows/`;
- validators detect/fail and do not silently repair investment semantics;
- downstream render/delivery does not change frozen semantic facts.

Executor reachability is verified by the current-kernel boundary tooling introduced under Revision V2. A file that merely looks old is not deleted without reference/reachability evidence; once a current responsibility supersedes it and no current reference remains, it must leave the current runtime/workflow namespace.

## Enforced gates

Current repository/product boundary checks include:
- `tools/validate_etf_eu_workflow_authority.py`;
- `tools/validate_etf_eu_repository_boundary.py`;
- Revision V2 read-first/current-kernel validators.

They must prove at minimum:
- `.github/workflows/` contains executable/current-supporting workflows only;
- no active workflow executes prohibited donor U.S. product paths;
- candidate workflow cannot send, self-assure or silently push production state to `main`;
- controlled transport requires exact authority and does not re-render approved artifacts;
- there is exactly one real ETF EU transport entrypoint;
- archive paths cannot become current imports/routing targets.

## Authority hierarchy

For operational routing:

`this index + current runbook > canonical current workflows > current-supporting EU validation workflows > explicit forensic archive > Git history`

For allocation/funding authority, defer to protected state plus `control/ETF_EU_ALLOCATION_AUTHORITY_V1.md`. This index never creates allocation authority.