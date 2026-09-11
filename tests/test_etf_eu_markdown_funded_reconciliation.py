from __future__ import annotations

from runtime.reconcile_etf_eu_funded_markdown import reconcile_funded_markdown


def _state() -> dict:
    return {
        "portfolio": {
            "cash_eur": 60439.44,
            "positions": [
                {"exchange_ticker": "VWCE"},
                {"exchange_ticker": "EUNA"},
                {"exchange_ticker": "SXR8"},
            ],
        }
    }


def test_dutch_markdown_reconciles_funded_positions() -> None:
    source = "\n".join(
        [
            "- **Actie:** geen transactie; EUR 100.000 cash behouden.",
            "- **Reden:** de portefeuille bevat nog geen gefinancierde UCITS-posities en de huidige prijsrun levert marktobservaties, geen zelfstandige basis voor aankoop of waardering.",
            "- **Core-aandelen:** operationeel het meest volwassen; SXR8 en CSPX blijven onderzoekskandidaten en zijn niet gefinancierd.",
            "- **Obligaties:** EUNA en AGGH kunnen later stabiliteit leveren; hun huidige rol blijft die van onderzoekskandidaat.",
            "- Rond verificatie van brokerbeschikbaarheid en EUR-handelslijnen af.",
        ]
    )
    output = reconcile_funded_markdown(source, _state(), language="nl")
    assert "VWCE, EUNA en SXR8 behouden" in output
    assert "EUR 60.439,44" in output
    assert "SXR8 is actief gefinancierd" in output
    assert "EUNA is actief gefinancierd" in output
    assert "brokerbeschikbaarheid" not in output
    assert "nog geen gefinancierde UCITS-posities" not in output


def test_english_markdown_reconciles_funded_positions() -> None:
    source = "\n".join(
        [
            "- **Action:** no trade; retain EUR 100,000 cash.",
            "- **Reason:** the portfolio still has no funded UCITS positions and the current pricing run provides market observations, not an independent basis for purchase or valuation.",
            "- **Core equity:** operationally most mature; SXR8 and CSPX remain research candidates and are not funded.",
            "- **Bonds:** EUNA and AGGH may later provide stability; their current role remains that of research candidates.",
            "- Complete broker availability and EUR trading-line verification.",
        ]
    )
    output = reconcile_funded_markdown(source, _state(), language="en")
    assert "maintain VWCE, EUNA and SXR8" in output
    assert "EUR 60,439.44" in output
    assert "SXR8 is actively funded" in output
    assert "EUNA is actively funded" in output
    assert "broker availability" not in output
    assert "no funded UCITS positions" not in output
