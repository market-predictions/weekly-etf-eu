# Weekly ETF EU Review | Nederlands | 2026-05-31

> **Status:** cash-only bootstrap. Dit is geen productiepublicatie en er is geen e-maillevering uitgevoerd.

## 1. Status

De EU/UCITS-versie van de Weekly ETF Review staat in bootstrapfase.

- **Huidige staat:** cash-only bootstrap.
- **Gefinancierde UCITS-posities:** geen.
- **Amerikaanse ETF's:** alleen onderzoeksproxy, niet investeerbaar portefeuille-instrument in dit EU-model.
- **UCITS-kandidaten:** vereisen ISIN-, KID-/PRIIPs- en handelslijnverificatie.
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

## 5. Status UCITS-register

Het UCITS-register is nog niet gevuld met geverifieerde instrumenten. Kandidaten blijven op `candidate_requires_verification` totdat ISIN, KID/PRIIPs, handelslijn, valuta en pricing zijn gecontroleerd.

## 6. Volgende bouwstappen

1. Vul het UCITS-symbolenregister met geverifieerde ISIN's en handelslijnen.
2. Koppel onderzoeksproxies aan daadwerkelijke UCITS-kandidaten.
3. Voeg pricing toe voor Europese handelslijnen en valuta.
4. Bouw daarna pas een gefinancierde modelportefeuille.
5. Houd productielevering uitgeschakeld totdat alle EU-validaties slagen.

## 7. Leveringsstatus

Deze output is alleen een niet-verzonden bootstraprapport. Er is geen PDF-rendering, portefeuille-executie of e-mailverzending uitgevoerd.
