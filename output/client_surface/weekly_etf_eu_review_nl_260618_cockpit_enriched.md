# Weekly ETF EU-review — verrijkte premium cockpit POC

## Cockpitsamenvatting

- **Rapportstatus:** proof of concept / review-only.
- **Huidige stand:** het UCITS-universum is uitgebreid voor review; er is geen portefeuilleactie.
- **Status UCITS-universum:** vier registry-items zijn zichtbaar: één geverifieerde kandidaat, één UCITS-kandidaat met ontbrekende prijsbasis, één geblokkeerde ETC-beleidszaak en één infrastructuurkandidaat met incomplete identiteit.
- **Belangrijkste bewijsgaten:** beurslijnverificatie, prijssymbooldekking, ISIN-aanvulling voor placeholders en beleid rond ETC-blootstelling.
- **Belangrijkste blokkade:** levering en portefeuilleautoriteit blijven geblokkeerd.
- **Volgende productactie:** integreer de verrijkte cockpitdata in een deterministische renderer en kwaliteitsgate.

## Kaarten in één oogopslag

| Kaart | Status | Betekenis voor de lezer |
| --- | --- | --- |
| UCITS-universum | Uitgebreid | De cockpit toont nu de geconfigureerde S&P 500-, semiconductor-, goud/ETC- en infrastructuurlanes. |
| Identiteitsbewijs | Gemengd | IE00B5BMR087 is geverifieerd; IE00BMC38736 is zichtbaar maar vraagt beurslijnhardening; twee entries blijven identity- of policy-incomplete. |
| Prijsbewijs | Gedeeltelijk | CSPX.L en SXR8.DE behouden slotkoersbewijs; andere kandidaatregels vragen prijssymboolverificatie. |
| Proxy-scheiding | Behouden | SPY, SMH, GLD en PAVE blijven alleen researchproxy's / benchmarks. |
| Leveringsstatus | Geblokkeerd | Productielevering is niet toegestaan. |
| Portefeuilleautoriteit | Geblokkeerd | Geen financiering, kandidaatpromotie of portefeuillewijziging toegestaan. |

## Zichtbaar UCITS-universum

| Kandidaat | ISIN | Rol | Beurslijnen | Researchproxy | Cockpitstatus | Betekenis voor de lezer |
| --- | --- | --- | --- | --- | --- | --- |
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | Kernblootstelling Amerikaanse aandelen | CSPX.L, SXR8.DE | SPY | visible_review_candidate | Eerste reviewkandidaat met ISIN, UCITS-status, KID-beschikbaarheid en slotkoersbewijs. |
| VanEck Semiconductor UCITS ETF | IE00BMC38736 | Semiconductor thematische blootstelling | SMH / prijs pending | SMH | pricing_incomplete | Interessante thematische kandidaat, maar EU-beurslijn en prijssymbool moeten nog worden bevestigd. |
| iShares Physical Gold ETC | TBD | Goud / hard-asset hedge | SGLN / prijs pending | GLD | blocked_until_verified | Dit is een ETC-beleidszaak, geen UCITS ETF; geblokkeerd houden tot beleid dit expliciet toestaat. |
| iShares Global Infrastructure UCITS ETF | TBD | Infrastructuur / real-asset capex | INFR / prijs pending | PAVE | identity_incomplete | De lane is zichtbaar vanuit registry/proxy mapping, maar vraagt issuer-, ISIN-, KID- en beurslijnbevestiging. |

## Bewijskaart per kandidaat

| Kandidaat | Identiteitsbewijs | Prijsbewijs | Bewijsstatus | Bewijsgaten |
| --- | --- | --- | --- | --- |
| IE00B5BMR087 | ISIN, provider, UCITS, KID, TER, benchmark en beurslijnen aanwezig. | CSPX.L en SXR8.DE slotkoersbewijs aanwezig voor 2026-06-17. | source_evidence_available | Brokerlijnbevestiging en bredere integratie in wekelijkse input. |
| IE00BMC38736 | ISIN, fondsnaam, provider, UCITS-naamgeving, KID en TER aanwezig. | Prijssymbool blijft pending verification. | pricing_incomplete | EU-beurslijn, prijssymbool, domicile, distributiebeleid en replicatiemethode. |
| iShares Physical Gold ETC | Productnaam en ETC-karakter zichtbaar. | Prijssymbool blijft pending verification. | blocked_policy_case | ISIN, valuta, beurslijn, KID-status en ETC-beleidsautoriteit. |
| Infrastructure UCITS placeholder | Fondsnaam en thema zichtbaar vanuit bestaande config. | Prijssymbool blijft pending verification. | identity_incomplete | ISIN, issuerbevestiging, KID, TER, beurslijn en prijsbron. |

## Prijs- en identiteitsgaten

| Gat | Betrokken kandidaten | Waarom dit belangrijk is |
| --- | --- | --- |
| Geverifieerde dagelijkse slotkoers bestaat alleen voor CSPX.L en SXR8.DE | Alleen S&P 500 UCITS-kandidaat | Andere kandidaten halen nog niet dezelfde cockpit-bewijsstandaard. |
| Prijssymbool pending | Semiconductor, goud/ETC, infrastructuur | Geen valuation-grade of financieringsautoriteit op incomplete prijsregels. |
| ISIN ontbreekt | Goud/ETC, infrastructuur | Het EU-model is ISIN-first; ontbrekende ISIN blokkeert kandidaatpromotie. |
| Productbeleid onduidelijk | Goud/ETC | ETC-behandeling moet worden besloten voordat dit meer wordt dan een geblokkeerde beleidszaak. |

## Scheiding met researchproxy

| Amerikaanse proxy | EU/UCITS-kandidaatbeeld | Toegestaan gebruik | Geblokkeerd gebruik |
| --- | --- | --- | --- |
| SPY | IE00B5BMR087 via CSPX.L en SXR8.DE | Benchmark / researchproxy | EU-positie of financieringsbron |
| SMH | VanEck Semiconductor UCITS ETF, IE00BMC38736 | Semiconductor benchmarkreferentie | Amerikaanse ETF-positie |
| GLD | iShares Physical Gold ETC beleidszaak | Alleen goudreferentie | UCITS-positie tenzij ETC-beleid wijzigt |
| PAVE | Infrastructure UCITS placeholder | Infrastructuur researchvergelijker | Gefinancierde kandidaat vóór identiteitsverificatie |

## Actiekaart voor de lezer

| Vraag van de lezer | Cockpitantwoord | Actie nu |
| --- | --- | --- |
| Wat is veranderd sinds WP14N? | Het cockpitdatamodel toont nu vier geconfigureerde reviewlanes in plaats van één zichtbare kandidaat. | Beoordeel kandidaatdekking en gaten. |
| Welke kandidaat heeft nu het sterkste bewijs? | IE00B5BMR087 via CSPX.L en SXR8.DE. | Behouden als bewijsbaseline. |
| Welke kandidaten zijn interessant maar incompleet? | Semiconductor, infrastructuur en goud/ETC-beleidszaak. | Identiteit, prijsbasis en beleid aanvullen. |
| Wat is nu actiegericht? | Alleen productreview. | Geen portefeuilleactie. |
| Wat is niet actiegericht? | Levering, financiering, valuation-grade gebruik, kandidaatpromotie en portefeuillewijziging. | Geblokkeerd houden tot expliciete poorten veranderen. |

## Huidige blokkades

| Blokkade | Huidige status | Betekenis |
| --- | --- | --- |
| Leveringsautoriteit | remain_blocked | Geen e-mail, geen ontvangeractivatie, geen productiesend. |
| Portefeuillewijziging | false | Geen wijziging in posities of cash. |
| Kandidaatpromotie | false | Geen kandidaat is gepromoveerd naar financierbare status. |
| Financieringsautoriteit | false | Geen koop- of financieringsbesluit. |
| Valuation-grade autoriteit | false | Prijzen zijn bewijs voor review, geen officiële waarderingsautoriteit. |

## Bijlage — technisch bewijs

- Bron premium cockpit manifest: `output/client_surface/etf_eu_premium_cockpit_surface_20260618_000000.json`
- Bron symbol registry: `config/ucits_symbol_registry.yml`
- Bron proxy map: `config/ucits_benchmark_proxy_map.yml`
- Autorisatiebesluit: `output/delivery/etf_eu_delivery_authorization_decision_20260618_000000.json`
- Validator: `tools/validate_etf_eu_cockpit_universe_enrichment.py`
- Testbestand: `tests/test_etf_eu_cockpit_universe_enrichment.py`
