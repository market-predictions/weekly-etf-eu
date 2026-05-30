# Weekly ETF report request

requested_at_utc: 2026-05-30T17:30:00Z
requested_run_date: 2026-05-30
mode: pro
requested_close_date:
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## Request
Queue a fresh Weekly ETF Review verification run after the post-execution delivery HTML copy-contract patch.

## Verification focus
- Confirm `execution_status=already_executed` is treated as a post-execution client-facing state.
- Confirm the GLD to GSG rotation is described as already reflected in official portfolio state and trade ledger.
- Confirm no proposed or pending execution language appears in rendered delivery HTML or PDF.
- Confirm the new delivery HTML validator blocks forbidden post-execution copy if it appears.
- Confirm no duplicate portfolio-state or trade-ledger mutation occurs on the already-executed path.
- Confirm GLD and GSG holdings remain arithmetically reconciled.
- Confirm the equity curve remains based on repaired canonical valuation history and does not inflate across reruns.
- Confirm final English and Dutch reports pass render and delivery validators.

## Expected success markers
- ETF_MODEL_EXECUTION_OK or ETF_MODEL_EXECUTION_VALIDATION_OK with already-executed/no-op semantics.
- ETF_DELIVERY_HTML_CONTRACT_OK with post_execution=True.
- ETF_EXECUTED_REPORT_FINALIZED or equivalent post-execution report finalization marker.
- No visible instances of: Rotation plan artifact is active, proposed until, pending execution, pending portfolio-state persistence, Proposed rotation, trade intents are proposed.
