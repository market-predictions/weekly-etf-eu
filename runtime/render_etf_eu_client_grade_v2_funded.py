from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

from weasyprint import HTML

from runtime.render_etf_eu_client_grade_v2 import build_html


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
    return str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()


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


def funded_overlay(state: dict[str, Any]) -> dict[str, Any]:
    state = dict(state)
    portfolio = dict(state.get("portfolio") or {})
    positions = [dict(row) for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    if not positions:
        return state

    nav = float(portfolio.get("nav_eur") or 0.0)
    cash = float(portfolio.get("cash_eur") or 0.0)
    cash_weight = round(cash / nav * 100.0, 2) if nav else 0.0
    by_ticker = {ticker_of(row): row for row in positions if ticker_of(row)}
    funded_tickers = list(by_ticker)

    allocation_map: list[dict[str, str]] = [
        {
            "segment_nl": "Cash",
            "segment_en": "Cash",
            "stance_nl": f"Huidig {cash_weight:.2f}% · reserve minimaal 7,50%",
            "stance_en": f"Current {cash_weight:.2f}% · reserve at least 7.50%",
            "note_nl": "Resterende doelcapaciteit blijft cash en wordt niet automatisch naar andere thema’s doorgeschoven.",
            "note_en": "Remaining target capacity stays in cash and is not automatically redistributed to other themes.",
        }
    ]

    detail_rows = [
        ("VWCE", "Wereldwijde aandelenkern", "Global equity core"),
        ("SXR8", "Amerikaanse aandelenoverweging", "U.S. equity overweight"),
        ("EUNA", "Wereldwijde obligatiestabilisator", "Global aggregate-bond stabiliser"),
    ]
    for ticker, segment_nl, segment_en in detail_rows:
        row = by_ticker.get(ticker)
        if not row:
            continue
        weight = float(row.get("current_weight_pct") or 0.0)
        strategic = float(row.get("strategic_target_weight_pct") or row.get("target_weight_pct") or 0.0)
        shares_nl = whole(row.get("shares"), "nl")
        shares_en = whole(row.get("shares"), "en")
        if ticker == "SXR8":
            note_nl = f"{shares_nl} stukken SXR8 actief; een tweede tranche is niet geautoriseerd."
            note_en = f"{shares_en} shares of SXR8 are active; a second tranche is not authorised."
        else:
            note_nl = f"{shares_nl} stukken {ticker} actief; extra inzet vereist een nieuw, afzonderlijk allocatiebesluit."
            note_en = f"{shares_en} shares of {ticker} are active; additional deployment requires a new separate allocation decision."
        allocation_map.append(
            {
                "segment_nl": segment_nl,
                "segment_en": segment_en,
                "stance_nl": f"Actief {weight:.2f}% · strategisch doel {strategic:.2f}%",
                "stance_en": f"Active {weight:.2f}% · strategic target {strategic:.2f}%",
                "note_nl": note_nl,
                "note_en": note_en,
            }
        )

    allocation_map.extend(
        [
            {
                "segment_nl": "Satellieten",
                "segment_en": "Satellites",
                "stance_nl": "Nog niet gefinancierd",
                "stance_en": "Not funded",
                "note_nl": "SXRV en semiconductorblootstelling vereisen exacte lijnidentiteit, verse prijzen, concentratiecontrole en een afzonderlijk besluit.",
                "note_en": "SXRV and semiconductor exposure require exact-line identity, fresh pricing, concentration review and a separate decision.",
            },
            {
                "segment_nl": "Goud / harde activa",
                "segment_en": "Gold / hard assets",
                "stance_nl": "Beleidsmatig geblokkeerd",
                "stance_en": "Policy blocked",
                "note_nl": "De ETC-structuur valt buiten het huidige UCITS-only beleid.",
                "note_en": "The ETC structure remains outside the current UCITS-only policy.",
            },
        ]
    )
    state["allocation_map"] = allocation_map

    lanes: list[dict[str, Any]] = []
    funded_set = set(funded_tickers)
    for source in state.get("opportunity_radar") or []:
        lane = dict(source)
        lane_tickers = {str(value).strip().upper() for value in (lane.get("candidate_tickers") or lane.get("tickers") or [])}
        active = sorted(lane_tickers & funded_set)
        lane["funded_count"] = len(active)
        lane["funded_tickers"] = active
        if active:
            lane["status"] = "funded_model_position_active"
            lane["implementation_score"] = 5
            lane["next_confirmation_nl"] = "Bewaak rol, bijdrage en overlap; geen uitbreiding zonder verse completed close, concentratiecontrole en afzonderlijk allocatiebesluit."
            lane["next_confirmation_en"] = "Monitor role, contribution and overlap; do not add without a fresh completed close, concentration review and a separate allocation decision."
        elif lane.get("status") == "operationally_mature_not_funded":
            lane["next_confirmation_nl"] = "Bevestig de exacte handelslijn, een verse completed close en een afzonderlijk allocatiebesluit."
            lane["next_confirmation_en"] = "Confirm the exact trading line, a fresh completed close and a separate allocation decision."
        lanes.append(lane)
    state["opportunity_radar"] = lanes

    funnel = dict(state.get("verification_funnel") or {})
    funnel.update(
        {
            "funded_positions": len(positions),
            "cash_eur": cash,
            "decision": "maintain_three_position_model_portfolio_and_require_separate_authority_for_any_change",
        }
    )
    state["verification_funnel"] = funnel

    next_run = dict(state.get("next_run_input") or {})
    next_run["priority_candidates"] = [*funded_tickers, "SXRV", "SMH"]
    next_run["required_actions"] = [
        "monitor VWCE, EUNA and SXR8 against role, contribution, overlap and invalidation conditions",
        "obtain fresh exact-line completed closes before any add, reduction or new position",
        "review global-equity overlap between VWCE and the direct SXR8 overweight",
        "keep satellite and later-tranche capacity in cash unless a separate validated allocation decision authorises change",
    ]
    state["next_run_input"] = next_run

    state["second_order_effects"] = [
        {
            "driver_nl": "Drie gefinancierde modelposities",
            "driver_en": "Three funded model positions",
            "first_nl": "VWCE, EUNA en SXR8 brengen wereldwijde aandelen-, obligatie- en Amerikaanse overweging samen.",
            "first_en": "VWCE, EUNA and SXR8 combine global equity, aggregate bonds and a direct U.S. overweight.",
            "second_nl": "Rendement, stabilisatie en overlap worden nu afzonderlijk meetbaar.",
            "second_en": "Return, stabilisation and overlap are now separately observable.",
            "implication_nl": "Beoordeel iedere positie op rol en bijdrage; wijzig niets zonder afzonderlijk besluit.",
            "implication_en": "Review every position by role and contribution; change nothing without a separate decision.",
        },
        {
            "driver_nl": "VWCE plus directe SXR8-overweging",
            "driver_en": "VWCE plus direct SXR8 overweight",
            "first_nl": "De portefeuille heeft brede werelddekking met aanvullende Amerikaanse blootstelling.",
            "first_en": "The portfolio combines broad global coverage with additional U.S. exposure.",
            "second_nl": "De feitelijke Amerikaanse weging is hoger dan de afzonderlijke SXR8-weging suggereert.",
            "second_en": "Effective U.S. exposure is higher than the standalone SXR8 weight suggests.",
            "implication_nl": "Meet overlap vóór een tweede SXR8-tranche of verdere wereldwijde aandeleninzet.",
            "implication_en": "Measure overlap before a second SXR8 tranche or further global-equity deployment.",
        },
        {
            "driver_nl": "EUNA als obligatiestabilisator",
            "driver_en": "EUNA as bond stabiliser",
            "first_nl": "De EUR-gehedgede aggregate-bondpositie voegt renterisicospreiding toe.",
            "first_en": "The EUR-hedged aggregate-bond position adds duration diversification.",
            "second_nl": "De stabiliserende werking kan afnemen bij gelijktijdige rente- en aandelenstress.",
            "second_en": "Its stabilising effect may weaken during simultaneous rate and equity stress.",
            "implication_nl": "Volg bijdrage en correlatie; behandel EUNA niet als gegarandeerde bescherming.",
            "implication_en": "Monitor contribution and correlation; do not treat EUNA as guaranteed protection.",
        },
        {
            "driver_nl": "Technologie- en halfgeleiderkandidaten",
            "driver_en": "Technology and semiconductor candidates",
            "first_nl": "Hogere structurele groeiblootstelling.",
            "first_en": "Higher structural growth exposure.",
            "second_nl": "Meer factorconcentratie en hogere volatiliteit dan brede kernblootstelling.",
            "second_en": "Greater factor concentration and volatility than broad core exposure.",
            "implication_nl": "Behandel als satellietblootstelling en vereis een afzonderlijk allocatiebesluit.",
            "implication_en": "Treat as satellite exposure and require a separate allocation decision.",
        },
    ]

    risks = []
    for source in state.get("risks") or []:
        item = dict(source)
        item["invalidation_nl"] = str(item.get("invalidation_nl") or "").replace(
            "identiteit, KID, handelslijn en brokerbeschikbaarheid",
            "identiteit, KID, exacte handelslijn, actuele prijsbasis en afzonderlijk allocatiebesluit",
        )
        item["invalidation_en"] = str(item.get("invalidation_en") or "").replace(
            "identity, KID, trading line and broker availability",
            "identity, KID, exact trading line, current pricing and a separate allocation decision",
        )
        risks.append(item)
    state["risks"] = risks

    macro = dict(state.get("macro") or {})
    macro["what_changed"] = [
        "The model portfolio now holds VWCE, EUNA and SXR8; review shifts from activation to contribution and overlap.",
        "AI and semiconductor leadership keeps the satellite watchlist relevant, but concentration risk still blocks automatic funding.",
    ]
    macro["portfolio_implications"] = [
        str(item)
        .replace("selected UCITS trading line, broker availability and current pricing are jointly verified", "selected UCITS trading line and current pricing are verified and a separate allocation decision exists")
        .replace("selected UCITS trading line, broker availability and current pricing", "selected UCITS trading line, current pricing and separate allocation authority")
        for item in macro.get("portfolio_implications") or []
    ]
    state["macro"] = macro

    authority = dict(state.get("authority") or {})
    authority.update(
        {
            "model_position_present": True,
            "real_broker_execution": False,
            "broker_specific_permission_required_for_model": False,
            "broker_permission_required_for_real_execution": True,
        }
    )
    state["authority"] = authority
    state["funded_consistency"] = {
        "position_count": len(positions),
        "funded_tickers": funded_tickers,
        "allocation_map_reconciled": True,
        "opportunity_radar_reconciled": True,
        "broker_neutral_model_language": True,
    }
    return state


def position_table(state: dict[str, Any], language: str) -> str:
    positions = state.get("portfolio", {}).get("positions") or []
    headers = ["Handelslijn", "Fonds", "ISIN", "Stukken", "Prijs", "Peildatum", "Marktwaarde", "Gewicht", "Fasedoel", "Status"] if language == "nl" else ["Trading line", "Fund", "ISIN", "Shares", "Price", "Pricing date", "Market value", "Weight", "Phase target", "Status"]
    rows: list[list[str]] = []
    for row in positions:
        status = "Modelpositie · geen brokerorder" if language == "nl" else "Model position · no brokerage order"
        rows.append([e(ticker_of(row)), e(row.get("fund_name")), e(row.get("isin")), e(whole(row.get("shares"), language)), money(row.get("current_price_local"), language), e(row.get("price_date") or "n/a"), money(row.get("market_value_eur"), language), num(row.get("current_weight_pct"), language) + "%", num(row.get("phase_target_weight_pct") or row.get("target_weight_pct"), language) + "%", e(status)])
    intro = "De gefinancierde posities zijn uitsluitend in de repository-modelportefeuille verwerkt. Resterende doelcapaciteit blijft cash totdat een afzonderlijk besluit wijziging autoriseert." if language == "nl" else "The funded positions exist only in the repository model portfolio. Remaining target capacity stays in cash until a separate decision authorises change."
    return '<div class="note-box">' + e(intro) + "</div>" + table(headers, rows)


def patch_copy(rendered: str, state: dict[str, Any], language: str) -> str:
    portfolio = state["portfolio"]
    positions = portfolio.get("positions") or []
    if not positions:
        return rendered

    count = len(positions)
    summary = position_summary(positions, language)
    invested = money(portfolio.get("invested_market_value_eur"), language)
    cash = money(portfolio.get("cash_eur"), language)
    new_positions = [row for row in positions if float(row.get("shares_delta_this_run") or 0) > 0]
    held_positions = [row for row in positions if row not in new_positions]
    new_summary = position_summary(new_positions, language)
    held_summary = joined([ticker_of(row) for row in held_positions], language)

    if language == "nl":
        weekly_action = (
            f"Deze week: eerste tranches toegevoegd in {new_summary}; {held_summary} aangehouden."
            if new_positions and held_positions
            else f"Deze week: {count} gefinancierde modelposities actief — {summary}."
        )
        replacements = {
            "Cash behouden": f"{count} modelposities actief",
            "Eerste modelpositie actief": f"{count} modelposities actief",
            "De S&amp;P 500 UCITS-lijnen zijn operationeel het verst gevorderd, maar inzet van kapitaal vereist een afzonderlijk allocatiebesluit.": f"Actieve modelportefeuille: {summary}; resterende doelcapaciteit blijft cash.",
            "De eerste tranche is geactiveerd: 151 hele stukken VWCE; geblokkeerde doelgewichten blijven cash.": f"Actieve modelportefeuille: {summary}; resterende doelcapaciteit blijft cash.",
            "Deze week: geen portefeuilletransactie; de EU-modelportefeuille blijft volledig in cash.": weekly_action,
            "Deze week: eerste modelaankoop uitgevoerd — 151 hele stukken VWCE.": weekly_action,
            "Volgende actie vereist brokerbeschikbaarheid, actuele prijsbasis, bronovereenkomst en een afzonderlijk allocatiebesluit.": "Volgende actie: bewaak rol, bijdrage en overlap; wijzig niets zonder verse prijzen en een afzonderlijk allocatiebesluit.",
            "Volgende actie: bewaak bijdrage en relatieve kracht; activeer geen volgend doelgewicht voordat de eigen verificatiegates slagen.": "Volgende actie: bewaak rol, bijdrage en overlap; wijzig niets zonder verse prijzen en een afzonderlijk allocatiebesluit.",
            "Versnel verificatie van SXR8/CSPX zonder het afzonderlijke allocatiebesluit over te slaan.": "Behoud VWCE, EUNA en SXR8; laat resterende capaciteit cash en beoordeel iedere wijziging afzonderlijk.",
            "Behoud de eerste tranche; laat geblokkeerde capaciteit cash en beoordeel de volgende tranche alleen met verse prijzen.": "Behoud VWCE, EUNA en SXR8; laat resterende capaciteit cash en beoordeel iedere wijziging afzonderlijk.",
            "De portefeuille is nog niet belegd. Dit is een bewuste kapitaalbeschermingsstatus.": f"De modelportefeuille heeft nu {invested} belegd en {cash} cash. Er is geen echte brokerorder geplaatst.",
            "Behoud EUR 100.000 cash totdat een afzonderlijk allocatiebesluit is genomen.": "Behoud de drie gefinancierde posities; resterende doelcapaciteit blijft cash totdat een afzonderlijk besluit wijziging autoriseert.",
            "Behoud de gefinancierde eerste tranche in VWCE; resterende doelcapaciteit blijft cash totdat de bijbehorende gates slagen.": "Behoud de drie gefinancierde posities; resterende doelcapaciteit blijft cash totdat een afzonderlijk besluit wijziging autoriseert.",
            "Kies de gewenste broker- en valutalijn, versterk de prijsbasis en maak daarna pas de kapitaalbeslissing.": "Beoordeel VWCE, EUNA en SXR8 op rol, bijdrage en overlap vóór verdere inzet.",
            "Beoordeel de positie tegen haar fasedoel en valideer de wereldwijde kern- en obligatielijnen vóór verdere inzet.": "Beoordeel VWCE, EUNA en SXR8 op rol, bijdrage en overlap vóór verdere inzet.",
            "Ververs macrodata vóór productiepromotie.": "Gebruik bij iedere wijziging opnieuw actuele macro- en prijsinformatie.",
            "Gebruik bij de volgende tranche opnieuw actuele macro- en prijsinformatie.": "Gebruik bij iedere wijziging opnieuw actuele macro- en prijsinformatie.",
            "De prijzen zijn marktobservaties en geen zelfstandige basis voor waardering of aankoop.": "Marktobservaties ondersteunen uitsluitend de transparante modelportefeuille; zij zijn geen echte brokeruitvoering.",
            "funded_model_position_active": "Gefinancierde modelpositie actief",
            "The model portfolio now holds VWCE, EUNA and SXR8; review shifts from activation to contribution and overlap.": "De modelportefeuille bevat nu VWCE, EUNA en SXR8; de review verschuift van activatie naar bijdrage en overlap.",
            "AI and semiconductor leadership keeps the satellite watchlist relevant, but concentration risk still blocks automatic funding.": "AI- en semiconductorleiderschap houdt de satellietvolglijst relevant, maar concentratierisico blokkeert automatische financiering.",
            "Geen inzet vóór identiteit, KID, broker en lijn zijn bevestigd.": "Geen inzet vóór identiteit, KID, exacte handelslijn, actuele prijsbasis en afzonderlijk besluit zijn bevestigd.",
            "monitor VWCE, EUNA and SXR8 against role, contribution, overlap and invalidation conditions": "Bewaak VWCE, EUNA en SXR8 op rol, bijdrage, overlap en invalidatievoorwaarden",
            "obtain fresh exact-line completed closes before any add, reduction or new position": "Verkrijg verse exact-line completed closes vóór iedere uitbreiding, reductie of nieuwe positie",
            "review global-equity overlap between VWCE and the direct SXR8 overweight": "Beoordeel de wereldwijde-aandelenoverlap tussen VWCE en de directe SXR8-overweging",
            "keep satellite and later-tranche capacity in cash unless a separate validated allocation decision authorises change": "Houd satelliet- en lateretranchecapaciteit cash tenzij een afzonderlijk gevalideerd allocatiebesluit wijziging autoriseert",
        }
    else:
        weekly_action = (
            f"This week: first tranches added in {new_summary}; {held_summary} maintained."
            if new_positions and held_positions
            else f"This week: {count} funded model positions active — {summary}."
        )
        replacements = {
            "Retain cash": f"{count} model positions active",
            "First model position active": f"{count} model positions active",
            "The S&amp;P 500 UCITS lines are operationally most advanced, but capital deployment requires a separate allocation decision.": f"Active model portfolio: {summary}; remaining target capacity stays in cash.",
            "The first tranche is active: 151 whole shares of VWCE; blocked target capacity remains cash.": f"Active model portfolio: {summary}; remaining target capacity stays in cash.",
            "This week: no portfolio transaction; the EU model portfolio remains fully in cash.": weekly_action,
            "This week: first model purchase executed — 151 whole shares of VWCE.": weekly_action,
            "Next action requires broker availability, current pricing, source agreement and a separate allocation decision.": "Next action: monitor role, contribution and overlap; change nothing without fresh pricing and a separate allocation decision.",
            "Next action: monitor contribution and relative strength; release no further target until its own verification gates pass.": "Next action: monitor role, contribution and overlap; change nothing without fresh pricing and a separate allocation decision.",
            "Accelerate SXR8/CSPX verification without bypassing the separate allocation decision.": "Maintain VWCE, EUNA and SXR8; keep remaining capacity in cash and review every change separately.",
            "Maintain the first tranche, keep blocked capacity in cash and review the next tranche only with fresh prices.": "Maintain VWCE, EUNA and SXR8; keep remaining capacity in cash and review every change separately.",
            "The portfolio is not yet invested. This is a deliberate capital-preservation state.": f"The model portfolio now has {invested} invested and {cash} in cash. No real brokerage order was placed.",
            "Retain EUR 100,000 cash until a separate allocation decision is made.": "Maintain all three funded positions; remaining target capacity stays in cash until a separate decision authorises change.",
            "Maintain the funded first tranche in VWCE; remaining target capacity stays cash until its gates pass.": "Maintain all three funded positions; remaining target capacity stays in cash until a separate decision authorises change.",
            "Select the preferred broker and currency line, strengthen pricing evidence, and only then make the capital decision.": "Review VWCE, EUNA and SXR8 by role, contribution and overlap before further deployment.",
            "Review the position against its phase target and validate the global-core and bond lines before further deployment.": "Review VWCE, EUNA and SXR8 by role, contribution and overlap before further deployment.",
            "Refresh macro data before production promotion.": "Use current macro and pricing inputs for every portfolio change.",
            "Use refreshed macro and pricing inputs before the next tranche.": "Use current macro and pricing inputs for every portfolio change.",
            "Prices are market observations and not an independent basis for valuation or purchase.": "Market observations support only the transparent model portfolio; they are not a real brokerage execution.",
            "funded_model_position_active": "Funded model position active",
            "No allocation before identity, KID, broker and trading line are confirmed.": "No allocation before identity, KID, exact trading line, current pricing and a separate decision are confirmed.",
        }
    for old, new in replacements.items():
        rendered = rendered.replace(old, new)
    return rendered.replace("<p>Position analysis active.</p>", position_table(state, language))


def render(state_path: Path, language: str, html_output: Path, pdf_output: Path) -> None:
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("state_valid") is not True:
        raise RuntimeError("Invalid report state: " + str(state.get("blockers")))
    state = funded_overlay(state)
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    rendered = patch_copy(build_html(state, language), state, language)
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
