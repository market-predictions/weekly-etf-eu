# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
MERGE_PR71_THEN_DECIDE_MODEL_ACTIVATION_OR_RETAIN_THREE_POSITIONS
```

The fresh 2026-08-03 report is complete and validated. It provides current closes for 13 controlled lines and a transparent five-position model proposal, while preserving the three-position official portfolio.

## Validated package

```text
pull_request=71
validated_runtime_sha=d9f49c6f729cb632e77f8b21f9558eeefc5f6b1c
run_id=20260803_30860298693_1
workflow_run=30860298693 success
artifact_id=8874130446
artifact_sha256=f451dc03ae726bcab519be21a566b72369c51f8396bb6e572624b16a3525fa57
priced_lines=13/13
funded_consensus=3/3
nl_pages=12
en_pages=11
protected_state_unchanged=true
email_delivery=false
```

## Immediate sequence

1. Merge PR #71 after confirming only documentation and workflow cleanup followed the validated runtime SHA.
2. Keep the official portfolio at VWCE, EUNA and SXR8 unless a separate activation package passes.
3. For VVSM and L0CK, acquire timestamped bid, ask and quote-size evidence.
4. Re-evaluate whether the current donor produces a fresh-add direction for the two themes.
5. Request the exact activation phrase only after all remaining gates pass.
6. If activation is not approved, retain the model proposal as monitored analytical context and keep cash unchanged.
7. Delivery remains a separate operation requiring exact-package authorization, transport manifest and independent receipt verification.

## Current model proposal

```text
VVSM=BUY_168_SHARES_AT_REFERENCE_CLOSE_88.15
L0CK=BUY_956_SHARES_AT_REFERENCE_CLOSE_10.594
proposed_position_count=5
projected_cash_eur=35477.44
projected_cash_weight_pct=35.563945
proposal_applied=false
```

These are analytical quantities, not executable trade intents.

## Prohibited shortcuts

Do not:

- treat the model proposal as funded holdings;
- change official shares, cash or ledger without explicit activation authority;
- use closing prices as substitutes for timestamped executable quotes;
- infer donor fresh-add direction from broad thematic promotion;
- claim report delivery without a real send manifest and independent inbox receipt;
- reuse the 2026-08-03 report as current truth for a later report date.
