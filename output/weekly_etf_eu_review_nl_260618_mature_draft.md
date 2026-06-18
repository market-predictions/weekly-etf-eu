# ETF EU-review — volwassen Nederlandse conceptversie

## 1. Status van dit concept

Deze Nederlandse companion is review-only en afgeleid van de Engelse/EU-bronartefacten. Dit is geen zelfstandig nieuw onderzoek.

```text
review-only
geen productielevering
geen mailverzending
geen ontvangers geactiveerd
geen portefeuillemutatie
geen financieringsautoriteit
geen waarderingsautoriteit
```

## 2. Kernsamenvatting

De EU-repository heeft bewezen dat de eerste UCITS-beurslijnen via de directe Yahoo chart-bron bruikbare slotkoersen kunnen opleveren. De gebruikte prijsrun bevat 2 gevonden prijzen, 2 geteste prijssymbolen en 0 bronfouten.

Deze prijsinformatie is bronbewijs. Het is geen waarderingsautoriteit, geen financieringsautoriteit, geen portefeuillemutatie en geen leveringsbewijs.

## 3. UCITS-prijsbewijs

Gebruikte prijsbron: `output/pricing/etf_eu_ucits_closing_price_smoke_20260618_000000.json`

| fondsnaam | ISIN | beurs-ticker | Yahoo-symbool | slotdatum | slotkoers | handelsvaluta | bronvaluta | bronbeurs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | CSPX | CSPX.L | 2026-06-17 | 809.239990234375 | USD | USD | LSE |
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | SXR8 | SXR8.DE | 2026-06-17 | 698.02001953125 | EUR | EUR | GER |

Bron- en versheidsbeperking: de koersen komen uit de directe Yahoo chart-bron als dagelijkse slotkoers voor UCITS-beurslijnen. De rapportage gebruikt de laatste niet-lege slotkoers uit het vastgelegde smoke-artefact.

## 4. UCITS-identiteit

| register-id | fondsnaam | ISIN | beurs | beurs-ticker | handelsvaluta | Yahoo-symbool | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| core_us_equity_cspx | iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | London Stock Exchange | CSPX | USD | CSPX.L | bevestigd |
| core_us_equity_cspx | iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | Xetra | SXR8 | EUR | SXR8.DE | bevestigd |

## 5. Scheiding tussen UCITS-kandidaat en Amerikaanse researchproxy

Amerikaanse ETF's zijn alleen researchproxy's en geen belegbare EU-posities.

| UCITS-register-id | Amerikaanse researchproxy | doel |
| --- | --- | --- |
| core_us_equity_cspx | SPY | benchmarkreferentie |

SPY mag alleen worden gebruikt als benchmarkreferentie of onderzoeksvergelijking. SPY is geen EU-belegging in deze rapportage.

## 6. EU-besliscockpit

- **Conceptstatus:** review-only; geen productielevering en geen portefeuillemutatie.
- **Prijsbasis:** UCITS-beurslijnslotkoersen uit het vastgelegde smoke-artefact.
- **Belangrijkste grens:** Amerikaanse ETF's blijven researchproxy's, geen EU-posities.
- **Volgende stap:** HTML/PDF-renderdry-run vanuit volwassen tweetalige rapporten, zonder ontvangers.

## 7. Open punten voor productiegebruik

- Bredere UCITS-dekking.
- KID/PRIIPs-validatie voor de volledige belegbare set.
- Liquiditeit, spread, beursgeschiktheid en TER-verrijking.
- Waarderingspoort met meerdere bronnen.
- Nederlandse taalcontrole en tweetalige pariteit.
- HTML/PDF-renderdry-run zonder ontvangers.
- Expliciet leveringsbeleid met manifest of ontvangstbewijs voordat levering ooit productiestatus krijgt.

## 8. Volgende ontwikkelstap

```text
WP14J — ETF EU HTML/PDF render dry run from mature bilingual reports, no recipients
```

Levering blijft geblokkeerd. Deze Nederlandse companion is uitsluitend een volwassen conceptoppervlak.

## 9. Autoriteitsdisclaimer

Geen productielevering. Geen mailverzending. Geen ontvangers geactiveerd. Geen portefeuillemutatie. Geen financieringsautoriteit. Geen waarderingsautoriteit. Yahoo-prijsinformatie is bronbewijs en geen zelfstandige waarderingsautoriteit.

Bronrapport: `output/weekly_etf_eu_review_260618_draft.md`
