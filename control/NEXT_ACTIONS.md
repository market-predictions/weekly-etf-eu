# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
REQUEST_MERGE_AUTHORITY_FOR_PR70
```

The critical funded-position pricing blocker is resolved. The cleaned PR #70 head passed every required current check: multi-provider pricing, Stooq diagnostics, allocator report validation, full bilingual routine preview, exact package manifest, all 22 PDF review pages and protected-state proof. There are no PR comments or review threads.

## Final validated baseline

```text
branch=sync/wp11-routine-production-promotion
pull_request=70
validated_source_sha=0794ad5373c4073dfe3051d6675c0689739dcd4d
report_date=2026-07-31
run_id=20260803_30850723696_1
routine_preview_run=30850723696 success
routine_preview_job=91809807838
artifact_id=8870570755
artifact_sha256=c11dd7d464e706cf5ed4d6c4afcfeccd556a34a11108a9dfcc5a8a4f7c651602
pricing_engine_run=30850723739 success
stooq_diagnostic_run=30850723694 success
allocator_report_run=30850723704 success
funded_consensus=3/3
funded_identity_anchors=3/3
run_scoped_nav_eur=99455.68
nl_pdf_pages=11
en_pdf_pages=11
visual_review_pages=22
low_content_pages=0
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

## Completed repository sequence

1. Removed the superseded duplicate WP-SYNC-12 provider implementation and workflow.
2. Confirmed the canonical integrated pricing engine is `pricing/ucits_price_provider_engine.py`.
3. Confirmed exact provider identity resides in `config/ucits_price_provider_registry.yml`.
4. Confirmed the exact cleaned head is green.
5. Confirmed no PR comments or unresolved review threads.
6. Updated the PR description with pricing, valuation, report and authority evidence.
7. Updated `control/CURRENT_STATE.md`.
8. Updated this file.
9. Recorded the stable pricing decision in `control/DECISION_LOG.md`.
10. Refreshed the canonical WP-SYNC-11A evidence file.

## Merge boundary

PR #70 remains draft, open and mergeable. Do not mark ready or merge until explicit merge authority is provided.

After authorization:

1. mark PR #70 ready for review;
2. verify the expected head SHA has not changed;
3. squash-merge the PR;
4. fetch `main` and verify the merge commit;
5. correct any post-merge control references if necessary;
6. do not send the July 31 preview as a new current report.

## Future-date pricing requirement

The accepted Alpha Vantage cache is valid only for report date `2026-07-31`. Every later report date must obtain fresh completed-close evidence and pass the same gate:

```text
two_same_date_providers=true
max_spread_pct<=1.0
exact_line_metadata_anchor>=1
funded_lines_pass=3/3
```

Before the next fresh-date report, establish at least one of these paths:

1. rotate `ALPHA_VANTAGE_API_KEY`, then commit the explicit rotation-confirmation control required by the secret-safety policy; or
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