# Weekly ETF EU — Current State

Date: 2026-09-27  
Repository: `market-predictions/weekly-etf-eu`  
Canonical work: PR #128 `WEEU-GOLDEN-PATH-20 — prove, purge, prove again`

## Snapshot

```text
integration_policy=HOLD_AFTER_PASS
candidate_branch=recovery/v6-golden-path-20
production_generation_workflow=.github/workflows/run-weekly-etf-eu-routine.yml
controlled_transport_workflow=.github/workflows/send-weekly-etf-eu-controlled-transport.yml
production_generation_repo_write_authority=false
production_generation_delivery_authority=false
real_broker_execution=false
portfolio_mutation=false
```

## Golden Path state

The original funded-position ISIN/PDF defect is repaired. A pre-purge exact-head NO EMAIL cycle proved funded pricing, UCITS/fundability processing, normalized NL/EN generation, strict client-grade validation and exact-head proof.

The structural liveness defect exposed by that proof is also repaired:

- generation/proof no longer commits generated output back to the governed branch;
- exact source SHA is checked out and re-verified before success;
- a moved branch fails closed as stale;
- generated evidence is retained as an immutable GitHub Actions artifact;
- concrete repair findings are recorded as ordinary SHA-bound PR comments rather than adding another state plane.

The purge has removed the temporary funded-ISIN dispatcher/request scaffolding and all committed Golden Path proof output. The branch now carries source, tests, workflow/governance and documentation changes only.

## Canonical post-purge architecture

The single generation workflow now:

1. proves a clean exact-head checkout;
2. creates or consumes a v2 NO EMAIL request;
3. resolves the latest plausible completed European close instead of hard-coding a repair date;
4. executes current donor/EU fundability, pricing, re-underwriting and normalized NL/EN generation;
5. runs strict Markdown/PDF/client-surface machine gates;
6. finalizes package/readiness/run-manifest state to `PRE_SEND_READY` only after those gates pass;
7. keeps delivery/send/funding/portfolio-mutation authority false;
8. uploads one frozen evidence bundle;
9. re-verifies exact live source SHA before declaring success.

Native weekly generation is configured for Wednesday `18:30 UTC` on `main`. Scheduled generation stops at `PRE_SEND_READY`; controlled transport remains separate and human/assurance gated.

## Authority boundaries

`PRE_SEND_READY` means generation and deterministic quality validation succeeded. It does **not** mean delivery is authorized.

The generation path must remain:

```text
ready_for_controlled_delivery=false
delivery_authorized=false
production_delivery_authority=false
send_executed=false
transport_attempted=false
funding_authority=false
portfolio_mutation=false
```

Independent exact-head assurance remains mandatory before governed integration. Controlled transport remains a separate post-integration operation with its existing authority checks.

## Remaining proof boundary

PR #128 can prove the post-purge candidate from a clean exact-head checkout and can prove that the scheduled path is configured correctly, but GitHub executes cron schedules only from the default branch. Therefore a genuine `event=schedule` observation can only be produced after this workflow is integrated into `main`.

That post-merge observation is tracked as a separate WEEU verification task; a manual dispatch is not accepted as substitute evidence.
