# ETF EU Structural Production Contract — Work Package 2026-08-05

## Claim

- Owner role: `implementation_operations`
- Independent approval role: `governance_release_assurance`
- Status: `IMPLEMENTATION_IN_PROGRESS`
- Target branch: `routine/20260804-fresh-send`

## Current issue

The final client-package validator rejects a valid four-position, partially activated ETF EU release candidate because it encodes the historical three-position and blocked-Stage-1 state in constants, exact prose fragments, and a CSS class.

## Root cause

The validator treats a prior presentation implementation as the business authority. It does not derive the funded roster, position count, Stage-1 status, activated and monitored candidates, authority flags, NAV, or cash from the immutable production convergence state and report manifest.

## Required change

1. Replace fixed three-position and blocked-state assumptions with a state-derived contract.
2. Validate report and manifest identity against the authoritative convergence state.
3. Keep client-surface hygiene, section completeness, PDF readability, and stale-content rejection.
4. Do not bind financial validity to exact client prose or CSS class names.
5. Cover both blocked three-position and partially activated four-position modes.
6. Add planted failures for roster divergence, incorrect funding status, authority escalation, and executable intents.
7. Require a fresh independent CI pass before merging.
8. Require a fresh governed production run and real transport receipt before declaring delivery.

## Files

- `tools/validate_etf_eu_production_converged_report.py`
- `tests/test_etf_eu_production_converged_report_contract.py`
- `.github/workflows/validate-etf-eu-production-contract.yml`
- `.github/workflows/run-weekly-etf-eu-20260804-fresh-send.yml`

## Acceptance criteria

- Positive blocked-state fixture passes.
- Positive partially activated fixture passes.
- All planted negative fixtures fail closed.
- Full four-position package passes the terminal report validator.
- Pricing, state, allocation, bilingual HTML/PDF and release assurance pass.
- SMTP transport produces a real manifest.
- Receiving-system verification confirms the expected messages and attachments before status becomes `DELIVERY_CONFIRMED`.
