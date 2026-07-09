# ETF-EU-MVP20 — Guarded Controlled Resend Instructions

Date: 2026-07-09  
Repository: `market-predictions/weekly-etf-eu`  
Work package: `ETF-EU-MVP20`  
Layer: operational runbook + output contract

## Purpose

Execute the next controlled resend step only after explicit user instruction.

`ETF-EU-MVP19-FIX2` has prepared a client-grade package for controlled resend. `ETF-EU-MVP20` is the guarded transport package that must preserve delivery evidence discipline.

## Current issue

A client-grade PDF/HTML package exists, but no resend has been performed and no receipt has been confirmed.

The inherited U.S. ETF workflow remains disabled in this EU repo. The EU workflow has an explicit `send` mode guard and confirmation input, but the historical MVP15 path still contains a transport placeholder. Therefore, MVP20 must not claim actual outbound delivery unless the transport layer produces real evidence.

## Authority rules

```text
source_of_truth_repo=market-predictions/weekly-etf-eu
reference_architecture_repo=market-predictions/weekly-etf
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
```

`weekly-etf` may be used as architecture donor only. Do not copy U.S. holdings, portfolio assumptions, U.S. instruments, or U.S. delivery authority into EU.

## Entry criteria

Before guarded resend work begins, verify:

```bash
python tools/validate_ucits_close_price_validation_basket_results.py \
  --artifact output/pricing/ucits_close_price_validation_basket_results_20260709_000000.json

python tools/validate_etf_eu_delivery_package_manifest.py \
  --manifest output/delivery_package/etf_eu_delivery_package_manifest_20260709_000000.json

python tools/validate_etf_eu_mvp19_fix2_ready_for_controlled_resend.py \
  --artifact output/client_surface/etf_eu_mvp19_fix2_ready_for_controlled_resend_20260709_000000.json
```

Expected result:

```text
client_grade_package_ready=true
pdf_output_available=true
html_output_available=true
ready_for_controlled_resend=true
resend_performed=false
receipt_confirmed=false
```

## Four-layer separation

### 1. Decision framework

The only MVP20 decision is whether the already-prepared package may be sent under controlled resend conditions.

MVP20 must not make investability, allocation, funding, or portfolio decisions.

### 2. Input/state contract

Use these committed package assets as the resend input unless the user explicitly asks to regenerate:

```text
output/weekly_etf_eu_review_nl_260709.md
output/weekly_etf_eu_review_260709.md
output/delivery_package/weekly_etf_eu_review_nl_260709.html
output/delivery_package/weekly_etf_eu_review_nl_260709.pdf
output/delivery_package/weekly_etf_eu_review_260709.html
output/delivery_package/weekly_etf_eu_review_260709.pdf
output/delivery_package/etf_eu_delivery_package_manifest_20260709_000000.json
```

### 3. Output contract

A successful MVP20 controlled resend may only be closed when there is a real delivery receipt, manifest, or equivalent transport evidence.

Do not mark these true without evidence:

```text
resend_performed=true
delivery_success_closed=true
receipt_confirmed=true
completion_claimed=true
```

### 4. Operational runbook

Do not execute transport unless the user explicitly instructs it.

When instructed, first inspect the current guarded delivery surface:

```bash
git pull --ff-only origin main
git status --short

sed -n '1,240p' .github/workflows/send-weekly-etf-eu-report.yml
sed -n '1,260p' send_report.py
```

Then choose the narrowest safe path:

1. If the EU workflow still contains only the MVP15 transport placeholder, do **not** claim delivery. Either implement the missing transport layer as a separate guarded package or report that outbound transport is still placeholder-only.
2. If a real guarded transport path exists, run it only with explicit confirmation and preserve the emitted receipt or manifest.
3. After the run, verify delivery evidence directly from GitHub artifacts, committed manifests, or receipt files.
4. Update `CURRENT_STATE.md` and `NEXT_ACTIONS.md` only after evidence exists.

## Prohibited in MVP20 unless separately authorized

```text
portfolio_mutation
funding_authority
valuation_grade promotion
US ETF holding import
unconfirmed delivery success claim
background or delayed delivery promise without automation/tool support
```

## Exit criteria

MVP20 may be closed only if one of these outcomes is recorded:

```text
status=completed_controlled_resend_with_receipt
```

or

```text
status=blocked_transport_placeholder_no_delivery_performed
```

or

```text
status=blocked_delivery_failed_with_exact_error
```

## Explicit non-execution statement

This instruction file prepares `ETF-EU-MVP20` only. It does not trigger workflow dispatch, queue files, email sending, or any guarded transport step.
