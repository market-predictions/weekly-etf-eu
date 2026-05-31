# Changelog — Phase 4 Euronext Custom Instrument Diagnostics

Date: 2026-06-01
Repository: market-predictions/weekly-etf-eu
Scope: structured Euronext Drupal settings diagnostics in the generic UCITS close-price engine.

## Current issue

The previous product-page signal diagnostics showed that the Euronext product page exposes a typed Drupal settings object with a custom instrument block. The important identity fields were visible only in context snippets, not as a structured diagnostic object.

## Change

Updated pricing/close_engine/adapters/euronext.py.

The adapter now adds a structured custom_instrument_summary under product_page_signal_diagnostics.

The summary records selected instrument identity fields, selected surrounding context fields, expected registry identity, explicit registry-vs-page identity match booleans, and identity match counts.

## Authority impact

No price extraction was added. No close date, currency, completed session, valuation authority, funding authority, portfolio mutation, PDF generation, email delivery, or production delivery authority was added.

The date_restriction and nb_session fields are explicitly treated as diagnostic request/window hints only, not completed-session validation.

## Next action

Queue the bootstrap workflow and inspect the persisted close-observation artifact. If the custom instrument summary consistently matches registry identity, the next safe step is a typed Euronext quote-endpoint evidence fetcher derived from the settings object, still evidence-only and still without valuation-grade promotion.
