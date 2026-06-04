# Twelve Data source policy review note

Date: 2026-06-04

Work package: Work Package 7 — Official/premium pricing source path

Status:

```text
adapter_path_implemented=true
focused_adapter_validation=passed
source_policy_decision=pending
workflow_integrated=false
valuation_authority_integrated=false
```

## Purpose

Prepare review of Twelve Data as a paid/provider-reviewed pricing source path for UCITS ETF close evidence.

This note does not approve Twelve Data as a valuation authority and does not wire it into the main workflow.

## Current implementation evidence

Adapter:

```text
pricing/sources/twelve_data.py
```

Focused tests:

```text
tests/test_twelve_data_adapter.py
```

Fixture evidence:

```text
tests/fixtures/pricing/twelve_data/resolved_time_series.json
tests/fixtures/pricing/twelve_data/provider_error.json
```

Focused validation command:

```bash
python -m pytest tests/test_twelve_data_adapter.py -q
```

Observed result:

```text
3 passed
```

## Review topics before any promotion

### 1. License and paid-plan assumptions

Confirm the exact Twelve Data subscription, terms, and permitted use case before using live data in recurring reports.

Questions:

- Is the selected plan permitted for automated portfolio/report pricing use?
- Are cached price artifacts allowed?
- Are internal client reports allowed?
- Are external redistributions or email attachments restricted?
- Are attribution requirements present?

### 2. Allowed report use

Confirm whether Twelve Data prices may appear in generated weekly ETF reports and under which wording.

Review should distinguish:

```text
internal evidence artifact
report-visible pricing evidence
production client delivery
```

### 3. Redistribution constraints

Confirm whether generated Markdown, PDF, email, or archive artifacts containing Twelve Data values are redistribution under the provider terms.

No delivery behavior should be enabled from this note.

### 4. UCITS ETF reliability and coverage

Check coverage for the target UCITS trading lines, especially:

```text
IE00B5BMR087 / CSPX / XAMS
IE00B5BMR087 / CSPX / LSE
IE00B5BMR087 / SXR8 / XETR
```

Confirm symbol mapping at ISIN + venue level, not ticker-only.

### 5. Currency, date, and session quality

Review whether Twelve Data provides enough evidence for:

```text
observed_date
close
currency
completed market session
trading venue / exchange identity
```

The current adapter validates date, close, currency, and completed-session output shape, but provider-level session authority still needs policy review.

### 6. Agreement-gate role

Decide whether Twelve Data can count as agreement-gate evidence.

Possible conservative outcomes:

```text
diagnostic_candidate_source only
provisional cross-check source
paid provider evidence source
valuation-grade eligible only with a second independent official/market-close source
```

### 7. Valuation-grade eligibility

Do not mark Twelve Data valuation-grade eligible until a separate decision updates:

```text
control/DATA_SOURCE_METADATA.md
config/ucits_pricing_source_policy.yml
control/DECISION_LOG.md
```

## Current boundary decision

The adapter remains evidence-only.

Current required lineage flags:

```text
valuation_grade_by_adapter=false
portfolio_mutation=false
production_delivery=false
funding_authority=false
```

Current integration restrictions:

```text
workflow_integrated=false
report_renderer_changed=false
portfolio_mutation=false
candidate_promotion=false
pdf_generation=false
email_delivery=false
production_delivery=false
```

## Next review action

Perform formal source-policy review against the active Twelve Data plan and terms. Only after that review should the repo consider metadata-policy changes or agreement-gate integration.
