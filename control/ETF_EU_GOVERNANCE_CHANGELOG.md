# Weekly ETF EU — Governance Changelog

## 2026-08-05 — Activate independent release assurance

### What changed

- Established one user-facing coordinator with two internally separated roles: `implementation_operations` and `governance_release_assurance`.
- Prohibited implementation self-certification and governance mutation of the candidate under review.
- Added `tools/build_etf_eu_release_assurance.py` to reconstruct a release candidate from immutable source, manifest, report, visual-review and delivery-queue evidence.
- Added `tools/validate_etf_eu_release_assurance.py` to enforce the evidence contract and reject incomplete, failed or self-certified decisions.
- Added positive and negative governance fixtures.
- Added `.github/workflows/validate-etf-eu-release-assurance.yml` for contract testing.
- Inserted the governance evidence builder and validator immediately before the guarded SMTP step in `.github/workflows/run-weekly-etf-eu-routine.yml`.
- Added pre-send artifact upload so the governance evidence remains available if transport later fails.
- Added persistence of the release-assurance evidence alongside successful production artifacts.
- Updated README, system index and next actions to describe the actual production and governance model.

### Why

The prior process allowed component-level success to be interpreted as end-to-end completion. A legacy scheduler and a stale final validator remained broken even after pricing and rendering milestones passed. The release path now requires a separate machine-readable governance decision tied to the exact source SHA, run identity and report hashes.

### Validation and activation evidence

- Python compilation passed for both governance tools.
- A synthetic valid release candidate produced `PASS` and was accepted by the validator.
- A deliberately failed visual-review fixture was rejected as expected.
- GitHub Actions run `31011973728` completed successfully.
- PR #73 was squash-merged into `main` as `30ae248c9eb61045cec8e963ebb9ac84dbf1e476`.
- No portfolio mutation or email delivery was performed by this governance change.

### Remaining implementation work

- Rebase or port the governance gate into the active fresh-report work from PR #72.
- Repair PR #72’s stale portfolio-mode validator.
- Quarantine the legacy FX scheduler as a Weekly ETF EU production entry point.
- Execute a fresh governed release cycle and independently confirm inbox receipt.
