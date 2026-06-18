# ETF EU Donor-Port Strategy Decision — 2026-06-18

## Decision

Do **not** fresh-clone `market-predictions/weekly-etf` over `market-predictions/weekly-etf-eu`.

Keep `market-predictions/weekly-etf-eu` as the EU/UCITS source-of-truth repository.

Use `market-predictions/weekly-etf` as an upstream donor repository for mature report/runtime/bilingual/macro/delivery safeguards.

Port mature layers in controlled slices and adapt them to EU-specific UCITS identity, pricing and investability contracts.

## Core strategy

```text
weekly-etf-eu remains the product authority for EU/UCITS state
weekly-etf becomes a donor for mature implementation patterns
port behavior, not U.S. assumptions
```

## Reason

`weekly-etf` is materially further ahead in:

```text
runtime-derived report rendering
English canonical + Dutch companion delivery pattern
bilingual report-quality safeguards
macro/geopolitical client-safe report surface
leakage/compliance validators
report polish and decision clarity
strict delivery HTML safeguards
pricing/state/run-manifest direction
```

But `weekly-etf` is a U.S. ETF product. Re-cloning it over the EU repo would risk reintroducing U.S. ETF assumptions as EU truth.

The EU repo has now established critical EU-specific foundations:

```text
ISIN-first UCITS identity
UCITS symbol registry
UCITS identity validator
proxy-vs-investable separation
Dutch/EU investability boundaries
U.S. ETFs as research proxies only
direct Yahoo chart UCITS closing-price smoke path
```

Those foundations should not be overwritten.

## Authority rule

```text
Port behavior, not U.S. assumptions.
```

Permitted donor imports from `weekly-etf` include:

```text
runtime report rendering pattern
report polish and decision clarity logic
English canonical + Dutch companion pattern
bilingual parity validators
Dutch language quality validators
macro/client-surface leakage validators
strict HTML layout safeguards
shadow PDF/render dry-run patterns
```

Disallowed donor imports without explicit EU adaptation:

```text
U.S. portfolio state as EU truth
U.S.-listed ETFs as EU investable holdings
U.S. pricing symbols as substitutes for UCITS exchange-line prices
U.S. recommendation/funding authority
production delivery settings
recipient activation
secrets/mail transport configuration
```

## Current product evidence

The EU repo has proven that direct Yahoo chart endpoint data can provide usable UCITS exchange-line daily closes for the first tested symbols:

```text
CSPX.L
SXR8.DE
```

This is source evidence only. It is not valuation-grade authority, not funding authority, not portfolio mutation authority, and not delivery authority.

## Roadmap

```text
WP14E-FIX — Direct Yahoo chart endpoint for UCITS closes                 completed / pending control closeout
WP14F     — First ETF EU draft report from UCITS identity and closes     next
WP14G     — Port weekly-etf runtime/bilingual/report quality layers      after draft baseline
WP14H     — ETF EU delivery/PDF dry run, no recipients                   later
Delivery  — blocked until explicit receipt/manifest authority            later
```

## WP14F scope

WP14F must produce the first markdown EU ETF draft report using:

```text
config/ucits_symbol_registry.yml
output/pricing/etf_eu_ucits_closing_price_smoke_20260618_000000.json
```

It must disclose:

```text
UCITS identity
ISIN
exchange ticker
trading currency
Yahoo chart source symbol
latest close date
latest close
U.S. proxy labels as research-only
source/freshness limitations
```

WP14F remains review-only.

## Standing boundaries

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
candidate_promotion=false
recipient_activation=false
email_delivery=false
pdf_generation=not_required_for_wp14f
wp14_authority=false
```

## Consequence

Future sessions should not ask whether to reclone `weekly-etf` as the main strategy unless this decision is explicitly reopened.

Future sessions should begin from the stated roadmap:

```text
first EU markdown draft
then donor-port mature runtime/bilingual/report quality layers
then shadow PDF/delivery dry run
then explicit delivery authorization only after receipt/manifest gates exist
```
