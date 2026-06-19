# Weekly ETF EU-review — pricing-geïntegreerde cockpit POC

## Cockpitsamenvatting

- **Status:** proof of concept / review-only.
- **Prijsbewijs:** CSPX.L en SXR8.DE zijn de enige huidige review-only prijsbaseline.
- **Niet veilig:** SMH blijft pricing_symbol_ambiguous en is geen veilige UCITS-prijsregel zonder exchange-specific verificatie.
- **Geblokkeerd:** Gold/ETC blijft policy_blocked; infrastructure blijft identity_incomplete.
- **Authority:** delivery_authorization_decision=remain_blocked; production_delivery=false; portfolio_mutation=false; candidate_promotion=false; funding_authority=false; valuation_grade=false.

## Prijsbewijs in één oogopslag

| Status | Aantal |
| --- | --- |
| source_evidence_available | 1 |
| pricing_symbol_ambiguous | 1 |
| policy_blocked | 1 |
| identity_incomplete | 1 |

## Zichtbaar UCITS-universum

| Kandidaat | ISIN | Prijsregelstatus | Prijsbewijsstatus | Prijssymbolen | Researchproxy | Safe voor cockpit-prijsbewijs |
| --- | --- | --- | --- | --- | --- | --- |
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | source_evidence_available | usable_for_review_only | CSPX.L, SXR8.DE | SPY | true |
| VanEck Semiconductor UCITS ETF | IE00BMC38736 | pricing_symbol_ambiguous | not_usable_until_exchange_line_verified | pending_verification | SMH | false |
| iShares Physical Gold ETC | TBD | policy_blocked | not_usable_until_policy_decision | pending_verification | GLD | false |
| iShares Global Infrastructure UCITS ETF | TBD | identity_incomplete | not_usable_until_isin_verified | pending_verification | PAVE | false |

## Prijsregel-bewijskaart

| Kandidaat | Reader meaning | Volgende prijsactie |
| --- | --- | --- |
| iShares Core S&P 500 UCITS ETF USD (Acc) | CSPX.L and SXR8.DE remain the current review-only pricing evidence baseline for the enriched cockpit. | Preserve CSPX.L and SXR8.DE as review-only baseline while broker and weekly input integration checks remain pending. |
| VanEck Semiconductor UCITS ETF | Semiconductor exposure is visible for research, but pricing is not safe until the UCITS exchange line and pricing symbol are verified. | Verify an exchange-specific UCITS line and pricing symbol before allowing cockpit pricing evidence. |
| iShares Physical Gold ETC | Gold/ETC remains a blocked policy case, not a UCITS ETF pricing candidate. | Resolve ETC policy decision before any promotion or pricing-line use; GLD remains a research proxy only. |
| iShares Global Infrastructure UCITS ETF | Infrastructure remains identity-incomplete and cannot support cockpit pricing evidence yet. | Verify ISIN and issuer evidence before exchange-line and pricing-symbol work. |

## Onveilige of geblokkeerde prijsregels

| Symbool | Reden |
| --- | --- |
| SMH | ambiguous ticker string; not safe as UCITS pricing evidence without exchange-specific UCITS line verification |
| GLD | U.S. research proxy only; not an EU pricing line or EU holding |
| PAVE | U.S. research proxy only; not an EU pricing line or EU holding |
| Gold/ETC | policy_blocked totdat ETC-beleid expliciet is besloten. |
| Infrastructure | identity_incomplete totdat ISIN en issuer zijn geverifieerd. |

## Scheiding met researchproxy

| Researchproxy | EU/UCITS-weergave | Toegestaan gebruik | Geblokkeerd gebruik |
| --- | --- | --- | --- |
| SPY | iShares Core S&P 500 UCITS ETF USD (Acc) / IE00B5BMR087 | alleen researchproxy / benchmark | EU-holding, EU-prijsregel of financieringsbron |
| SMH | VanEck Semiconductor UCITS ETF / IE00BMC38736 | alleen researchproxy / benchmark | EU-holding, EU-prijsregel of financieringsbron |
| GLD | iShares Physical Gold ETC / TBD | alleen researchproxy / benchmark | EU-holding, EU-prijsregel of financieringsbron |
| PAVE | iShares Global Infrastructure UCITS ETF / TBD | alleen researchproxy / benchmark | EU-holding, EU-prijsregel of financieringsbron |

## Actiekaart voor de lezer

| Vraag | Antwoord | Actie |
| --- | --- | --- |
| Wat is bruikbaar? | IE00B5BMR087 blijft usable_for_review_only via CSPX.L en SXR8.DE. | Gebruik alleen als reviewbewijs. |
| Wat is onveilig? | IE00BMC38736 / SMH blijft ambiguous of pending. | Eerst exchange-specific UCITS-prijsregel verifiëren. |
| Wat blijft geblokkeerd? | Gold/ETC policy_blocked; infrastructure identity_incomplete. | Niet promoveren of financieren. |

## Huidige blokkades

| Blokkade | Status |
| --- | --- |
| Delivery | delivery_authorization_decision=remain_blocked |
| Productie | production_delivery=false |
| Portefeuille | portfolio_mutation=false |
| Kandidaatpromotie | candidate_promotion=false |
| Funding | funding_authority=false |
| Valuation-grade | valuation_grade=false |

## Bijlage — technisch bewijs

- Renderer: `tools/render_etf_eu_pricing_integrated_cockpit.py`
- Validator: `tools/validate_etf_eu_cockpit_pricing_integration.py`
- Testbestand: `tests/test_etf_eu_cockpit_pricing_integration.py`
