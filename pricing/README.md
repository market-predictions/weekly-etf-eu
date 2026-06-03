# UCITS Pricing Interface

This directory contains the shared pricing spine for UCITS end-of-day close retrieval.

The interface is deliberately provider-neutral. Adapter workstreams should implement this contract without mutating portfolio state, promoting candidates, rendering PDFs, or sending email.

## Core objects

- `PriceIdentity` — ISIN-first trading-line identity: `registry_id`, `isin`, `exchange`, `exchange_ticker`, `trading_currency`, `provider_symbol`.
- `SourceLineage` — source metadata: `source_id`, `provider_name`, `license_class`, `authority_tier`, `observed_at_utc`, optional `raw_evidence_path`, optional `raw_evidence`.
- `PriceResult` — normalized provider output for one completed-session close.
- `PriceRequest` — provider-agnostic request wrapper.
- `PriceSource` — abstract provider interface with `fetch_eod_close(request) -> PriceResult`.

## Standard result statuses

Resolved:

```text
observed
```

Unresolved:

```text
unresolved_no_data
unresolved_provider_error
unresolved_dependency_missing
unresolved_not_configured
```

A resolved result must contain:

```text
observed_date
close
currency
completed_session=true
```

An unresolved result must not contain `close`.

## License classes

```text
exchange_public
provider_free_personal
provider_paid
issuer_public
unknown
```

## Authority tiers

```text
exchange_official
candidate_valuation_source
diagnostic_candidate_source
non_authoritative_connectivity_only
unknown
```

These strings describe evidence quality. They do not by themselves create `valuation_grade=true`. The later agreement-gate workstream must decide whether multiple sources can promote a row.

## Adapter implementation rule

Every provider adapter should:

1. subclass `PriceSource`;
2. accept a `PriceRequest`;
3. return `PriceResult.observed(...)` when a completed-session close is available;
4. return `PriceResult.unresolved(...)` for missing credentials, provider errors, missing data, currency/date uncertainty, or unsupported trading lines;
5. preserve raw source evidence either in `raw_evidence` or as a path in `raw_evidence_path`;
6. never write portfolio state, valuation history, output reports, PDFs, delivery receipts, or email.

## Config-driven selection

`SourceSelection.from_policy_row(...)` reads a policy row with `source_order` entries and returns providers in configured order via `select_sources(...)`.

`first_resolved_or_last_unresolved(...)` tries providers in order and returns the first resolved result, otherwise the last typed unresolved result. This is only selection plumbing; it is not a valuation-grade agreement gate.

## Test command

```bash
python -m pytest tests/test_pricing_interface.py
```

The tests use only fake/static providers and local fixtures. They must not perform network calls.
