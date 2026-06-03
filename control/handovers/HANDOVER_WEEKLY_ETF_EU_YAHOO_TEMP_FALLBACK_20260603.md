# Handover — Weekly ETF EU Phase 4 Yahoo Temporary Fallback

Date: 2026-06-03
Repository: `market-predictions/weekly-etf-eu`

## Fresh-chat start instructions

Continue in `market-predictions/weekly-etf-eu`.

Read, in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/handovers/HANDOVER_WEEKLY_ETF_EU_YAHOO_TEMP_FALLBACK_20260603.md`

Then read only the minimum relevant execution files:

- `config/ucits_pricing_source_policy.yml`
- `control/YAHOO_VERIFIED_FALLBACK_CONTRACT_V1.md`
- `pricing/build_yahoo_ucits_close_diagnostics.py`
- `pricing/build_yahoo_fallback_gate_evaluation.py`
- `pricing/build_yahoo_completed_session_gate.py`
- `pricing/build_ucits_valuation_prices.py`
- `tools/validate_yahoo_fallback_gate_evaluation.py`
- `tools/validate_ucits_valuation_prices.py`
- `.github/workflows/validate-yahoo-fallback-gates.yml`
- `.github/workflows/send-weekly-etf-eu-report.yml`

## User decision recorded

The user decided to use Yahoo/yfinance as the practical close-price source for now:

> Use Yahoo/yfinance for UCITS ETF closing prices for now. Revisit official exchange endpoints or premium data providers later if needed.

Important interpretation:

- Yahoo/yfinance may become a temporary close-price fallback for explicitly configured UCITS trading lines.
- Yahoo/yfinance is not official exchange authority.
- Yahoo/yfinance is not funding authority.
- Pricing must still be lineage-recorded and validated.
- Pricing still must not mutate portfolio state, fund candidates, generate PDFs, send email, or create delivery receipts by itself.

## Current issue

We have proven Yahoo can return fresh observed closes for configured UCITS lines, but the repo still has mixed policy state:

- `config/ucits_pricing_source_policy.yml` has already been modified toward `temporary_yahoo_verified_fallback`.
- `control/YAHOO_VERIFIED_FALLBACK_CONTRACT_V1.md` still says Yahoo remains non-authoritative connectivity only.
- `pricing/build_ucits_valuation_prices.py` still validates policy as `valuation_grade_pending` and blocks Yahoo as valuation-grade.
- `tools/validate_ucits_valuation_prices.py` still rejects Yahoo valuation-grade rows under current policy.
- `pricing/build_yahoo_fallback_gate_evaluation.py` still hard-codes `fallback_policy_enabled=false`, `completed_session_validated=false`, and `cross_source_check_passed=false`.
- `tools/validate_yahoo_fallback_gate_evaluation.py` still requires the Yahoo fallback gate to remain blocked.

So the next chat must complete the policy and code transition cleanly.

## Evidence already gathered

The dedicated Yahoo fallback validation workflow has built and committed repo-native diagnostic evidence across multiple runs.

Most recent run observed from commit comparison:

```text
run_id: 20260602_233840
```

Artifacts committed include:

```text
output/pricing/yahoo_ucits_close_diagnostics_20260602_233840.json
output/pricing/yahoo_fallback_gate_evaluation_20260602_233840.json
output/pricing/yahoo_completed_session_gate_20260602_233840.json
output/pricing/yahoo_cross_source_gate_20260602_233840.json
output/pricing/ucits_twelve_data_symbol_discovery_20260602_233840.json
output/pricing/issuer_reference_sanity_gate_20260602_233840.json
output/pricing/ishares_reference_endpoint_discovery_20260602_233840.json
output/pricing/ishares_endpoint_evidence_20260602_233840.json
output/pricing/ishares_endpoint_structure_probe_20260602_233840.json
output/pricing/ishares_controlled_parser_probe_20260602_233840.json
output/pricing/ishares_reference_value_candidates_20260602_233840.json
output/validation/yahoo_fallback_gate_shadow_evidence_20260602_233840.json
```

The latest iShares value-candidate artifact confirmed:

```text
candidate_count = 84
row_count = 2
rows_with_date_or_currency_candidates = 2
rows_with_nav_or_price_candidates = 2
valuation_authority = false
value_extraction = false
reference_price_extraction = diagnostic_candidate_only_no_values
```

This proves issuer reference paths have useful structure, but no issuer values have been extracted and no issuer source is valuation authority.

## Key diagnostic conclusions

### Yahoo/yfinance

Yahoo returned practical close evidence for the configured UCITS trading lines:

- `CSPX.AS` — Euronext Amsterdam line, EUR
- `CSPX.L` — London Stock Exchange line, USD
- `SXR8.DE` — Xetra line, EUR

Yahoo evidence passed practical gates in previous runs:

- fresh close present;
- currency matches registry;
- completed session validated;
- lineage recorded.

### Twelve Data

Twelve Data is useful for symbol discovery but not usable as a free independent close validator under current tier/policy. The cross-source gate remains blocked because independent closes are unavailable or plan-gated.

### BlackRock/iShares

The issuer route is useful for product/reference diagnostics, but not official exchange close authority. The current implementation has endpoint discovery, endpoint evidence, structure probe, controlled parser probe, and value-candidate artifacts. It still extracts no NAV/reference values and creates no valuation authority.

## Required next implementation

### 1. Update Yahoo fallback contract

Edit:

```text
control/YAHOO_VERIFIED_FALLBACK_CONTRACT_V1.md
```

Change it from `non-authoritative connectivity only` to:

```text
Yahoo/yfinance is approved as a temporary UCITS close-price fallback for explicitly configured trading lines.
Yahoo is not official exchange authority.
Yahoo does not create funding authority.
Yahoo does not mutate portfolio state.
Yahoo can support valuation-price rows only when policy, freshness, currency, completed-session and lineage gates pass.
Cross-source check is no longer required for temporary Yahoo fallback while premium/official data is deferred.
```

### 2. Update Yahoo fallback gate evaluator

Edit:

```text
pricing/build_yahoo_fallback_gate_evaluation.py
```

Recommended behavior:

- `registry_symbol_present=true` when the Yahoo symbol is listed in the source policy for that trading line.
- `fallback_policy_enabled=true` when source policy status/authority is `temporary_valuation_fallback` / `temporary_yahoo_verified_fallback` and `accept_as_valuation_grade=true`.
- Keep `currency_matches_registry`, `fresh_close_present`, `lineage_recorded` from current evidence.
- Do not require `cross_source_check_passed` for temporary fallback; record it as diagnostic-only if present.
- Do not set top-level `valuation_authority=true` in the gate artifact.
- The gate artifact should remain non-mutating.

### 3. Update completed-session integration

The completed-session gate already exists:

```text
pricing/build_yahoo_completed_session_gate.py
```

Use its artifact as the completed-session evidence when deciding whether a Yahoo row can become valuation-grade in `ucits_valuation_prices`.

### 4. Update UCITS valuation-price builder

Edit:

```text
pricing/build_ucits_valuation_prices.py
```

Current blocker: it still validates `pricing_authority_mode == valuation_grade_pending` and rejects Yahoo policy.

Required changes:

- Allow `pricing_authority_mode: temporary_yahoo_verified_fallback`.
- Allow `rules.yfinance_default_authority: temporary_yahoo_verified_fallback`.
- Read latest validated Yahoo artifacts, or accept explicit CLI paths if cleaner:
  - `yahoo_ucits_close_diagnostics_*.json`
  - `yahoo_completed_session_gate_*.json`
  - optionally `yahoo_fallback_gate_evaluation_*.json`
- For each candidate trading line, if the source policy has a Yahoo source with `accept_as_valuation_grade=true`, and Yahoo evidence passes close/date/currency/completed-session/lineage checks, emit:

```json
"valuation_status": "valuation_grade",
"valuation_grade": true,
"pricing_source": "yahoo_yfinance",
"source_authority": "temporary_yahoo_verified_fallback",
"official_exchange_authority": false,
"observed_date": "YYYY-MM-DD",
"close": positive number,
"currency": registry trading currency,
"completed_session": true,
"temporary_fallback": true,
"funding_authority": false,
"portfolio_mutation": false,
"production_delivery": false
```

Keep unresolved rows pending/blocker-based.

### 5. Update UCITS valuation-price validator

Edit:

```text
tools/validate_ucits_valuation_prices.py
```

Required changes:

- Allow `temporary_yahoo_verified_fallback` in the source authority set.
- Stop rejecting `pricing_source == yahoo_yfinance` when policy explicitly enables temporary fallback.
- Still require:
  - positive close;
  - ISO observed date;
  - currency equals trading currency;
  - completed session true;
  - source lineage present;
  - official exchange authority false for Yahoo;
  - funding authority false;
  - portfolio mutation false;
  - production delivery false.

### 6. Update Yahoo fallback gate validator

Edit:

```text
tools/validate_yahoo_fallback_gate_evaluation.py
```

Required changes:

- Stop requiring all rows to remain blocked.
- Allow rows to be `eligible_for_fallback_review` or equivalent when policy/freshness/currency/lineage pass.
- Do not require `cross_source_check_passed` for temporary fallback.
- Keep forbidden authority flags false.

### 7. Run validation

After patching:

1. Queue/run the dedicated Yahoo fallback validation workflow.
2. Inspect committed artifacts from GitHub files, not only Actions UI.
3. Queue/run the main EU validation workflow if valuation artifact integration is wired there.
4. Confirm whether `ucits_valuation_prices_*.json` now has Yahoo `valuation_grade=true` rows while keeping no funding authority and no portfolio mutation.

## Files likely to update

```text
control/YAHOO_VERIFIED_FALLBACK_CONTRACT_V1.md
pricing/build_yahoo_fallback_gate_evaluation.py
tools/validate_yahoo_fallback_gate_evaluation.py
pricing/build_ucits_valuation_prices.py
tools/validate_ucits_valuation_prices.py
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/DECISION_LOG.md
control/ETF_EU_CHANGELOG_PHASE4_YAHOO_TEMP_FALLBACK_20260603.md
```

Possibly update workflows if additional artifact paths are needed:

```text
.github/workflows/validate-yahoo-fallback-gates.yml
.github/workflows/send-weekly-etf-eu-report.yml
```

## Authority boundaries to preserve

Do not allow any of the following from pricing alone:

```text
funding_authority=true
portfolio_mutation=true
production_delivery=true
PDF generation
email delivery
delivery receipt
candidate promotion to fundable
```

Yahoo temporary fallback solves practical close-price availability for now. It does not solve the long-term official/premium data-source challenge.

## Suggested first response in fresh chat

State the current issue, root cause, recommended change, exact files to edit, and next action.

Recommended first implementation step:

1. Patch `control/YAHOO_VERIFIED_FALLBACK_CONTRACT_V1.md`.
2. Patch `pricing/build_yahoo_fallback_gate_evaluation.py` and `tools/validate_yahoo_fallback_gate_evaluation.py`.
3. Patch `pricing/build_ucits_valuation_prices.py` and `tools/validate_ucits_valuation_prices.py`.
4. Queue validation and inspect the resulting artifacts.
