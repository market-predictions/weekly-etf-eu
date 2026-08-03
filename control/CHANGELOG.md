# Weekly ETF EU Review OS — Changelog

This file records integration-level changes made to the EU/UCITS ETF review repository.

---

## 2026-08-03 — Complete WP-SYNC-10 production engine convergence

Status:

```text
WP-SYNC-10 production convergence = completed
machine_validation = passed
visual_review = passed
routine_production_promotion = not yet enabled
report_delivery = not performed
```

### Current issue resolved

The premium routine EU report and the merged donor-synchronized report engine were separate paths. The legacy premium renderer could drift through hardcoded candidate copy and string replacements, while the synchronized report retained development terminology and analytical trade scenarios.

### Implementation

Added:

```text
runtime/build_etf_eu_production_convergence_state.py
runtime/finalize_etf_eu_wp10_source_language.py
runtime/prepare_etf_eu_wp10_client_executive_surface.py
runtime/promote_etf_eu_sister_report_to_production_candidate.py
tools/validate_etf_eu_production_convergence_state.py
tools/validate_etf_eu_production_converged_report.py
.github/workflows/validate-etf-eu-production-convergence.yml
```

Added exact, non-authorizing current water mappings:

```text
water_infrastructure=XMLC / IE00BK5BC891 / A2PM52
water_utilities=IQQQ / IE00B1TXK627 / A0MM0S
```

Updated:

```text
config/shared_exposure_ucits_map.yml
runtime/merge_etf_eu_sync_registries.py
```

### Stable state-model decision

The report now separates:

```text
current_promoted_exposures=6
mapped_promoted_exposures=6
frozen_stage_1_review_candidates=2
VVSM_currently_promoted=false
L0CK_currently_promoted=true
```

VVSM remains visible only as earlier Stage-1 review continuity. L0CK remains currently promoted but blocked. Both have zero actionable target.

### Client report result

Generated and validated:

```text
output/production_convergence/client_report/weekly_etf_eu_review_nl_260729_converged.html
output/production_convergence/client_report/weekly_etf_eu_review_nl_260729_converged.pdf
output/production_convergence/client_report/weekly_etf_eu_review_260729_converged.html
output/production_convergence/client_report/weekly_etf_eu_review_260729_converged.pdf
```

Contract:

```text
nl_sections=19
en_sections=19
nl_pages=11
en_pages=11
funded_positions=VWCE,EUNA,SXR8
cash_weight_pct=60.59
portfolio_delta=0
client_development_language_absent=true
stale_simulated_trade_content_absent=true
```

### Defects discovered and corrected

- two current water exposures were unmapped;
- Dutch water labels were introduced after the earlier localization pass;
- VVSM was incorrectly assumed to remain currently promoted;
- current opportunity and frozen Stage-1 review semantics were conflated;
- client pages retained shadow/development wording and raw machine tokens;
- regime metadata rendered as an object rather than a client label;
- footers retained development wording;
- cash displayed the analytical 35.57% scenario rather than official 60.59% cash;
- official positions displayed analytical targets rather than no-change targets;
- stale `VVSM/SMH` labeling remained visible.

### Validation evidence

```text
validated_head_sha=0997545ad0cf670d805536414d05abde17ff89f2
strategy_synchronization_run=30810262285 success
target_allocator_run=30810262293 success
allocator_report_run=30810262292 success
production_convergence_run=30810262300 success
job_id=91675081232
artifact_id=8854509533
artifact_digest=sha256:19a5bfcc2db4f813bebc3588946e4843c587ff17aa021d0150835bde58208d65
```

Full visual review covered 22 pages and found no blank pages, clipping, overlap or orphaned rows.

### Authority boundary

```text
portfolio_mutation=false
ledger_write=false
funding_authority=false
execution_authority=false
activation_authority=false
production_delivery_authority=false
executable_trade_intents=[]
```

Next package: `ETF-EU-WP-SYNC-11_ROUTINE_PRODUCTION_PROMOTION_AND_GUARDED_DELIVERY`.

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
