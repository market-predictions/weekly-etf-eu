from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from weasyprint import HTML

from runtime import render_etf_eu_client_grade_v2_funded as legacy
from runtime.render_etf_eu_client_grade_v2 import build_html


CLIENT_RENDERER_MODE = "client_grade_v3_donor_converged"


def ticker_of(row: dict[str, Any]) -> str:
    return str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()


def _money(value: Any, language: str) -> str:
    return legacy.money(value, language)


def _num(value: Any, language: str, decimals: int = 2) -> str:
    return legacy.num(value, language, decimals)


def _whole(value: Any, language: str) -> str:
    return legacy.whole(value, language)


def current_overlay(state: dict[str, Any]) -> dict[str, Any]:
    state = dict(state)
    portfolio = dict(state.get("portfolio") or {})
    positions = [dict(row) for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    if not positions:
        return state

    nav = float(portfolio.get("nav_eur") or 0.0)
    cash = float(portfolio.get("cash_eur") or 0.0)
    cash_weight = round(cash / nav * 100.0, 2) if nav else 0.0
    funded = [ticker_of(row) for row in positions if ticker_of(row)]

    allocation_map: list[dict[str, str]] = [
        {
            "segment_nl": "Cash",
            "segment_en": "Cash",
            "stance_nl": f"Huidig {cash_weight:.2f}% · inzetten of uitleggen",
            "stance_en": f"Current {cash_weight:.2f}% · deploy or explain",
            "note_nl": "Geen vast minimum uit het historische transitiebeleid. Niet-inzetbare of onvoldoende onderbouwde capaciteit blijft cash.",
            "note_en": "No fixed minimum from historical transition policy. Unfundable or insufficiently evidenced capacity remains cash.",
        }
    ]
    for row in positions:
        ticker = ticker_of(row)
        weight = float(row.get("current_weight_pct") or row.get("weight_pct") or 0.0)
        shares = _whole(row.get("shares"), "en")
        role = str(row.get("portfolio_role") or "Current funded position")
        allocation_map.append(
            {
                "segment_nl": ticker,
                "segment_en": ticker,
                "stance_nl": f"Actueel gewicht {weight:.2f}%",
                "stance_en": f"Current weight {weight:.2f}%",
                "note_nl": f"{shares} stuks actief · {role}. Iedere wijziging vereist actuele completed-close evidence, re-underwriting en een afzonderlijk allocatiebesluit.",
                "note_en": f"{shares} shares active · {role}. Any change requires current completed-close evidence, re-underwriting and a separate allocation decision.",
            }
        )
    state["allocation_map"] = allocation_map

    radar: list[dict[str, Any]] = []
    for source in state.get("opportunity_radar") or []:
        lane = dict(source)
        lane_tickers = {str(value).strip().upper() for value in (lane.get("candidate_tickers") or lane.get("tickers") or [])}
        active = sorted(lane_tickers & set(funded))
        lane["funded_count"] = len(active)
        lane["funded_tickers"] = active
        if active:
            lane["status"] = "funded_current_position_reunderwriting_required"
            lane["next_confirmation_nl"] = "Bewaak huidige rol, bijdrage en overlap; geen wijziging zonder actuele evidence en afzonderlijk besluit."
            lane["next_confirmation_en"] = "Monitor current role, contribution and overlap; no change without current evidence and a separate decision."
        else:
            lane["allocation_authority"] = False
            lane["next_confirmation_nl"] = str(lane.get("next_confirmation_nl") or "") \
                .replace("brokerbeschikbaarheid, ", "") \
                .replace("brokerbeschikbaarheid en ", "")
            lane["next_confirmation_en"] = str(lane.get("next_confirmation_en") or "") \
                .replace("broker availability, ", "") \
                .replace("broker availability and ", "")
        radar.append(lane)
    state["opportunity_radar"] = radar

    funnel = dict(state.get("verification_funnel") or {})
    funnel.update(
        {
            "funded_positions": len(positions),
            "cash_eur": cash,
            "decision": "current_four_position_state_preserved_pending_current_reunderwriting_and_separate_allocation_decision",
        }
    )
    state["verification_funnel"] = funnel

    state["second_order_effects"] = [
        {
            "driver_nl": f"{len(positions)} gefinancierde modelposities",
            "driver_en": f"{len(positions)} funded model positions",
            "first_nl": "De portefeuille combineert brede aandelenblootstelling, een obligatiestabilisator en een cybersecurity-satelliet.",
            "first_en": "The portfolio combines broad equity exposure, a bond stabiliser and a cybersecurity satellite.",
            "second_nl": "Overlap, rolbijdrage en opportunity cost zijn belangrijker dan het aantal tickers op zichzelf.",
            "second_en": "Overlap, role contribution and opportunity cost matter more than ticker count by itself.",
            "implication_nl": "Herbeoordeel elk huidig gewicht met fresh-cash discipline; historische targetgewichten zijn geen actuele handelsinstructie.",
            "implication_en": "Re-underwrite each current weight with fresh-cash discipline; historical target weights are not current trade instructions.",
        },
        {
            "driver_nl": "VWCE plus SXR8",
            "driver_en": "VWCE plus SXR8",
            "first_nl": "Brede werelddekking bevat al aanzienlijke Amerikaanse megacapblootstelling.",
            "first_en": "Broad global coverage already embeds meaningful U.S. mega-cap exposure.",
            "second_nl": "Een extra Amerikaanse of semiconductorpositie kan meer factorconcentratie creëren dan tickerdiversificatie suggereert.",
            "second_en": "Additional U.S. or semiconductor exposure may create more factor concentration than ticker diversification suggests.",
            "implication_nl": "Gebruik gemeten overlap als analytische ondergrens en beoordeel concentratie zonder een niet-geautoriseerde vaste cap te verzinnen.",
            "implication_en": "Use measured overlap as an analytical lower bound and review concentration without inventing an unauthorised fixed cap.",
        },
        {
            "driver_nl": "L0CK cybersecurity-satelliet",
            "driver_en": "L0CK cybersecurity satellite",
            "first_nl": "De portefeuille heeft nu een directe thematische cybersecurityblootstelling.",
            "first_en": "The portfolio now has direct thematic cybersecurity exposure.",
            "second_nl": "Brede kernfondsen bevatten eveneens cybersecuritybedrijven; de gemeten overlap is onvolledig en dus een ondergrens.",
            "second_en": "Broad core funds also hold cybersecurity companies; measured overlap is incomplete and therefore a lower bound.",
            "implication_nl": "Bewaak effectieve exposure en relatieve sterkte vóór uitbreiding.",
            "implication_en": "Monitor effective exposure and relative strength before adding.",
        },
        {
            "driver_nl": "EUNA als ballast",
            "driver_en": "EUNA as ballast",
            "first_nl": "De EUR-gehedgede aggregate-bondpositie diversifieert het aandelenrisico.",
            "first_en": "The EUR-hedged aggregate-bond position diversifies equity risk.",
            "second_nl": "Ballastwerking is empirisch en moet opnieuw worden getoetst; het label alleen is onvoldoende.",
            "second_en": "Ballast behavior is empirical and must be re-tested; the label alone is insufficient.",
            "implication_nl": "Gebruik actuele bijdrage/drawdown in de re-underwriting.",
            "implication_en": "Use current contribution/drawdown evidence in re-underwriting.",
        },
    ]

    macro = dict(state.get("macro") or {})
    macro["what_changed"] = [
        f"The model portfolio contains {len(positions)} funded positions: {', '.join(funded)}.",
        "Current review authority is fresh-cash re-underwriting plus exact UCITS fundability; historical Stage-1 percentages are not current controls.",
    ]
    macro["portfolio_implications"] = [
        str(item)
        .replace("broker availability and ", "")
        .replace("broker availability, ", "")
        for item in macro.get("portfolio_implications") or []
    ]
    state["macro"] = macro

    next_run = dict(state.get("next_run_input") or {})
    next_run["priority_candidates"] = funded
    next_run["required_actions"] = [
        "re-underwrite every funded position using current completed-close evidence",
        "compare mapped UCITS challengers directly when a holding is replaceable or weakening",
        "deploy or explain meaningful cash against current fundable opportunities without a fixed cash minimum",
        "keep U.S.-listed donor ETFs research-only and preserve exact ISIN/trading-line authority",
    ]
    state["next_run_input"] = next_run

    authority = dict(state.get("authority") or {})
    authority.update(
        {
            "allocation_authority_contract": "control/ETF_EU_ALLOCATION_AUTHORITY_CONVERGENCE_V1.md",
            "shadow_policy_used_for_current_allocation": False,
            "retired_fixed_percentage_used": False,
            "historical_target_used_for_current_trade": False,
            "broker_specific_permission_required_for_model": False,
            "broker_permission_required_for_real_execution": True,
            "model_position_present": True,
            "real_broker_execution": False,
        }
    )
    state["authority"] = authority
    state["client_renderer_mode"] = CLIENT_RENDERER_MODE
    state["funded_consistency"] = {
        "position_count": len(positions),
        "funded_tickers": funded,
        "allocation_map_current_actuals_only": True,
        "historical_targets_client_authority": False,
        "broker_neutral_model_language": True,
    }
    return state


def position_table(state: dict[str, Any], language: str) -> str:
    positions = state.get("portfolio", {}).get("positions") or []
    reviews = {
        str(row.get("exchange_ticker") or "").upper(): row
        for row in state.get("current_reunderwriting") or []
        if isinstance(row, dict)
    }
    headers = (
        ["Handelslijn", "Fonds", "ISIN", "Stukken", "Prijs", "Peildatum", "Marktwaarde", "Gewicht", "Current review", "Status"]
        if language == "nl"
        else ["Trading line", "Fund", "ISIN", "Shares", "Price", "Pricing date", "Market value", "Weight", "Current review", "Status"]
    )
    rows: list[list[str]] = []
    for row in positions:
        ticker = ticker_of(row)
        review = reviews.get(ticker, {})
        review_status = str(review.get("would_initiate_today") or review.get("reunderwriting_status") or "Current review required")
        status = "Modelpositie · geen brokerorder" if language == "nl" else "Model position · no brokerage order"
        rows.append(
            [
                legacy.e(ticker),
                legacy.e(row.get("fund_name")),
                legacy.e(row.get("isin")),
                legacy.e(_whole(row.get("shares"), language)),
                _money(row.get("current_price_local"), language),
                legacy.e(row.get("price_date") or "n/a"),
                _money(row.get("market_value_eur"), language),
                _num(row.get("current_weight_pct"), language) + "%",
                legacy.e(review_status),
                legacy.e(status),
            ]
        )
    intro = (
        "Actuele gewichten en aantallen komen uit de beschermde modelportefeuille. Historische strategische/fasedoelen zijn geen actuele handelsinstructies."
        if language == "nl"
        else "Current weights and share counts come from the protected model portfolio. Historical strategic/phase targets are not current trade instructions."
    )
    return '<div class="note-box">' + legacy.e(intro) + "</div>" + legacy.table(headers, rows)


def _final_sanitize(rendered: str, state: dict[str, Any], language: str) -> str:
    count = len(state.get("portfolio", {}).get("positions") or [])
    replacements = {
        "reserve minimaal 7,50%": "geen vast cashminimum",
        "reserve at least 7.50%": "no fixed cash minimum",
        "drie gefinancierde posities": f"{count} gefinancierde posities",
        "three funded positions": f"{count} funded positions",
        "alle drie gefinancierde posities": f"alle {count} gefinancierde posities",
        "all three funded positions": f"all {count} funded positions",
        "VWCE, EUNA en SXR8": "VWCE, EUNA, SXR8 en L0CK",
        "VWCE, EUNA and SXR8": "VWCE, EUNA, SXR8 and L0CK",
        "strategisch doel": "historisch doel (geen huidige authority)",
        "strategic target": "historical target (not current authority)",
        "fasedoel": "historisch fasedoel",
        "phase target": "historical phase target",
        "brokerbeschikbaarheid": "uitvoerbaarheid",
        "broker availability": "execution availability",
    }
    for old, new in replacements.items():
        rendered = rendered.replace(old, new)

    forbidden = [
        "reserve minimaal 7,50%",
        "reserve at least 7.50%",
        "35% minimum cash",
        "15% maximum new",
        "50% cash-first",
        "25% turnover ceiling",
        "18% semiconductor cap",
        "Max. nieuwe ETF",
        "Max. new ETF",
    ]
    leaked = [token for token in forbidden if token.casefold() in rendered.casefold()]
    if leaked:
        raise RuntimeError(f"Converged client renderer still contains retired/shadow authority: {leaked}")
    return rendered


def render(state_path: Path, language: str, html_output: Path, pdf_output: Path) -> None:
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("state_valid") is not True:
        raise RuntimeError("Invalid report state: " + str(state.get("blockers")))
    state = current_overlay(state)
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    original_position_table = legacy.position_table
    legacy.position_table = position_table
    try:
        rendered = legacy.patch_copy(build_html(state, language), state, language)
    finally:
        legacy.position_table = original_position_table
    rendered = _final_sanitize(rendered, state, language)

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
    print("ETF_EU_CLIENT_GRADE_V3_DONOR_CONVERGED_RENDER_OK | language=" + args.language)


if __name__ == "__main__":
    main()
