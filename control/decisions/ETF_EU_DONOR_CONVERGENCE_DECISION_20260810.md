# Decision — Weekly ETF EU Donor Convergence

Date: 2026-08-10  
Decision ID: `ETF-EU-DONOR-CONVERGENCE-20260810`

## Decision

Weekly ETF EU will converge on mature Weekly ETF donor **behavior** for discovery, capital re-underwriting, recommendation memory, normalized runtime state and routine-production discipline while retaining EU/UCITS product authority.

The repository will not clone or import U.S. portfolio state or U.S. investability assumptions.

## Authority correction

The historical transition policy and all allocator variants derived from it are non-authoritative for current allocation unless a specific value is separately reauthorized by a current decision.

Specifically, the following cannot act as current Weekly ETF EU allocation controls merely because they exist in transition artifacts:

- 35% minimum cash;
- 15% maximum new ETF/direct position;
- fixed 50% cash-first scenario;
- 25% gross turnover ceiling;
- 18% semiconductor theme cap;
- 15% cybersecurity theme cap;
- historical maximum-position count;
- donor target weights.

No replacement numerical caps are created by this decision.

## Embedded-exposure decision

Measured embedded thematic exposure from incomplete holdings evidence is an analytical lower bound. It is not a portfolio minimum, target or cap.

## Broker-neutrality decision

Model investability/fundability remains broker-neutral. Account-specific broker permission is required only for real execution.

## Historical Stage-1 decision

The two-theme Stage-1 selection remains historical activation provenance. It does not freeze future weekly allocation review to the same two exposures.

## Canonical routine decision

`.github/workflows/run-weekly-etf-eu-routine.yml` is the canonical routine-production workflow. Date-specific repair/probe/preview workflows are historical/diagnostic evidence unless another current decision explicitly promotes them.

## Assurance consequence

PR #84 remains frozen evidence with issue #87 PASS. The broader convergence work is performed on `agent/etf-eu-donor-convergence-v1` and requires a new exact-head independent assurance verdict before merge/release.

## Principal-decision boundary

This decision resolves stale/shadow authority and architecture routing. It does not authorize:

- a new hard portfolio cap;
- portfolio/ledger mutation;
- real broker execution;
- recipient changes;
- report delivery.

Any new hard allocation constraint requires a separate explicit decision with rationale.
