# ETF EU WP-SYNC-11 — Stooq Connectivity Evidence

## Scope

Determine whether the Weekly ETF EU GitHub Actions pricing workflow failed because:

1. a Stooq API key was missing;
2. the tested symbols were unsupported; or
3. Stooq blocked unattended HTTP clients before authentication and symbol lookup.

## Corrective implementation

The WP-SYNC-11 branch now:

- classifies Stooq HTTP-200 non-CSV responses explicitly;
- distinguishes browser verification, API-key requirement, daily-limit exhaustion, missing symbols, malformed schemas and valid completed-close CSV;
- accepts an optional `STOOQ_API_KEY` without logging its value;
- probes both `stooq.com` and `stooq.pl`;
- uses `AAPL.US` as a known positive control before testing ETF symbols;
- stops repeatedly querying Stooq after a runner-level browser challenge is established.

Relevant files:

- `pricing/ucits_close_price_multi_source_v2.py`
- `pricing/build_ucits_close_price_validation_basket_results.py`
- `tools/probe_stooq_connectivity.py`
- `.github/workflows/probe-stooq-connectivity.yml`

## Live test evidence

### Probe run 3

```text
run_id=30819868668
job_id=91706780127
artifact_id=8858361516
artifact_sha256=69265ae81355474aadfa30364df7e89b11ecb6c074480ff7cbecb8fd969d2ca6
conclusion=success
api_key_present=false
valid_csv_responses=0
determination=github_actions_blocked_by_stooq_browser_verification
```

### Probe run 4 — final cached adapter

```text
run_id=30820114314
job_id=91707616438
artifact_id=8858463814
artifact_sha256=0a7859d2f4cab74a83280a821e3671408e073693b079626fbe2151fdb580c51c
conclusion=success
api_key_present=false
valid_csv_responses=0
determination=github_actions_blocked_by_stooq_browser_verification
```

## Tested matrix

Endpoints:

- `https://stooq.com/q/d/l/`
- `https://stooq.pl/q/d/l/`

Symbols:

- `AAPL.US` — positive control;
- `VWCE.DE` — funded Xetra line;
- `EUNA.DE` — funded Xetra line;
- `SXR8.DE` — funded Xetra line;
- `IWDA.UK` — cross-venue ETF diagnostic.

Every endpoint/symbol combination returned:

```text
http_status=200
content_type=text/html
response_classification=browser_verification_challenge
valid_csv=false
```

The returned page required JavaScript proof-of-work browser verification. Because the positive control failed identically to all ETF symbols, the response occurred before meaningful symbol-coverage testing.

## Determination

```text
stooq_api_key_currently_proven_necessary=false
stooq_api_key_currently_proven_sufficient=false
github_hosted_actions_compatibility=false
exact_etf_line_coverage=not_testable_behind_browser_challenge
production_provider_status=unavailable_on_github_hosted_runner
```

Historically, Stooq required an API key for historical CSV downloads. The current GitHub Actions failure is earlier in the request path: both Stooq domains impose JavaScript browser verification. Adding a key cannot be represented as a verified fix without a successful positive-control test.

## Authority decision

- Do not promote Stooq as the primary production close provider.
- Do not ask the user to disclose a key in chat.
- Retain optional `STOOQ_API_KEY` support only for a controlled future experiment.
- Use an officially supported API provider for routine production pricing.
- Stooq may remain diagnostics-only until its positive control returns valid CSV from the production runner.

No portfolio, ledger, report delivery or recipient state was changed by this investigation.
