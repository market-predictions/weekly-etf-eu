# Production Dutch-First Report Contract V1

## Purpose

This contract defines the next maturity phase after the bootstrap pricing-surface shadow workflow: a Dutch-first production-quality EU/UCITS report.

It is not a delivery contract and does not enable email, PDF generation, portfolio mutation, or candidate promotion.

## Required separation

The production Dutch-first report phase must stay separate from:

```text
portfolio funding
portfolio mutation
PDF/email delivery
delivery receipt or manifest
candidate promotion to fundable
```

## Report authority model

The Dutch report is the primary client-facing report.

The English report is a companion/operator-facing report unless explicitly changed later.

The Dutch report must be independently written for Dutch/EU clients. It must not be a mechanical translation of a U.S.-ETF report.

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

4. **Agreement-gate pricing surface**
   - source agreement status;
   - observed date;
   - close;
   - currency;
   - source IDs;
   - staleness / blockers;
   - explicit no-valuation-authority statement when not valuation-grade.

5. **Fundability gate status**
   - which required gates are passed/missing;
   - no automatic promotion from pricing success;
   - no funded position unless separate promotion decision exists.

6. **Risk and role discussion**
   - why each candidate is being watched;
   - role versus U.S. research proxy;
   - key risks and overlap.

7. **Next actions**
   - missing source evidence;
   - missing broker/liquidity checks;
   - missing KID/PRIIPs or issuer verification;
   - decision items before funding.

8. **Delivery status**
   - explicit whether report is shadow/bootstrap/non-delivered;
   - no delivery claim without manifest/receipt.

## Hard prohibitions

The report must not say or imply:

```text
buy recommendation
funded holding
valuation authority
delivery completed
PDF generated
email sent
```

unless the corresponding state, validator, and receipt/manifest layer exists.

## Current next step

Run the manual shadow workflow:

```text
Weekly ETF EU pricing surface shadow validation
```

Only after that passes should the existing EU bootstrap workflow be switched to the wrapper path.
