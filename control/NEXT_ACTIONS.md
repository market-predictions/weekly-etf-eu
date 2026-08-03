# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
VERIFY_CLEANED_PR70_AND_PREPARE_MERGE_REVIEW
```

The critical funded-position pricing blocker is resolved for the validated 2026-07-31 development run. The multi-provider engine is integrated into the routine preview, all three funded positions pass consensus and identity-anchor gates, the bilingual report package validates, and protected official state remains unchanged.

## Validated baseline

```text
branch=sync/wp11-routine-production-promotion
pull_request=70
report_date=2026-07-31
run_id=20260803_30842139405_1
funded_consensus=3/3
funded_identity_anchors=3/3
run_scoped_nav_eur=99455.68
nl_pdf_pages=11
en_pdf_pages=11
visual_review_pages=22
protected_state_unchanged=true
report_delivery=false
```

Official state remains separately protected:

```text
official_nav_eur=99756.76
official_cash_eur=60439.44
portfolio_mutation=false
ledger_write=false
```

## Immediate repository sequence

1. Confirm the cleaned PR #70 head has no duplicate pricing implementation.
2. Confirm the exact-head pricing-engine and routine-preview workflows are green.
3. Confirm no unresolved review threads or unrelated official-state mutations.
4. Update the PR description with the validated pricing, valuation, report and authority evidence.
5. Keep the PR draft until merge authority is explicitly granted.
6. After merge, update `main` control files if the merge strategy changes any recorded SHA or path.

## Future-date pricing requirement

The accepted Alpha Vantage cache is valid only for report date `2026-07-31`. Every later report date must obtain fresh completed-close evidence and pass the same gate:

```text
two_same_date_providers=true
max_spread_pct<=1.0
exact_line_metadata_anchor>=1
funded_lines_pass=3/3
```

Before the next fresh-date report, establish at least one of these paths:

1. rotate `ALPHA_VANTAGE_API_KEY`, then commit the explicit rotation-confirmation control file required by the secret-safety policy; or
2. configure one or more additional development providers:
   - `LEEWAY_API_TOKEN`
   - `EODHD_API_TOKEN`
   - `MARKETSTACK_ACCESS_KEY`

Do not weaken the consensus gate merely because only Yahoo Chart is available.

## Remaining non-funded pricing gap

```text
instrument=CBUF
isin=IE00BJ5JNZ06
venue=XETR
currency=EUR
status=unpriced_diagnostics_only
```

Resolve CBUF only through an exact-line provider result. Do not substitute WHCS, another exchange line, issuer NAV or a proxy unless a separate explicit identity and valuation policy permits it. CBUF does not currently block funded NAV.

## Routine report sequence after merge

1. Select a new report date and suffix.
2. Resolve the latest accepted Weekly ETF donor commit.
3. Run fresh multi-provider qualification.
4. Fail closed unless all funded lines pass consensus and identity gates.
5. Build the run-scoped valuation overlay without mutating official state.
6. Generate Dutch-primary and English-companion HTML/PDF.
7. Run machine validation and render every PDF page.
8. Create the exact four-file routine manifest.
9. Keep delivery disabled until a separately authorized guarded-send step.
10. Claim delivery only after a real transport manifest and independent inbox receipt.

## Deferred matters

Commercial licensing and a permanent supported production market-data subscription were explicitly deferred for this development stage. They must be revisited before external commercial redistribution or production-grade provider promotion.

## Authority boundary

```text
pricing_development_model=validated
commercial_licensing_authority=false
funding_authority=false
portfolio_mutation=false
ledger_write=false
execution_authority=false
delivery_authority=false
merge_authority=false
```

## Prohibited shortcuts

Do not:

- reuse the July 31 provider cache for a later report date;
- accept a single provider for funded valuation;
- infer exact-line identity from ticker similarity;
- average providers from different close dates;
- overwrite official portfolio state with a report overlay;
- send the validated preview without an exact guarded-send authorization;
- claim receipt from SMTP success or artifact creation alone.