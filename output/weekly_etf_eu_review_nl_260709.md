# Weekly ETF EU Review | Nederlands | 2026-07-09

> **Pakketstatus:** EU/UCITS-clientpakket in validatiefase. Dit rapport is geen koopadvies, geen portefeuille-opdracht en geen waarderingsautoriteit.

## 1. Kernsamenvatting

De EU/UCITS-versie gebruikt uitsluitend UCITS-handelslijnen als potentieel investeerbare instrumenten. Amerikaanse ETF-symbolen horen niet in de primaire clienttabel en worden alleen in de bijlage als onderzoeksreferentie bewaard.

- **Modelstaat:** cash-only, geen gefinancierde UCITS-posities.
- **Beslissing:** nog geen allocatie; eerst datakwaliteit en handelslijnverificatie afronden.
- **Koersinformatie:** alleen niet-autoritatieve connectiviteits- of diagnostische observatie totdat aparte waarderingslineage is goedgekeurd.

## 2. Portefeuille-overzicht

| Component | Waarde |
|---|---:|
| Startkapitaal | EUR 100000.00 |
| Cash | EUR 100000.00 |
| Belegde marktwaarde | EUR 0.00 |
| Totale portefeuillewaarde | EUR 100000.00 |
| Gefinancierde posities | 0 |

## 3. UCITS observatielijst

Deze tabel toont alleen ISIN-first UCITS-handelslijnen die voldoende zijn om in de primaire clientwatchlist te staan. Onopgeloste of beleidsmatige items staan niet in deze hoofdtabel.

| Rol | UCITS ETF | ISIN | Handelslijn | Datastatus | Portefeuille-status |
|---|---|---|---|---|---|
| Core U.S. equity exposure | iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | CSPX / USD / London Stock Exchange | niet-autoritatieve close: 800.12 (2026-07-08) | Niet gefinancierd; geen waarderings- of fundingautoriteit |
| Core U.S. equity exposure | iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | SXR8 / EUR / Xetra | geen bruikbare close; diagnostiek vereist | Niet gefinancierd; geen waarderings- of fundingautoriteit |

## 4. Koersvalidatie en datakwaliteit

Koersen in dit pakket zijn diagnostisch. Een positieve close in de pipeline bewijst connectiviteit, maar creëert geen waarderingsautoriteit en geen fundingbesluit.

## 5. Besliscockpit / Volgende actie

| Vraag | Antwoord |
|---|---|
| Is er een gefinancierde positie? | Nee |
| Is er koopadvies? | Nee |
| Is pricing valuation-grade? | Nee |
| Volgende stap | PDF-pakket en UCITS close-fetch validatie afronden vóór gecontroleerde herverzending |

## 6. Bijlage: onderzoeksproxies en diagnostiek

Onderzoeksreferenties hieronder zijn niet investeerbaar in dit EU-model. Ze mogen niet worden gelezen als portefeuille-instrument.

| Thema | Onderzoeksreferentie | EU-rol | Status |
|---|---|---|---|
| S&P 500 core beta | SPY | Core U.S. equity exposure through UCITS ETF | Alleen onderzoeksreferentie; niet investeerbaar in het EU-model |
| Semiconductor leadership | SMH | Semiconductor thematic exposure through UCITS ETF | Alleen onderzoeksreferentie; niet investeerbaar in het EU-model |
| Gold / hard-asset hedge | GLD | Gold or commodity hedge through EU-listed product | Alleen onderzoeksreferentie; niet investeerbaar in het EU-model |
| Infrastructure / real asset capex | PAVE | Infrastructure exposure through UCITS ETF | Alleen onderzoeksreferentie; niet investeerbaar in het EU-model |

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
| Geen pricingregels | - | - | geen agreement-gate bewijs | niet gefinancierd; geen waarderingsautoriteit |

## Fundability gate status

De fundability gate status is zichtbaar als rapportbewijs. Deze sectie promoveert geen kandidaat naar fundable en creëert geen funding authority.

- **Kandidaten:** 0.
- **Niet fundable / geblokkeerd:** 0.
- **candidate_promotion=false**.
- **funding_authority=false**.
- **portfolio_mutation=false**.
- **production_delivery=false**.

| Instrument | ISIN | Fundability gate status | Gate blockers | Gates | Authority |
|---|---|---|---|---|---|
| Geen fundabilityregels | - | niet beschikbaar | geen artifact beschikbaar | - | candidate_promotion=false; funding_authority=false; portfolio_mutation=false; production_delivery=false |
