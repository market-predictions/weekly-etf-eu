# Weekly ETF EU Review OS — Next Actions

## Status legend

- `[USER]` = must be done manually by you in UI or external systems
- `[ASSISTANT]` = can be done directly in chat/repo
- `[JOINT]` = I prepare, you approve or verify

---

## Current priority

The repo has moved from the adapter-only pricing spine to an agreement-aware pricing-surface shadow path.

Current critical path:

```text
verify shadow workflow
→ switch main EU workflow to wrappers only after verification
→ build production Dutch-first report surface
→ enable delivery only after validators and receipt/manifest path exist
```

Do not treat the shadow workflow as passed until GitHub Actions status or committed validation evidence proves it.

---

## Completed work packages and integrations

### 1. EU repo split and control/state separation

- Owner: `[ASSISTANT]`
- Status: done
- Result:
  - EU repo exists as `market-predictions/weekly-etf-eu`;
  - control layer identifies it as a Dutch/EU UCITS product;
  - EU cash-only state files exist;
  - inherited U.S. holdings are not EU authority.

### 2. EU output and bootstrap validation

- Owner: `[ASSISTANT]`
- Status: done
- Result:
  - inherited U.S. send path disabled;
  - EU output contract added;
  - Dutch-first and English companion skeleton reports added;
  - output-contract and candidate-report validators exist.

### 3. UCITS registry, investability and pricing-line scaffold

- Owner: `[ASSISTANT]`
- Status: done
- Result:
  - UCITS registry seeded;
  - UCITS registry validator added;
  - UCITS investability validator added;
  - UCITS pricing-line contract, candidate extractor, pricing preflight and validators added.

### 4. Initial valuation-pricing scaffold

- Owner: `[ASSISTANT]`
- Status: done
- Result:
  - `control/UCITS_VALUATION_PRICING_CONTRACT_V1.md` added;
  - `config/ucits_pricing_source_policy.yml` added;
  - `pricing/build_ucits_valuation_prices.py` added;
  - `tools/validate_ucits_valuation_prices.py` added;
  - valuation artifacts remain pending/non-mutating with no valuation-grade rows.

### 5. M0/M1 pricing spine

- Owner: `[ASSISTANT]`
- Status: done
- Integrated PRs:
  - `#1` M0 ground-clearing — `c1476171606206d369190bf4c8cf126222a1e753`
  - `#3` common pricing interface — `0c21629aa315f18a0ebceb0a301841d457d2a554`
  - `#4` Stooq pricing adapter — `c92cff7a973f27f152b4c866515d7c84e28135d6`
  - `#5` Börse Frankfurt / Xetra pricing adapter — `34d6c909e87015de49e31ed3fc25294084faad16`
  - `#6` Yahoo fallback pricing adapter — `9138efd0d5613527bd6ab6f44313596e6cb6907f`
  - `#7` issuer NAV reference adapter — `7b74a36de88b8fdb5b4a4f8709312df533c27a9d`
- Result:
  - typed provider evidence spine exists;
  - adapters return typed `PriceResult` evidence;
  - adapters do not create valuation authority, portfolio mutation, report output, PDF, email or delivery.

### 6. Source metadata policy

- Owner: `[ASSISTANT]`
- Status: done
- Integrated PR:
  - `#8 — M5: Add source metadata policy`
- Merge commit:
  - `270446ee54d7f97223b2b94f6207ec2b7c88de22`
- Target files:
  - `control/DATA_SOURCE_METADATA.md`
  - `pricing/source_metadata_policy.py`
  - `tests/test_source_metadata_policy.py`
- Result:
  - source metadata categories align with pricing evidence;
  - pricing sources can be filtered by deterministic policy modes;
  - no source was promoted to valuation authority by metadata alone.

### 7. Agreement gate

- Owner: `[ASSISTANT]`
- Status: done
- Integrated PR:
  - `#9 — M1: Add agreement gate integration`
- Merge commit:
  - `575f919614690a3a851dc4968dea0cfe3a1a870d`
- Target files:
  - `pricing/price_agreement_gate.py`
  - `tools/validate_price_agreement_gate.py`
  - `tests/test_price_agreement_gate.py`
- Result:
  - gate can classify evidence as `valuation_grade`, `provisional`, or `blocked`;
  - only metadata-approved market-close agreement sources count toward agreement;
  - issuer NAV/reference evidence does not count as independent market-close agreement evidence;
  - Yahoo/yfinance alone cannot become valuation authority;
  - no funding authority or portfolio mutation was added.

### 8. Valuation agreement bridge

- Owner: `[ASSISTANT]`
- Status: done as wrapper bridge
- Integrated PR:
  - `#10 — Draft: Add agreement-aware valuation artifact bridge`
- Merge commit:
  - `51f91751e8df19bc5879b4a6ee4c3280e663c55e`
- Target files:
  - `control/VALUATION_AGREEMENT_INTEGRATION_PLAN_20260604.md`
  - `pricing/valuation_agreement_evidence.py`
  - `pricing/enrich_ucits_valuation_agreement.py`
  - `pricing/build_ucits_valuation_prices_with_agreement.py`
  - `tests/test_valuation_agreement_evidence.py`
  - `tests/test_build_ucits_valuation_prices_with_agreement.py`
- Result:
  - agreement-gate evidence can be attached to valuation artifacts;
  - valuation promotion remains blocked under current bootstrap posture;
  - no workflow, output artifact, portfolio state, report renderer, PDF/email or delivery behavior changed by PR #10 itself.

### 9. Pricing-surface wrapper

- Owner: `[ASSISTANT]`
- Status: done
- Target files:
  - `runtime/render_etf_eu_report_with_pricing_surface.py`
  - `runtime/etf_eu_pricing_surface.py`
  - `tools/validate_etf_eu_pricing_surface.py`
  - `tests/test_etf_eu_pricing_surface.py`
  - `tests/test_etf_eu_report_pricing_surface_wrapper.py`
- Result:
  - report wrapper can display agreement-gate pricing evidence;
  - Dutch and English pricing-surface validation exists;
  - pricing surface remains evidence-only and not valuation/funding authority.

### 10. Fundability promotion contract

- Owner: `[ASSISTANT]`
- Status: done
- Target files:
  - `control/UCITS_FUNDABILITY_PROMOTION_CONTRACT_V1.md`
  - `tools/validate_ucits_fundability_promotion_contract.py`
  - `tests/test_ucits_fundability_promotion_contract.py`
- Result:
  - candidate promotion requires explicit identity, investability, trading-line, pricing-quality, tradability/liquidity, portfolio-role and decision gates;
  - no automatic promotion from pricing success or report visibility is allowed;
  - all current candidates remain not funded and not fundable.

### 11. Non-production pricing-surface shadow workflow

- Owner: `[ASSISTANT]`
- Status: created, verification pending
- Target file:
  - `.github/workflows/weekly-etf-eu-pricing-surface-shadow.yml`
- Created by:
  - `03e7b539b8bc26c746db51c1db383f728e773e71`
- Queue-triggerable update:
  - `4b458a30405958b06e833bdb4de73cabf48c6d8c`
- Result:
  - workflow can run the wrapper path outside production;
  - it is designed to avoid delivery, PDF generation, email, portfolio mutation and candidate promotion;
  - latest queue commits have not yet produced connector-visible workflow-run evidence.

---

## Pending work

### 12. Verify shadow workflow

- Owner: `[ASSISTANT]`
- Status: pending
- Target:
  - `.github/workflows/weekly-etf-eu-pricing-surface-shadow.yml`
  - `output/validation/etf_eu_pricing_surface_shadow_*.json`
- Done when:
  - GitHub Actions run/job status confirms success, or
  - a validation artifact with `schema_version=etf_eu_pricing_surface_shadow_validation_v1` and `status=passed` is committed.
- Do not claim:
  - shadow workflow passed;
  - delivery succeeded;
  - PDF/email was produced;
  - candidates were promoted.

### 13. Switch main EU workflow to wrapper path

- Owner: `[ASSISTANT]`
- Status: pending until shadow workflow is verified
- Target file:
  - `.github/workflows/send-weekly-etf-eu-report.yml`
- Action:
  - replace the legacy valuation build step with `pricing.build_ucits_valuation_prices_with_agreement`;
  - replace the report render step with `runtime.render_etf_eu_report_with_pricing_surface`;
  - add pricing-surface and fundability validators;
  - keep the workflow non-delivery until production gates are ready.
- Done when:
  - main workflow passes with wrapper path;
  - authority boundaries remain unchanged.

### 14. Build production Dutch-first report surface

- Owner: `[ASSISTANT]`
- Status: pending after main wrapper switch
- Action:
  - convert the bootstrap skeleton into a full Dutch-first UCITS report surface;
  - keep U.S. proxies research-only;
  - present UCITS candidates, pricing evidence and fundability status without funded-position claims;
  - keep English as companion/operator surface unless a later decision changes this.
- Done when:
  - Dutch report is client-native, not a U.S. report translation;
  - output validators pass;
  - report does not imply funding authority.

### 15. Enable delivery only after validators and receipt/manifest path exist

- Owner: `[JOINT]`
- Status: blocked
- Action:
  - enable PDF/email only after EU state, pricing, report, localization and delivery contracts pass;
  - require a real delivery receipt or manifest before claiming delivery success.
- Done when:
  - production delivery workflow produces a real manifest/receipt;
  - no delivery claim is made without evidence.

---

## Roadmap after control consolidation

1. Shadow workflow verification.
2. Main workflow wrapper switch.
3. Production Dutch-first UCITS report surface.
4. Candidate/fundability enrichment only after explicit gates pass.
5. Delivery enablement only after validators and manifest/receipt path exist.

## Standing authority boundaries

Until a future decision log entry and validator-backed implementation explicitly changes them:

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
no delivery receipt
no candidate promotion to fundable
```

Adapters, wrappers, report surfaces and validators produce evidence and checks only. They do not fund candidates, mutate portfolio state, generate production PDFs, send email or create delivery receipts.
