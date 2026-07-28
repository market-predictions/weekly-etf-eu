# ETF EU Cutover Evidence Contract V1

**Status:** cutover-readiness control; no activation authority  
**Scope:** candidate identity, product documents, valuation and tradability evidence  
**Initial review date:** 2026-07-28

## 1. Purpose

The synchronization shadow can size a theoretical portfolio using connectivity data, but a cutover candidate requires stronger evidence before it can become an activation package.

Each candidate is assessed on four independent grades:

1. `identity_grade` — exact fund, ISIN, venue, trading line and currency;
2. `document_grade` — UCITS/product structure plus an accepted KID/PRIIPs artifact;
3. `valuation_grade` — a completed and accepted valuation for the exact trading line, cross-checked against fund-level NAV where available;
4. `tradability_grade` — accepted bid/ask or equivalent spread evidence, observation timestamp, venue state and minimum displayed/quoted size.

A pass in one grade must never be used to infer a pass in another.

## 2. Evidence hierarchy

### Identity and documents

Preferred sources:

- issuer product page;
- issuer-hosted KID/PRIIPs PDF;
- official exchange instrument record;
- regulator or issuer prospectus.

Search snippets, third-party aggregators and generic statements that a document exists are not accepted substitutes for the exact product document when activation readiness is assessed.

### Valuation

A valuation-grade line observation requires:

- exact ISIN and venue line;
- currency;
- completed-close or timestamped executable-market observation;
- source timestamp and retrieval timestamp;
- no lookahead or intraday value mislabeled as a completed close;
- a source accepted by the cutover package.

An issuer NAV may validate fund-level value but does not by itself establish the market price of an EUR Xetra trading line.

### Tradability

Tradability-grade evidence requires:

- venue and instrument identity;
- timestamp during a declared market state;
- bid and ask, or an official spread/liquidity measure accepted by policy;
- relative spread calculation;
- displayed or guaranteed quote size sufficient for the simulated order or a documented staged-order rule;
- evidence age within the activation window.

Average daily traded value alone is not spread evidence.

## 3. Status values

Each grade is one of:

```text
pass
partial
fail
not_assessed
```

`partial` is informative but blocking for activation.

The candidate-level status is:

```text
shadow_eligible
cutover_evidence_incomplete
cutover_evidence_complete
blocked
```

`cutover_evidence_complete` requires all four grades to pass.

## 4. Current interpretation rules

- An official product page that states PRIIPs documentation is available changes the issue from `kid_missing` to `exact_kid_artifact_not_captured`; it does not produce a document-grade pass.
- An issuer-hosted exact KID PDF with matching ISIN produces a document-grade pass, subject to date and jurisdiction review.
- A current issuer NAV produces a fund-level valuation pass but not an exact EUR-line valuation pass.
- A Börse Frankfurt or Xetra page that exposes bid/ask only after authenticated real-time access confirms the availability mechanism, not the observed spread.
- Yahoo/yfinance completed closes and traded values remain connectivity evidence unless separately accepted by the activation policy.

## 5. Activation boundary

This contract and its evidence artifacts:

- do not recommend a transaction;
- do not grant portfolio mutation authority;
- do not grant funding or execution authority;
- do not write the trade ledger;
- do not authorize production delivery.

An activation package must reference an immutable evidence artifact in which every candidate intended for activation has `cutover_evidence_complete` status.

## 6. Required pre-activation capture

For each intended Xetra line, capture within the activation window:

1. completed previous trading-day close from an accepted source;
2. issuer NAV and date where available;
3. live or timestamped bid and ask;
4. relative spread;
5. bid and ask size or accepted quote-size parameter;
6. market state and observation timestamp;
7. exact KID/PRIIPs artifact and document date;
8. reviewer acceptance and expiry time.

If the evidence cannot be obtained programmatically, a controlled manual capture may be used only if the artifact records source, timestamp, reviewer and immutable file hash.