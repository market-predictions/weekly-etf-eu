# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
PASS_PRODUCT_BOUNDARY_AND_ALLOCATION_LINEAGE_THEN_BUILD_ONE_REVIEWABLE_ETF_EU_CANDIDATE
```

The project must not move directly from code changes to email. The next objective is one current, product-pure, lineage-valid, Dutch/English Weekly ETF EU candidate that the user can review before any delivery queue or send authority exists.

## Active workstreams

### A. Product-boundary repair

```text
owner_role=implementation_operations
status=IN_PROGRESS
```

1. Complete CI verification that the ETF EU repository contains no active FX scheduler, FX generator, DailyTradeBias instructions, `daily_outputs`, or `mt5_output` production artifacts.
2. Complete the equivalent cleanup in Weekly ETF PR #119 so the donor cannot regenerate unrelated FX output.
3. Keep the product-boundary validators active on pull requests and `main`.

### B. Allocation-lineage repair

```text
policy_id=ETF_EU_RELEASE_LINEAGE_POLICY_V2
owner_role=implementation_operations
status=IN_PROGRESS
```

1. Preserve the protected ticker roster, exact shares and cash during valuation-only runs.
2. Bind the four-position state to the current L0CK allocation decision and activation ID.
3. Reject any share or cash mutation lacking an explicit allocation-decision artifact.
4. Reconcile shares × current price, market values, invested value, cash, NAV and stated weights.
5. Treat concentration as a weekly underwriting observation unless a separately approved decision creates a hard cap.

The removed assumptions are:

```text
universal_maximum_position_weight_pct=NOT_AUTHORIZED
mandatory_cash_floor_pct=NOT_AUTHORIZED
```

The Weekly ETF donor's `75` threshold is pricing coverage, not portfolio concentration.

### C. Fresh client candidate

```text
owner_role=implementation_operations
status=BLOCKED_UNTIL_A_AND_B_PASS
```

1. Run current completed-close pricing for all protected funded positions.
2. Build exactly four client files: Dutch HTML/PDF and English HTML/PDF.
3. Bind the package to one immutable run ID, report date, source SHA, donor SHA, protected-state hash, allocation-decision hash, policy hash and pricing evidence.
4. Run machine validation and rendered-page visual review.
5. Persist the exact candidate and evidence without send authority.

### D. Independent release assurance

```text
owner_role=governance_release_assurance
status=NOT_STARTED_FOR_CURRENT_CANDIDATE
```

1. Reconstruct the candidate from immutable evidence.
2. Verify policy PASS, protected-state lineage, completed-close coverage, bilingual parity, visual review and package hashes.
3. Return `GOVERNANCE_PASS_PRE_SEND`, `GOVERNANCE_FAIL`, or `GOVERNANCE_INDETERMINATE` without modifying the candidate.

### E. Review, transport and receipt

```text
status=NOT_AUTHORIZED
```

1. Present the completed candidate to the user.
2. Create a delivery queue only after explicit review approval.
3. Bind the queue to the exact candidate and assurance hashes.
4. Execute guarded ETF EU transport.
5. Independently verify inbox receipt and attachment identity.
6. Write the production closeout manifest.
7. Claim `OUTCOME_CONFIRMED` only after the independent receipt exists.

## Maturation gaps after the current repair

The following remain even after FX separation and lineage validation pass:

1. Replace multiple allocator/transition surfaces with one canonical weekly EU underwriting decision artifact.
2. Create one immutable run-input manifest covering donor, protected state, ledger, UCITS identity, pricing and macro evidence.
3. Designate one canonical production renderer and archive alternative production paths.
4. Reduce workflow sprawl to an allowlist:
   - one generation workflow;
   - one assurance workflow;
   - one guarded transport workflow;
   - one receipt-closeout workflow;
   - bounded diagnostics without delivery authority.
5. Consolidate historical send workflows so a manually invoked legacy workflow cannot bypass current governance.
6. Complete one fresh governed end-to-end delivery and retain the independent receipt/closeout evidence.

## Acceptance criteria for user review

The user should be prompted to review only when all of the following are true:

```text
product_boundary_validation=PASS
allocation_lineage_validation=PASS
funded_pricing_gate=PASS
four_file_package_complete=true
machine_report_validation=PASS
visual_review=PASS
release_candidate_hashes_complete=true
email_delivery=false
```

## Prohibited shortcuts

Do not:

- run or surface FX output from an ETF repository;
- interpret the donor's 75% pricing threshold as a position-weight rule;
- invent a 50% cap or cash floor without an explicit decision record;
- let donor opportunity state silently mutate the EU portfolio;
- treat arithmetic consistency as allocation authority;
- treat a rendered report as a completed release;
- build a delivery queue before user review;
- let implementation self-certify governance PASS;
- claim delivery from SMTP success alone.
