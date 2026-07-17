from __future__ import annotations

from typing import Any


def _money(value: Any, language: str) -> str:
    raw = f"{float(value or 0):,.2f}"
    if language == "nl":
        raw = raw.replace(",", "X").replace(".", ",").replace("X", ".")
    return "EUR " + raw


def reconcile_funded_markdown(text: str, state: dict[str, Any], *, language: str) -> str:
    portfolio = state.get("portfolio") or {}
    positions = list(portfolio.get("positions") or [])
    if not positions:
        return text

    cash = _money(portfolio.get("cash_eur"), language)
    tickers = [str(row.get("exchange_ticker") or row.get("ticker") or "").upper() for row in positions]
    position_names = ", ".join(tickers[:-1]) + (" en " if language == "nl" else " and ") + tickers[-1]

    if language == "nl":
        replacements = {
            "- **Actie:** geen transactie; EUR 100.000 cash behouden.": f"- **Actie:** {position_names} behouden; resterende liquiditeit {cash}.",
            "- **Reden:** de portefeuille bevat nog geen gefinancierde UCITS-posities en de huidige prijsrun levert marktobservaties, geen zelfstandige basis voor aankoop of waardering.": "- **Reden:** de modelportefeuille bevat drie gefinancierde UCITS-posities; de review richt zich nu op rol, bijdrage en overlap.",
            "- **Beste operationele kandidaat:** de geverifieerde S&P 500 UCITS-lijnen blijven het verst gevorderd voor verdere bevestiging bij de broker en van de handelslijn.": "- **Huidige positiegrondslag:** VWCE is de wereldwijde kern, EUNA de obligatiestabilisator en SXR8 de Amerikaanse overweging.",
            "- **Portefeuillebesluit:** cash behouden; geen instrument is door deze prijsrun automatisch geschikt geworden voor opname in de portefeuille.": "- **Portefeuillebesluit:** bestaande posities behouden; geen automatische uitbreiding of nieuwe positie.",
            "- **Kernaandelen:** operationeel het meest volwassen; SXR8 en CSPX blijven onderzoekskandidaten en zijn niet gefinancierd.": "- **Kernaandelen:** SXR8 is actief gefinancierd; CSPX blijft uitsluitend een alternatieve onderzoeks- en handelslijnreferentie.",
            "- **Core-aandelen:** operationeel het meest volwassen; SXR8 en CSPX blijven onderzoekskandidaten en zijn niet gefinancierd.": "- **Kernaandelen:** SXR8 is actief gefinancierd; CSPX blijft uitsluitend een alternatieve onderzoeks- en handelslijnreferentie.",
            "- **Wereldwijde aandelen:** IWDA, EUNL en VWCE blijven interessant voor brede spreiding, maar verificatie van handelslijn en bron is nog niet volledig.": "- **Wereldwijde aandelen:** VWCE is actief gefinancierd; IWDA en EUNL blijven ongefinancierde vergelijkingslijnen.",
            "- **Obligaties:** EUNA en AGGH kunnen later stabiliteit leveren; hun huidige rol blijft die van onderzoekskandidaat.": "- **Obligaties:** EUNA is actief gefinancierd als stabilisator; AGGH blijft een alias- of onderzoeksreferentie.",
            "- Rond verificatie van brokerbeschikbaarheid en EUR-handelslijnen af.": "- Bewaak VWCE, EUNA en SXR8 op rol, bijdrage, overlap en invalidatievoorwaarden.",
            "- Verbeter de bronovereenkomst voordat de prijsinformatie als voldoende betrouwbaar voor waardering kan worden beschouwd.": "- Verkrijg verse exact-line completed closes vóór iedere uitbreiding, reductie of nieuwe positie.",
            "- Herbeoordeel pas daarna of cash gedeeltelijk mag worden ingezet.": "- Laat satelliet- en lateretranchecapaciteit cash tenzij een afzonderlijk gevalideerd allocatiebesluit wijziging autoriseert.",
        }
    else:
        replacements = {
            "- **Action:** no trade; retain EUR 100,000 cash.": f"- **Action:** maintain {position_names}; remaining liquidity is {cash}.",
            "- **Reason:** the portfolio still has no funded UCITS positions and the current pricing run provides market observations, not an independent basis for purchase or valuation.": "- **Reason:** the model portfolio contains three funded UCITS positions; the review now focuses on role, contribution and overlap.",
            "- **Most advanced operational candidate:** the verified S&P 500 UCITS lines remain furthest advanced for broker and trading-line confirmation.": "- **Current position structure:** VWCE is the global core, EUNA the bond stabiliser and SXR8 the U.S. overweight.",
            "- **Portfolio decision:** retain cash; this pricing run did not automatically make any instrument eligible for portfolio inclusion.": "- **Portfolio decision:** maintain existing positions; no automatic add or new position.",
            "- **Core equity:** operationally most mature; SXR8 and CSPX remain research candidates and are not funded.": "- **Core equity:** SXR8 is actively funded; CSPX remains an alternative research and trading-line reference only.",
            "- **Global equity:** IWDA, EUNL and VWCE remain relevant for broad diversification, but trading-line and source verification is incomplete.": "- **Global equity:** VWCE is actively funded; IWDA and EUNL remain unfunded comparison lines.",
            "- **Bonds:** EUNA and AGGH may later provide stability; their current role remains that of research candidates.": "- **Bonds:** EUNA is actively funded as a stabiliser; AGGH remains an alias or research reference.",
            "- Complete broker availability and EUR trading-line verification.": "- Monitor VWCE, EUNA and SXR8 against role, contribution, overlap and invalidation conditions.",
            "- Improve source agreement before the pricing evidence is considered sufficiently reliable for valuation.": "- Obtain fresh exact-line completed closes before any add, reduction or new position.",
            "- Only then reassess whether part of the cash may be deployed.": "- Keep satellite and later-tranche capacity in cash unless a separate validated allocation decision authorises change.",
        }

    for old, new in replacements.items():
        text = text.replace(old, new)
    return text
