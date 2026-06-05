# Weekly ETF EU Review OS — Changelog

This file records integration-level changes made to the EU/UCITS ETF review repository.

---

## 2026-06-05 — Verify WP5 production Dutch-first report surface

Status:

```text
WP5 production Dutch-first report surface = verified complete
```

Verification evidence:

```text
GitHub Actions run #36 on main: success
trigger commit: 6c7851de339259baa258687196fc3e3dd68bd56a
artifact commit: f3ad95bb4b94eab8be54ae80e0eefc2e00fce478
```

Generated artifacts:

```text
output/weekly_etf_eu_review_260605.md
output/weekly_etf_eu_review_nl_260605.md
output/fundability/ucits_fundability_gate_20260605_070115.json
output/validation/etf_eu_shadow_validation_evidence_20260605_070115.json
```

Report-surface verification:

- Dutch report includes `Productierapport-volwassenheid`.
- Dutch report explicitly presents the Dutch report as the primary client report.
- English report remains companion/operator-facing.
- Agreement-gate pricing evidence is visible.
- Fundability gate status is visible.
- Gate blockers and gate-level statuses are visible.
- `candidate_promotion=false` is visible.
- `funding_authority=false` is visible.
- `portfolio_mutation=false` is visible.
- `production_delivery=false` is visible.
- No funded UCITS positions are shown.
- No buy recommendation is made.
- No production delivery or delivery receipt is claimed.

Patch made during verification:

```text
tools/validate_etf_eu_output_contract.py
.github/workflows/send-weekly-etf-eu-report.yml
tests/test_production_dutch_first_report_maturity.py
control/run_queue/weekly_etf_eu_report_request_20260605_020001.md
```

Reason for patch:

The first WP5 validation run failed because strict Dutch-first validation scanned historical `weekly_etf_eu_review*.md` files in `output/`, including older reports that predated the WP5 production maturity layer. The validator now supports `--report-suffix`, and the workflow validates only the current generated report pair in strict production-Dutch-first mode.

Authority boundaries after verification:

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
candidate_promotion=false
no PDF generation
no email delivery
no delivery receipt
```

Delivery remains blocked. WP8 is design-only and no operational delivery path has been enabled.

---

## Prior integration history summary

Earlier changelog entries in this repository recorded these completed milestones:

- 2026-06-04 — control-file consolidation after agreement-aware pricing-surface work.
- 2026-06-04 — non-production pricing-surface shadow workflow creation.
- 2026-06-04 — UCITS fundability promotion contract.
- 2026-06-04 — pricing-surface report wrapper and validator.
- 2026-06-04 — valuation agreement bridge.
- 2026-06-04 — agreement gate.
- 2026-06-04 — source metadata policy.
- 2026-06-04 — M1 pricing-spine integration state consolidation.
- 2026-06-03 — M1 provider-adapter workstreams.
- 2026-06-03 — M0 ground-clearing workstream.

Detailed pre-WP5 changelog history remains available in Git before commit `f3ad95bb4b94eab8be54ae80e0eefc2e00fce478` and before this WP5 verification-control update.
