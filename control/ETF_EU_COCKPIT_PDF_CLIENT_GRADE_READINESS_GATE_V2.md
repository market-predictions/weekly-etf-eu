# ETF EU cockpit PDF client-grade readiness gate v2

## Purpose

This contract defines the v2 client-grade readiness gate for the accepted WP15AB/WP15AC review-only foundation.

It separates review-only PDF evidence from client-grade report authority, delivery-preflight authority, and production delivery authority.

The current PDF remains review-only foundation. It is not client-grade and it does not authorize outbound delivery.

## Scope

This gate applies to:

- the WP15AB PDF cockpit preview;
- the WP15AB machine artifact;
- the WP15AC visual closeout artifact;
- later evidence audits that may evaluate whether the cockpit can become client-grade.

This gate does not fetch new prices, regenerate a PDF, mutate portfolio state, or change delivery configuration.

## Authority boundary

```text
review_only=true
client_grade_readiness_gate_created=true
client_grade_claim=false
client_grade_enough_for_delivery_preflight_discussion=false
delivery_ready=false
delivery_preflight_allowed=false
delivery_authorization_decision=remain_blocked
outbound_path_enabled=false
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
pricing_evidence_for_client_grade=false
pricing_evidence_for_delivery_preflight=false
recipient_config_changed=false
smtp_or_secret_config_changed=false
receipt_artifact_created=false
production_manifest_created=false
fake_price_used=false
us_proxy_price_used=false
live_data_fetch_performed=false
pricing_evidence_changed=false
recommendation_logic_changed=false
source_pdf_replaced=false
new_pdf_created=false
renderer_changed=false
```

## Layer 1 — Decision framework

Client-grade report authority requires decision framework evidence that is not present in the review-only pricing cockpit.

Required gates:

- portfolio posture is explicit;
- funded holdings are explicit;
- candidate status is explicit;
- no candidate is presented as funded without funding authority;
- investment thesis is present for every proposed funded position;
- invalidation criteria are present for every proposed funded position;
- risk posture is clear;
- position sizing or no-position rationale is clear;
- concentration risk is clear;
- cash posture is clear.

Current WP15AD status:

```text
decision_framework_status=not_client_grade
```

## Layer 2 — Input/state contract

Client-grade report authority requires complete ISIN-first and UCITS-first input evidence.

Required gates:

- ISIN-first identity is present;
- UCITS instrument identity is present;
- trading line is present;
- trading currency is present;
- latest close date is present;
- latest close is present;
- pricing source is present;
- pricing timestamp is present;
- pricing freshness policy is present;
- TER / ongoing charge evidence is present;
- replication method evidence is present;
- distribution policy evidence is present;
- hedged/unhedged status is present;
- liquidity/spread evidence is present;
- PRIIPs/KID availability is present;
- fund domicile and exchange-line evidence are present.

Current WP15AD status:

```text
input_state_contract_status=partial_not_client_grade
```

## Layer 3 — Output contract

The output contract can accept a PDF as review-only foundation without making it client-grade.

Required gates:

- Dutch-first client language is clear;
- review-only status is visible;
- pricing table is readable;
- SMH skipped/pending is visible;
- no U.S. proxy is shown as investable;
- boundary caveat is visible;
- no client-grade claim is made;
- no delivery-ready claim is made;
- no funding implication is made;
- PDF path is distinct from prior candidates;
- visual review closeout exists;
- proxy disclosure is clear.

Current WP15AD status:

```text
output_contract_status=review_only_foundation_accepted
```

## Layer 4 — Operational runbook

Operational reproducibility is necessary but not sufficient for client-grade status.

Required gates:

- deterministic PDF renderer exists;
- PDF artifact exists;
- machine artifact exists;
- visual closeout artifact exists;
- validator exists;
- targeted tests exist;
- no delivery workflow changed;
- no recipients changed;
- no SMTP/secrets changed;
- no production manifest created;
- no delivery receipt created;
- no live data fetch in WP15AD;
- no portfolio mutation in WP15AD.

Current WP15AD status:

```text
operational_runbook_status=review_only_reproducible
```

## Blocking gates before client-grade

The cockpit PDF cannot be called client-grade until all of these are resolved by later authorized packages:

- investment thesis for proposed funded positions;
- invalidation criteria for proposed funded positions;
- funding decision or cash posture;
- TER / ongoing charge evidence;
- replication method evidence;
- distribution policy evidence;
- hedged/unhedged status evidence;
- PRIIPs/KID availability evidence;
- liquidity/spread evidence;
- pricing freshness policy;
- valuation reconciliation policy;
- client language quality gate.

## Blocking gates before delivery-preflight

Delivery-preflight authority remains blocked until all client-grade gates pass and delivery-specific evidence exists:

- all client-grade gates passed;
- delivery receipt or manifest contract;
- recipient configuration authority;
- SMTP/secrets/recipients authority;
- production delivery manifest path;
- outbound runbook;
- post-send verification loop;
- rollback or abort policy.

## Completion semantics

Completing WP15AD means the gate is defined and validated, not passed.

Expected state:

```text
readiness_gate_status=gate_defined_not_passed
client_grade_claim=false
client_grade_enough_for_delivery_preflight_discussion=false
delivery_preflight_allowed=false
production_delivery=false
```

## Non-authorized actions

WP15AD does not authorize:

- new live pricing;
- PDF regeneration;
- renderer changes;
- portfolio mutation;
- candidate promotion;
- funding authority;
- valuation-grade status;
- client-grade report authority;
- delivery-preflight authority;
- delivery receipt creation;
- production manifest creation;
- SMTP/secrets/recipients changes;
- outbound delivery.
