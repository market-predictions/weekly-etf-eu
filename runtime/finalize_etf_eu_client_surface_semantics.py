from __future__ import annotations

import re
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any


def _ticker(row: dict[str, Any]) -> str:
    return str(row.get("ticker") or row.get("exchange_ticker") or "").strip().upper()


def _join(items: list[str], language: str) -> str:
    clean = [item for item in items if item]
    if not clean:
        return ""
    if len(clean) == 1:
        return clean[0]
    conjunction = " en " if language == "nl" else " and "
    return ", ".join(clean[:-1]) + conjunction + clean[-1]


def _replace_list_item(text: str, prefix: str, replacement: str) -> str:
    pattern = re.compile(r"<li>" + re.escape(prefix) + r".*?</li>", flags=re.IGNORECASE | re.DOTALL)
    return pattern.sub("<li>" + replacement + "</li>", text, count=1)


def _replace_english_no_regime_change_sentence(text: str) -> str:
    """Normalize donor English macro summary leakage on the Dutch client surface."""
    pattern = re.compile(
        r"No material regime change was recorded[^.<]*(?:\.[^<]*)?\.",
        flags=re.IGNORECASE,
    )
    replacement = (
        "Ten opzichte van de vorige review is geen materiële regimewijziging vastgesteld; "
        "de actuele marktbreedte en cross-asset bevestiging blijven onderdeel van de "
        "beschrijvende macrocontext en vormen op zichzelf geen allocatie-authority."
    )
    return pattern.sub(replacement, text)


def _funded_grade_count(positions: list[dict[str, Any]]) -> int:
    total = 0
    for row in positions:
        pricing = str(row.get("pricing_status") or "").strip().casefold()
        if pricing in {"fresh_exact_verified", "fresh_exact_unverified"}:
            total += 1
    return total


def _observed_line_count(state: dict[str, Any], funded_count: int) -> int:
    funnel = state.get("verification_funnel") if isinstance(state.get("verification_funnel"), dict) else {}
    try:
        observed = int(funnel.get("observed_lines") or 0)
    except (TypeError, ValueError):
        observed = 0
    return max(observed, funded_count)


def _apply_donor_equity_surface(text: str, state: dict[str, Any], language: str) -> str:
    """Materialize the final assured HTML equity surface using the donor PNG contract."""
    curve = state.get("equity_curve") if isinstance(state.get("equity_curve"), dict) else {}
    if curve.get("show_chart") is not True:
        return text

    from runtime.standalone_html_equity_embed import (
        materialize_standalone_equity_html,
        validate_standalone_html_equity,
    )

    with TemporaryDirectory(prefix="etf-eu-equity-") as tmp:
        chart_path = Path(tmp) / f"equity_curve_{language}.png"
        text = materialize_standalone_equity_html(
            text,
            state,
            language=language,
            chart_path=chart_path,
        )
    validate_standalone_html_equity(text, state)
    return text


def finalize_client_html_semantics(text: str, state: dict[str, Any], *, language: str) -> str:
    portfolio = state.get("portfolio") if isinstance(state.get("portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    if not positions:
        return text

    tickers = [_ticker(row) for row in positions if _ticker(row)]
    decision = state.get("current_allocation_decision") if isinstance(state.get("current_allocation_decision"), dict) else {}
    additions = [str(value).strip().upper() for value in decision.get("added_tickers") or [] if str(value).strip()]
    funded_count = len(positions)
    funded_grade = _funded_grade_count(positions)
    observed = _observed_line_count(state, funded_count)
    research_count = max(observed - funded_count, 0)

    if language == "nl":
        ticker_list = _join(tickers, "nl")
        addition_list = _join(additions, "nl")
        action = (
            f"Deze run: {addition_list} als modelposities toegevoegd via een expliciet current allocation decision; huidige modelportefeuille bevat {funded_count} posities — {ticker_list}. Geen echte brokeruitvoering."
            if additions
            else f"Deze run: {funded_count} beschermde modelposities actief — {ticker_list}; geen wijziging zonder actuele re-underwriting en afzonderlijk allocatiebesluit."
        )
        text = _replace_list_item(text, "Deze run:", action)
        text = _replace_list_item(
            text,
            "Meest volwassen implementatie:",
            f"Gefinancierde exact-line waardering: {funded_grade} van {funded_count} gefinancierde lijnen hebben valuation-grade exact completed-close pricing authority en vormen de actuele waarderingsbasis.",
        )
        text = _replace_list_item(
            text,
            "Belangrijkste blokkade:",
            f"Research-/vergelijkingslaag: {research_count} niet-gefinancierde prijsregels blijven research-only; marktprijsbeschikbaarheid creëert geen funding-authority.",
        )

        replacements = {
            "Prijsobservaties zijn nog niet waarderingswaardig.": f"De {funded_grade} gefinancierde exact-lines hebben valuation-grade exact completed-close pricing authority.",
            "Promoveer pas wanneer bronovereenkomst en prijslineage voldoende sterk zijn.": "Behoud exact requested-date primary-close authority als actuele waarderingsgate; onafhankelijke same-date verificatie verhoogt confidence maar is geen liveness-eis.",
            f"{observed} handelslijnen wachten nog op volledige verificatie.": f"{research_count} niet-gefinancierde prijsregels blijven research-/vergelijkingsevidence zonder funding-authority.",
            "Geen financiering vóór identiteit, KID, handelslijn en brokerbeschikbaarheid zijn bevestigd.": "Geen nieuwe financiering vóór identiteit, KID, exacte handelslijn, current re-underwriting, valuation-grade pricing en expliciet allocatiebesluit zijn bevestigd.",
            "Behoud kwaliteit en kasdiscipline; any allocation still requires a verified UCITS instrument, current pricing, re-underwriting and a separate capital decision.": "Behoud kwaliteit en kasdiscipline; iedere allocatie vereist een geverifieerd UCITS-instrument, actuele pricing, re-underwriting en een afzonderlijk kapitaalbesluit.",
            "Europese aandelen- of obligatieblootstelling blijft afhankelijk on UCITS identity, exact-line verification, current pricing, re-underwriting and a separate capital decision.": "Europese aandelen- of obligatieblootstelling blijft afhankelijk van UCITS-identiteit, exact-line verificatie, actuele pricing, re-underwriting en een afzonderlijk kapitaalbesluit.",
            "No material regime change was recorded versus the prior review; the Risk-on growth backdrop remained intact, market breadth is mixed, and cross-asset confirmation is mixed.": "Ten opzichte van de vorige review is geen materiële regimewijziging vastgesteld; de risk-on-groeiomgeving bleef intact, terwijl marktbreedte en cross-asset bevestiging gemengd zijn.",
            "0 lijn heeft geen bruikbare prijs in deze run.": "Alle huidige gefinancierde lijnen hebben bruikbare completed-close pricing; research-only lijnen blijven afzonderlijk geclassificeerd.",
            "Laat onopgeloste lijnen buiten vergelijking en allocatie.": "Laat onopgeloste researchlijnen buiten allocatie en maak hun bewijsstatus expliciet in vergelijking.",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        text = _replace_english_no_regime_change_sentence(text)

        required = [
            f"Gefinancierde exact-line waardering: {funded_grade} van {funded_count}",
            (f"Deze run: {addition_list} als modelposities toegevoegd" if additions else f"Deze run: {funded_count} beschermde modelposities actief"),
        ]
        forbidden = [
            "geen portefeuillewijziging geautoriseerd",
            "0 geverifieerde UCITS-handelslijnen",
            f"{observed} lijnen zijn nog niet volledig geverifieerd of geprijsd",
            "Prijsobservaties zijn nog niet waarderingswaardig",
            "any allocation still requires",
            "afhankelijk on UCITS identity",
            "No material regime change was recorded",
        ]
    else:
        ticker_list = _join(tickers, "en")
        addition_list = _join(additions, "en")
        action = (
            f"This run: added {addition_list} as model positions through an explicit current allocation decision; the current model portfolio contains {funded_count} positions — {ticker_list}. No real broker execution."
            if additions
            else f"This run: {funded_count} protected model positions are active — {ticker_list}; no change without current re-underwriting and a separate allocation decision."
        )
        text = _replace_list_item(text, "This run:", action)
        text = _replace_list_item(
            text,
            "Most mature implementation:",
            f"Funded exact-line valuation: {funded_grade} of {funded_count} funded lines have valuation-grade exact completed-close pricing authority and form the current valuation basis.",
        )
        text = _replace_list_item(
            text,
            "Main blocker:",
            f"Research/comparison layer: {research_count} unfunded pricing rows remain research-only; market-price availability creates no funding authority.",
        )
        replacements = {
            "Pricing observations are not yet valuation-grade.": f"The {funded_grade} funded exact lines have valuation-grade exact completed-close pricing authority.",
            "Promote only when source agreement and price lineage are sufficiently strong.": "Maintain exact requested-date primary-close authority as the current valuation gate; independent same-date verification raises confidence but is not a liveness requirement.",
            f"{observed} trading lines are still awaiting full verification.": f"{research_count} unfunded pricing rows remain research/comparison evidence without funding authority.",
            "No funding before identity, KID, trading line and broker availability are confirmed.": "No new funding before identity, KID, exact trading line, current re-underwriting, valuation-grade pricing and an explicit allocation decision are confirmed.",
            "0 lines have no usable price in this run.": "All current funded lines have usable completed-close pricing; research-only lines remain separately classified.",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        required = [
            f"Funded exact-line valuation: {funded_grade} of {funded_count}",
            (f"This run: added {addition_list} as model positions" if additions else f"This run: {funded_count} protected model positions are active"),
        ]
        forbidden = [
            "no portfolio change is authorised",
            "0 verified UCITS trading lines",
            f"{observed} lines are not yet fully verified or priced",
            "Pricing observations are not yet valuation-grade",
        ]

    missing = [token for token in required if token not in text]
    residuals = [token for token in forbidden if token.casefold() in text.casefold()]
    if missing or residuals:
        raise RuntimeError(
            "ETF EU final client HTML semantics failed: "
            + f"missing={missing}; residual_stale={residuals}"
        )
    return _apply_donor_equity_surface(text, state, language)
