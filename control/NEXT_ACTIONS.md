# Weekly ETF EU — Next Actions

Date: 2026-09-27

## Current priority

Finish `WEEU-GOLDEN-PATH-20` on PR #128 without reopening architecture.

The implementation path is already converged. Remaining work is verification and governed lifecycle progression:

1. freeze one post-purge exact candidate;
2. pass canonical regression/product/release-preflight CI on that exact head;
3. run the complete NO EMAIL generation from a clean exact-head checkout;
4. require terminal `PRE_SEND_READY` current truth and a frozen Actions evidence bundle;
5. obtain fresh internal review and fresh external exact-candidate assurance;
6. stop at `HOLD_AFTER_PASS` unless separate integration authority exists;
7. after integration to `main`, observe one real cron-triggered Wednesday generation reaching `PRE_SEND_READY` without manual repair or any transport/send side effect.

## Current production path

Generation/validation:

```text
.github/workflows/run-weekly-etf-eu-routine.yml
```

Controlled transport:

```text
.github/workflows/send-weekly-etf-eu-controlled-transport.yml
```

No third production route is allowed.

## Required proof invariants

The frozen candidate proof must show:

```text
clean_checkout=true
manual_repair_applied=false
exact_source_sha=true
funded pricing/client-grade gates=PASS
NL/EN funded ISIN coverage=PASS
pre_send_ready=true
full_generation_status=PRE_SEND_READY
ready_for_controlled_delivery=false
delivery_authorized=false
send_executed=false
transport_attempted=false
portfolio_mutation=false
```

Generated evidence stays in GitHub Actions artifacts and is not committed back to the candidate branch.

## Post-merge scheduled proof

GitHub cron runs from the default branch, so a genuine scheduled observation cannot be produced on an unmerged PR head. The production cadence is Wednesday `18:30 UTC`, generation-only.

The post-merge verification task must accept only a real `schedule` event on `main` and must verify:

- fresh completed-close resolution;
- clean checkout;
- all quality gates green;
- terminal `PRE_SEND_READY` artifacts;
- frozen evidence artifact;
- no repository write, send, transport, broker execution or portfolio mutation.

Manual dispatch is useful for candidate proof but is not evidence that the cron trigger itself works.

## Protected boundaries

- no real broker execution;
- no protected share/cash/trade-ledger mutation without separate explicit authority;
- no SMTP or controlled transport from scheduled generation;
- no delivery-success claim from generation or SMTP success;
- no self-assurance;
- no merge from `HOLD_AFTER_PASS` without governed integration authority;
- no revival of retired repair/preview/send workflows merely to obtain evidence.
