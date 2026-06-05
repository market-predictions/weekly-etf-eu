# Weekly ETF EU Review | Nederlands | 2026-06-05

> **Status:** cash-only bootstrap. Dit is geen productiepublicatie en er is geen e-maillevering uitgevoerd.

## 1. Status

De EU/UCITS-versie van de Weekly ETF Review staat in bootstrapfase.

- **Huidige staat:** cash-only bootstrap.
- **Gefinancierde UCITS-posities:** geen.
- **Amerikaanse ETF's:** alleen onderzoeksproxy, niet investeerbaar portefeuille-instrument in dit EU-model.
- **UCITS-kandidaten:** vereisen ISIN-, KID-/PRIIPs- en handelslijnverificatie.
- **Pricing-preflight:** niet-autoritatieve connectiviteitstest, geen waarderingsautoriteit.
- **Productielevering:** uitgeschakeld.

## 2. Huidige portefeuillestaat

| Component | Waarde |
|---|---:|
| Startkapitaal | EUR 100000.00 |
| Cash | EUR 100000.00 |
| Belegde marktwaarde | EUR 0.00 |
| Totale portefeuillewaarde | EUR 100000.00 |
| Gefinancierde posities | 0 |

Er zijn nog geen UCITS ETF's gefinancierd. De portefeuille blijft volledig in cash totdat instrumenten het EU-investeerbaarheidscontract passeren.

## 3. Investeerbaarheidsfilter

Een ETF kan pas fundable worden wanneer minimaal de volgende velden zijn geverifieerd:

| Vereiste | Status |
|---|---|
| ISIN | vereist |
| UCITS-status | vereist |
| PRIIPs/KID beschikbaarheid | vereist |
| Handelsbeurs en ticker | vereist |
| Handelsvaluta | vereist |
| Pricinglijn | vereist |
| Productkosten / TER | te vullen waar beschikbaar |
| Replicatiemethode | te vullen waar beschikbaar |
| Accumulerend / distribuerend | te vullen waar beschikbaar |

## 4. Onderzoeksproxies

Amerikaanse ETF's mogen alleen als onderzoeksproxy of benchmarkreferentie worden gebruikt. Ze mogen niet als gefinancierde EU-portefeuillepositie verschijnen.

| Thema | Amerikaanse proxy | EU-rol | Status |
|---|---|---|---|
| S&P 500 core beta | SPY — alleen onderzoeksproxy | Core U.S. equity exposure through UCITS ETF | UCITS-kandidaat moet nog worden geverifieerd |
| Semiconductor leadership | SMH — alleen onderzoeksproxy | Semiconductor thematic exposure through UCITS ETF | UCITS-kandidaat moet nog worden geverifieerd |
| Gold / hard-asset hedge | GLD — alleen onderzoeksproxy | Gold or commodity hedge through EU-listed product | UCITS-kandidaat moet nog worden geverifieerd |
| Infrastructure / real asset capex | PAVE — alleen onderzoeksproxy | Infrastructure exposure through UCITS ETF | UCITS-kandidaat moet nog worden geverifieerd |

## 5. UCITS-kandidatenregister

Onderstaande tabel toont registerkandidaten en een eventuele pricing-preflight. Deze tabel is **geen portefeuille**, **geen koopadvies** en **geen waarderingsautoriteit**.

| Rol | Instrument | ISIN | Handelslijn | Status | Amerikaanse proxy | Pricing-preflight | Portefeuille-status |
|---|---|---|---|---|---|---|---|
| Core U.S. equity exposure | iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | CSPX / USD / London Stock Exchange | verified_candidate_not_funded | SPY — alleen onderzoeksproxy | niet-autoritatief geprijsd CSPX.L: 814.74 op 2026-06-04; niet-autoritatief geprijsd SXR8.DE: 700.74 op 2026-06-04 | niet gefinancierd; geen waarderingsautoriteit |
| Semiconductor thematic exposure | VanEck Semiconductor UCITS ETF | IE00BMC38736 | SMH / USD / primary_line_pending_verification | candidate_requires_verification | SMH — alleen onderzoeksproxy | niet getest / niet van toepassing | niet gefinancierd; geen waarderingsautoriteit |
| Gold / hard-asset hedge | iShares Physical Gold ETC | TBD | SGLN / pending_verification / pending_verification | policy_review_required_not_ucits | GLD — alleen onderzoeksproxy | niet getest / niet van toepassing | niet gefinancierd; geen waarderingsautoriteit |
| Infrastructure / real-asset capex exposure | iShares Global Infrastructure UCITS ETF | TBD | INFR / pending_verification / pending_verification | candidate_requires_verification | PAVE — alleen onderzoeksproxy | niet getest / niet van toepassing | niet gefinancierd; geen waarderingsautoriteit |

## 6. Status UCITS-register

Het UCITS-register bevat nu bootstrapkandidaten, maar er is nog geen gefinancierde modelportefeuille. Kandidaten blijven niet-gefinancierd totdat ISIN, KID/PRIIPs, handelslijn, valuta, pricingkwaliteit, liquiditeit en portefeuillerol voldoende zijn gecontroleerd.

## 7. Volgende bouwstappen

1. Verrijk het UCITS-symbolenregister met extra geverifieerde ISIN's en handelslijnen.
2. Koppel onderzoeksproxies aan daadwerkelijke UCITS-kandidaten.
3. Promoveer pricing van connectiviteitstest naar valuation-grade alleen na aparte pricing-lineagebeslissing.
4. Bouw daarna pas een gefinancierde modelportefeuille.
5. Houd productielevering uitgeschakeld totdat alle EU-validaties slagen.

## Productierapport-volwassenheid

Deze laag maakt het rapport geschikt als **Nederlandse hoofdrapportage** voor een Dutch/EU-client review, maar verandert niets aan portefeuille- of leveringsautoriteit.

| Controlepunt | Huidige status |
|---|---|
| Rapportrol | primaire clientrapportage in het Nederlands |
| Engelse rapportage | Engelse rapportage is companion/operator-facing |
| Clientbesluit | onderzoeks- en bewijsfase; geen koopadvies |
| UCITS-portefeuille | geen gefinancierde UCITS-posities |
| Portefeuille-impact | geen portefeuille-mutatie |
| Pricingkwaliteit | agreement-gate bewijs zichtbaar, geen waarderingsautoriteit |
| Fundability | fundability gate status zichtbaar; geen kandidaat automatisch fundable |
| Productielevering | geen productielevering |
| Delivery bewijs | geen delivery receipt |

De tekst is geschreven voor Nederlandse/EU-clientbesluitvorming. Amerikaanse ETF's blijven onderzoeksproxy's en mogen niet als investeerbare EU-portefeuillepositie worden gepresenteerd.

## Agreement-gate pricing oppervlak

Onderstaande pricingregels zijn bewijsregels voor kandidaten. Deze sectie is **geen portefeuille**, **geen koopadvies** en **geen waarderingsautoriteit**.

| Instrument | ISIN | Handelslijn | Agreement-gate pricing | Portefeuille-status |
|---|---|---|---|---|
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | CSPX / USD / London Stock Exchange | status=provisional; datum=-; slot=-; valuta=-; bronnen=- | niet gefinancierd; geen waarderingsautoriteit |
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | SXR8 / EUR / Xetra | status=provisional; datum=-; slot=-; valuta=-; bronnen=- | niet gefinancierd; geen waarderingsautoriteit |

## Fundability gate status

De fundability gate status is zichtbaar als rapportbewijs. Deze sectie promoveert geen kandidaat naar fundable en creëert geen funding authority.

- **Kandidaten:** 4.
- **Niet fundable / geblokkeerd:** 4.
- **candidate_promotion=false**.
- **funding_authority=false**.
- **portfolio_mutation=false**.
- **production_delivery=false**.

| Instrument | ISIN | Fundability gate status | Gate blockers | Gates | Authority |
|---|---|---|---|---|---|
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | not_fundable_blocked | pricing_quality:pricing_evidence_provisional_or_reference_only, pricing_quality:valuation_grade_false, tradability_liquidity:liquidity_check_missing_or_not_passed, tradability_liquidity:spread_check_missing_or_not_passed, tradability_liquidity:broker_availability_not_confirmed, portfolio_role:portfolio_role_review_missing | decision=blocked; eu_investability=passed; instrument_identity=passed; portfolio_role=blocked; pricing_quality=blocked; tradability_liquidity=blocked; trading_line=passed | candidate_promotion=false; funding_authority=false; portfolio_mutation=false; production_delivery=false |
| VanEck Semiconductor UCITS ETF | IE00BMC38736 | not_fundable_blocked | eu_investability:ucits_status_not_fully_confirmed, eu_investability:domicile_missing_or_pending, eu_investability:distribution_policy_missing_or_pending, eu_investability:replication_method_missing_or_pending, trading_line:no_verified_trading_line, pricing_quality:agreement_gate_valuation_status_missing | decision=blocked; eu_investability=blocked; instrument_identity=passed; portfolio_role=blocked; pricing_quality=blocked; tradability_liquidity=blocked; trading_line=blocked | candidate_promotion=false; funding_authority=false; portfolio_mutation=false; production_delivery=false |
| iShares Physical Gold ETC | TBD | not_fundable_blocked | instrument_identity:isin_missing_or_placeholder, instrument_identity:instrument_type_not_ucits_etf_under_current_policy, eu_investability:ucits_status_not_fully_confirmed, eu_investability:priips_kid_not_confirmed_available, eu_investability:domicile_missing_or_pending, eu_investability:ter_pct_missing_or_pending | decision=blocked; eu_investability=blocked; instrument_identity=blocked; portfolio_role=blocked; pricing_quality=blocked; tradability_liquidity=blocked; trading_line=blocked | candidate_promotion=false; funding_authority=false; portfolio_mutation=false; production_delivery=false |
| iShares Global Infrastructure UCITS ETF | TBD | not_fundable_blocked | instrument_identity:isin_missing_or_placeholder, eu_investability:ucits_status_not_fully_confirmed, eu_investability:priips_kid_not_confirmed_available, eu_investability:domicile_missing_or_pending, eu_investability:distribution_policy_missing_or_pending, eu_investability:replication_method_missing_or_pending | decision=blocked; eu_investability=blocked; instrument_identity=blocked; portfolio_role=blocked; pricing_quality=blocked; tradability_liquidity=blocked; trading_line=blocked | candidate_promotion=false; funding_authority=false; portfolio_mutation=false; production_delivery=false |

## 8. Leveringsstatus

Deze output is alleen een niet-verzonden bootstraprapport. Er is geen PDF-rendering, portefeuille-executie of e-mailverzending uitgevoerd.
