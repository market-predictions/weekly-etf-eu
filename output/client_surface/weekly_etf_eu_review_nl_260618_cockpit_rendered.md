# Weekly ETF EU-review — gerenderde verrijkte cockpit POC

## Cockpitsamenvatting

- **Rapportstatus:** proof of concept / review-only.
- **Huidige stand:** de verrijkte UCITS-cockpit wordt deterministisch uit gestructureerde input gegenereerd; er is geen portefeuilleactie.
- **Status UCITS-universum:** 4 zichtbare reviewlanes worden uit het enrichment manifest gerenderd.
- **Belangrijkste bewijsgaten:** prijssymbooldekking, beurslijnverificatie, ISIN-aanvulling en beleid rond ETC-blootstelling.
- **Belangrijkste blokkade:** levering, financiering, valuation-grade gebruik, kandidaatpromotie en portefeuillewijziging blijven geblokkeerd.
- **Volgende productactie:** breid prijsbewijs per beurslijn uit voor de verrijkte cockpitkandidaten.

## Kaarten in één oogopslag

| Kaart | Status | Betekenis voor de lezer |
| --- | --- | --- |
| UCITS-universum | Gerenderd | 4 gestructureerde kandidaten zijn zichtbaar in de cockpit. |
| Identiteitsbewijs | Gemengd | ISIN-first identiteit blijft behouden; incomplete lanes blijven gemarkeerd. |
| Prijsbewijs | Gedeeltelijk | CSPX.L en SXR8.DE behouden prijsbewijs; andere regels blijven pending. |
| Proxy-scheiding | Behouden | SPY, SMH, GLD en PAVE zijn alleen researchproxy's / benchmarks. |
| Leveringsstatus | Geblokkeerd | delivery_authorization_decision=remain_blocked. |
| Portefeuilleautoriteit | Geblokkeerd | production_delivery=false; portfolio_mutation=false; candidate_promotion=false; funding_authority=false; valuation_grade=false. |

## Zichtbaar UCITS-universum

| Kandidaat | ISIN | Provider | UCITS-status | Beurslijnen | Researchproxy | Cockpitstatus |
| --- | --- | --- | --- | --- | --- | --- |
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | iShares / BlackRock | confirmed | CSPX.L (USD, London Stock Exchange), SXR8.DE (EUR, Xetra) | SPY | visible_review_candidate |
| VanEck Semiconductor UCITS ETF | IE00BMC38736 | VanEck | confirmed_by_fund_name | pending_verification (USD, primary_line_pending_verification) | SMH | pricing_incomplete |
| iShares Physical Gold ETC | TBD | iShares / BlackRock | not_ucits_etc | pending_verification (pending_verification, pending_verification) | GLD | blocked_until_verified |
| iShares Global Infrastructure UCITS ETF | TBD | iShares / BlackRock | pending_verification | pending_verification (pending_verification, pending_verification) | PAVE | identity_incomplete |

## Bewijskaart per kandidaat

| Kandidaat | Identiteitsbewijs | Prijsbewijs | Bewijsstatus | Bewijsgaten |
| --- | --- | --- | --- | --- |
| IE00B5BMR087 / iShares Core S&P 500 UCITS ETF USD (Acc) | UCITS=confirmed; KID=available; benchmark=S&P 500 Index | CSPX.L, SXR8.DE | source_evidence_available | broker_line_confirmation, weekly_input_integration |
| IE00BMC38736 / VanEck Semiconductor UCITS ETF | UCITS=confirmed_by_fund_name; KID=available; benchmark=semiconductor_equity_basket | pending_verification | pricing_incomplete | eu_exchange_line, pricing_symbol_yahoo, domicile, distribution_policy, replication_method |
| TBD / iShares Physical Gold ETC | UCITS=not_ucits_etc; KID=pending_verification; benchmark=LBMA gold price reference | pending_verification | blocked_policy_case | isin, trading_currency, exchange_line, kid_status, etc_policy_authority |
| TBD / iShares Global Infrastructure UCITS ETF | UCITS=pending_verification; KID=pending_verification; benchmark=FTSE Global Core Infrastructure reference_pending_verification | pending_verification | identity_incomplete | isin, issuer_confirmation, kid_status, ter, exchange_line, pricing_source |

## Prijs- en identiteitsgaten

| Gat | Betrokken gebied | Waarom dit belangrijk is |
| --- | --- | --- |
| Prijssymbolen pending | Semiconductor-, goud/ETC- en infrastructuurlanes | Deze lanes kunnen geen valuation-grade bewijs worden voordat prijsregels zijn geverifieerd. |
| ISIN-placeholders | Goud/ETC- en infrastructuurlanes | ISIN-first identiteit is verplicht vóór kandidaatpromotie. |
| ETC-beleid | Goud/ETC-lane | De goudcase blijft geblokkeerd totdat beleid dit expliciet toestaat. |

## Scheiding met researchproxy

| Amerikaanse proxy | Gerenderde EU/UCITS-weergave | Toegestaan gebruik | Geblokkeerd gebruik |
| --- | --- | --- | --- |
| SPY | iShares Core S&P 500 UCITS ETF USD (Acc) / IE00B5BMR087 | alleen benchmark / researchproxy | EU-positie, financieringsbron of portefeuillepositie |
| SMH | VanEck Semiconductor UCITS ETF / IE00BMC38736 | alleen benchmark / researchproxy | EU-positie, financieringsbron of portefeuillepositie |
| GLD | iShares Physical Gold ETC / TBD | alleen benchmark / researchproxy | EU-positie, financieringsbron of portefeuillepositie |
| PAVE | iShares Global Infrastructure UCITS ETF / TBD | alleen benchmark / researchproxy | EU-positie, financieringsbron of portefeuillepositie |

## Actiekaart voor de lezer

| Vraag van de lezer | Cockpitantwoord | Actie nu |
| --- | --- | --- |
| Wat is veranderd? | De cockpit wordt uit gestructureerde input gegenereerd. | Controleer renderdeterminisme. |
| Welke kandidaat heeft het sterkste bewijs? | IE00B5BMR087 via CSPX.L en SXR8.DE. | Behoud dit als bewijsbaseline. |
| Wat blijft geblokkeerd? | Levering, financiering, valuation-grade gebruik, kandidaatpromotie en portefeuillewijziging. | Geblokkeerd houden. |

## Huidige blokkades

| Blokkade | Huidige status | Betekenis |
| --- | --- | --- |
| Leveringsautoriteit | delivery_authorization_decision=remain_blocked | Geen e-mail, geen ontvangeractivatie, geen productiesend. |
| Productielevering | production_delivery=false | Geen rapportlevering ingeschakeld. |
| Portefeuillewijziging | portfolio_mutation=false | Geen wijziging in posities of cash. |
| Kandidaatpromotie | candidate_promotion=false | Geen kandidaat is gepromoveerd. |
| Financieringsautoriteit | funding_authority=false | Geen koop- of financieringsbesluit. |
| Valuation-grade autoriteit | valuation_grade=false | Prijzen blijven alleen reviewbewijs. |

## Bijlage — technisch bewijs

- Bron universe enrichment manifest: `output/client_surface/etf_eu_cockpit_universe_enrichment_20260618_000000.json`
- Render manifest: `output/client_surface/etf_eu_enriched_cockpit_render_20260618_000000.json`
- Renderer: `tools/render_etf_eu_enriched_cockpit.py`
- Validator: `tools/validate_etf_eu_enriched_cockpit_render.py`
- Testbestand: `tests/test_etf_eu_enriched_cockpit_render.py`
