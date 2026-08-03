# ETF-EU-WP-SYNC-11A — Multi-provider pricing evidence

## Final validated revision

```text
repository=market-predictions/weekly-etf-eu
pull_request=70
branch=sync/wp11-routine-production-promotion
validated_pricing_head=6d281593b80e8e44d21c994f869cab8c2e42a9e3
report_date=2026-07-31
routine_run_id=20260803_30842139405_1
workflow_run_id=30842139405
workflow_job_id=91781522951
artifact_id=8867298602
artifact_sha256=38522912996254d76b77b59b5e9fea43b6ea2b6ecf1d33ba70e5c3d36e30068d
workflow_conclusion=success
```

The deterministic pricing, evidence-cache, secret-redaction, identity-anchor, valuation-overlay and bilingual client-performance tests passed. Subsequent repository-hygiene commits removed a superseded duplicate provider implementation and aligned `CURRENT_STATE.md`, `NEXT_ACTIONS.md` and `DECISION_LOG.md`; they did not change the validated pricing runtime.

## Decision framework

The development pricing engine uses this provider order:

1. Leeway;
2. EODHD;
3. Marketstack;
4. Alpha Vantage;
5. direct Yahoo Chart endpoint.

The report gate requires, for every funded position:

- a completed close on or before the requested report date;
- two providers on the same close date;
- provider spread no greater than 1.0%;
- no venue or currency contradiction;
- at least one agreeing provider returning matching symbol, venue and currency metadata.

This package establishes development-grade technical qualification only. It provides no commercial redistribution or production licensing authority.

## Input and state contract

Exact trading-line identity is controlled by:

```text
config/ucits_price_provider_registry.yml
```

The registry contains 12 controlled lines and records ISIN, expected MIC, expected currency, exact provider symbol and provider exchange code.

Accepted historical corroboration for the funded positions is date-bound in:

```text
config/etf_eu_provider_close_cache_20260731.json
```

The cache is valid only for report date `2026-07-31`, exact basket ID, provider and provider symbol. It is ignored automatically for future report dates.

## Funded completed-close qualification

All three funded positions passed the price-consensus and identity-anchor gates.

| Position | Alpha Vantage corroboration | Yahoo Chart identity anchor | Consensus close | Spread | Close date |
|---|---:|---:|---:|---:|---|
| VWCE | €162.96000000 | €162.96000671 | €162.96000335 | 0.000004% | 2026-07-31 |
| EUNA | €4.88000000 | €4.88000011 | €4.88000006 | 0.000002% | 2026-07-31 |
| SXR8 | €696.24000000 | €696.23999023 | €696.23999512 | 0.000001% | 2026-07-31 |

```text
funded_line_count=3
funded_consensus_count=3
funded_identity_anchor_count=3
report_pricing_gate_passed=true
provider_cache_used_count=3
```

Yahoo Chart returned matching Xetra symbols, German venue metadata and EUR currency for each funded line. Alpha Vantage evidence is historical corroboration from the accepted July 31 qualification artifact and is not treated as an identity anchor.

## Run-scoped valuation

```text
nav_eur=99455.68
cash_eur=60439.44
invested_market_value_eur=39016.24
since_inception_return_pct=-0.544320
pricing_close_dates=2026-07-31
```

| Position | Shares | Current close | Market value | Weight | Unrealized P/L | Since entry | Run contribution |
|---|---:|---:|---:|---:|---:|---:|---:|
| VWCE | 151 | €162.96000335 | €24,606.96 | 24.741634% | -€356.36 | -1.427532% | -€199.32 |
| EUNA | 1,526 | €4.88000006 | €7,446.88 | 7.487637% | -€50.36 | -0.671686% | -€18.16 |
| SXR8 | 10 | €696.23999512 | €6,962.40 | 7.000505% | -€137.60 | -1.938029% | -€83.60 |

Total run contribution is `-€301.08`, reconciling the previous official valuation of `€99,756.76` to the fresh run valuation of `€99,455.68`.

The visible section 7A performance table in both Dutch and English was rebuilt from this reconciled state. Stale July 24 weights, P/L and contribution values are no longer present.

## Provider status

```text
leeway=adapter_implemented_secret_not_configured
eodhd=adapter_implemented_secret_not_configured
marketstack=adapter_implemented_secret_not_configured
alpha_vantage=live_secret_disabled_pending_rotation
yahoo_chart=live_and_configured_without_secret
stooq=diagnostics_only_blocked_by_browser_verification
```

For the non-funded research basket:

- Yahoo Chart returned a usable single-source close for L0CK, ISAE, XMLC, IQQQ, DFEN, CSPX, IWDA and CNDX;
- CBUF remained unpriced;
- no non-funded single-source result was promoted to funded consensus authority.

## Secret-safety remediation

During early qualification, an Alpha Vantage quota message echoed the API key. The following remediation is complete:

- provider response-message bodies are never persisted;
- provider failures are stored as classifications only;
- secret-like fields are stripped from identity evidence;
- deterministic redaction tests pass;
- pre-redaction GitHub Actions artifacts were purged;
- the one-shot elevated artifact-purge workflow was removed;
- live Alpha Vantage use is disabled unless `config/alpha_vantage_key_rotation_confirmed.json` exists.

The repository secret `ALPHA_VANTAGE_API_KEY` must still be rotated before future live report dates. No secret value is stored in this evidence file or elsewhere in the repository.

## Client package and visual review

The exact routine package contains four validated files:

- Dutch HTML;
- Dutch PDF;
- English HTML;
- English PDF.

The final report date displayed in both reports is `2026-07-31`.

```text
nl_pdf_pages=11
en_pdf_pages=11
total_rendered_pages=22
low_content_pages=0
rendering_backend=pymupdf
visual_review=passed_all_pages
```

Visual review confirmed:

- no empty or one-row spillover pages;
- the complete three-position performance table remains on page 4;
- fresh P/L and contribution figures are visible in Dutch and English;
- the report-date masthead and valuation-history notes are correct and localized;
- no clipping or material layout break was observed across all 22 pages.

## Protected-state and authority proof

Before and after the complete routine preview:

```text
portfolio_sha256=6642334558818e630f0b22a2500ef44b2489ff237aacca638e81f184c165aa6f
ledger_sha256=718f0681fe0d1162f9a91c34aa90489eb8566aecb06c12a1a2d9ad251be3e87c
protected_state_unchanged=true
portfolio_mutation=false
ledger_write=false
execution_authority=false
delivery_authority=false
```

No report was sent and no delivery receipt or transport manifest was created.

## Final determination

```text
pricing_engine_status=VALIDATED_DEVELOPMENT_MODEL
funded_pricing_status=PASS_3_OF_3
client_report_pricing_consistency=PASS
full_routine_preview=PASS
protected_state=UNCHANGED
work_package=CLOSED_VALIDATED
pr_merge=NOT_AUTHORIZED
report_delivery=NOT_AUTHORIZED
future_date_consensus=REQUIRES_FRESH_SECOND_PROVIDER
```
