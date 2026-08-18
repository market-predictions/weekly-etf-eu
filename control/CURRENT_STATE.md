# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-08-18
repository=market-predictions/weekly-etf-eu
state=ROUTINE_IDLE_EMAIL_EQUITY_PARITY_REPAIRED
report_cycle=2026-08-14 CLOSED
report_run_id=20260814_235900
report_delivery_confirmed=true
recipient_inbox_observed=true
attachment_hash_confirmation=true
email_equity_parity_issue=105 CLOSED
email_equity_parity_pr=106 MERGED
email_equity_parity_assurance=issue_108 PASS
email_equity_parity_candidate=57fef69626951f2a33bc63ced25253bcc4e84df0
email_equity_parity_merge=1fb7168f7ba433e138503c68aa9447c5f7ebbc65
email_equity_parity_workpackage=CLOSED
principal_decision_required=false
real_broker_execution=false
portfolio_mutation_from_delivery=false
corrected_resend_authorized=false
corrected_resend_executed=false
```

## Current outcome

The fresh Weekly ETF EU report cycle for completed close `2026-08-14` remains fully closed and delivery-confirmed. The exact independently assured six-artifact client package from PR #101 was previously delivered through the controlled transport path, directly observed in the recipient inbox in both NL and EN, and both received PDF attachments were byte-verified against the approved artifacts.

That historical delivery is not reopened by the later email-rendering repair.

## Email equity-curve defect — closed

A post-delivery defect was confirmed: the approved PDF visibly rendered the portfolio equity curve, while Gmail did not render the same graph from the delivered HTML email because the delivery representation used inline SVG.

Issue #105 / PR #106 repaired the representation by converging on the established Weekly ETF donor architecture:

```text
portfolio/equity state
-> deterministic PNG before SMTP
-> final standalone HTML embeds PNG as data URI
-> final PDF regenerated from that final HTML
-> controlled email reuses identical approved PNG bytes as cid:equitycurve
-> no chart redraw/rasterization in transport
-> fail closed on residual SVG or invalid/missing/ambiguous PNG
```

Independent `governance_release_assurance` issue #108 returned `PASS` on exact candidate `57fef69626951f2a33bc63ced25253bcc4e84df0`. All required exact-head CI gates were green. The unchanged candidate was merged as `1fb7168f7ba433e138503c68aa9447c5f7ebbc65`.

The repair changed no portfolio, pricing, allocation, trade-ledger or broker-execution behavior and created no report-send authority.

## Stable delivery architecture

- Candidate generation remains non-delivery authority.
- Final client HTML/PDF are completed before guarded delivery authority.
- When an equity chart is required, the final HTML contains one validated embedded PNG representation.
- Controlled transport does not redraw or rasterize that graph; it only translates the already-approved PNG bytes to MIME CID form.
- Guarded-delivery authority, artifact-hash binding and explicit send confirmations remain separate requirements.
- Delivery success still requires real recipient-side receipt/closeout evidence.
- No prior report may be resent merely because a delivery-surface defect was repaired.

## Decision framework retained

- full weekly portfolio re-underwrite; no ticker-count target;
- broad donor discovery is research input only;
- EU-local UCITS mapping/fundability owns funding eligibility;
- current exact trading-line pricing is distinct from historical report context;
- funded exact lines require the existing two-provider completed-close consensus gate;
- 50% maximum position, 35% minimum cash and 15% maximum new ETF remain retired as current authority;
- 75% remains pricing-coverage context only, not a position cap;
- model portfolio decisions remain distinct from real broker execution;
- delivery may not mutate portfolio state.

## Operational state

```text
2026_08_14_report_cycle=CLOSED_CONFIRMED
issue_105=CLOSED
pr_106=MERGED
issue_108=CLOSED_PASS
email_equity_parity_workpackage=CLOSED
donor_aligned_email_graph_contract=ACTIVE
corrected_resend=NOT_AUTHORIZED_NOT_EXECUTED
routine_state=IDLE_READY_FOR_NEXT_FRESH_CYCLE
principal_decision_required=false
```

## Next lifecycle

No report, resend, assurance or closeout action remains for the 2026-08-14 cycle or for issue #105. The next production action is only the next normal fresh Weekly ETF EU cycle based on a new completed-close date and fresh evidence.
