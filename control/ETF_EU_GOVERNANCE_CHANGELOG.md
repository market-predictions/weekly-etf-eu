# Weekly ETF EU — Governance Changelog

## 2026-08-10 — Post-merge US donor execution leak repair

### Trigger

- Independent issue #93 returned `ETF_EU_PR91_ASSURANCE_FAIL_REPAIR_REVERIFY: PASS` on frozen PR #91 head `686c658c03d5ba4cbd208e254822a73b3fb514f2`.
- PR #91 was merged unchanged as `202b0a629af34c697c7b7cb8fdce97fbb56bddbc`.
- Post-merge push workflow `Persist ETF pricing audit` then executed retained US Weekly ETF runtime `pricing.run_pricing_pass` and committed `d771bde734ffda6120a77b1f4fe0e99bd198cc96` to ETF EU `main`.
- The bot commit added US pricing artifacts containing GLD/GSG/PAVE/PPA/SMH/SPY/URNM rather than the protected EU funded set VWCE/EUNA/SXR8/L0CK.
- `Validate ETF runtime changes` also executed the same donor pricing path and legacy `send_report.py` renderer.
- After the product-boundary gate was hardened, it found a third active donor-report route: `validate-etf-lane-breadth.yml`, anchored to donor `weekly_analysis_pro_*` output rather than the current ETF EU discovery/fundability bridge.

### Root cause

The repository retained donor/US runtime and report-validation modules for historical/donor purposes, which is acceptable. The defect was that three active ETF EU workflows still invoked donor operational/output conventions. `pricing/run_pricing_pass.py` defaults to donor state/output conventions (`output/etf_portfolio_state.json`, `weekly_analysis_pro_*`, U.S. close timing). The pre-existing repository-boundary gate protected against FX product leakage but not US Weekly ETF donor-runtime/report leakage.

### Repair line

- Opened issue #94 and draft PR #95.
- Created successor claim `ETF-EU-POST-MERGE-US-DONOR-LEAK-REPAIR-V1`.
- Marked merged PR #91 claim `ETF-EU-DONOR-PARITY-RECONCILIATION-V1` `SUPERSEDED` with explicit handover; parent issue #90 remains open until successor exact-main closeout.
- Retired `.github/workflows/persist-etf-pricing-audit.yml` to `.yml.disabled` audit history.
- Retired `.github/workflows/validate-etf-runtime.yml` to `.yml.disabled` audit history.
- Retired `.github/workflows/validate-etf-lane-breadth.yml` to `.yml.disabled` audit history; its desired discovery-breadth behavior remains represented through the current donor-discovery → UCITS mapping/fundability bridge.
- Removed `output/pricing/price_audit_2026-08-10_20260810_214841.json` and `output/pricing/price_cache_2026-08-10.json` from the repaired candidate.
- Extended `tools/validate_etf_eu_repository_boundary.py` to reject active FX and US donor execution/report tokens in `.yml/.yaml` workflows while ignoring `.yml.disabled` audit history.
- Extended `tools/validate_etf_eu_workflow_authority.py` to scan `.yml` + `.yaml`, reject active US donor tokens and require all retired routes to retain non-executable `.disabled` evidence.
- Added planted regressions proving donor pricing/report invocations fail when active but are allowed as disabled audit history.
- Updated workflow-authority index, roadmap, work package, current state, next actions and handovers around the successor line.

### Exact semantic validation

Semantic baseline:

`d9b5731bbd0b125e2df9b778282116f9d8c32314`

Evidence:
- product-boundary run `31436751783` — SUCCESS;
- product-boundary planted tests — 6 passed;
- full active-workflow product-boundary scan — PASS;
- donor-parity/full-package run `31436751773` — SUCCESS;
- package/blocker regression suite — 31 passed;
- workflow authority — `PASS | active_workflows=32 | retired_disabled=23 | candidate_route=1 | delivery_route=1 | us_donor_execution_routes=0`;
- candidate pricing/Markdown wiring — PASS;
- allocation-authority audit — PASS.

### Authority correction

The post-merge incident establishes an explicit additional rule:

```text
green CI != product identity
retained donor source != active ETF EU execution authority
```

The only report/pricing release path is the EU/UCITS candidate route under `run-weekly-etf-eu-routine.yml`. The only real delivery path remains `send-weekly-etf-eu-controlled-transport.yml`.

### Protected boundaries

```text
portfolio_mutation=false
trade_ledger_write=false
real_broker_execution=false
report_delivery=false
smtp_send=false
allocation_decision_reopened=false
```

PR #95 requires fresh exact-head independent assurance before merge. The PASS from issue #93 does not transfer to the successor candidate.

---

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
- Removed a post-normalization shadow renderer that recreated a 7.50% cash reserve, strategic/phase targets and three-position copy; funded rendering is dynamic and fail-closed on retired client copy.
- Replaced the routine production workflow with a candidate-only non-main route that cannot self-assure, push candidate output to main or send email.
- Disabled nineteen historical activation/send/repair/preview workflows by retaining them only as `.yml.disabled` audit evidence.
- During final workflow audit, also retired the old 2026-07-27 allocator `sister report` workflow because it rendered a parallel client-like report from historical transition/shadow allocation state. This raised the disabled historical/parallel route count to twenty before the later post-merge donor-runtime correction above.
- Reconciled `config/weekly_etf_donor_contract_pin.json` and its validator to exactly three active immutable-donor research-only workflows plus the disabled allocator sister-report route as retired audit evidence.
- Made controlled transport the sole active real ETF EU delivery route and bound it to independent PASS, approved main-lineage commit, principal guarded-send authority and SHA-256 for all six approved NL/EN MD/HTML/PDF artifacts.
- Controlled transport no longer re-renders an assured report; it sends the exact approved artifacts.
- Added workflow-authority, guarded-delivery, candidate-request, funded-renderer and donor-parity regressions.

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

### Release outcome update

PR #91 later received independent PASS in issue #93 and was merged as `202b0a629af34c697c7b7cb8fdce97fbb56bddbc`. The subsequent post-merge donor-runtime defect is handled by issue #94 / PR #95.

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
