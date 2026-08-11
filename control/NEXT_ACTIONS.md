# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
FREEZE_AND_INDEPENDENTLY_ASSURE_FRESH_20260810_CANDIDATE
```

Current authoritative candidate status:

```text
issue=97
branch=agent/etf-eu-fresh-260810-v1
run_id=20260810_123000
report_date=2026-08-10
active_claim=ETF-EU-FRESH-REPORT-260810-V1
funded_positions=6
added_positions=DFEN,IQQQ
cash_eur=28101.01
nav_eur=100738.73
semantic_rerender_run=31502986816
semantic_rerender_verdict=PASS
delivery_authorized=false
real_broker_execution=false
principal_decision_required=false
```

## Completed in this current report cycle — do not reopen without contradictory evidence

1. Broad donor discovery is integrated into the canonical non-main candidate workflow.
2. Donor U.S.-portfolio `is_fundable_candidate` is not used as EU funding authority; EU-local mapping/fundability owns the decision.
3. Allocation-candidate second-source pricing can use quota-aware Alpha Vantage capacity before funding, preventing the old circular deadlock.
4. The Alpha Vantage secret is correctly wired into the current pricing workflow.
5. Exact-line validation distinguishes trading lines even when they share an ISIN; SXR8/CSPX no longer overwrite each other.
6. Current completed-close revaluation precedes allocation sizing.
7. An explicit current allocation decision added DFEN 207 and IQQQ 149 to the model-only portfolio; no real broker order exists.
8. The final model candidate has six funded positions and EUR 28,101.01 cash on NAV EUR 100,738.73.
9. Funded valuation is 6/6 two-provider completed-close consensus for 2026-08-10.
10. NL/EN Markdown, HTML and PDF current semantics are derived from one normalized state and passed strict machine validation.
11. Legacy stale HTML/PDF wording and Dutch/English leakage are blocked by permanent fail-closed semantics finalizers.
12. Semantic rerender run `31502986816` is PASS through PDF review and branch persist.
13. The temporary rerender workflow is removed.
14. The temporary issue-#97 push trigger is removed from the canonical candidate workflow while broad-discovery wiring is retained.
15. The fresh work claim is ACTIVE and bound to issue #97 / the fresh work package.

## Next execution sequence

1. Open the fresh candidate pull request against `main`.
2. Let PR-triggered CI validate workflow/product boundaries and exact candidate content.
3. Repair any genuine PR-head failure; do not waive gates.
4. Once green, freeze the exact PR head and record the implementation handover/evidence bundle.
5. Obtain a fresh independent `governance_release_assurance` verdict `PASS | FAIL | INDETERMINATE` on the frozen head.
6. If FAIL, repair on a new head and repeat assurance. If PASS, verify the head is unchanged.
7. Merge only the independently PASSed unchanged head.
8. Run exact-main validation and confirm candidate/delivery/product-boundary topology.
9. Build a delivery-package manifest bound to exact assured/merged artifacts and hashes.
10. Invoke only `send-weekly-etf-eu-controlled-transport.yml` under separate guarded-send authority.
11. Verify transport result plus receipt/attachment evidence; only then state that email delivery succeeded.
12. Close issue #97, work package and active claim, and reconcile `CURRENT_STATE.md`, `NEXT_ACTIONS.md`, `DECISION_LOG.md` and the control-plane cache.

## Protected boundaries

Until the independent assurance and delivery stages explicitly grant their separate authorities:

- delivery authority = false;
- SMTP authority = false;
- real broker execution = false;
- no additional portfolio mutation is implied;
- no ticker is added merely to increase position count;
- research-only prices or mappings do not create funding authority.

No principal decision is currently required.
