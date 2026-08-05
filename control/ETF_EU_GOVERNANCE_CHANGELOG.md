# Weekly ETF EU — Governance Changelog

## 2026-08-05 — Introduce independent release assurance

### What changed

- Established one user-facing coordinator with two internally separated roles: `implementation_operations` and `governance_release_assurance`.
- Prohibited implementation self-certification and governance mutation of the candidate under review.
- Added `tools/build_etf_eu_release_assurance.py` to reconstruct a release candidate from immutable source, manifest, report, visual-review and delivery-queue evidence.
- Added `tools/validate_etf_eu_release_assurance.py` to enforce the evidence contract and reject incomplete, failed or self-certified decisions.
- Added positive and negative governance fixtures.
- Added `.github/workflows/validate-etf-eu-release-assurance.yml` for contract testing.
- Inserted the governance evidence builder and validator immediately before the guarded SMTP step in `.github/workflows/run-weekly-etf-eu-routine.yml`.
- Added persistence of the release-assurance evidence alongside the production artifacts.
- Updated README, system index and next actions to describe the actual production and governance model.

### Why

The prior process allowed component-level success to be interpreted as end-to-end completion. A legacy scheduler and a stale final validator remained broken even after pricing and rendering milestones passed. The release path now requires a separate machine-readable governance decision tied to the exact source SHA, run identity and report hashes.

### Validation performed before push

- Python compilation passed for both governance tools.
- A synthetic valid release candidate produced `PASS` and was accepted by the validator.
- A deliberately failed visual-review fixture was rejected as expected.
- No portfolio mutation or email delivery was performed.

### Remaining verification

- GitHub Actions must validate the branch workflow and fixtures.
- The governance change must be merged or rebased into the active fresh-report branch.
- PR #72’s stale portfolio-mode validator and the legacy FX scheduler remain separate implementation defects.
