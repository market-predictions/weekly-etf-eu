# Weekly ETF EU — Governance Changelog

## 2026-08-11 — Donor-parity reconciliation fully closed

### Final governance result

- Issue #96 returned independent `ETF_EU_POST_MERGE_US_DONOR_LEAK_ASSURANCE: PASS` on frozen PR #95 head `e5d3470e1e1ab7f402a02cb31b775f3f902d4928`.
- PR #95 merged unchanged as `10823b7c457a253e409a768f52ee95b1522c363f`.
- Exact-main product-boundary run `31472717495` checked out that exact SHA and returned PASS with 6 planted tests, 32 active workflows scanned and no blockers.
- The real merge tree and the assurance synthetic merge tree are identical: `71a614575bdc1d675ece53684d14601ce76fde90`.
- Therefore the frozen-tree workflow-authority evidence applies to exact merged code content: `32 active | 23 retired-disabled | candidate=1 | delivery=1 | US donor execution=0`.
- The three retired U.S. donor workflows did not execute on the merge push.
- The two erroneous U.S. pricing artifact paths remained absent after merge.
- Protected portfolio and trade-ledger blobs remained `df710b5f...` and `c6765ba3...` respectively.
- Successor claim `ETF-EU-POST-MERGE-US-DONOR-LEAK-REPAIR-V1` closed with explicit handover `handover/ETF_EU_POST_MERGE_US_DONOR_LEAK_REPAIR_V1_CLOSE_20260811.md`.
- No report delivery, SMTP send, portfolio mutation, ledger write, allocation reopening or broker execution occurred in this closeout.

### Durable outcome

The Weekly ETF EU environment now treats `weekly-etf` as a strategy/behavior donor only. U.S. donor runtime, U.S. report filenames and U.S. portfolio state cannot become active ETF EU operational authority through GitHub Actions without failing the product/workflow boundary gates.

The next current Weekly ETF EU report is a separate production candidate cycle with fresh completed-close data, current re-underwriting, fresh independent assurance and separately authorized guarded delivery.

---

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
- Marked merged PR #91 claim `ETF-EU-DONOR-PARITY-RECONCILIATION-V1` `SUPERSEDED` with explicit handover.
- Retired `.github/workflows/persist-etf-pricing-audit.yml` to `.yml.disabled` audit history.
- Retired `.github/workflows/validate-etf-runtime.yml` to `.yml.disabled` audit history.
- Retired `.github/workflows/validate-etf-lane-breadth.yml` to `.yml.disabled` audit history.
- Removed `output/pricing/price_audit_2026-08-10_20260810_214841.json` and `output/pricing/price_cache_2026-08-10.json` from the repaired candidate.
- Extended `tools/validate_etf_eu_repository_boundary.py` to reject active FX and US donor execution/report tokens in `.yml/.yaml` workflows while ignoring `.yml.disabled` audit history.
- Extended `tools/validate_etf_eu_workflow_authority.py` to scan `.yml` + `.yaml`, reject active US donor tokens and require all retired routes to retain non-executable `.disabled` evidence.
- Added planted regressions proving donor pricing/report invocations fail when active but are allowed as disabled audit history.

### Exact semantic validation

Semantic baseline `d9b5731bbd0b125e2df9b778282116f9d8c32314`:
- product-boundary run `31436751783` — SUCCESS;
- planted tests — 6 passed;
- donor-parity/full-package run `31436751773` — SUCCESS;
- package/blocker suite — 31 passed;
- workflow authority — `32 active | 23 retired | candidate=1 | delivery=1 | US donor execution=0`;
- candidate pricing/Markdown wiring — PASS;
- allocation-authority audit — PASS.

### Authority correction

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
- Disabled nineteen historical activation/send/repair/preview workflows, then retired the allocator sister-report route, and finally retired the three active U.S. donor workflows during the post-merge correction.
- Made controlled transport the sole active real ETF EU delivery route and bound it to independent PASS, approved main-lineage commit, principal guarded-send authority and SHA-256 for all six approved NL/EN MD/HTML/PDF artifacts.
- Added workflow-authority, guarded-delivery, candidate-request, funded-renderer and donor-parity regressions.

### Assurance correction

Machine-generated release evidence is preflight/supporting evidence only:

```text
artifact_type=etf_eu_release_evidence_preflight
machine_preflight_status=PASS|FAIL
independent_assurance_verdict=null
independent_assurance_required=true
merge_authority=false
delivery_authority=false
```

A separate role-B reviewer on one exact frozen PR head is mandatory.

### Release outcome

PR #91 received independent PASS in issue #93 and merged as `202b0a629af34c697c7b7cb8fdce97fbb56bddbc`. Its post-merge donor-runtime defect was subsequently repaired and closed through issue #94 / PR #95 / issue #96.

---

## 2026-08-05 — Activate independent release assurance

### What changed

- Established one user-facing coordinator with two internally separated roles: `implementation_operations` and `governance_release_assurance`.
- Prohibited implementation self-certification and governance mutation of the candidate under review.
- Added machine release-evidence preflight tooling and negative fixtures.
- Added GitHub Actions contract testing and pre-send artifact persistence concepts.

### Historical note corrected on 2026-08-10

The original 2026-08-05 implementation incorrectly allowed machine evidence produced in implementation/CI to be described as independent release assurance. PR #91 corrected this: machine evidence is supporting evidence only and cannot grant assurance, merge or delivery authority.

### Validation and activation evidence

- Python compilation passed for the governance tools.
- Synthetic machine evidence could be validated and negative fixtures rejected.
- GitHub Actions run `31011973728` completed successfully.
- PR #73 was squash-merged into `main` as `30ae248c9eb61045cec8e963ebb9ac84dbf1e476`.
- No portfolio mutation or email delivery was performed by that governance change.
