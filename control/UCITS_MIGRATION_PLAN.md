# UCITS Migration Plan

## Strategic direction as of 2026-06-18

Status: adopted.

The ETF EU repository will **not** be recloned from `market-predictions/weekly-etf`.

Instead, the adopted development strategy is:

```text
keep market-predictions/weekly-etf-eu as the EU/UCITS source-of-truth repo
use market-predictions/weekly-etf as an upstream donor for mature report/runtime/bilingual/macro/delivery safeguards
port mature layers in controlled slices
connect those layers to EU-specific UCITS identity, pricing and investability contracts
```

This preserves the EU-specific work already completed while avoiding a slow rebuild of mature report capabilities that already exist in `weekly-etf`.

## Why not fresh-clone `weekly-etf` again?

A fresh clone would import mature U.S. report infrastructure quickly, but it would also reintroduce U.S. ETF assumptions as dominant defaults.

That is not acceptable because the EU product must remain:

```text
ISIN-first
UCITS-first
Dutch/EU-client scoped
U.S. ETFs as research proxies only
EU portfolio state separate from U.S. portfolio state
UCITS exchange-line pricing based on EU trading lines
```

A fresh clone risks losing or bypassing:

```text
UCITS symbol registry
UCITS identity validator
proxy-vs-investable separation
Dutch/EU investability boundaries
direct Yahoo chart UCITS closing-price smoke path
no-U.S.-ETF-as-holding boundary
```

## Why not continue the old EU roadmap unchanged?

The prior roadmap was useful for control-plane safety, but it became too slow and review-heavy after UCITS identity and first UCITS pricing access were proven.

The next phase must be **product assembly**:

```text
price UCITS lines
build first EU draft report
port mature bilingual/runtime/report polish from weekly-etf
port leakage and client-surface gates
perform shadow PDF/render dry run only after markdown report quality is acceptable
enable delivery only after explicit receipt/manifest path exists
```

## Donor-port rule

`market-predictions/weekly-etf` is the donor repository for mature implementation layers.

Allowed donor layers include:

```text
runtime-derived English/Dutch report rendering
report polish and decision clarity logic
bilingual parity and Dutch language quality validators
macro/geopolitical client-safe report surface
macro/thesis leakage validators
ticker linkification and delivery HTML strict-layout safeguards
report-quality tests
delivery/PDF dry-run mechanics, only after EU report draft quality is acceptable
```

Disallowed donor imports without EU adaptation:

```text
U.S. ETF portfolio state as EU truth
U.S.-listed ETFs as EU investable holdings
U.S. pricing symbols as substitutes for UCITS exchange-line prices
U.S. recommendation/funding authority
production delivery settings
recipient/secrets/mail transport configuration
```

## Phase 0 — repo clone

Status: done.

`market-predictions/weekly-etf-eu` was cloned from `market-predictions/weekly-etf`.

## Phase 1 — authority separation

Status: substantially complete / continue hardening as needed.

Completed or established:

```text
EU/UCITS control layer
UCITS review contract
investability rules
symbol registry contract
UCITS symbol registry
EU authority boundaries
no-U.S.-ETF-as-holding discipline
```

Remaining hardening may continue only when it directly supports report assembly or pricing integrity.

## Phase 2 — workflow isolation

Status: partially complete / keep blocked for delivery.

Tasks:

```text
disable or avoid inherited production send assumptions
preserve EU-specific workflow/run queue naming
keep production delivery blocked
keep recipient activation blocked
keep delivery receipt requirements explicit
```

Do not prioritize delivery until the first EU report draft is acceptable.

## Phase 3 — UCITS instrument registry

Status: active baseline complete enough for first pricing/report draft.

Completed or established:

```text
ISIN-first UCITS registry
proxy-to-UCITS candidate mapping
trading-line metadata
pricing_symbol_yahoo fields
identity validator and unsafe-state fixtures
```

Remaining work:

```text
expand UCITS universe after first draft report
complete KID/PRIIPs/liquidity/TER fields as needed
harden exchange-line mapping only where pricing/report gaps appear
```

## Phase 4 — pricing migration

Status: first live source path proven.

Completed:

```text
direct Yahoo chart endpoint returns usable daily closes for CSPX.L and SXR8.DE
latest non-null close logic implemented in smoke fetcher
pending pricing symbols are skipped clearly
U.S. proxy substitution remains blocked
```

Next pricing tasks:

```text
commit and preserve the live smoke artifact
promote direct Yahoo chart endpoint from smoke path into the EU report input/state path
keep Yahoo as source evidence, not automatic valuation-grade authority
add source/freshness disclosure to report draft
expand symbol coverage only after first draft exists
```

## Phase 5 — first EU report draft

Status: next product milestone.

Package:

```text
WP14F — First ETF EU draft report from UCITS identity and closing-price smoke data, review-only
```

Goal:

```text
produce the first markdown EU ETF report draft using UCITS registry and real UCITS close data
```

Boundaries:

```text
review-only
no production delivery
no email
no PDF requirement yet
no portfolio mutation
no candidate funding/promotion authority
```

The first draft report must visibly disclose:

```text
UCITS instrument identity
ISIN
exchange ticker
trading currency
Yahoo chart source symbol
latest close date
latest close
U.S. proxy labels as research-only
pricing source/freshness limitations
```

## Phase 6 — port mature report/runtime/bilingual layer

Status: planned immediately after first EU draft report or in parallel if scoped tightly.

Package:

```text
WP14G — Port weekly-etf bilingual/runtime report polish into weekly-etf-eu
```

Scope:

```text
runtime report rendering pattern
English canonical + Dutch companion pattern
bilingual parity safeguards
Dutch language quality gates
report decision clarity polish
macro/client-surface leakage guards where applicable
```

Rule:

```text
Port behavior, not U.S. assumptions.
```

Every imported layer must read EU-specific state/artifacts and must preserve UCITS/proxy separation.

## Phase 7 — shadow PDF / delivery dry run

Status: later.

Package:

```text
WP14H — ETF EU delivery/PDF dry run, no recipients
```

Scope:

```text
HTML/PDF render dry run
strict-layout validation
manifest-only delivery evidence
no recipient activation
no live send
no delivery success claim
```

## Phase 8 — production delivery enablement

Status: blocked.

Delivery can be enabled only after:

```text
EU markdown report quality passes
bilingual parity gates pass
Dutch language gates pass
UCITS pricing/freshness disclosure is stable
PDF/HTML dry run passes
recipient policy exists
secrets policy exists
a real delivery receipt/manifest path exists
explicit control-layer delivery authorization is recorded
```

## Immediate roadmap summary

```text
WP14E-FIX — direct Yahoo chart endpoint for UCITS closes                 completed/pending control closeout
WP14F     — first ETF EU draft report from UCITS closes                  next
WP14G     — port weekly-etf runtime/bilingual/report quality layers      next after draft baseline
WP14H     — shadow PDF/delivery dry run, no recipients                   later
Delivery  — blocked until explicit receipt/manifest authority            later
```
