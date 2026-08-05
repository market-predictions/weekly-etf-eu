# Weekly ETF EU Review OS

This repository is the European / Dutch-client UCITS ETF review and controlled-delivery system derived from `market-predictions/weekly-etf`.

It is **not** a mechanical translation of the U.S. ETF model. U.S.-listed ETFs and inherited production artifacts are donor material only unless a current EU control contract explicitly grants authority.

## Canonical start sequence

For architecture, pricing, portfolio, report, workflow, governance or delivery work, read:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/ETF_EU_TWO_ROLE_GOVERNANCE_MODEL_V1.md`
5. the minimum relevant implementation files

## One project, two internal roles

The user works through one instruction stream and receives one consolidated project status. Internally, the project separates:

- `implementation_operations` — builds and repairs the release candidate;
- `governance_release_assurance` — independently reconstructs and certifies or rejects that candidate.

The implementation role may not certify its own work. The governance role may not mutate the candidate it certifies.

## Canonical routine production workflow

The routine generation and guarded-delivery path is:

```text
.github/workflows/run-weekly-etf-eu-routine.yml
```

Before SMTP delivery, the workflow must build and validate:

```text
output/quality/etf_eu_release_assurance_<run_id>.json
```

using:

```text
tools/build_etf_eu_release_assurance.py
tools/validate_etf_eu_release_assurance.py
```

A missing or failed governance decision blocks delivery.

## Completion semantics

The project distinguishes:

```text
RELEASE_CANDIDATE_READY
GOVERNANCE_PASS_PRE_SEND
TRANSPORT_SENT_UNVERIFIED
DELIVERY_CONFIRMED
```

A successful renderer, validator, workflow step or SMTP handoff is not by itself proof of delivered production output. Delivery is complete only after independent receipt evidence and production closeout.

## Current authority

Current portfolio, report and delivery authority is documented in `control/CURRENT_STATE.md`. Preferred EU state and output paths are registered in `control/SYSTEM_INDEX.md`.

## Inherited artifacts

The repository still contains inherited U.S., FX and experimental files. They are not Weekly ETF EU production entry points unless the live system index explicitly says otherwise. Legacy scheduled workflows must not be interpreted as current product automation merely because they still exist in the repository.

## Dependency discipline

Use `requirements.txt` for local/static validation. GitHub workflows may install their minimal dependencies directly where the relevant runbook permits it.
