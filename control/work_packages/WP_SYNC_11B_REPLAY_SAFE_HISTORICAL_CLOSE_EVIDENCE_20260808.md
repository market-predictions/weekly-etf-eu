# ETF-EU-WP-SYNC-11B — Replay-safe historical completed-close evidence

## Status

```text
work_package=ETF-EU-WP-SYNC-11B
priority=P1
claimed_by=implementation_operations
claim_date=2026-08-08
status=RELEASE_CANDIDATE_READY
portfolio_mutation=false
ledger_write=false
email_delivery=false
implementation_ci=PASS
independent_release_assurance=PENDING_FULL_PACKAGE_BINDING
```

## Why this was the roadmap priority

WP-SYNC-11A established the two-provider completed-close gate and explicitly allowed historical evidence reuse only when bound to the exact report date, basket ID, provider and symbol with immutable provenance. A rolling `previous close` endpoint cannot independently replay an older requested report date after multiple sessions have elapsed.

This blocked deterministic regeneration and independent assurance of the 2026-08-05 candidate. Rendering or delivery work therefore did not outrank this defect.

## Decision framework

Pricing lineage does not decide portfolio composition. It decides whether a funded line may be represented as current for the requested completed close.

Stable rules:

1. Preserve two independent providers on the same completed-close date.
2. Preserve the 1.0% agreement tolerance.
3. Preserve ISIN-first EU line identity.
4. Never infer an old close from a rolling live `previous close` field after it has advanced.
5. Preserve accepted report-time two-provider evidence immutably so an issued report can be reproduced later even if providers retroactively adjust their public history.
6. Treat source or provenance failure as a blocker, not permission to fabricate, relabel or silently rebase a close.

## Provider research result

A date-addressable Börse Frankfurt adapter was implemented for:

```text
/v1/data/price_history
```

The adapter is strict exact-date only and has deterministic tests for date normalization, missing-date rejection and non-positive-close rejection.

Live GitHub-runner probes on 2026-08-08 showed that this endpoint returns HTTP 200 with an empty `{}` payload for the tested Xetra ETF requests. It therefore cannot currently serve as the sole durable second historical provider.

The two-provider gate was not weakened.

## Durable replay architecture

The successful original 2026-08-05 production run still exists as GitHub Actions evidence:

```text
source_workflow_run_id=31051399761
source_run_id=20260805_31051399761_1
source_workflow_head_sha=476579ecc0644250d7d12a8f69784a279118d389
actions_artifact_id=8948609199
actions_artifact_name=etf-eu-final-package-20260805_31051399761_1
actions_artifact_digest=sha256:631f90f24caabc271b1d290b519adf5c3e667cb717f35563f522d030cb49c55a
qualification_member=pricing/ucits_price_provider_qualification_20260805_31051399761_1.json
qualification_member_sha256=02ad0fa5dd431eebadf73c370b6ab9fdc85a570332667a26234ad0d1758611d4
```

That original qualification record proves:

```text
report_date=2026-08-05
funded_line_count=4
funded_consensus_count=4
funded_identity_anchor_count=4
report_pricing_gate_passed=true
agreement_tolerance_pct=1.0
```

Funded accepted report-time closes:

| Ticker | Börse Frankfurt | Yahoo | Spread |
|---|---:|---:|---:|
| VWCE | 168.04 | 168.04 | 0.0% |
| EUNA | 4.9116 | 4.9116 | 0.0% |
| SXR8 | 722.42 | 722.42 | 0.0% |
| L0CK | 10.932 | 10.932 | 0.0% |

The original two-provider observations are now preserved in:

```text
state/price_evidence_cache/ucits_close_evidence_2026-08-05.json
```

Replay requires exact matching on report date, basket ID, ticker, ISIN, MIC, currency, provider set and provider symbol. The cache also binds the source workflow SHA, GitHub Actions artifact ID/digest and original qualification-member SHA-256.

## Important historical-series finding

A later Yahoo historical query on 2026-08-08 returned adjusted values for some of the same 2026-08-05 ETF dates that differed materially from the accepted report-time closes. This proves that a later mutable provider history must not silently rewrite the economic facts used in an already-issued report.

For replay of an accepted report, the immutable report-time evidence set is therefore authoritative. A later live historical query is diagnostic/verification evidence only unless a separately governed corporate-action normalization process explicitly supersedes the report-time record.

## Input/state contract

Implemented:

- `pricing/accepted_close_evidence_cache.py`
- `pricing/boerse_frankfurt_historical_close.py`
- replay routing in `pricing/build_current_session_close_results_v2.py`
- immutable evidence file `state/price_evidence_cache/ucits_close_evidence_2026-08-05.json`

The replay loader rejects:

- wrong report date;
- wrong basket identity;
- wrong ISIN/MIC/currency/ticker identity;
- missing or unexpected provider set;
- missing provider symbol;
- non-positive close;
- provider close-date mismatch;
- spread beyond the accepted tolerance;
- incomplete source workflow/artifact/hash provenance.

## Output contract

The existing `ucits_price_provider_qualification_v2` compatibility surface is preserved.

A successful replay still requires:

```text
funded_line_count=4
funded_consensus_count=4
funded_identity_anchor_count=4
report_pricing_gate_passed=true
```

Provider rows reproduced from accepted evidence are explicitly labeled:

```text
retrieval_mode=immutable_report_time_evidence_cache
```

They are not misrepresented as new live observations.

## Operational runbook

Isolated CI workflow:

```text
.github/workflows/validate-etf-eu-replay-safe-pricing.yml
```

Successful evidence run:

```text
workflow_run_id=31254153417
job_id=93094895139
conclusion=success
```

The successful job proved:

- replay adapters compile;
- deterministic exact-date tests pass;
- cache tamper/identity tests pass;
- the exact 2026-08-05 accepted close reproduces for all four funded positions;
- 4/4 funded two-provider consensus is preserved;
- 4/4 identity anchors are preserved;
- exact source workflow and Actions-artifact provenance is present;
- no portfolio or ledger mutation occurs;
- no email is sent.

## Governance / assurance boundary

`implementation_operations` has completed the replay-safety implementation and machine-evidence package.

This work package alone does not issue `GOVERNANCE_PASS_PRE_SEND`. The next full governed package must bind the resulting replay-safe pricing artifact into the exact report manifest and allow `governance_release_assurance` to independently verify report/state/price equality before transport becomes reachable.

## Acceptance result

```text
deterministic_replay_tests=PASS
cache_tamper_tests=PASS
historical_live_endpoint_research=COMPLETE_PROVIDER_NOT_DURABLE
immutable_report_time_replay=PASS
funded_two_provider_replay=4/4
funded_identity_anchor_replay=4/4
pricing_gate=PASS
portfolio_mutation=false
ledger_write=false
email_delivery=false
implementation_status=RELEASE_CANDIDATE_READY
```
