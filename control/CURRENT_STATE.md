# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-08-03
repository=market-predictions/weekly-etf-eu
working_branch=sync/wp11-routine-production-promotion
pull_request=70
validated_source_sha=0794ad5373c4073dfe3051d6675c0689739dcd4d
operating_mode=routine_production_pricing_validated_no_send
wp10_status=merged
wp11_status=fresh_routine_preview_validated
wp11a_status=closed_validated
selected_next_action=REQUEST_MERGE_AUTHORITY_FOR_PR70
```

WP-SYNC-11 has promoted the converged report engine into a fresh, no-send routine package. WP-SYNC-11A has resolved the funded-position pricing blocker with a deterministic multi-provider completed-close gate. The cleaned PR head passed the dedicated provider tests, allocator validation, full routine preview, all 22 rendered PDF pages and protected-state proof. No report was sent.

## Official protected EU model portfolio

Authoritative state remains:

```text
portfolio_state=output/etf_eu_portfolio_state.json
trade_ledger=output/etf_eu_trade_ledger.csv
starting_capital_eur=100000.00
official_nav_eur=99756.76
official_cash_eur=60439.44
official_invested_market_value_eur=39317.32
position_count=3
portfolio_state_sha256=6642334558818e630f0b22a2500ef44b2489ff237aacca638e81f184c165aa6f
trade_ledger_sha256=718f0681fe0d1162f9a91c34aa90489eb8566aecb06c12a1a2d9ad251be3e87c
portfolio_mutation=false
ledger_write=false
```

The official state has not been overwritten. Fresh report valuation is a separate run-scoped overlay.

## Validated run-scoped valuation

```text
report_date=2026-07-31
routine_run_id=20260803_30850723696_1
pricing_gate_passed=true
funded_consensus_count=3/3
funded_identity_anchor_count=3/3
cash_eur=60439.44
invested_market_value_eur=39016.24
run_scoped_nav_eur=99455.68
since_inception_return_pct=-0.544320
```

| Position | Shares | Accepted close | Market value | Weight | Run contribution |
|---|---:|---:|---:|---:|---:|
| VWCE | 151 | €162.96000335 | €24,606.96 | 24.741634% | -€199.32 |
| EUNA | 1,526 | €4.88000006 | €7,446.88 | 7.487637% | -€18.16 |
| SXR8 | 10 | €696.23999512 | €6,962.40 | 7.000505% | -€83.60 |

The run-scoped NAV reconciles exactly from cash plus the three freshly valued positions. Total contribution versus the previous official valuation is `-€301.08`.

## Pricing architecture

Development provider order:

```text
Leeway
→ EODHD
→ Marketstack
→ Alpha Vantage
→ direct Yahoo Chart
```

Stable gate for every funded position:

- two providers on the same completed-close date;
- maximum spread of 1.0%;
- at least one agreeing exact-line symbol/venue/currency metadata anchor;
- positive finite close on or before the report date;
- no proxy-line substitution;
- no venue or currency contradiction.

Current provider status:

```text
leeway=adapter_implemented_secret_not_configured
eodhd=adapter_implemented_secret_not_configured
marketstack=adapter_implemented_secret_not_configured
alpha_vantage=live_use_disabled_pending_key_rotation; exact_date_cache_used
yahoo_chart=live_unkeyed_identity_anchor
stooq=diagnostics_only_blocked_by_browser_verification
```

The accepted Alpha Vantage evidence cache is provenance-bound to `2026-07-31` and is ignored automatically for future report dates. It is not a standing source of current prices.

## Non-funded basket status

Yahoo Chart supplied usable development closes for L0CK, ISAE, XMLC, IQQQ, DFEN, CSPX, IWDA and CNDX. CBUF remained unpriced. Because CBUF is not funded, it does not block NAV, but it remains diagnostics-only and cannot be promoted by price inference or proxy substitution.

## Fresh report package

```text
nl_html=output/fresh_generation/weekly_etf_eu_review_nl_260731_01.html
nl_pdf=output/fresh_generation/weekly_etf_eu_review_nl_260731_01.pdf
en_html=output/fresh_generation/weekly_etf_eu_review_260731_01.html
en_pdf=output/fresh_generation/weekly_etf_eu_review_260731_01.pdf
routine_manifest=output/run_manifests/etf_eu_routine_run_manifest_2026-07-31_20260803_30850723696_1.json
```

Final exact-head validation:

```text
source_sha=0794ad5373c4073dfe3051d6675c0689739dcd4d
workflow_run=30850723696
workflow_job=91809807838
artifact_id=8870570755
artifact_sha256=c11dd7d464e706cf5ed4d6c4afcfeccd556a34a11108a9dfcc5a8a4f7c651602
pricing_engine_workflow_run=30850723739 success
stooq_diagnostic_workflow_run=30850723694 success
allocator_report_workflow_run=30850723704 success
languages=nl,en
sections_per_language=19
pages_nl=11
pages_en=11
rendered_pages=22
low_content_pages=0
client_report_validation=true
routine_manifest_validation=true
protected_state_unchanged=true
```

## Authority boundaries

```text
development_pricing_model=true
commercial_redistribution_authority=false
funding_authority=false
portfolio_mutation=false
ledger_write=false
execution_authority=false
activation_authority=false
production_delivery_authority=false
email_sent=false
delivery_receipt_created=false
merge_authority=false
```

## Current conclusion

The development pricing model and its integration into the fresh routine report are working and validated on the cleaned PR head. Pricing is no longer the current development blocker for the three funded positions. PR #70 remains draft, open and mergeable with no review threads; merging requires explicit authority. Future report dates must obtain fresh same-date consensus and cannot reuse the July 31 cache.