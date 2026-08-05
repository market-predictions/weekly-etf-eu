# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-08-05
repository=market-predictions/weekly-etf-eu
operating_mode=production_with_independent_release_assurance
cross_project_governance_role=interim_canonical_host
control_plane_repository_status=USER_ACTION_REQUIRED
```

## Governance baseline

The Weekly ETF EU repository now has an enforced two-role governance model:

```text
implementation_role=implementation_operations
assurance_role=governance_release_assurance
user_interface=single_coordinated_project_stream
enforcement_maturity=LEVEL_4_POST_ACTION_INDEPENDENT_CONFIRMATION
```

The pre-send workflow creates an independent release-assurance record, binds the exact source SHA and Dutch/English artifact hashes, rejects incomplete or self-certified evidence, and blocks guarded transport unless assurance returns `PASS`. Delivery confirmation remains dependent on independent inbox receipt and production closeout evidence.

The repository also temporarily hosts the cross-project standard and adoption register until `market-predictions/control-plane` is created.

## Official protected portfolio

```text
VWCE_shares=151
EUNA_shares=1526
SXR8_shares=10
cash_eur=60439.44
current_nav_eur=99937.41
official_position_count=3
portfolio_state_sha256=6642334558818e630f0b22a2500ef44b2489ff237aacca638e81f184c165aa6f
trade_ledger_sha256=718f0681fe0d1162f9a91c34aa90489eb8566aecb06c12a1a2d9ad251be3e87c
portfolio_mutation=false
ledger_write=false
```

## Latest validated expanded report baseline

```text
report_date=2026-08-03
controlled_line_count=13
priced_line_count=13
funded_consensus=3/3
pricing_gate_passed=true
report_suffix=260803_05
run_id=20260803_30860298693_1
nl_pages=12
en_pages=11
email_delivery=false
```

The 2026-08-03 package contains current closing-price evidence for 13 controlled lines and an unexecuted model-expansion proposal. It is historical strategy context for the next run and is not automatic current-price truth.

## Model expansion proposal

```text
proposed_position_count=5
VVSM_proposed_shares=168
L0CK_proposed_shares=956
projected_cash_eur=35477.44
projected_cash_weight_pct=35.563945
proposal_applied=false
real_broker_execution=false
```

The proposal is not portfolio authority. A fresh governed run must reconstruct current state, pricing, selected portfolio mode, validator expectations, report artifacts, delivery authority, and receipt evidence.

## Known implementation defects awaiting repair

- PR #72 contains a stale production validator that assumes exactly three positions and a blocked Stage-1 state.
- `.github/workflows/generate_predictions.yml` is a legacy FX scheduler and is not a valid Weekly ETF EU production entry point.
- No fresh governed end-to-end report delivery has yet been completed after activation of the new governance gate.

## Cross-project governance rollout

Canonical interim files:

```text
control/CROSS_PROJECT_TWO_ROLE_GOVERNANCE_STANDARD_V1.md
control/CROSS_PROJECT_GOVERNANCE_ADOPTION_REGISTER.md
control/PROJECT_GOVERNANCE_BOOTSTRAP_TEMPLATE.md
control/PROJECT_PROMPT_GOVERNANCE_CLAUSE.md
control/CROSS_PROJECT_GOVERNANCE_ROLLOUT_WORK_PACKAGE_20260805.md
```

Current rollout scope:

```text
weekly_etf_eu=enforced
weekly_etf=bootstrap_rollout
weekly_index=bootstrap_rollout
weekly_fx=bootstrap_rollout
control_plane_repository=not_created
```

## Authority boundary

```text
portfolio_mutation=false
ledger_write=false
execution_authority=false
model_activation_authority=false
delivery_authority=false
email_delivery=false
cross_project_standard_authority=shared_role_separation_only
```
