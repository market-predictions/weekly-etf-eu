# Weekly ETF report request

requested_at_utc: 2026-05-30T14:31:30Z
requested_run_date: 2026-05-30
mode: pro
requested_close_date:
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## Request
Queue a fresh Weekly ETF Review run after the executed-report wording and before/after table contract patch.

## Checks requested
- Confirm guarded-auto model execution still passes.
- Confirm post-execution reports do not use proposed/pending rotation wording.
- Confirm Section 14 / Dutch Section 14 uses real previous weight, new weight, weight change and share delta from the guarded-auto artifact.
- Block delivery if a row has non-zero shares_delta but unchanged previous/new weights.
- Confirm final Section 15 holdings remain reconciled to official portfolio state.
- This is model-portfolio state handling only, not broker order placement.
