# Weekly ETF report request

requested_at_utc: 2026-05-30T17:33:00Z
requested_run_date: 2026-05-30
mode: pro
requested_close_date:
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## Request
Queue a fresh Weekly ETF Review run after fixing valuation persistence to preserve official shares.

## Checks requested
- Persist successful valuation state may reprice official holdings but must not import pre-execution runtime/report shares.
- Confirm GLD remains the canonical post-rotation share count, not 29 shares.
- Confirm already-executed GLD to GSG rotation produces an idempotent artifact and does not mutate state or ledger.
- Validate trade-ledger idempotency before and after guarded execution.
- Confirm equity curve remains based on repaired canonical valuation history and does not inflate from duplicate execution.
- Confirm final EN/NL reports pass render and delivery validators.
