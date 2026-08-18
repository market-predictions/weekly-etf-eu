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
status=ACTIVE
opened_at=2026-08-18T16:52:00+02:00
depends_on_report_issue=109
principal_decision_required=false
```

## Current issue
The fresh 2026-08-17 candidate is blocked because the current pricing gate requires two providers on the same date for every funded line even when one qualified provider has an exact requested-date close and the second provider is merely stale.

## Root cause
Stable UCITS trading-line identity, current close selection and independent close verification were coupled into one live two-provider requirement. The project already owns stable ISIN-first trading-line/provider-symbol identity in `config/ucits_symbol_registry.yml`.

## Decision framework
No change to instrument selection, portfolio construction, allocation methodology or re-underwriting. Pricing confidence must not become an allocation rule.

## Input/state contract
- funded universe remains authoritative from `output/etf_eu_portfolio_state.json`;
- stable trading-line identity remains authoritative from `config/ucits_symbol_registry.yml`;
- provider registry must deterministically match the verified symbol-registry line by ISIN + ticker + venue + currency and provider symbol;
- one exact requested-date price from a qualified configured provider may be valuation-grade when the static identity binding passes;
- additional exact same-date providers are verification evidence, not a universal liveness dependency.

## Output contract
Funded lines must classify clearly:
- `fresh_exact_verified`: exact requested date plus at least one agreeing same-date verifier;
- `fresh_exact_unverified`: exact requested date from one qualified identity-bound provider, verifier unavailable/stale;
- `provider_disagreement`: at least two exact requested-date providers outside tolerance; blocked;
- `no_exact_close`: no accepted provider on requested date; blocked.

Both exact verified and exact unverified may be valuation-grade. No stale close may be relabeled fresh.

## Operational runbook
1. Validate provider-registry identity against the canonical UCITS symbol registry.
2. Fetch configured provider closes.
3. Consider only accepted prices on the exact requested report date for production selection.
4. Select the first exact provider by configured provider priority as primary.
5. Use other exact same-date providers as verifiers.
6. Block on material same-date disagreement.
7. Permit exact primary without verifier as `fresh_exact_unverified`.
8. Preserve candidate-only/no-SMTP/no-broker boundaries.
9. Run deterministic tests and existing donor/product/release gates.
10. Freeze exact candidate for independent assurance before merge.
11. After merge, resume report issue #109 and rerun the canonical 2026-08-17 candidate.

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

## Definition of done
`ASSURANCE_READY`: donor-aligned primary+verification contract is implemented on one exact frozen head, identity-binding and pricing-policy tests cover verified/unverified/stale/disagreement/no-exact/mismatch cases, required CI is green, and no report delivery or portfolio action occurred.
