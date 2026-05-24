# Weekly ETF production run request

requested_at_utc: 2026-05-24T00:00:00Z
requested_run_date: 2026-05-24
mode: production-validation
note: Validate ETF pricing-lineage Phase 1B immutable run identity, explicit audit/runtime paths, run manifest wiring, and artifact commit-back.

## Validation targets

- PRICING_AUDIT_PATH_OK
- LANE_ARTIFACT_PATH_OK
- ETF_RUNTIME_STATE_OK
- ETF_RUN_MANIFEST_OK
- immutable price audit under output/pricing/
- run-scoped runtime state under output/runtime/
- run manifest under output/run_manifests/
