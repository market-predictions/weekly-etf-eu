from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

from weasyprint import HTML

from runtime.render_etf_eu_client_grade_v2 import build_html


FORBIDDEN_CLIENT_PHRASES = (
    "reserve minimaal 7,50%",
    "reserve at least 7.50%",
    "strategisch doel",
    "strategic target",
    "fasedoel",
    "phase target",
    "drie gefinancierde modelposities",
    "three funded model positions",
    "alle drie gefinancierde posities",
    "all three funded positions",
)


def e(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def num(value: Any, language: str, decimals: int = 2) -> str:
    try:
        raw = f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return "n/a"
    return raw.replace(",", "X").replace(".", ",").replace("X", ".") if language == "nl" else raw


def money(value: Any, language: str) -> str:
    return "€ " + num(value, language)


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join("<th>" + e(item) + "</th>" for item in headers)
    body = "".join("<tr>" + "".join("<td>" + value + "</td>" for value in row) + "</tr>" for row in rows)
    return '<table class="data-table"><thead><tr>' + head + "</tr></thead><tbody>" + body + "</tbody></table>"


def ticker_of(row: dict[str, Any]) -> str:
    ticker = str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def whole(value: Any, language: str) -> str:
    try:
        amount = int(float(value))
    except (TypeError, ValueError):
        return "0"
    return f"{amount:,}".replace(",", ".") if language == "nl" else f"{amount:,}"


def joined(items: list[str], language: str) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    conjunction = " en " if language == "nl" else " and "
    return ", ".join(items[:-1]) + conjunction + items[-1]


def position_summary(positions: list[dict[str, Any]], language: str) -> str:
    return joined([f"{whole(row.get('shares'), language)} {ticker_of(row)}" for row in positions], language)


def _current_run_change_authorized(state: dict[str, Any]) -> bool:
    authority = state.get("authority") if isinstance(state.get("authority"), dict) else {}
    return bool(authority.get("portfolio_mutation") is True or authority.get("trade_ledger_mutation") is True)


def funded_overlay(state: dict[str, Any]) -> dict[str, Any]:
    """Add only current-state consistency metadata.

    Allocation map and position rows are already normalized by
    apply_etf_eu_donor_parity_contract. This layer must never recreate CAP01 targets,
    fixed cash floors or hard-coded funded-position counts.
    """
    state = dict(state)
    portfolio = dict(state.get("portfolio") or {})
    positions = [dict(row) for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    portfolio["positions"] = positions
    state["portfolio"] = portfolio
    if not positions:
        return state

    funded_tickers = [ticker_of(row) for row in positions if ticker_of(row)]
    funded_set = set(funded_tickers)

    lanes: list[dict[str, Any]] = []
    for source in state.get("opportunity_radar") or []:
        lane = dict(source)
        lane_tickers = {
            str(value).strip().upper()
            for value in (lane.get("candidate_tickers") or lane.get("tickers") or [])
        }
        active = sorted(lane_tickers & funded_set)
        lane["funded_count"] = len(active)
        lane["funded_tickers"] = active
        if active:
            lane["status"] = "funded_model_position_active"
            lane["next_confirmation_nl"] = "Bewaak rol, bijdrage, overlap en actuele re-underwriting; geen wijziging zonder verse evidence en afzonderlijk allocatiebesluit."
            lane["next_confirmation_en"] = "Monitor role, contribution, overlap and current re-underwriting; no change without fresh evidence and a separate allocation decision."
        lanes.append(lane)
    state["opportunity_radar"] = lanes

    funnel = dict(state.get("verification_funnel") or {})
    funnel["funded_positions"] = len(positions)
    funnel["cash_eur"] = portfolio.get("cash_eur")
    funnel["decision"] = "preserve_protected_funded_state_pending_current_reunderwriting_and_explicit_allocation_decision"
    state["verification_funnel"] = funnel

    next_run = dict(state.get("next_run_input") or {})
    existing_priority = [str(item).strip().upper() for item in next_run.get("priority_candidates") or []]
    next_run["priority_candidates"] = list(dict.fromkeys([*funded_tickers, *existing_priority]))
    next_run["required_actions"] = [
        f"re-underwrite every funded position ({', '.join(funded_tickers)}) from current evidence rather than historical target metadata",
        "obtain fresh exact-line completed closes before any add, reduction or new position",
        "run direct replacement duels for any replaceable or weakening holding",
        "classify material cash and apply deploy-or-explain only when a fully fundable actionable lane exists",
    ]
    state["next_run_input"] = next_run

    effects: list[dict[str, str]] = [
        {
            "driver_nl": f"{len(positions)} gefinancierde modelposities",
            "driver_en": f"{len(positions)} funded model positions",
            "first_nl": f"De beschermde modelportefeuille bevat {joined(funded_tickers, 'nl')}.",
            "first_en": f"The protected model portfolio contains {joined(funded_tickers, 'en')}.",
            "second_nl": "Iedere positie moet kapitaal per run opnieuw verdienen via fresh-cash en implementation re-underwriting.",
            "second_en": "Every position must re-earn capital each run through fresh-cash and implementation re-underwriting.",
            "implication_nl": "Een historische aankoop of doelweging geeft geen actuele Hold-, Add- of Reduce-authority.",
            "implication_en": "A historical purchase or target weight creates no current Hold, Add or Reduce authority.",
        }
    ]
    if {"VWCE", "SXR8"} <= funded_set:
        effects.append({
            "driver_nl": "VWCE plus directe SXR8-overweging",
            "driver_en": "VWCE plus direct SXR8 overweight",
            "first_nl": "Brede werelddekking bevat al Amerikaanse mega-capblootstelling naast de directe SXR8-positie.",
            "first_en": "Broad global exposure already contains U.S. mega-cap exposure alongside the direct SXR8 position.",
            "second_nl": "Tickerdiversificatie kan daardoor meer factoroverlap bevatten dan de positietelling suggereert.",
            "second_en": "Ticker diversification can therefore contain more factor overlap than the position count suggests.",
            "implication_nl": "Meet factoroverlap vóór verdere inzet; de donor-40%-regel is een concentratiewaarschuwing, geen position cap.",
            "implication_en": "Measure factor overlap before further deployment; the donor 40% rule is a concentration warning, not a position cap.",
        })
    if "EUNA" in funded_set:
        effects.append({
            "driver_nl": "EUNA als obligatiestabilisator",
            "driver_en": "EUNA as bond stabiliser",
            "first_nl": "De EUR-gehedgede aggregate-bondpositie kan renterisicospreiding toevoegen.",
            "first_en": "The EUR-hedged aggregate-bond position can add duration diversification.",
            "second_nl": "Ballastwerking is empirisch te toetsen en niet gegarandeerd.",
            "second_en": "Ballast behaviour is empirical and not guaranteed.",
            "implication_nl": "Hedge-/ballastvaliditeit moet expliciet worden herbeoordeeld.",
            "implication_en": "Hedge/ballast validity must be explicitly re-underwritten.",
        })
    if "L0CK" in funded_set:
        effects.append({
            "driver_nl": "L0CK cybersecurity-satelliet",
            "driver_en": "L0CK cybersecurity satellite",
            "first_nl": "De portefeuille heeft een expliciete cybersecurity-satelliet naast kernblootstellingen.",
            "first_en": "The portfolio has an explicit cybersecurity satellite alongside core exposures.",
            "second_nl": "Satellietbijdrage en overlap moeten afzonderlijk van de structurele cybersecurity-thesis worden gemeten.",
            "second_en": "Satellite contribution and overlap must be measured separately from the structural cybersecurity thesis.",
            "implication_nl": "Een geldige thesis rechtvaardigt niet automatisch het huidige instrument of gewicht.",
            "implication_en": "A valid thesis does not automatically justify the current instrument or weight.",
        })
    state["second_order_effects"] = effects

    authority = dict(state.get("authority") or {})
    authority.update({
        "model_position_present": True,
        "real_broker_execution": False,
        "broker_specific_permission_required_for_model": False,
        "broker_permission_required_for_real_execution": True,
    })
    state["authority"] = authority
    state["funded_consistency"] = {
        "position_count": len(positions),
        "funded_tickers": funded_tickers,
        "allocation_map_source": "donor_parity_normalized_current_state",
        "historical_target_copy_rendered": False,
        "broker_neutral_model_language": True,
    }
    return state


def position_table(state: dict[str, Any], language: str) -> str:
    positions = state.get("portfolio", {}).get("positions") or []
    headers = (
        ["Handelslijn", "Fonds", "ISIN", "Stukken", "Prijs", "Peildatum", "Marktwaarde", "Gewicht", "Re-underwriting"]
        if language == "nl"
        else ["Trading line", "Fund", "ISIN", "Shares", "Price", "Pricing date", "Market value", "Weight", "Re-underwriting"]
    )
    memory = {
        str(row.get("ticker") or "").upper(): row
        for row in state.get("recommendation_memory") or []
        if isinstance(row, dict)
    }
    rows: list[list[str]] = []
    for row in positions:
        ticker = ticker_of(row)
        decision = memory.get(ticker, {})
        reunderwriting = (
            "Actueel afgerond" if decision.get("reunderwriting_complete") is True else "Onopgelost · review vereist"
        ) if language == "nl" else (
            "Current and complete" if decision.get("reunderwriting_complete") is True else "Unresolved · review required"
        )
        rows.append([
            e(ticker),
            e(row.get("fund_name")),
            e(row.get("isin")),
            e(whole(row.get("shares"), language)),
            money(row.get("current_price_local"), language),
            e(row.get("price_date") or "n/a"),
            money(row.get("market_value_eur"), language),
            num(row.get("current_weight_pct"), language) + "%",
            e(reunderwriting),
        ])
    intro = (
        "Dit zijn de beschermde modelposities. Historische CAP01-/transition-doelgewichten zijn auditmetadata en worden niet als actuele targets weergegeven. Iedere wijziging vereist actuele re-underwriting en een afzonderlijk allocatiebesluit."
        if language == "nl"
        else
        "These are the protected model positions. Historical CAP01/transition target weights are audit metadata and are not displayed as current targets. Every change requires current re-underwriting and a separate allocation decision."
    )
    return '<div class="note-box">' + e(intro) + "</div>" + table(headers, rows)


def patch_copy(rendered: str, state: dict[str, Any], language: str) -> str:
    portfolio = state["portfolio"]
    positions = portfolio.get("positions") or []
    if not positions:
        return rendered

    count = len(positions)
    tickers = [ticker_of(row) for row in positions]
    ticker_list = joined(tickers, language)
    summary = position_summary(positions, language)
    invested = money(portfolio.get("invested_market_value_eur"), language)
    cash = money(portfolio.get("cash_eur"), language)
    mutation = _current_run_change_authorized(state)

    if language == "nl":
        weekly_action = (
            f"Deze run: een expliciete modelportefeuillewijziging is geautoriseerd; actuele staat bevat {count} posities — {summary}."
            if mutation else
            f"Deze run: geen portefeuillewijziging geautoriseerd; {count} beschermde modelposities actief — {summary}."
        )
        replacements = {
            "Cash behouden": f"{count} modelposities actief",
            "Eerste modelpositie actief": f"{count} modelposities actief",
            "De S&amp;P 500 UCITS-lijnen zijn operationeel het verst gevorderd, maar inzet van kapitaal vereist een afzonderlijk allocatiebesluit.": f"Beschermde modelportefeuille: {ticker_list}; iedere wijziging vereist actuele re-underwriting en afzonderlijk allocatiebesluit.",
            "Deze week: geen portefeuilletransactie; de EU-modelportefeuille blijft volledig in cash.": weekly_action,
            "Deze week: eerste modelaankoop uitgevoerd — 151 hele stukken VWCE.": weekly_action,
            "De portefeuille is nog niet belegd. Dit is een bewuste kapitaalbeschermingsstatus.": f"De modelportefeuille heeft {invested} belegd en {cash} cash; geen echte brokeruitvoering.",
            "Behoud EUR 100.000 cash totdat een afzonderlijk allocatiebesluit is genomen.": f"Behoud de beschermde staat ({ticker_list}) totdat actuele re-underwriting een afzonderlijk allocatiebesluit ondersteunt.",
            "Best onderbouwde implementatie:": "Geverifieerde implementatielijnen:",
            "Kies de gewenste broker- en valutalijn, versterk de prijsbasis en maak daarna pas de kapitaalbeslissing.": "Gebruik exacte handelslijn, actuele prijsbasis, re-underwriting en afzonderlijke allocatie-authority voor iedere wijziging.",
            "Ververs macrodata vóór productiepromotie.": "Gebruik donor-provenance om macroversheid fail-closed te beoordelen.",
            "Volgende actie vereist brokerbeschikbaarheid, actuele prijsbasis, bronovereenkomst en een afzonderlijk allocatiebesluit.": "Volgende actie: completeer actuele re-underwriting en wijzig niets zonder verse exacte-lijnprijzen en afzonderlijk allocatiebesluit.",
            "Versnel verificatie van SXR8/CSPX zonder het afzonderlijke allocatiebesluit over te slaan.": f"Re-underwrite {ticker_list}; beoordeel challengers via de donor→UCITS→pricing→fundability-keten.",
            "Geen inzet vóór identiteit, KID, broker en lijn zijn bevestigd.": "Geen inzet vóór identiteit, KID, exacte handelslijn, actuele prijsbasis, fundability en afzonderlijk allocatiebesluit zijn bevestigd.",
            "De prijzen zijn marktobservaties en geen zelfstandige basis voor waardering of aankoop.": "Prijsbewijs ondersteunt actuele modelwaardering en vergelijking; het creëert nooit zelfstandig funding- of brokerauthority.",
        }
    else:
        weekly_action = (
            f"This run: an explicit model-portfolio change is authorised; current state contains {count} positions — {summary}."
            if mutation else
            f"This run: no portfolio change is authorised; {count} protected model positions are active — {summary}."
        )
        replacements = {
            "Retain cash": f"{count} model positions active",
            "First model position active": f"{count} model positions active",
            "The S&amp;P 500 UCITS lines are operationally most advanced, but capital deployment requires a separate allocation decision.": f"Protected model portfolio: {ticker_list}; every change requires current re-underwriting and a separate allocation decision.",
            "This week: no portfolio transaction; the EU model portfolio remains fully in cash.": weekly_action,
            "This week: first model purchase executed — 151 whole shares of VWCE.": weekly_action,
            "The portfolio is not yet invested. This is a deliberate capital-preservation state.": f"The model portfolio has {invested} invested and {cash} in cash; no real broker execution.",
            "Retain EUR 100,000 cash until a separate allocation decision is made.": f"Preserve the protected state ({ticker_list}) until current re-underwriting supports a separate allocation decision.",
            "Best-supported implementation:": "Verified implementation lines:",
            "Select the preferred broker and currency line, strengthen pricing evidence, and only then make the capital decision.": "Use exact trading-line identity, current pricing, re-underwriting and separate allocation authority for every change.",
            "Refresh macro data before production promotion.": "Use donor provenance to fail-close macro freshness.",
            "Next action requires broker availability, current pricing, source agreement and a separate allocation decision.": "Next action: complete current re-underwriting and change nothing without fresh exact-line pricing and a separate allocation decision.",
            "Accelerate SXR8/CSPX verification without bypassing the separate allocation decision.": f"Re-underwrite {ticker_list}; assess challengers through the donor→UCITS→pricing→fundability chain.",
            "No allocation before identity, KID, broker and trading line are confirmed.": "No allocation before identity, KID, exact trading line, current pricing, fundability and a separate allocation decision are confirmed.",
            "Prices are market observations and not an independent basis for valuation or purchase.": "Pricing evidence supports current model valuation and comparison; it never creates funding or broker authority on its own.",
        }
    for old, new in replacements.items():
        rendered = rendered.replace(old, new)
    return rendered.replace("<p>Position analysis active.</p>", position_table(state, language))


def validate_client_surface(rendered: str, state: dict[str, Any]) -> None:
    lowered = rendered.lower()
    for phrase in FORBIDDEN_CLIENT_PHRASES:
        if phrase.lower() in lowered:
            raise RuntimeError(f"ETF_EU_RETIRED_CLIENT_COPY_LEAK={phrase}")
    funded = [ticker_of(row) for row in state.get("portfolio", {}).get("positions") or [] if ticker_of(row)]
    missing = [ticker for ticker in funded if ticker not in rendered]
    if missing:
        raise RuntimeError(f"ETF_EU_FUNDED_TICKER_MISSING_FROM_CLIENT_SURFACE={missing}")
    if "50% maximum" in lowered or "35% minimum" in lowered or "15% maximum" in lowered:
        raise RuntimeError("ETF_EU_RETIRED_50_35_15_POLICY_LEAK")


def render(state_path: Path, language: str, html_output: Path, pdf_output: Path) -> None:
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("state_valid") is not True:
        raise RuntimeError("Invalid report state: " + str(state.get("blockers")))
    state = funded_overlay(state)
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    rendered = patch_copy(build_html(state, language), state, language)
    validate_client_surface(rendered, state)
    html_output.parent.mkdir(parents=True, exist_ok=True)
    pdf_output.parent.mkdir(parents=True, exist_ok=True)
    html_output.write_text(rendered, encoding="utf-8")
    HTML(string=rendered, base_url=str(state_path.parent.resolve())).write_pdf(str(pdf_output))
    if not pdf_output.exists() or pdf_output.stat().st_size <= 0:
        raise RuntimeError("PDF output was not created")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True)
    parser.add_argument("--language", choices=["nl", "en"], required=True)
    parser.add_argument("--html-output", required=True)
    parser.add_argument("--pdf-output", required=True)
    args = parser.parse_args()
    render(Path(args.state), args.language, Path(args.html_output), Path(args.pdf_output))
    print("ETF_EU_CLIENT_GRADE_V2_FUNDED_RENDER_OK | language=" + args.language)


if __name__ == "__main__":
    main()
