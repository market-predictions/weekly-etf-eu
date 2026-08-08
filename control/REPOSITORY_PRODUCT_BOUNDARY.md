# Weekly ETF EU repository product boundary

## Product identity

This repository produces the **Weekly ETF EU** review only.

Valid production concerns include:

- EU-domiciled UCITS ETF and permitted ETC identity;
- EUR model-portfolio state and trade ledger;
- donor strategy translation into investable EU lines;
- completed-close pricing and macro/policy evidence;
- Dutch-primary and English-companion HTML/PDF reports;
- governed ETF EU transport and receipt closeout.

## Prohibited production concerns

The following are different products and must not have active runners, schedules or current outputs in this repository:

- daily or weekly FX predictions;
- TwelveData currency-pair generation;
- MT5 FX ranking packs;
- DailyTradeBias artifacts;
- `daily-fx` master prompts;
- generic `prediction.py` runners.

Git history preserves removed provenance. Current repository surfaces must remain product-pure.

## Machine enforcement

`tools/validate_etf_eu_repository_boundary.py` fails when prohibited root assets or FX execution tokens appear in active workflow files.

`.github/workflows/validate-etf-eu-repository-boundary.yml` runs the validator on pull requests, pushes to `main`, and manual dispatch.

## Canonical production workflows

The target allowlist is:

1. one fresh ETF EU candidate-generation workflow;
2. one independent release-assurance workflow;
3. one guarded ETF EU transport workflow;
4. one independent receipt-closeout workflow;
5. bounded diagnostic workflows with no delivery authority.

Historical patch, recovery and send workflows are not automatically canonical merely because they remain present. Their retirement is a separate controlled cleanup step.
