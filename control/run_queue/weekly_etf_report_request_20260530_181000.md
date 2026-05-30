# Weekly ETF report request

requested_at_utc: 2026-05-30T18:10:00Z
requested_run_date: 2026-05-30
mode: pro
requested_close_date:
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## Request
Queue a fresh Weekly ETF Review run after the already-executed post-execution wording patch.

## Checks requested
- Treat execution_status=already_executed as a post-execution report state.
- Confirm the GLD to GSG rotation is described as already reflected in official portfolio state, not proposed or pending.
- Block delivery if post-execution reports contain proposed or pending wording.
- Confirm no portfolio-state or trade-ledger mutation occurs on the already-executed path.
- Confirm GLD and GSG holdings remain arithmetically reconciled.
- Confirm the equity curve remains based on repaired canonical valuation history.
- Confirm final EN/NL reports pass render and delivery validators.
