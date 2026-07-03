# ETF-EU-WP15V client-grade readiness gate notes

```text
repository=market-predictions/weekly-etf-eu
work_package_id=ETF-EU-WP15V
legacy_work_package_id=WP15V
source_work_package=ETF-EU-WP15U
status=completed_after_readiness_contract_and_evidence_gate_definition
readiness_contract_path=control/ETF_EU_COCKPIT_PDF_CLIENT_GRADE_READINESS_CONTRACT_V1.md
readiness_gate_artifact=output/client_surface/etf_eu_cockpit_pdf_client_grade_readiness_gate_20260703_000000.json
readiness_gate_validator=tools/validate_etf_eu_cockpit_pdf_client_grade_readiness_gate.py
readiness_gate_tests=tests/test_etf_eu_cockpit_pdf_client_grade_readiness_gate.py
readiness_gate_status=contract_defined_not_passed
selected_next_package=ETF-EU-WP15W
```

## Current issue

WP15U accepted the WP15T PDF as a review-only premium Dutch cockpit foundation, but it explicitly did not make the PDF client-grade and did not authorize delivery preflight.

## Root cause

The system needs a stricter readiness contract and evidence gate between a visually acceptable review-only foundation and any later client-grade or delivery-preflight discussion.

## Recommended change implemented

WP15V adds a formal readiness contract and JSON evidence gate. The gate covers four layers:

1. decision framework;
2. input/state contract;
3. output contract;
4. operational runbook.

The gate status is deliberately:

```text
readiness_gate_status=contract_defined_not_passed
```

This means the contract exists, but the current PDF has not yet been audited against it.

## Four-layer separation

Decision framework:

```text
Defines gates for weekly posture, action labels, candidate promotion status, thesis/invalidation, concentration, U.S.-ETF exclusion and unsupported-product blocking.
```

Input/state contract:

```text
Defines gates for ISIN-first identity, UCITS status, PRIIPs/KID, trading line, currency, pricing symbol, latest close, pricing freshness, TER, replication, distribution, hedging and liquidity/spread evidence.
```

Output contract:

```text
Defines gates for Dutch-first client language, readable hierarchy, no clipping/overlap, tables/cards, evidence badges, proxy disclosure, limitations, governance footer and render review before any client-grade claim.
```

Operational runbook:

```text
Defines gates for deterministic build command, validator command, targeted pytest, rendered PDF review evidence, no delivery workflow changes, no recipients/secrets/SMTP changes, no unauthorized live data fetch and no unauthorized portfolio mutation.
```

## Boundary confirmation

```text
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
delivery_authorization_decision=remain_blocked
delivery_preflight_allowed=false
outbound_path_enabled=false
live_data_fetch_performed=false
pricing_evidence_changed=false
recommendation_logic_changed=false
client_distribution_claimed=false
receipt_artifact_created=false
production_manifest_created=false
source_pdf_replaced=false
new_pdf_created=false
renderer_changed=false
```

## Important limitation

WP15V does not audit the current PDF against the readiness contract. It only defines the contract and evidence gate.

## Recommended next package

```text
ETF-EU-WP15W — ETF EU cockpit PDF readiness gate implementation audit, no delivery
```

Purpose:

```text
Audit the current WP15T/WP15U PDF candidate against the WP15V readiness contract and produce a pass/fail readiness matrix without delivery, live data refresh or portfolio mutation.
```
