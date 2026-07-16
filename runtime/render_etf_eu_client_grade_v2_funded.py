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


def funded_overlay(state: dict[str, Any]) -> dict[str, Any]:
    state = dict(state)
    portfolio = dict(state.get("portfolio") or {})
    positions = [dict(row) for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    if not positions:
        return state
    nav = float(portfolio.get("nav_eur") or 0.0)
    cash = float(portfolio.get("cash_eur") or 0.0)
    cash_weight = round(cash / nav * 100.0, 2) if nav else 0.0
    position_weight = round(sum(float(row.get("current_weight_pct") or 0.0) for row in positions), 2)
    funded_lines = ", ".join(str(row.get("exchange_ticker") or row.get("ticker") or "") for row in positions)
    state["allocation_map"] = [
        {"segment_nl": "Cash", "segment_en": "Cash", "stance_nl": f"Huidig {cash_weight:.2f}% · reserve minimaal 7,50%", "stance_en": f"Current {cash_weight:.2f}% · reserve at least 7.50%", "note_nl": "Niet-uitvoerbare doelgewichten blijven cash en worden niet naar andere thema’s doorgeschoven.", "note_en": "Non-executable target capacity remains cash and is not redistributed to other themes."},
        {"segment_nl": "Gefinancierde UCITS-posities", "segment_en": "Funded UCITS positions", "stance_nl": f"{position_weight:.2f}% belegd via {funded_lines}", "stance_en": f"{position_weight:.2f}% invested through {funded_lines}", "note_nl": "Eerste tranche, hele stukken, modelportefeuille; geen brokerorder uitgevoerd.", "note_en": "First tranche, whole shares, model portfolio; no brokerage order was placed."},
        {"segment_nl": "Wereldwijde aandelenkern", "segment_en": "Global equity core", "stance_nl": "Doel 50% · verificatie vereist", "stance_en": "Target 50% · verification required", "note_nl": "VWCE-capaciteit blijft cash totdat de exacte handelslijn is geverifieerd.", "note_en": "VWCE capacity remains cash until the exact trading line is verified."},
        {"segment_nl": "Obligaties en satellieten", "segment_en": "Bonds and satellites", "stance_nl": "Nog niet gefinancierd", "stance_en": "Not yet funded", "note_nl": "EUNA, SXRV en semiconductorblootstelling blijven geblokkeerd tot hun eigen gates slagen.", "note_en": "EUNA, SXRV and semiconductor exposure remain blocked until their own gates pass."},
        {"segment_nl": "Goud / harde activa", "segment_en": "Gold / hard assets", "stance_nl": "Beleidsmatig geblokkeerd", "stance_en": "Policy blocked", "note_nl": "ETC-structuur valt buiten het huidige UCITS-only beleid.", "note_en": "The ETC structure remains outside the current UCITS-only policy."},
    ]
    funnel = dict(state.get("verification_funnel") or {})
    funnel.update({"funded_positions": len(positions), "cash_eur": cash, "decision": "maintain_first_funded_model_position_and_verify_next_targets"})
    state["verification_funnel"] = funnel
    next_run = dict(state.get("next_run_input") or {})
    next_run["required_actions"] = [
        "monitor the funded SXR8 model position against its phase target and invalidation conditions",
        "verify the preferred global-core trading line before releasing its blocked capacity",
        "repair aggregate-bond share-class identity before any bond allocation",
        "rerun the guarded allocation decision with fresh pricing; do not redistribute blocked capacity",
    ]
    state["next_run_input"] = next_run
    effects = list(state.get("second_order_effects") or [])
    if effects:
        effects[0] = {"driver_nl": "Eerste gefinancierde modelpositie", "driver_en": "First funded model position", "first_nl": "Een deel van het kapitaal neemt nu marktrisico via een geverifieerde UCITS-handelslijn.", "first_en": "Part of the capital now carries market risk through a verified UCITS trading line.", "second_nl": "Rendement en drawdown worden zichtbaar, terwijl geblokkeerde doelgewichten cash blijven.", "second_en": "Return and drawdown become observable while blocked target weights remain cash.", "implication_nl": "Beoordeel bijdrage en relatieve kracht voordat de volgende tranche wordt vrijgegeven.", "implication_en": "Review contribution and relative strength before releasing the next tranche."}
        state["second_order_effects"] = effects
    authority = dict(state.get("authority") or {})
    authority.update({"model_position_present": True, "real_broker_execution": False})
    state["authority"] = authority
    return state


def position_table(state: dict[str, Any], language: str) -> str:
    positions = state.get("portfolio", {}).get("positions") or []
    headers = ["Handelslijn", "Fonds", "ISIN", "Stukken", "Prijs", "Marktwaarde", "Gewicht", "Fasedoel", "Status"] if language == "nl" else ["Trading line", "Fund", "ISIN", "Shares", "Price", "Market value", "Weight", "Phase target", "Status"]
    rows: list[list[str]] = []
    for row in positions:
        status = "Modelpositie · geen brokerorder" if language == "nl" else "Model position · no brokerage order"
        rows.append([e(row.get("exchange_ticker") or row.get("ticker")), e(row.get("fund_name")), e(row.get("isin")), e(row.get("shares")), money(row.get("current_price_local"), language), money(row.get("market_value_eur"), language), num(row.get("current_weight_pct"), language) + "%", num(row.get("phase_target_weight_pct") or row.get("target_weight_pct"), language) + "%", e(status)])
    intro = "De eerste tranche is uitsluitend in de repository-modelportefeuille verwerkt. Niet-uitvoerbare doelgewichten blijven cash." if language == "nl" else "The first tranche is recorded only in the repository model portfolio. Non-executable target weights remain cash."
    return '<div class="note-box">' + e(intro) + "</div>" + table(headers, rows)


def patch_copy(rendered: str, state: dict[str, Any], language: str) -> str:
    portfolio = state["portfolio"]
    positions = portfolio.get("positions") or []
    if not positions:
        return rendered
    first = positions[0]
    ticker = str(first.get("exchange_ticker") or first.get("ticker") or "UCITS ETF")
    shares = int(float(first.get("shares") or 0))
    invested = money(portfolio.get("invested_market_value_eur"), language)
    cash = money(portfolio.get("cash_eur"), language)
    if language == "nl":
        replacements = {
            "Cash behouden": "Eerste modelpositie actief",
            "De S&amp;P 500 UCITS-lijnen zijn operationeel het verst gevorderd, maar inzet van kapitaal vereist een afzonderlijk allocatiebesluit.": f"De eerste tranche is geactiveerd: {shares} hele stukken {ticker}; geblokkeerde doelgewichten blijven cash.",
            "Deze week: geen portefeuilletransactie; de EU-modelportefeuille blijft volledig in cash.": f"Deze week: eerste modelaankoop uitgevoerd — {shares} hele stukken {ticker}.",
            "Volgende actie vereist brokerbeschikbaarheid, actuele prijsbasis, bronovereenkomst en een afzonderlijk allocatiebesluit.": "Volgende actie: bewaak bijdrage en relatieve kracht; activeer geen volgend doelgewicht voordat de eigen verificatiegates slagen.",
            "Versnel verificatie van SXR8/CSPX zonder het afzonderlijke allocatiebesluit over te slaan.": "Behoud de eerste tranche; laat geblokkeerde capaciteit cash en beoordeel de volgende tranche alleen met verse prijzen.",
            "De portefeuille is nog niet belegd. Dit is een bewuste kapitaalbeschermingsstatus.": f"De modelportefeuille heeft nu {invested} belegd en {cash} cash. Er is geen echte brokerorder geplaatst.",
            "Behoud EUR 100.000 cash totdat een afzonderlijk allocatiebesluit is genomen.": f"Behoud de gefinancierde eerste tranche in {ticker}; resterende doelcapaciteit blijft cash totdat de bijbehorende gates slagen.",
            "Kies de gewenste broker- en valutalijn, versterk de prijsbasis en maak daarna pas de kapitaalbeslissing.": "Beoordeel de positie tegen haar fasedoel en valideer de wereldwijde kern- en obligatielijnen vóór verdere inzet.",
            "Ververs macrodata vóór productiepromotie.": "Gebruik bij de volgende tranche opnieuw actuele macro- en prijsinformatie.",
            "De prijzen zijn marktobservaties en geen zelfstandige basis voor waardering of aankoop.": "Marktobservaties worden alleen gebruikt voor de transparante modelportefeuille op een geverifieerde handelslijn; zij zijn geen echte brokeruitvoering.",
        }
    else:
        replacements = {
            "Retain cash": "First model position active",
            "The S&amp;P 500 UCITS lines are operationally most advanced, but capital deployment requires a separate allocation decision.": f"The first tranche is active: {shares} whole shares of {ticker}; blocked target capacity remains cash.",
            "This week: no portfolio transaction; the EU model portfolio remains fully in cash.": f"This week: first model purchase executed — {shares} whole shares of {ticker}.",
            "Next action requires broker availability, current pricing, source agreement and a separate allocation decision.": "Next action: monitor contribution and relative strength; release no further target until its own verification gates pass.",
            "Accelerate SXR8/CSPX verification without bypassing the separate allocation decision.": "Maintain the first tranche, keep blocked capacity in cash and review the next tranche only with fresh prices.",
            "The portfolio is not yet invested. This is a deliberate capital-preservation state.": f"The model portfolio now has {invested} invested and {cash} in cash. No real brokerage order was placed.",
            "Retain EUR 100,000 cash until a separate allocation decision is made.": f"Maintain the funded first tranche in {ticker}; remaining target capacity stays cash until its gates pass.",
            "Select the preferred broker and currency line, strengthen pricing evidence, and only then make the capital decision.": "Review the position against its phase target and validate the global-core and bond lines before further deployment.",
            "Refresh macro data before production promotion.": "Use refreshed macro and pricing inputs before the next tranche.",
            "Prices are market observations and not an independent basis for valuation or purchase.": "Market observations support only the transparent model portfolio on a verified trading line; they are not a real brokerage execution.",
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
