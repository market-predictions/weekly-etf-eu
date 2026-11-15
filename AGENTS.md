# AGENTS.md — werkwijze voor elke AI in deze repo (ChatGPT, Codex, Claude)

1. **Lees eerst `OUTCOME.md`.** Dat is het doel en de definitie van klaar. Lees daarna `v2/README.md` en bekijk de laatste run (log + PDF).
2. **Draai en kijk.** Geen wijziging zonder dat je het resultaat hebt gedraaid en bekeken. `python -m v2.acceptance` moet slagen.
3. **Kleinste stap naar het doel.** Verwijderen en vervangen hebben de voorkeur boven toevoegen. Herbouwen mag als het goedkoper is dan repareren; zeg dan waarom.
4. **Productkeuzes en alles onder "Alleen met akkoord van de eigenaar"** in `OUTCOME.md`: stel de eigenaar een korte vraag met opties. Al het andere beslis je zelf.
5. **Controles alleen op de uitkomst.** Elke controle noemt de concrete fout die ze voorkomt. Geen gesimuleerde rollen, certificeringsstappen, poorten op het proces of bewijsbestanden als doel.
6. **Documentatie:** alleen `OUTCOME.md` (incl. één regel per besluit), `AGENTS.md`, `README.md`, `v2/README.md`. Geen nieuwe plan-, status- of controledocumenten. Werk in uitvoering leeft in een PR en verdwijnt daarmee.
7. **Twee keer vast op hetzelfde?** Stop, vereenvoudig of vraag. Voeg geen bewaker toe.
8. **Eerlijk rapporteren:** zeg wat kapot is. Onderscheid gedraaid / gecontroleerd / aangenomen. Nooit succes melden zonder bewijs uit de run zelf.
9. **De AI rekent en beslist niets in het rapport.** Code rekent en beslist; de AI schrijft alleen tekst, en elk getal daarin moet in de feiten staan.
