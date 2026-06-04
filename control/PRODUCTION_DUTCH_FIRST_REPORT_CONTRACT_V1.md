# Production Dutch-First Report Contract V1

## Purpose

This contract defines the next maturity phase after the bootstrap candidate/pricing-surface report: a Dutch-first, production-quality EU/UCITS client report.

It is **not** a delivery contract and does not enable email, PDF generation, portfolio mutation, valuation-grade promotion, or candidate promotion.

This work can proceed as design, renderer structure, validator logic and tests while final workflow integration waits for the shadow workflow and wrapper path to be verified.

## Required separation

The production Dutch-first report phase must stay separate from:

```text
portfolio funding
portfolio mutation
PDF/email delivery
delivery receipt or manifest
candidate promotion to fundable
valuation-grade promotion
main workflow switch before shadow verification
```

## Four-layer operating model

### 1. Decision framework

The report may explain candidate quality, pricing evidence, missing gates and next decisions.

It must distinguish:

```text
funded holding
fundable candidate
verified candidate not funded
research proxy
blocked instrument
```

Current bootstrap status remains:

```text
no funded UCITS holdings
no fundable candidates
research and pricing evidence only
```

### 2. Input/state contract

The report may read:

```text
output/etf_eu_portfolio_state.json
config/ucits_symbol_registry.yml
config/ucits_benchmark_proxy_map.yml
output/pricing/ucits_pricing_preflight_*.json
output/pricing/ucits_valuation_prices_*.json
```

The report must not treat markdown text, inherited U.S. outputs or U.S. ETF tickers as EU portfolio state.

### 3. Output contract

The Dutch report is the primary client-facing report.

The English report is a companion/operator-facing report unless explicitly changed later.

The Dutch report must be independently written for Dutch/EU clients. It must not be a mechanical translation of a U.S.-ETF report.

The Dutch report must include a production-maturity layer before the delivery-status block with these visible concepts:

```text
Nederlandse hoofdrapportage
primaire clientrapportage
geen gefinancierde UCITS-posities
geen koopadvies
geen portefeuille-mutatie
geen productielevering
geen delivery receipt
```

The English companion must state that the Dutch report is primary and the English version is an operator companion.

### 4. Operational runbook

During this work package, implementation may add:

```text
contract text
renderer sections
validator strict mode
tests
```

It must not:

```text
switch the main workflow
claim the shadow workflow passed
create a production report delivery
render a PDF
send email
create a delivery receipt
mutate portfolio state
promote candidates to fundable
```

## Required report sections before production quality

1. **Status and authority summary**
   - cash-only or funded-state status;
   - production/delivery status;
   - funding authority status;
   - valuation-grade status summary.

2. **Portfolio state**
   - cash;
   - invested market value;
   - total NAV;
   - funded UCITS positions;
   - explicit statement when there are no funded positions.

3. **UCITS candidate / holding table**
   - ISIN-first identity;
   - fund name;
   - provider;
   - exchange;
   - ticker;
   - trading currency;
   - investability status;
   - fundability status;
   - U.S. proxy as research-only if shown.

4. **Production report maturity / Productierapport-volwassenheid**
   - Dutch report primacy;
   - current client decision status;
   - portfolio impact;
   - pricing-quality status;
   - fundability gate status;
   - delivery boundary.

5. **Agreement-gate pricing surface**
   - source agreement status;
   - observed date;
   - close;
   - currency;
   - source IDs;
   - staleness / blockers;
   - explicit no-valuation-authority statement when not valuation-grade.

6. **Fundability gate status**
   - which required gates are passed/missing;
   - no automatic promotion from pricing success;
   - no funded position unless separate promotion decision exists.

7. **Risk and role discussion**
   - why each candidate is being watched;
   - role versus U.S. research proxy;
   - key risks and overlap.

8. **Next actions**
   - missing source evidence;
   - missing broker/liquidity checks;
   - missing KID/PRIIPs or issuer verification;
   - decision items before funding.

9. **Delivery status**
   - explicit whether report is shadow/bootstrap/non-delivered;
   - no delivery claim without manifest/receipt.

## Validator expectations

Validators should support a transitional model:

- default mode remains compatible with the existing bootstrap report;
- strict production-Dutch-first mode requires the production-maturity layer;
- if the production-maturity layer is present, validators must confirm it is client-safe;
- strict mode must validate both Dutch primary and English companion outputs.

## Hard prohibitions

The report must not say or imply:

```text
buy recommendation
funded holding
fundable candidate
valuation authority
delivery completed
PDF generated
email sent
delivery receipt exists
```

unless the corresponding state, validator and receipt/manifest layer exists and a later decision log entry explicitly changes the authority boundary.

## Current authority boundaries

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
no delivery receipt
no candidate promotion to fundable
```

## Integration gate

This work package can add design and tests now.

Final integration waits until:

1. WP1 shadow workflow is verified end-to-end.
2. WP4 main workflow wrapper switch is reviewed and ready.
3. Production Dutch-first report validators pass in strict mode.
4. Delivery remains disabled unless a later delivery work package explicitly changes it.
