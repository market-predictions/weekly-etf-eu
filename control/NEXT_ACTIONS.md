# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
ETF-EU-WP33_COCKPIT_FRONT_PAGE_PRODUCTION_ENABLEMENT
```

## Current authoritative baseline

```text
portfolio_position_count=3
cash_eur=60439.44
invested_market_value_eur=39577.16
nav_eur=100016.60
latest_report_run_id=20260717_141500
latest_transport_run_id=20260717_170931
transport_success=true
send_executed=true
resend_allowed=false
```

| Ticker | Role | Shares | Value | Weight | Current action |
|---|---|---:|---:|---:|---|
| VWCE | Global core | 151 | €24,963.32 | 24.959177% | Hold after first tranche |
| EUNA | Aggregate-bond stabiliser | 1,526 | €7,497.24 | 7.495996% | Hold after first tranche |
| SXR8 | U.S. equity overweight | 10 | €7,116.60 | 7.115419% | Hold; no second tranche |

No automatic add, reduction, exit, later tranche or satellite activation is authorised.

## Completed WP32 preview capability

```text
pull_request=61
merge_commit=348c324d911b142f0871e9a67f875b76b3450447
final_validation_run=29667194382
status=merged_validated_preview_only
production_enablement=false
```

WP32 proved:

```text
cockpit_front_page_count_NL=1
cockpit_front_page_count_EN=1
classic_pdf_pages=6
cockpit_pdf_pages=7
page_delta=1
classic_sections_preserved=15
email_safe_surface_passed=true
primary_visual_review_passed=true
secondary_adversarial_review_passed=true
protected_inputs_unchanged=true
blockers=0
```

The selected document hierarchy is:

```text
EU/UCITS cockpit front page
→ investor report
→ analyst report
```

## WP33 exact-current production-enablement package

Create and claim:

```text
ETF-EU-WP33_COCKPIT_FRONT_PAGE_PRODUCTION_ENABLEMENT
```

### Required implementation boundary

WP33 may change only the report output and operational integration layers. It must not change:

```text
portfolio state
trade ledger
recommendation scorecard
pricing authority
macro authority
allocation authority
real broker execution
current accepted 2026-07-17 package
```

### Required sequence

1. Re-read the donor production enablement decision and current EU package builder.
2. Create an exact-current, non-delivery replay using the latest valid EU normalized state.
3. Integrate the additive cockpit through the existing package-build path rather than duplicating report logic.
4. Keep the EU feature flag explicit:

   ```text
   MRKT_RPRTS_ETF_EU_COCKPIT_FRONT_PAGE=disabled|enabled
   ```

5. Prove disabled mode reproduces the current two-part report.
6. Prove enabled mode adds exactly one page before the investor and analyst reports.
7. Prove render failure and invalid feature values fall back to the current report.
8. Prove the email-safe surface remains readable without head-level CSS.
9. Re-run the full client-grade machine gate and complete NL/EN page review.
10. Require a separate secondary adversarial review.
11. Verify protected input hashes before and after the replay.
12. Record a separate production-enablement decision only when every gate passes.

### WP33 acceptance contract

```text
exact_current_state_used=true
non_delivery_replay=true
disabled_classic_contract_passed=true
enabled_page_delta=1
cockpit_investor_analyst_order_passed=true
classic_sections_preserved=15
email_safe_surface_passed=true
protected_inputs_unchanged=true
primary_review_passed=true
secondary_review_passed=true
blockers=[]
```

## WP31 governance closeout boundary

The 2026-07-17 transport result and delivery evidence are committed. An independent connected-mailbox match was observed with all four expected file roles, but connector privacy controls prevented persistence of mailbox-derived receipt metadata.

```text
transport_success=true
send_executed=true
independent_mailbox_match_observed=true
formal_receipt_artifact_persisted=false
production_delivery_cycle_closed_in_repo=false
resend_allowed=false
```

Do not combine WP31 persistence work with WP33. Do not resend the accepted package.

## After WP33

When WP33 passes, update:

```text
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/DECISION_LOG.md
```

Then decide whether the next routine Weekly ETF EU generation should use the enabled cockpit. A real future report run and any later delivery remain separately governed.