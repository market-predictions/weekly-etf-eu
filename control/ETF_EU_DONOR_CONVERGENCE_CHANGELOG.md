# ETF EU Donor Convergence — Changelog

This log records only the `ETF-EU-DONOR-CONVERGENCE-V1` line. Stable decisions belong in `control/decisions/ETF_EU_DONOR_CONVERGENCE_DECISION_20260810.md` and, at final closeout, the project decision log.

## 2026-08-10 — Convergence line opened

- Created successor branch `agent/etf-eu-donor-convergence-v1` from exact assured PR #84 head `888a55b5bc8ae3d465691117157c616893b3addb`.
- Preserved PR #84 and issue #87 PASS as frozen evidence; no modification to the assured candidate.
- Added roadmap `docs/roadmaps/WEEKLY_ETF_EU_DONOR_CONVERGENCE_ROADMAP_20260810.md`.
- Added work package `control/work_packages/ETF_EU_WP_DONOR_CONVERGENCE_V1_20260810.md`.
- Added allocation-authority contract `control/ETF_EU_ALLOCATION_AUTHORITY_CONVERGENCE_V1.md`.
- Added architecture decision `control/decisions/ETF_EU_DONOR_CONVERGENCE_DECISION_20260810.md`.
- Added PR84 → convergence lineage handover.
- Transferred the active release claim from V3 to `ETF-EU-DONOR-CONVERGENCE-V1`.
- Confirmed live `main=76325f60a3abcda4a059f7823c9c0b5024802870` at opening reconciliation.

### Diagnosed P0 runtime defect

`runtime/build_etf_eu_target_allocator_shadow_v3.py` actively computes its preferred shadow allocation from transition-policy values including cash reserve, turnover, direct-position and theme caps. `runtime/build_etf_eu_target_allocator_shadow_v3_policy_gate.py` additionally enforces the historical two-exposure Stage-1 allowlist.

These mechanics are now explicitly non-authoritative for current allocation and will be removed from current routine/client authority while retained only where needed for historical reproducibility.

### Boundaries

No portfolio mutation, ledger write, real broker execution or delivery has been authorized or performed by this convergence line.
