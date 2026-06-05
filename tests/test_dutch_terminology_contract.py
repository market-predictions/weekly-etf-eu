from __future__ import annotations

from pathlib import Path

from runtime import nl_terminology as nl


def test_core_dutch_aliases_are_canonical() -> None:
    assert nl.localize_action_status("No") == "Nee"
    assert nl.localize_text_aliases("No / under review") == "Nee / onder herbeoordeling"
    assert nl.localize_action_status("Hold but replaceable") == "Aanhouden, maar vervangbaar"
    assert nl.localize_action_status("Smaller / under review") == "Kleiner / onder herbeoordeling"
    assert nl.localize_decision_status("Not fundable - close proof incomplete.") == "Niet geschikt voor allocatie — sluitkoersbevestiging is onvolledig."
    assert nl.localize_trigger_status("Upgrade challenger to valuation-grade pricing before any funding decision.") == "Verbeter de prijsbevestiging van het alternatief tot waarderingskwaliteit vóór een allocatiebesluit."


def test_terminology_contract_contains_delivery_surface_labels() -> None:
    assert nl.localize_label("Portfolio Action Snapshot") == "Portefeuille-acties"
    assert nl.localize_label("Current Position Review") == "Review huidige posities"
    assert nl.localize_label("Replacement Duel Table v2") == "Vervangingsanalyse"
    assert nl.localize_label("Portfolio value (EUR)") == "Portefeuillewaarde (EUR)"


def test_sitecustomize_has_no_dutch_enum_status_patch() -> None:
    source = Path("sitecustomize.py").read_text(encoding="utf-8")
    forbidden = [
        "DECISION_TRANSLATIONS.update",
        "TRIGGER_TRANSLATIONS.update",
        "Not fundable - close proof incomplete",
        "Replacement trigger watch - challenger leading over 3m",
        "Upgrade challenger to valuation-grade pricing before any funding decision",
    ]
    for token in forbidden:
        assert token not in source
