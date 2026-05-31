# Changelog — Phase 4 Close Engine Adapter Diagnostics

Date: 2026-06-01
Repository: `market-predictions/weekly-etf-eu`
Scope: generic UCITS close-price engine adapter diagnostics.

## Current issue

The Phase 4 generic close-price engine scaffold is present, but the official-source adapters needed clearer diagnostics before stable endpoint integration can be designed.

Before this change:

- Euronext / CSPX / XAMS had page evidence and endpoint hints, but no stable quote endpoint integrated.
- Deutsche Boerse / SXR8 / XETR found relevant page labels, but correctly refused to promote noisy page values to a close price.

## Files changed

```text
pricing/close_engine/adapters/euronext.py
pricing/close_engine/adapters/deutsche_boerse.py
```

## Change summary

### Euronext adapter

Added non-authoritative diagnostics for endpoint hints, current-path hints, search-quote hints, product-code presence, script count, page size and next-step metadata.

### Deutsche Boerse adapter

Added non-authoritative diagnostics for numeric candidate audits, rejection reasons, label offsets, script count, embedded quote-key hits, endpoint-like hints and next-step metadata.

## Authority impact

No authority was added. The close-observation layer remains evidence-only.

The following remain false:

```text
portfolio_mutation=false
production_delivery=false
funding_authority=false
valuation_authority=false
completed_session=false
```

Candidate close parsing remains blocked from valuation authority until a separate promotion layer validates source, date, close, currency, completed session, source lineage and staleness.

## Next action

Queue and verify the EU bootstrap workflow. Then inspect the persisted `ucits_close_observations_*.json` artifact for richer adapter diagnostics.
