from __future__ import annotations

from typing import Any


def _money(value: Any, language: str) -> str:
    raw = f"{float(value or 0):,.2f}"
    if language == "nl":
        raw = raw.replace(",", "X").replace(".", ",").replace("X", ".")
    return "EUR " + raw


def _ticker(row: dict[str, Any]) -> str:
    return str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()


def _join_tickers(tickers: list[str], language: str) -> str:
    clean = [ticker for ticker in tickers if ticker]
    if not clean:
        return ""
    if len(clean) == 1:
        return clean[0]
    conjunction = " en " if language == "nl" else " and "
    return ", ".join(clean[:-1]) + conjunction + clean[-1]


def validate_funded_markdown(text: str, state: dict[str, Any], *, language: str) -> list[str]:
    portfolio = state.get("portfolio") if isinstance(state.get("portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    if not positions:
        return []

    blockers: list[str] = []
    tickers = [_ticker(row) for row in positions if _ticker(row)]
    folded = text.casefold()

    count_token = (
        f"{len(positions)} gefinancierde ucits-posities"
        if language == "nl"
        else f"{len(positions)} funded ucits positions"
    )
    if count_token.casefold() not in folded:
        blockers.append("dynamic funded position count missing from Markdown")

    for ticker in tickers:
        if ticker.casefold() not in folded:
            blockers.append(f"funded ticker missing from Markdown: {ticker}")

    forbidden = (
        [
            "drie gefinancierde ucits-posities",
            "reserve minimaal 7,50%",
            "vaste 7,50% reserve",
            "strategisch doelgewicht",
            "fase-doelgewicht",
            "fasedoelgewicht",
            "do not allocate capital to thematic or gold exposure",
        ]
        if language == "nl"
        else [
            "three funded ucits positions",
            "minimum cash reserve 7.50%",
            "fixed 7.50% reserve",
            "strategic target weight",
            "phase target weight",
        ]
    )
    for token in forbidden:
        if token.casefold() in folded:
            blockers.append(f"retired/stale Markdown wording present: {token}")
    return blockers


def reconcile_funded_markdown(text: str, state: dict[str, Any], *, language: str) -> str:
    portfolio = state.get("portfolio") if isinstance(state.get("portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    if not positions:
        return text

    cash = _money(portfolio.get("cash_eur"), language)
    tickers = [_ticker(row) for row in positions if _ticker(row)]
    position_names = _join_tickers(tickers, language)
    count = len(positions)

    if language == "nl":
        replacements = {
            "- **Actie:** geen transactie; EUR 100.000 cash behouden.": f"- **Actie:** {position_names} als huidige modelposities beoordelen; resterende liquiditeit {cash}.",
            "- **Reden:** de portefeuille bevat nog geen gefinancierde UCITS-posities en de huidige prijsrun levert marktobservaties, geen zelfstandige basis voor aankoop of waardering.": f"- **Reden:** de modelportefeuille bevat {count} gefinancierde UCITS-posities ({position_names}); de review gebruikt actuele state, completed-close prijsbewijs en re-underwriting.",
            "- **Beste operationele kandidaat:** de geverifieerde S&P 500 UCITS-lijnen blijven het verst gevorderd voor verdere bevestiging bij de broker en van de handelslijn.": f"- **Huidige positiegrondslag:** {position_names}; rollen, bijdrage, overlap en re-underwriting komen uit de actuele genormaliseerde state.",
            "- **Niet doen:** do not allocate capital to thematic or gold exposure until identity, KID, trading-line and product-policy checks are complete.": "- **Niet doen:** geen nieuw kapitaal toewijzen uitsluitend op basis van proxy, mapping of prijsbeschikbaarheid; identiteit, KID, exacte handelslijn, re-underwriting en expliciet allocatiebesluit blijven verplicht.",
            "- **Portefeuillebesluit:** cash behouden; geen instrument is door deze prijsrun automatisch geschikt geworden voor opname in de portefeuille.": "- **Portefeuillebesluit:** bestaande posities blijven uitsluitend onder actuele re-underwriting; mapping of pricing alleen creëert geen Add/Hold/Reduce- of funding-authority.",
            "- **Kernaandelen:** operationeel het meest volwassen; SXR8 en CSPX blijven onderzoekskandidaten en zijn niet gefinancierd.": "- **Kernaandelen:** funded/unfunded status wordt uitsluitend uit de protected portfolio state afgeleid; research-alternatieven blijven niet-gefinancierde vergelijkingslijnen.",
            "- **Core-aandelen:** operationeel het meest volwassen; SXR8 en CSPX blijven onderzoekskandidaten en zijn niet gefinancierd.": "- **Kernaandelen:** funded/unfunded status wordt uitsluitend uit de protected portfolio state afgeleid; research-alternatieven blijven niet-gefinancierde vergelijkingslijnen.",
            "- **Wereldwijde aandelen:** IWDA, EUNL en VWCE blijven interessant voor brede spreiding, maar verificatie van handelslijn en bron is nog niet volledig.": "- **Wereldwijde aandelen:** actuele funded status en exacte lijnidentiteit komen uit protected state plus UCITS-registry; alternatieven blijven research-only tenzij alle fundability-gates passeren.",
            "- **Obligaties:** EUNA en AGGH kunnen later stabiliteit leveren; hun huidige rol blijft die van onderzoekskandidaat.": "- **Obligaties:** actuele funded status en rol komen uit protected state en current re-underwriting; alternatieven blijven research-only zonder expliciet allocatiebesluit.",
            "- Rond verificatie van brokerbeschikbaarheid en EUR-handelslijnen af.": f"- Herbeoordeel {position_names} op fresh-cash, bijdrage, overlap, invalidatievoorwaarden en beste alternatief.",
            "- Verbeter de bronovereenkomst voordat de prijsinformatie als voldoende betrouwbaar voor waardering kan worden beschouwd.": "- Vereis voor iedere gefinancierde lijn verse exact-line completed-close evidence met twee-provider consensus vóór current valuation/re-underwriting.",
            "- Herbeoordeel pas daarna of cash gedeeltelijk mag worden ingezet.": "- Classificeer materiële cash via de donor cash-discipline; alleen een afzonderlijk expliciet allocatiebesluit mag funding wijzigen.",
        }
    else:
        replacements = {
            "- **Action:** no trade; retain EUR 100,000 cash.": f"- **Action:** review {position_names} as the current model positions; remaining liquidity is {cash}.",
            "- **Reason:** the portfolio still has no funded UCITS positions and the current pricing run provides market observations, not an independent basis for purchase or valuation.": f"- **Reason:** the model portfolio contains {count} funded UCITS positions ({position_names}); the review uses current state, completed-close pricing evidence and re-underwriting.",
            "- **Most advanced operational candidate:** the verified S&P 500 UCITS lines remain furthest advanced for broker and trading-line confirmation.": f"- **Current position structure:** {position_names}; roles, contribution, overlap and re-underwriting are derived from the current normalized state.",
            "- **Portfolio decision:** retain cash; this pricing run did not automatically make any instrument eligible for portfolio inclusion.": "- **Portfolio decision:** existing positions remain subject to current re-underwriting; mapping or pricing alone creates no Add/Hold/Reduce or funding authority.",
            "- **Core equity:** operationally most mature; SXR8 and CSPX remain research candidates and are not funded.": "- **Core equity:** funded/unfunded status is derived only from protected portfolio state; research alternatives remain unfunded comparison lines.",
            "- **Global equity:** IWDA, EUNL and VWCE remain relevant for broad diversification, but trading-line and source verification is incomplete.": "- **Global equity:** current funded status and exact-line identity come from protected state plus the UCITS registry; alternatives remain research-only unless all fundability gates pass.",
            "- **Bonds:** EUNA and AGGH may later provide stability; their current role remains that of research candidates.": "- **Bonds:** current funded status and role come from protected state and current re-underwriting; alternatives remain research-only without an explicit allocation decision.",
            "- Complete broker availability and EUR trading-line verification.": f"- Re-underwrite {position_names} on fresh cash, contribution, overlap, invalidation conditions and best alternative.",
            "- Improve source agreement before the pricing evidence is considered sufficiently reliable for valuation.": "- Require fresh exact-line completed-close evidence with two-provider consensus for every funded line before current valuation/re-underwriting.",
            "- Only then reassess whether part of the cash may be deployed.": "- Classify material cash through donor cash discipline; only a separate explicit allocation decision may change funding.",
        }

    for old, new in replacements.items():
        text = text.replace(old, new)

    blockers = validate_funded_markdown(text, state, language=language)
    if blockers:
        raise RuntimeError("Funded Markdown reconciliation failed: " + "; ".join(blockers))
    return text
