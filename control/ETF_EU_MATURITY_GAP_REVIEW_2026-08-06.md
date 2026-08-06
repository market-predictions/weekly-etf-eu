# Weekly ETF EU maturity gap review — 2026-08-06

## Scope

This review compares `market-predictions/weekly-etf-eu` with the active `market-predictions/weekly-etf` donor environment. It distinguishes reusable operating patterns from product-specific assumptions. The Weekly ETF donor is not an allocation oracle for the EU portfolio; it is a reference implementation for fresh generation, state protection, bilingual packaging, validation, transport and receipt handling.

## Confirmed cross-product contamination

Both ETF repositories inherited an unrelated TwelveData FX generator:

- active workflow path: `.github/workflows/generate_predictions.yml`;
- root runner: `prediction.py`;
- output paths: `daily_outputs/latest` and `mt5_output/latest`;
- FX identity markers: `TWELVEDATA_API_KEY`, curated currency pairs, `FX_BACKTEST`, and DailyTradeBias instructions.

These assets are outside the Weekly ETF and Weekly ETF EU product boundaries. In Weekly ETF EU they are removed in the current remediation branch and a repository-boundary CI gate prevents recurrence. The donor Weekly ETF requires a separate cleanup PR for the same inherited defect.

## Allocation-rule correction

The donor Weekly ETF capital rules require a full weekly portfolio re-underwrite. They do **not** define:

- a universal 50% maximum position;
- a mandatory 35% cash reserve;
- a rule allowing 75% portfolio concentration.

The number 75 in the donor environment refers to a default minimum pricing-coverage percentage, not a position-size rule.

Weekly ETF EU therefore uses allocation lineage rather than an invented hard cap:

1. protected portfolio state and trade ledger are authoritative for a valuation-only run;
2. any share or cash mutation requires an explicit allocation decision;
3. report generation must preserve protected tickers, shares and cash unless such a decision exists;
4. market-driven concentration is disclosed as an observation;
5. allocator-created concentration without authorized lineage blocks release.

## Layer-by-layer comparison

### 1. Decision framework

**Weekly ETF**

- full portfolio is re-underwritten each cycle;
- cash, sells, replacements and additions are active decisions;
- no mandatory cash reserve;
- historical reports are context, not current-price authority.

**Weekly ETF EU**

- currently combines donor opportunity promotion, EU investability mapping, Stage-1 transition logic and long-horizon target-allocation context;
- before remediation, these layers could be mistaken for current mutation authority;
- current remediation establishes explicit precedence: allocation decision → protected state/ledger → valuation → donor opportunity state → historical context.

**Remaining gap**

- a single machine-readable weekly EU underwriting decision artifact must replace multiple partially overlapping allocator/transition surfaces.

### 2. Input/state contract

**Weekly ETF**

- one protected portfolio-state file;
- one trade ledger;
- fresh pricing and current report inputs;
- relatively direct lineage into report generation.

**Weekly ETF EU**

- protected EUR portfolio state and ledger;
- donor strategy import;
- UCITS identity and investability evidence;
- multi-provider completed-close pricing;
- macro/policy pack;
- transition and convergence artifacts.

**Remaining gap**

- the richer EU evidence stack is justified, but needs a canonical run-input manifest so every report binds one exact version of each source.

### 3. Output contract

**Weekly ETF**

- stable four-file bilingual package: Dutch HTML/PDF plus English HTML/PDF;
- release manifest and hashes;
- established client-facing structure.

**Weekly ETF EU**

- same intended four-file package;
- multiple preview, convergence and historical renderer paths still coexist;
- no single current candidate has yet completed all machine, visual and assurance gates.

**Remaining gap**

- designate one renderer and one release manifest schema as canonical; archive or disable alternative production paths.

### 4. Operational runbook

**Weekly ETF**

- mature fresh-generation and guarded-delivery route;
- still contains workflow sprawl and inherited FX contamination;
- recent real run artifacts exist.

**Weekly ETF EU**

- excessive workflow count with many one-off patch, recovery and diagnostic workflows;
- canonical scheduler exists, but historical send and preview workflows remain active or manually invokable;
- FX contamination was able to emit unrelated output.

**Remaining gap**

- workflow allowlist and retirement programme: one canonical generation workflow, one assurance workflow, one guarded transport workflow, one receipt-closeout workflow, bounded diagnostics.

### 5. Governance and release assurance

**Weekly ETF**

- proven delivery mechanics and package validation;
- formal two-role assurance maturity remains below the target control-plane level.

**Weekly ETF EU**

- stronger documented two-role governance;
- policy-bound release assurance is being implemented;
- operational evidence and canonical workflow wiring remain incomplete.

**Remaining gap**

- independent assurance must consume the exact policy, protected-state, pricing, visual-review, package and queue hashes before transport.

### 6. Delivery and receipt

**Weekly ETF**

- Outlook transport and self-copy receipt mechanism are established;
- production receipt evidence exists for recent runs, although control documents need freshness repairs.

**Weekly ETF EU**

- historical deliveries exist, but the current remediated package has not been sent;
- SMTP success cannot be treated as delivery confirmation;
- current workflow must end in independent inbox receipt evidence and a closeout manifest.

**Remaining gap**

- one canonical receipt verifier and immutable post-send closeout receipt.

## Maturity status

| Layer | Current maturity | Release target |
|---|---|---|
| Decision framework | explicit precedence added; weekly decision still fragmented | one canonical weekly underwriting decision |
| Input/state contract | strong evidence depth; lineage now enforced | one immutable run-input manifest |
| Output contract | four-file target established; renderer paths fragmented | one canonical renderer and manifest |
| Operational runbook | FX path removed; workflow sprawl remains | allowlisted production workflows only |
| Governance/assurance | policy-bound pre-send gate under test | independent hard CI gate |
| Delivery/receipt | current candidate unsent and unconfirmed | guarded send plus independent receipt closeout |

## Required maturation sequence

1. Complete and pass product-boundary and allocation-lineage CI.
2. Produce a fresh four-file ETF EU candidate using current completed closes.
3. Validate portfolio identity, pricing completeness, bilingual parity and visual quality.
4. Retire or disable non-canonical generation/send workflows.
5. Build a policy- and hash-bound delivery queue only after review approval.
6. Run independent pre-send assurance.
7. Execute guarded transport.
8. Confirm receipt independently and write the closeout manifest.

Until step 8 completes, status must not exceed `ACTION_EXECUTED_UNVERIFIED`; before transport, the current status remains `RELEASE_CANDIDATE_READY` at most.
