# ETF EU replay-safe pricing decision — 2026-08-08

## Decision

For a historical Weekly ETF EU report that already passed the two-provider completed-close gate at report time, the immutable accepted report-time qualification record is authoritative replay evidence.

A later mutable provider history may be used as diagnostic or corporate-action review evidence, but it may not silently rewrite the closing prices used in the issued report.

## Reason

The 2026-08-05 accepted qualification artifact proved 4/4 funded two-provider consensus with zero spread. On 2026-08-08, Yahoo's historical series returned materially different values for some of those same ETF dates, while Börse Frankfurt's public `price_history` endpoint returned HTTP 200 with an empty object on hosted GitHub runners.

Relying on later provider history alone would therefore make report replay non-deterministic and could retroactively change portfolio valuations.

## Stable contract

Historical replay is allowed only when all of the following match exactly:

- report date;
- basket ID;
- ticker;
- ISIN;
- MIC;
- currency;
- independent provider set;
- provider symbol;
- original accepted close date and close;
- original agreement tolerance and PASS;
- source workflow run ID and head SHA;
- source GitHub Actions artifact ID and digest;
- original qualification-member SHA-256.

Cached observations must be labelled as immutable report-time replay evidence and not as new live observations.

## Current evidence

```text
report_date=2026-08-05
source_workflow_run_id=31051399761
source_run_id=20260805_31051399761_1
source_workflow_head_sha=476579ecc0644250d7d12a8f69784a279118d389
actions_artifact_id=8948609199
actions_artifact_digest=sha256:631f90f24caabc271b1d290b519adf5c3e667cb717f35563f522d030cb49c55a
qualification_member_sha256=02ad0fa5dd431eebadf73c370b6ab9fdc85a570332667a26234ad0d1758611d4
funded_consensus=4/4
funded_identity_anchors=4/4
```

Replay implementation validation:

```text
workflow_run_id=31254153417
job_id=93094895139
conclusion=success
```

## Authority boundary

This decision does not authorize:

- portfolio mutation;
- trade execution;
- a hard position-weight cap;
- report delivery;
- email transport;
- delivery confirmation.

It governs pricing lineage and deterministic historical replay only.
