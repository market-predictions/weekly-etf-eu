# OUTCOME — Weekly ETF Review (EU)

**Doel:** elke donderdag vóór 08:00 (NL-tijd) een correct, helder NL/EN-rapport over een regelgebaseerde
modelportefeuille van Europese UCITS-ETF's bij de lezers.

**Klaar als** (automatisch getoetst):
- de wekelijkse run is geslaagd en het rapport verzonden, of de eigenaar kreeg een waarschuwing (`v2-weekly.yml`);
- waarde = posities × koers + kas, tot op de cent, voor elke week in de historie (`acceptance.yml`);
- het rapport is maximaal 4 pagina's, zonder interne termen, en elk getal in de tekst staat in de berekende feiten (`acceptance.yml`);
- de regels houden zich aan de limieten van `v2/policy.yml` (`acceptance.yml`);
- geen marktinformatie ouder dan 10 dagen; geen hard gecodeerde markt- of beleidsteksten.

**Alleen met akkoord van de eigenaar:** naar lezers versturen (`v2/delivery.yml` → `live`) · ontvangers wijzigen ·
beleggingsregels of benchmark wijzigen (`v2/policy.yml`) · fondsen toevoegen aan of verwijderen uit de kern.

**Status:** zie de laatste run van *Weekly ETF Review (v2)* en de uitkomstmonitor in `market-predictions/control-plane`.

## Besluiten
- 2026-11-15 — Inflatieregel live (HICP ≥ 3% en stijgend → obligatiekern in IBGS). Positionering: meedoen met de markt, grote verliezen beperken; geen alfa-belofte.
- 2026-11-15 — Vaste kern (VWCE + EUNA) blijft; benchmark 70% VWCE / 30% EUNA; IWDA en SXR8 alleen referentie.
- 2026-11-15 — Werkwijze: uitkomst-eerst (dit bestand + `AGENTS.md`); oude opzet gearchiveerd in branch `archive/v1-pre-outcome-model-2026-11-15`.
- 2026-11-14 — Herbouw v2; startportefeuille 14 aug 2026; gratis data (Yahoo + Alpha Vantage); automatisch versturen; proefperiode alleen naar eigenaar.
