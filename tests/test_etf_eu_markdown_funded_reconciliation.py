from __future__ import annotations

from runtime.finalize_etf_eu_markdown_semantics import finalize_markdown_semantics
from runtime.reconcile_etf_eu_funded_markdown import reconcile_funded_markdown, validate_funded_markdown


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


def _primary_only_state() -> dict:
    return {
        "portfolio": {
            "cash_eur": 60439.44,
            "positions": [
                {
                    "exchange_ticker": "VWCE",
                    "pricing_status": "qualified_completed_close_primary_plus_verification",
                    "verification_status": "fresh_exact_unverified",
                }
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


def test_primary_only_funded_price_is_truthfully_disclosed_without_two_provider_claim() -> None:
    source = "\n".join(
        [
            "- **Action:** review current position.",
            "- **Reason:** current review.",
            "1 funded UCITS positions: VWCE",
        ]
    )
    output = reconcile_funded_markdown(source, _primary_only_state(), language="en")
    assert "1 of 1 funded lines have authorized exact-line completed-close pricing" in output
    assert "0 independently verified and 1 primary-authoritative without a current verifier" in output
    assert "two-provider completed-close consensus" not in output.casefold()
    assert validate_funded_markdown(output, _primary_only_state(), language="en") == []


def test_validator_rejects_retired_universal_two_provider_claim() -> None:
    stale = "\n".join(
        [
            "1 funded UCITS positions: VWCE",
            "1 of 1 funded lines have authorized exact-line completed-close pricing.",
            "A current price verification with two independent sources is available for all funded positions; spreads are immaterial.",
        ]
    )
    blockers = validate_funded_markdown(stale, _primary_only_state(), language="en")
    assert any("two independent sources" in blocker for blocker in blockers)


def test_finalizer_rewrites_retired_primary_verifier_wording() -> None:
    source = "\n".join(
        [
            "- **Reason:** current review.",
            "A current price verification with two independent sources is available for all funded positions; spreads are immaterial.",
            "Each position's current price is checked through two sources (Alpha Vantage and Yahoo).",
        ]
    )
    output = finalize_markdown_semantics(source, {}, language="en")
    assert "authorized exact-line completed-close primary price" in output
    assert "independent verification increases confidence" in output
    assert "two independent sources" not in output
    assert "checked through two sources" not in output
