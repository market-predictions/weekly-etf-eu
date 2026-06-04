# Post PR #10 consolidation — 2026-06-04

Repository: `market-predictions/weekly-etf-eu`

## Confirmed merged PR

### PR #10 — Add agreement-aware valuation artifact bridge

Merge commit:

```text
51f91751e8df19bc5879b4a6ee4c3280e663c55e
```

Files integrated:

```text
control/VALUATION_AGREEMENT_INTEGRATION_PLAN_20260604.md
pricing/valuation_agreement_evidence.py
pricing/enrich_ucits_valuation_agreement.py
pricing/build_ucits_valuation_prices_with_agreement.py
tests/test_valuation_agreement_evidence.py
tests/test_build_ucits_valuation_prices_with_agreement.py
```

## Roadmap state after PR #10

Completed:

```text
source metadata policy
agreement gate
valuation artifact bridge with agreement-gate evidence
```

Next:

```text
first report pricing surface
```

Then:

```text
fundability / candidate-promotion contract
production Dutch-first report
delivery enablement after validators and manifest/receipt path exist
```

## Important distinction

PR #10 adds an agreement-aware wrapper path. It does not switch the existing workflow to that wrapper and does not change generated output artifacts yet.

## Authority boundaries still unchanged

```text
valuation_grade=false
valuation_grade_row_count=0
funding_authority=false
portfolio_mutation=false
production_delivery=false
no workflow changes
no output artifact changes
no portfolio state changes
no report renderer changes
no PDF generation
no email delivery
no delivery receipt
no candidate promotion to fundable
```

## Control-file note

`control/CURRENT_STATE.md`, `control/NEXT_ACTIONS.md`, and `control/CHANGELOG.md` remain candidates for direct consolidation. This file records the current source-of-truth roadmap status until those larger files can be safely rewritten.
