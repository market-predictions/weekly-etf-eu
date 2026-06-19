# Weekly ETF EU-review — premium cockpit POC

## Cockpitsamenvatting

- **Rapportstatus:** proof of concept / review-only.
- **Huidige stand:** de UCITS-oppervlakte is zichtbaar; er is geen portefeuilleactie.
- **UCITS-bewijs:** IE00B5BMR087 is zichtbaar via CSPX.L en SXR8.DE.
- **Belangrijkste blokkade:** levering en portefeuilleautoriteit blijven geblokkeerd.
- **Volgende productactie:** verbeter de cockpit en breid het UCITS-universum uit.

## Kaarten in één oogopslag

| Kaart | Status | Betekenis voor de lezer |
| --- | --- | --- |
| UCITS-zichtbaarheid | Zichtbaar | De eerste UCITS-kandidaat is duidelijk zichtbaar met ISIN en beurslijnen. |
| Prijsbewijs | Aanwezig | Slotkoersbewijs bestaat voor CSPX.L en SXR8.DE. |
| Researchproxy's | Gescheiden | SPY is alleen benchmark / researchproxy, geen EU-positie. |
| Leveringsstatus | Geblokkeerd | Productielevering is niet toegestaan. |
| Portefeuilleautoriteit | Geblokkeerd | Geen financiering, kandidaatpromotie of portefeuillewijziging toegestaan. |

## Zichtbare UCITS-kandidaat

| Fonds | ISIN | Beurslijn | Valuta | Gebruik voor de lezer |
| --- | --- | --- | --- | --- |
| iShares Core S&P 500 UCITS ETF | IE00B5BMR087 | CSPX.L | USD | UCITS-kandidaat zichtbaar met prijsbewijs per beurslijn. |
| iShares Core S&P 500 UCITS ETF | IE00B5BMR087 | SXR8.DE | EUR | EUR-beurslijn zichtbaar voor Nederlandse/EU-review. |

## Prijsbewijs

| Prijssymbool | Slotdatum | Slotkoers | Valuta | Status |
| --- | --- | ---: | --- | --- |
| CSPX.L | 2026-06-17 | 809.24 | USD | Bronbewijs beschikbaar. |
| SXR8.DE | 2026-06-17 | 698.02 | EUR | Bronbewijs beschikbaar. |

Dit prijsbewijs ondersteunt de cockpitweergave, maar geeft geen valuation-grade autoriteit.

## Scheiding met researchproxy

SPY blijft alleen benchmark en researchproxy. SPY kan helpen om het Amerikaanse S&P 500-gedrag te vergelijken met de UCITS-kandidaat, maar SPY is geen EU-belegbare positie in dit rapport.

## Actiekaart voor de lezer

| Vraag van de lezer | Cockpitantwoord | Actie nu |
| --- | --- | --- |
| Wat is de ETF EU-status? | Proof of concept, review-only. | Beoordeel cockpitindeling en helderheid van bewijs. |
| Welke UCITS-kandidaat is zichtbaar? | IE00B5BMR087 via CSPX.L en SXR8.DE. | Controleer ISIN, beurslijn, valuta en slotkoersbewijs. |
| Wat is nu actiegericht? | Alleen productreview. | Geen portefeuilleactie. |
| Wat is niet actiegericht? | Levering, financiering, valuation-grade gebruik en kandidaatpromotie. | Geblokkeerd houden tot expliciete poorten veranderen. |
| Waar moet ik eerst naar kijken? | UCITS-identiteit, prijsbewijs en proxy-scheiding. | Gebruik deze panelen vóór de bijlage. |

## Huidige blokkades

| Blokkade | Huidige status | Betekenis |
| --- | --- | --- |
| Leveringsautoriteit | remain_blocked | Geen e-mail, geen ontvangeractivatie, geen productiesend. |
| Portefeuillewijziging | false | Geen wijziging in posities of cash. |
| Financieringsautoriteit | false | Geen koop- of financieringsbesluit. |
| Valuation-grade autoriteit | false | Prijzen zijn bewijs voor review, geen officiële waarderingsautoriteit. |
| Breedte UCITS-universum | beperkt | Het volgende pakket moet het UCITS-universum uitbreiden en cockpitdata verrijken. |

## Bijlage — technisch bewijs

- Bron client-surface manifest: `output/client_surface/etf_eu_client_surface_20260618_000000.json`
- Bron Engelse client surface: `output/client_surface/weekly_etf_eu_review_260618_client_surface.md`
- Bron Nederlandse client surface: `output/client_surface/weekly_etf_eu_review_nl_260618_client_surface.md`
- Autorisatiebesluit: `output/delivery/etf_eu_delivery_authorization_decision_20260618_000000.json`
- Validator: `tools/validate_etf_eu_premium_cockpit_surface.py`
- Testbestand: `tests/test_etf_eu_premium_cockpit_surface.py`
