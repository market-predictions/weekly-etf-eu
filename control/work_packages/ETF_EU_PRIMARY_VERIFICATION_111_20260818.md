# ETF EU Pricing Authority Convergence — Issue #111

## Identity
```text
workpackage_id=ETF-EU-PRIMARY-VERIFICATION-111
claim_id=ETF-EU-PRIMARY-VERIFICATION-111
issue=111
repository=market-predictions/weekly-etf-eu
branch=agent/etf-eu-primary-verification-111
base_main_sha=0ea61c349b99dcd23f61fed1e72b46326d516914
owner_role=implementation_operations
status=REPAIR_VALIDATION
opened_at=2026-08-18T16:52:00+02:00
handover_ready_at=2026-08-18T17:31:00+02:00
h1_assurance=FAIL
h1_result=control-runtime-state:control/worker-results/ETF-EU-111-PR112-H1.json
h2_repair_request=control-runtime-state:control/handovers/ETF-EU-111-PR112-H2.json
repair_started_at=2026-08-18T21:34:55+02:00
repair_parent_candidate=e5329910d3364db97688c785d105a1a2d46f9db4
depends_on_report_issue=109
principal_decision_required=false
```

## Current issue
The fresh 2026-08-17 candidate is blocked because the prior pricing gate required two providers on the same date for every funded line even when one qualified provider had an exact requested-date close and the second provider was merely stale.

## Root cause
Stable UCITS trading-line identity, provider-specific symbol binding, current close selection and independent close verification were coupled into one live two-provider requirement. The project already owns stable ISIN-first trading-line identity in `config/ucits_symbol_registry.yml`.

## Decision framework
No change to instrument selection, portfolio construction, allocation methodology or re-underwriting. Pricing confidence must not become an allocation rule.

## Input/state contract
- funded universe remains authoritative from `output/etf_eu_portfolio_state.json`;
- stable source-independent trading-line identity remains authoritative from `config/ucits_symbol_registry.yml` using ISIN + ticker + exchange/MIC + currency;
- each provider actually used as primary or verifier must separately bind its configured provider symbol to the canonical symbol-registry line;
- one exact requested-date price from a statically bound qualified provider may be valuation-grade;
- additional exact same-date bound providers are verification evidence, not a universal liveness dependency;
- a broken/stale/missing verifier does not invalidate a correctly bound exact primary;
- a broken primary provider-symbol binding rejects that primary.

## Output contract
Funded lines classify explicitly:
- `fresh_exact_verified`: exact requested date plus at least one agreeing bound same-date verifier;
- `fresh_exact_unverified`: exact requested date from one qualified statically bound primary, with no usable same-date verifier;
- `provider_disagreement`: at least two bound exact requested-date providers outside tolerance; blocked;
- `no_exact_close`: no accepted bound provider on the requested date; blocked;
- `identity_binding_failed`: canonical trading-line identity cannot be established; blocked.

Both exact verified and exact unverified may be valuation-grade. No stale close may be relabeled fresh. The selected valuation price is the primary provider close, not a median blend. Client surfaces distinguish price-verification confidence from trading-line identity.

## Operational runbook
1. Validate the source-independent trading line against the canonical UCITS symbol registry.
2. Validate each configured provider symbol separately against that canonical line.
3. Fetch configured provider closes.
4. Reject a provider on explicit returned-symbol, venue or currency mismatch.
5. Consider only accepted prices on the exact requested report date for production selection.
6. Select the first exact accepted provider by configured provider priority as primary.
7. Use other bound exact same-date providers as verifiers.
8. Block on material same-date disagreement.
9. Permit an exact bound primary without verifier as `fresh_exact_unverified`.
10. Preserve candidate-only/no-SMTP/no-broker boundaries.
11. Obtain independent exact-head assurance before merge.
12. After merge, resume report issue #109 using a new canonical run identity for the latest applicable completed-close date.

## Implementation summary
- added `pricing/ucits_provider_identity_binding.py` for source-independent exact-line identity plus per-provider symbol bindings;
- replaced the retired live two-provider identity-anchor policy with donor-aligned primary+verification policy in `pricing/ucits_price_qualification_policy.py`;
- wired the policy through `pricing/build_ucits_close_price_validation_basket_results.py`;
- added `pricing/ucits_primary_verification_legacy.py` so existing v2 downstream consumers receive explicit primary/verification/static-identity evidence without a second pricing control plane;
- migrated `pricing/ucits_close_price_validation_contract_v2.py` and normalized report-state semantics;
- updated the full routine package builder without removing its existing ready/routine-manifest/delivery-boundary logic;
- client-facing NL/EN status labels now distinguish exact independently verified closes from exact closes without a current second verifier;
- preserved secret redaction, product boundary, donor boundary and no-delivery/no-broker authority.

## H1 independent assurance and repair
Independent H1 assurance accepted the core primary-plus-verification pricing semantics but returned formal `FAIL` because the actual promoted v2 package builder reintroduced `funded_two_provider_consensus_required=true` after normalized state had already established `second_provider_required_for_liveness=false`.

H2 therefore requires exactly this bounded repair:
- make the final v2 promotion metadata derive the pricing-authority fields from normalized `pricing_contract` state rather than hard-code the retired universal two-provider requirement;
- prove through the actual v2 package path that the final package manifest, ready artifact and routine run manifest all retain `funded_exact_primary_pricing_required=true`, `second_provider_required_for_liveness=false`, `funded_two_provider_consensus_required=false` and the donor-aligned pricing-authority mode;
- rerun all required exact-head gates and obtain fresh independent assurance on the repaired frozen head.

Repair commit `e5329910d3364db97688c785d105a1a2d46f9db4` changes only `tools/build_etf_eu_routine_report_package_v2.py` and `tests/test_etf_eu_full_candidate_package_end_to_end.py`. It derives final promotion fields from the normalized state contract and adds the required three-artifact regression. This work package remains in `REPAIR_VALIDATION` until the new exact-head CI is green.

## Regression evidence
The implementation parent `ac21efb97badedf227bd58718f1260c0a5b01cf7` passed all required broad gates before the original handover commit:

```text
focused_primary_verification_run=32154779246 SUCCESS
multi_provider_engine_run=32154779190 SUCCESS
product_boundary_run=32154779271 SUCCESS
donor_full_package_parity_run=32154779196 SUCCESS
```

Deterministic coverage includes:
- exact primary + stale verifier => `fresh_exact_unverified` and valuation-grade;
- two exact agreeing providers => `fresh_exact_verified`;
- same-date disagreement => blocked;
- stale-only => blocked;
- live returned-symbol mismatch => provider rejected;
- canonical trading-line identity failure => blocked;
- broken verifier provider-symbol binding => verifier rejected while a correctly bound exact primary may continue unverified;
- broken primary provider-symbol binding => blocked;
- current six funded lines bind to canonical Alpha Vantage and Yahoo symbols;
- legacy v2 contract accepts exact unverified primary but rejects non-exact or unbound-primary evidence;
- exact 2026-08-17 incident regression reproduces the six observed Alpha-exact/Yahoo-stale lines and requires 6/6 `fresh_exact_unverified` pricing authorization;
- client labels do not conflate missing independent price verification with uncertain UCITS trading-line identity;
- repaired v2 package path must inspect final manifest, ready artifact and routine run manifest so a later promotion overwrite cannot silently restore the old two-provider liveness contract.

The live repaired assurance candidate head must be reconstructed from GitHub after this metadata commit and must itself pass the applicable exact-head gates before a fresh independent B1 review.

## Protected boundaries
```text
portfolio_mutation=false
trade_ledger_mutation=false
real_broker_execution=false
smtp_send=false
delivery_authority=false
diagnostic_source_promotion=false
self_assurance=false
merge_before_independent_PASS=false
```

## Report dependency status
Issue #109 remains blocked pending integration of this architecture repair. No new report has been regenerated, merged or sent under this repair. No allocation or portfolio action has occurred.

## Definition of done for this phase
`ASSURANCE_READY`: donor-aligned primary+verification contract including the final v2 package metadata is implemented on one frozen live PR head, exact-head implementation gates are green, and a new immutable assurance handover is ready for a fresh independent `governance_release_assurance` verdict. Merge, report rerun and any delivery remain separate later steps.
