# Weekly ETF EU Review | Nederlands | 2026-06-01

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
| Core U.S. equity exposure | iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | CSPX / USD / London Stock Exchange | verified_candidate_not_funded | SPY — alleen onderzoeksproxy | niet-autoritatief geprijsd CSPX.L: 816.18 op 2026-06-01; niet-autoritatief geprijsd SXR8.DE: 702.42 op 2026-06-01 | niet gefinancierd; geen waarderingsautoriteit |
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

## 8. Leveringsstatus

Deze output is alleen een niet-verzonden bootstraprapport. Er is geen PDF-rendering, portefeuille-executie of e-mailverzending uitgevoerd.
