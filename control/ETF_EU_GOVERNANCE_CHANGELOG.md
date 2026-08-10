# Weekly ETF EU — Governance Changelog

## 2026-08-10 — Donor-parity authority reconciliation and release-topology hardening

### What changed

- Opened issue #90 and PR #91 as the clean post-PR84 donor-parity reconciliation line.
- Installed `control/ETF_EU_ALLOCATION_AUTHORITY_V1.md` and made unsupported 50%/35%/15% shadow controls non-executable; 75% is explicitly pricing coverage, not a position cap.
- Kept 25% turnover and 18% semiconductor values research/shadow-only pending any future explicit decision.
- Imported donor cash >3%/>5% and ~40% factor thresholds with their correct semantics as review/disclosure triggers, never sizing caps.
- Isolated historical CAP01/transition target-weight fields as non-current audit metadata before client rendering.
- Added current per-funded-position re-underwriting memory; missing evidence is `UNRESOLVED`, not implicit Hold.
- Added donor discovery → UCITS mapping → exact-line pricing → fundability lineage.
- Made the UCITS registry identity/investability-only; mutable funded state remains in the protected portfolio state.
- Bound macro freshness to donor source provenance and added dynamic completed-close date resolution.
- Removed a post-normalization shadow renderer that recreated a 7.50% cash reserve, strategic/phase targets and three-position copy; funded rendering is now dynamic and fail-closed on retired client copy.
- Replaced the routine production workflow with a candidate-only non-main route that cannot self-assure, push candidate output to main or send email.
- Disabled nineteen historical activation/send/repair/preview workflows by retaining them only as `.yml.disabled` audit evidence.
- During final workflow audit, also retired the old 2026-07-27 allocator `sister report` workflow because it rendered a parallel client-like report from historical transition/shadow allocation state. This raises the disabled historical/parallel route count to twenty.
- Reconciled `config/weekly_etf_donor_contract_pin.json` and its validator to exactly three active immutable-donor research-only workflows plus the disabled allocator sister-report route as retired audit evidence.
- Made controlled transport the sole active real ETF EU delivery route and bound it to independent PASS, approved main-lineage commit, principal guarded-send authority and SHA-256 for all six approved NL/EN MD/HTML/PDF artifacts.
- Controlled transport no longer re-renders an assured report; it sends the exact approved artifacts.
- Added workflow-authority, guarded-delivery, candidate-request, funded-renderer and donor-parity regressions.
- Reconciled roadmap/work-package/current-state/next-actions toward one PR #91 assurance handover.

### Assurance correction

The 2026-08-05 implementation described machine-generated JSON as `independent release assurance`. That terminology and authority were too strong because deterministic tooling run inside implementation/CI cannot satisfy the independent `governance_release_assurance` role by itself.

The historical filenames are retained for compatibility, but their schema/semantics are corrected:

```text
artifact_type=etf_eu_release_evidence_preflight
machine_preflight_status=PASS|FAIL
independent_assurance_verdict=null
independent_assurance_required=true
merge_authority=false
delivery_authority=false
```

A separate role-B reviewer on one exact frozen PR head is mandatory. The candidate workflow cannot create that verdict.

### Protected boundaries

No protected portfolio or trade-ledger mutation, real broker execution, SMTP send or delivery claim occurred as part of PR #91 implementation.

### Release state

Implementation is converged. Final exact-head CI, final handover commit and independent assurance remain required before merge. Post-merge exact-main validation and claim/state closeout remain required after PASS.

---

## 2026-08-05 — Activate independent release assurance

### What changed

- Established one user-facing coordinator with two internally separated roles: `implementation_operations` and `governance_release_assurance`.
- Prohibited implementation self-certification and governance mutation of the candidate under review.
- Added `tools/build_etf_eu_release_assurance.py` to reconstruct release evidence from immutable source, manifest, report, visual-review and delivery-queue evidence.
- Added `tools/validate_etf_eu_release_assurance.py` to enforce the evidence contract.
- Added positive and negative governance fixtures.
- Added `.github/workflows/validate-etf-eu-release-assurance.yml` for contract testing.
- Added pre-send artifact persistence concepts.
- Updated README, system index and next actions to describe the intended production and governance model.

### Historical note corrected on 2026-08-10

The original 2026-08-05 implementation incorrectly allowed machine evidence produced in implementation/CI to be described as independent release assurance. PR #91 corrects this: machine evidence is now preflight/supporting evidence only and cannot grant an assurance verdict, merge authority or delivery authority.

### Validation and activation evidence

- Python compilation passed for both governance tools.
- Synthetic machine evidence could be validated and negative fixtures rejected.
- GitHub Actions run `31011973728` completed successfully.
- PR #73 was squash-merged into `main` as `30ae248c9eb61045cec8e963ebb9ac84dbf1e476`.
- No portfolio mutation or email delivery was performed by that governance change.
