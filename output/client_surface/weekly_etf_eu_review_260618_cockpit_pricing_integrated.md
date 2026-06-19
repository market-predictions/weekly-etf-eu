# Weekly ETF EU Review — Pricing-Integrated Cockpit POC

## Cockpit summary

- **Status:** proof of concept / review-only.
- **Pricing evidence:** CSPX.L and SXR8.DE are the only current review-only pricing baseline.
- **Unsafe:** SMH remains pricing_symbol_ambiguous and is not safe UCITS pricing evidence without exchange-specific verification.
- **Blocked:** Gold/ETC remains policy_blocked; infrastructure remains identity_incomplete.
- **Authority:** delivery_authorization_decision=remain_blocked; production_delivery=false; portfolio_mutation=false; candidate_promotion=false; funding_authority=false; valuation_grade=false.

## Pricing evidence at a glance

| Status | Count |
| --- | --- |
| source_evidence_available | 1 |
| pricing_symbol_ambiguous | 1 |
| policy_blocked | 1 |
| identity_incomplete | 1 |

## Visible UCITS universe

| Candidate | ISIN | Pricing-line status | Pricing evidence status | Pricing symbols | Research proxy | Safe for cockpit pricing evidence |
| --- | --- | --- | --- | --- | --- | --- |
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | source_evidence_available | usable_for_review_only | CSPX.L, SXR8.DE | SPY | true |
| VanEck Semiconductor UCITS ETF | IE00BMC38736 | pricing_symbol_ambiguous | not_usable_until_exchange_line_verified | pending_verification | SMH | false |
| iShares Physical Gold ETC | TBD | policy_blocked | not_usable_until_policy_decision | pending_verification | GLD | false |
| iShares Global Infrastructure UCITS ETF | TBD | identity_incomplete | not_usable_until_isin_verified | pending_verification | PAVE | false |

## Pricing-line evidence map

| Candidate | Reader meaning | Next pricing action |
| --- | --- | --- |
| iShares Core S&P 500 UCITS ETF USD (Acc) | CSPX.L and SXR8.DE remain the current review-only pricing evidence baseline for the enriched cockpit. | Preserve CSPX.L and SXR8.DE as review-only baseline while broker and weekly input integration checks remain pending. |
| VanEck Semiconductor UCITS ETF | Semiconductor exposure is visible for research, but pricing is not safe until the UCITS exchange line and pricing symbol are verified. | Verify an exchange-specific UCITS line and pricing symbol before allowing cockpit pricing evidence. |
| iShares Physical Gold ETC | Gold/ETC remains a blocked policy case, not a UCITS ETF pricing candidate. | Resolve ETC policy decision before any promotion or pricing-line use; GLD remains a research proxy only. |
| iShares Global Infrastructure UCITS ETF | Infrastructure remains identity-incomplete and cannot support cockpit pricing evidence yet. | Verify ISIN and issuer evidence before exchange-line and pricing-symbol work. |

## Unsafe or blocked pricing lines

| Symbol | Reason |
| --- | --- |
| SMH | ambiguous ticker string; not safe as UCITS pricing evidence without exchange-specific UCITS line verification |
| GLD | U.S. research proxy only; not an EU pricing line or EU holding |
| PAVE | U.S. research proxy only; not an EU pricing line or EU holding |
| Gold/ETC | policy_blocked until ETC policy is explicitly decided. |
| Infrastructure | identity_incomplete until ISIN and issuer evidence are verified. |

## Proxy separation map

| Research proxy | EU/UCITS view | Allowed use | Blocked use |
| --- | --- | --- | --- |
| SPY | iShares Core S&P 500 UCITS ETF USD (Acc) / IE00B5BMR087 | research proxy / benchmark only | EU holding, EU pricing line, or funding source |
| SMH | VanEck Semiconductor UCITS ETF / IE00BMC38736 | research proxy / benchmark only | EU holding, EU pricing line, or funding source |
| GLD | iShares Physical Gold ETC / TBD | research proxy / benchmark only | EU holding, EU pricing line, or funding source |
| PAVE | iShares Global Infrastructure UCITS ETF / TBD | research proxy / benchmark only | EU holding, EU pricing line, or funding source |

## Reader action map

| Question | Answer | Action |
| --- | --- | --- |
| What is usable? | IE00B5BMR087 remains usable_for_review_only through CSPX.L and SXR8.DE. | Use only as review evidence. |
| What is unsafe? | IE00BMC38736 / SMH remains ambiguous or pending. | Verify exchange-specific UCITS pricing line first. |
| What is blocked? | Gold/ETC is policy_blocked; infrastructure is identity_incomplete. | Do not promote or fund. |

## Current blockers

| Blocker | Status |
| --- | --- |
| Delivery | delivery_authorization_decision=remain_blocked |
| Production | production_delivery=false |
| Portfolio | portfolio_mutation=false |
| Candidate promotion | candidate_promotion=false |
| Funding | funding_authority=false |
| Valuation-grade | valuation_grade=false |

## Appendix — Technical evidence

- Renderer: `tools/render_etf_eu_pricing_integrated_cockpit.py`
- Validator: `tools/validate_etf_eu_cockpit_pricing_integration.py`
- Test file: `tests/test_etf_eu_cockpit_pricing_integration.py`
