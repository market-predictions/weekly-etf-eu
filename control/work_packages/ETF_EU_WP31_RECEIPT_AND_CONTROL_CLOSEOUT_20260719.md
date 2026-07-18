# ETF-EU-WP31 — Receipt and control closeout

Date: 2026-07-19
Repository: `market-predictions/weekly-etf-eu`
Branch: `feature/etf-eu-wp31-receipt-control-closeout`

## Layer

```text
decision framework: unchanged
input/state contract: redaction-safe receipt evidence
output contract: unchanged
operational runbook: close completed delivery cycle
```

## Current issue

The 2026-07-17 package completed guarded transport and an independent mailbox match exists, but GitHub controls still describe the package as awaiting manual dispatch. The current-run receipt evidence and production closeout manifests are absent.

## Root cause

The mailbox check occurred after transport, but connector safety controls blocked the earlier attempt to persist Gmail-derived evidence to GitHub. This left the operational source of truth behind the observed delivery state.

## Donor inspection

Inspected in `market-predictions/weekly-etf`:

- the latest run and delivery manifest closeout pattern;
- independent inbox receipt as a condition for a completed cycle;
- strict separation between transport success and receipt confirmation;
- redaction-safe hashes rather than raw mailbox identifiers.

Adapted for EU:

- exact four-file current-package contract;
- Dutch-primary plus English-companion identity;
- no plaintext subject, sender, recipient or mailbox message id in GitHub;
- no report regeneration, resend, pricing mutation or portfolio mutation.

## Deliverables

- redaction-safe receipt evidence;
- delivery monitor receipt;
- production delivery closeout manifest;
- reconciled routine run manifest;
- corrected `control/CURRENT_STATE.md` and `control/NEXT_ACTIONS.md`;
- work-package handover.

## Completion definition

WP31 is complete only when:

1. transport evidence still reports `transport_success=true` and `send_executed=true`;
2. a fresh independent inbox search matches the 2026-07-17 report;
3. INBOX presence and all four expected attachment names are confirmed;
4. attachment sizes match the accepted delivery package;
5. GitHub stores only hashes, timestamps, booleans, sizes and artifact paths;
6. the routine manifest records `receipt_confirmed=true`;
7. the production cycle records `production_delivery_cycle_closed=true`;
8. controls no longer instruct a resend or manual dispatch.

## Authority boundary

```text
report_regeneration=false
transport_retry=false
send_executed_by_wp31=false
portfolio_mutation=false
funding_authority=false
production_delivery_authority=false
```