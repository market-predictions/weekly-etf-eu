# Post PR #8/#9 consolidation — 2026-06-04

Repository: `market-predictions/weekly-etf-eu`

## Confirmed merged PRs

### PR #8 — M5: Add source metadata policy

Merge commit:

```text
270446ee54d7f97223b2b94f6207ec2b7c88de22
```

Files integrated:

```text
control/DATA_SOURCE_METADATA.md
pricing/source_metadata_policy.py
tests/test_source_metadata_policy.py
```

Validation reported:

```text
python -m pytest tests/test_source_metadata_policy.py -q
9 passed in 0.12s
```

### PR #9 — M1: Add agreement gate integration

Merge commit:

```text
575f919614690a3a851dc4968dea0cfe3a1a870d
```

Files integrated:

```text
pricing/price_agreement_gate.py
tools/validate_price_agreement_gate.py
tests/test_price_agreement_gate.py
```

Validation reported:

```text
python -m pytest tests/test_price_agreement_gate.py -q
6 passed in 0.10s

python tools/validate_price_agreement_gate.py
PRICE_AGREEMENT_GATE_OK
```

## Updated roadmap state

Completed:

```text
source metadata policy
agreement gate
```

Next:

```text
valuation artifact integration with agreement-gate output
```

Then:

```text
first report pricing surface
fundability / candidate-promotion contract
production Dutch-first report
delivery enablement after validators and manifest/receipt path exist
```

## Authority boundaries still unchanged

```text
funding_authority=false
portfolio_mutation=false
production_delivery=false
no workflow changes
no output artifact changes
no report renderer changes
no PDF generation
no email delivery
no delivery receipt
no candidate promotion to fundable
```

## Control-file note

A direct full replacement update for `control/CHANGELOG.md` was attempted after PR #8/#9 merge but was blocked by the GitHub tool safety layer.

`control/CURRENT_STATE.md`, `control/NEXT_ACTIONS.md`, and `control/CHANGELOG.md` should still be updated directly when the file update layer accepts the change. Until then, this file records the current source-of-truth consolidation note.
