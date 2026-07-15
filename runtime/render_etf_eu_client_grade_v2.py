from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any, Iterable

from weasyprint import HTML

from runtime.equity_curve_eu_contract import render_equity_curve_svg


LABELS = {
    "nl": {
        "brand": "WEKELIJKSE ETF EU-REVIEW",
        "investor": "Beleggersrapport",
        "analyst": "Analistenrapport",
        "regime": "Primair regime",
        "action": "Portefeuilleactie",
        "conclusion": "Kernconclusie",
        "macro_refresh": "Macro-refresh vereist",
        "cash": "Cash behouden",
        "takeaway": "De S&P 500 UCITS-lijnen zijn operationeel het verst gevorderd, maar inzet van kapitaal vereist een afzonderlijk allocatiebesluit.",
        "sections": [
            "Besliscockpit", "Portefeuille en kapitaal", "Regime- en beleidsdashboard",
            "Structurele UCITS-kansenradar", "Belangrijkste risico’s en invalidaties",
            "Portefeuilleontwikkeling", "Conclusie", "Allocatiekaart", "Tweede-orde-effecten",
            "UCITS-kandidaten en prijsbewijs", "Verificatiefunnel", "Review huidige posities",
            "Vervanging, rotatie en vermijdingsradar", "Input voor de volgende run", "Disclaimer",
        ],
    },
    "en": {
        "brand": "WEEKLY ETF EU REVIEW",
        "investor": "Investor report",
        "analyst": "Analyst report",
        "regime": "Primary regime",
        "action": "Portfolio action",
        "conclusion": "Main conclusion",
        "macro_refresh": "Macro refresh required",
        "cash": "Retain cash",
        "takeaway": "The S&P 500 UCITS lines are operationally most advanced, but capital deployment requires a separate allocation decision.",
        "sections": [
            "Decision cockpit", "Portfolio and capital", "Regime and policy dashboard",
            "Structural UCITS opportunity radar", "Key risks and invalidations",
            "Portfolio development", "Conclusion", "Allocation map", "Second-order effects",
            "UCITS candidates and pricing evidence", "Verification funnel", "Current-position review",
            "Replacement, rotation and avoidance radar", "Input for the next run", "Disclaimer",
        ],
    },
}

STATUS = {
    "nl": {
        "verified_ucits_trading_line": "UCITS-handelslijn geverifieerd",
        "candidate_requires_verification": "Handelslijn nog te verifiëren",
        "fetch_failed": "Prijs niet beschikbaar",
        "operationally_mature_not_funded": "Operationeel volwassen, niet gefinancierd",
        "watchlist_verification_required": "Volglijst, verificatie vereist",
        "research_only_not_priced": "Onderzoek, nog niet geprijsd",
        "policy_blocked": "Beleidsmatig geblokkeerd",
    },
    "en": {
        "verified_ucits_trading_line": "Verified UCITS trading line",
        "candidate_requires_verification": "Trading line requires verification",
        "fetch_failed": "Price unavailable",
        "operationally_mature_not_funded": "Operationally mature, not funded",
        "watchlist_verification_required": "Watchlist, verification required",
        "research_only_not_priced": "Research only, not priced",
        "policy_blocked": "Policy blocked",
    },
}


def e(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def num(value: Any, language: str, decimals: int = 2) -> str:
    if value is None:
        return "n/a"
    try:
        raw = f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return "n/a"
    return raw.replace(",", "X").replace(".", ",").replace("X", ".") if language == "nl" else raw


def money(value: Any, language: str) -> str:
    return "€ " + num(value, language)


def table(headers: Iterable[str], rows: Iterable[Iterable[str]], css_class: str = "data-table") -> str:
    head = "".join("<th>" + e(item) + "</th>" for item in headers)
    body = "".join("<tr>" + "".join("<td>" + str(value) + "</td>" for value in row) + "</tr>" for row in rows)
    return '<table class="' + css_class + '"><thead><tr>' + head + "</tr></thead><tbody>" + body + "</tbody></table>"


def section(number: int, title: str, body: str, extra: str = "") -> str:
    head = '<div class="section-head"><span class="badge">' + str(number) + '</span><span class="section-title">' + e(title) + "</span></div>"
    return '<section class="panel ' + extra + '">' + head + body + "</section>"


def hero(state: dict[str, Any], language: str, report_type: str) -> str:
    labels = LABELS[language]
    macro = state["macro"]
    regime = macro["regime_nl"] if language == "nl" else macro["regime"]
    if not macro["fresh_for_report"]:
        regime = labels["macro_refresh"]
    class_name = "hero hero-secondary" if report_type == "analyst" else "hero"
    report_label = labels["analyst"] if report_type == "analyst" else labels["investor"]
    result = (
        '<header class="' + class_name + '"><div class="hero-row"><div><div class="masthead">' + e(labels["brand"]) +
        '</div><div class="hero-date">' + e(state["report_date"]) + '</div></div><div class="hero-type">' + e(report_label) +
        '</div></div></header><div class="hero-rule"></div>'
    )
    if report_type == "investor":
        notice = (
            "Dit rapport is uitsluitend informatief en educatief. UCITS-identiteit, handelslijn en productbeleid blijven leidend; zie de disclaimer aan het einde."
            if language == "nl" else
            "This report is for informational and educational purposes only. UCITS identity, trading line and product policy remain authoritative; see the disclaimer at the end."
        )
        result += '<div class="notice">' + e(notice) + "</div>"
        cards = [
            (labels["regime"], regime),
            (labels["action"], labels["cash"]),
            (labels["conclusion"], labels["takeaway"]),
        ]
        result += '<div class="summary-strip">' + "".join(
            '<div class="mini-card"><div class="mini-label">' + e(key) + '</div><div class="mini-value">' + e(value) + "</div></div>"
            for key, value in cards
        ) + "</div>"
    return result


def investor_sections(state: dict[str, Any], language: str) -> str:
    labels = LABELS[language]["sections"]
    p = state["portfolio"]
    f = state["verification_funnel"]
    m = state["macro"]

    if language == "nl":
        cockpit = [
            "Deze week: geen portefeuilletransactie; de EU-modelportefeuille blijft volledig in cash.",
            f"Meest volwassen implementatie: {f['verified_lines']} geverifieerde UCITS-handelslijnen.",
            f"Belangrijkste blokkade: {f['observed_lines'] - f['verified_lines']} lijnen zijn nog niet volledig geverifieerd of geprijsd.",
            "Volgende actie vereist brokerbeschikbaarheid, actuele prijsbasis, bronovereenkomst en een afzonderlijk allocatiebesluit.",
        ]
        portfolio_headers = ["Component", "Waarde"]
        portfolio_rows = [
            ["Startkapitaal", money(p["starting_capital_eur"], language)],
            ["Cash", money(p["cash_eur"], language)],
            ["Belegde marktwaarde", money(p["invested_market_value_eur"], language)],
            ["Totale portefeuillewaarde", money(p["nav_eur"], language)],
            ["Rendement sinds start", num(p["since_inception_return_pct"], language) + "%"],
            ["Gefinancierde posities", e(p["position_count"])],
        ]
    else:
        cockpit = [
            "This week: no portfolio transaction; the EU model portfolio remains fully in cash.",
            f"Most mature implementation: {f['verified_lines']} verified UCITS trading lines.",
            f"Main blocker: {f['observed_lines'] - f['verified_lines']} lines are not yet fully verified or priced.",
            "Next action requires broker availability, current pricing, source agreement and a separate allocation decision.",
        ]
        portfolio_headers = ["Component", "Value"]
        portfolio_rows = [
            ["Starting capital", money(p["starting_capital_eur"], language)],
            ["Cash", money(p["cash_eur"], language)],
            ["Invested market value", money(p["invested_market_value_eur"], language)],
            ["Total portfolio value", money(p["nav_eur"], language)],
            ["Return since inception", num(p["since_inception_return_pct"], language) + "%"],
            ["Funded positions", e(p["position_count"])],
        ]

    cockpit_body = "<ul>" + "".join("<li>" + e(item) + "</li>" for item in cockpit) + "</ul>"
    decision_rule = (
        "Versnel verificatie van SXR8/CSPX zonder het afzonderlijke allocatiebesluit over te slaan."
        if language == "nl" else
        "Accelerate SXR8/CSPX verification without bypassing the separate allocation decision."
    )
    cockpit_body += '<div class="takeaway"><strong>' + ("Beslisregel: " if language == "nl" else "Decision rule: ") + "</strong>" + e(decision_rule) + "</div>"

    portfolio_body = table(portfolio_headers, portfolio_rows, "summary-table")
    portfolio_body += '<div class="note-box">' + e(
        "De portefeuille is nog niet belegd. Dit is een bewuste kapitaalbeschermingsstatus."
        if language == "nl" else
        "The portfolio is not yet invested. This is a deliberate capital-preservation state."
    ) + "</div>"

    stale = not m["fresh_for_report"]
    freshness = (
        f"Historische macrocontext van {m.get('source_report_date')}; {m.get('age_days')} dagen oud. Verversing vereist vóór productiepromotie."
        if language == "nl" else
        f"Historical macro context dated {m.get('source_report_date')}; {m.get('age_days')} days old. Refresh required before production promotion."
    ) if stale else ("Macro-pack is voldoende actueel." if language == "nl" else "Macro pack is sufficiently current.")
    macro_rows = [
        ["Regime", e(m["regime_nl"] if language == "nl" else m["regime"]), e("Historische context; geen allocatiebevoegdheid." if language == "nl" else "Historical context; no allocation authority.")],
        ["Federal Reserve", e(m["fed"]["stance_nl"] if language == "nl" else m["fed"]["stance"]), e(m["fed"].get("implication") or "n/a")],
        ["ECB", e(m["ecb"]["stance_nl"] if language == "nl" else m["ecb"]["stance"]), e(m["ecb"].get("implication") or "n/a")],
    ]
    macro_headers = ["Onderdeel", "Lezing", "Implicatie"] if language == "nl" else ["Component", "Reading", "Implication"]
    macro_body = '<div class="freshness warning">' + e(freshness) + "</div>" + table(macro_headers, macro_rows)
    if m.get("what_changed"):
        macro_body += "<ul>" + "".join("<li>" + e(item) + "</li>" for item in m["what_changed"]) + "</ul>"

    radar_headers = (
        ["Thema", "UCITS-kandidaten", "Onderzoeksreferentie", "Waarom relevant", "Structureel", "Implementatie", "Status", "Benodigde bevestiging", "Horizon"]
        if language == "nl" else
        ["Theme", "UCITS candidates", "Research reference", "Why relevant", "Structural", "Implementation", "Status", "Required confirmation", "Horizon"]
    )
    radar_rows = []
    for lane in state["opportunity_radar"]:
        radar_rows.append([
            e(lane["name_nl"] if language == "nl" else lane["name_en"]),
            e(", ".join(lane["candidate_tickers"])),
            e(lane["research_reference"] + (" · alleen onderzoek" if language == "nl" else " · research only")),
            e(lane["why_nl"] if language == "nl" else lane["why_en"]),
            e(lane["structural_score"]),
            e(lane["implementation_score"]),
            e(STATUS[language].get(lane["status"], lane["status"])),
            e(lane["next_confirmation_nl"] if language == "nl" else lane["next_confirmation_en"]),
            e(lane["horizon"]),
        ])
    radar_body = '<div class="note-box">' + e(
        "Scores tonen relevantie en implementatiematuriteit, niet allocatiebevoegdheid."
        if language == "nl" else
        "Scores show relevance and implementation maturity, not allocation authority."
    ) + "</div>" + table(radar_headers, radar_rows, "wide-table")

    risk_headers = ["Actief risico", "Oplossing / invalidatie"] if language == "nl" else ["Active risk", "Resolution / invalidation"]
    risk_rows = [[e(item["risk_nl"] if language == "nl" else item["risk_en"]), e(item["invalidation_nl"] if language == "nl" else item["invalidation_en"])] for item in state["risks"]]

    curve = render_equity_curve_svg(state, language=language)
    if curve:
        development_body = curve
    else:
        fallback = state["equity_curve"]["fallback_nl"] if language == "nl" else state["equity_curve"]["fallback_en"]
        development_body = '<div class="cash-callout"><div class="cash-value">' + money(p["cash_eur"], language) + '</div><div class="cash-text">' + e(fallback) + "</div></div>"
    history_headers = ["Datum", "Portefeuillewaarde", "Cash", "Belegd", "Toelichting"] if language == "nl" else ["Date", "Portfolio value", "Cash", "Invested", "Comment"]
    history_rows = [[e(row["date"]), money(row["nav_eur"], language), money(row["cash_eur"], language), money(row["invested_market_value_eur"], language), e(row["comment"])] for row in state.get("valuation_history") or []]
    if history_rows:
        development_body += table(history_headers, history_rows)

    conclusion_items = (
        [
            "Behoud EUR 100.000 cash totdat een afzonderlijk allocatiebesluit is genomen.",
            f"Best onderbouwde implementatie: {f['verified_lines']} geverifieerde S&P 500 UCITS-handelslijnen.",
            "Kies de gewenste broker- en valutalijn, versterk de prijsbasis en maak daarna pas de kapitaalbeslissing.",
            "Ververs macrodata vóór productiepromotie.",
        ]
        if language == "nl" else
        [
            "Retain EUR 100,000 cash until a separate allocation decision is made.",
            f"Best-supported implementation: {f['verified_lines']} verified S&P 500 UCITS trading lines.",
            "Select the preferred broker and currency line, strengthen pricing evidence, and only then make the capital decision.",
            "Refresh macro data before production promotion.",
        ]
    )
    conclusion_body = "<ul>" + "".join("<li>" + e(item) + "</li>" for item in conclusion_items) + "</ul>"

    return "".join([
        section(1, labels[0], cockpit_body),
        section(2, labels[1], portfolio_body),
        section(3, labels[2], macro_body),
        section(4, labels[3], radar_body, "panel-wide"),
        section(5, labels[4], table(risk_headers, risk_rows)),
        section(6, labels[5], development_body),
        section(7, labels[6], conclusion_body),
    ])


def analyst_sections(state: dict[str, Any], language: str) -> str:
    labels = LABELS[language]["sections"]
    allocation_headers = ["Segment", "Positionering", "Toelichting"] if language == "nl" else ["Segment", "Positioning", "Explanation"]
    allocation_rows = [[e(item["segment_nl"] if language == "nl" else item["segment_en"]), e(item["stance_nl"] if language == "nl" else item["stance_en"]), e(item["note_nl"] if language == "nl" else item["note_en"])] for item in state["allocation_map"]]

    effect_headers = ["Drijver", "Eerste orde", "Tweede orde", "ETF EU-implicatie"] if language == "nl" else ["Driver", "First order", "Second order", "ETF EU implication"]
    effect_rows = [[e(item["driver_nl"] if language == "nl" else item["driver_en"]), e(item["first_nl"] if language == "nl" else item["first_en"]), e(item["second_nl"] if language == "nl" else item["second_en"]), e(item["implication_nl"] if language == "nl" else item["implication_en"])] for item in state["second_order_effects"]]

    pricing_headers = ["Handelslijn", "Fonds", "ISIN", "Beurs", "Peildatum", "Slot", "Valuta", "Status", "Onderzoeksreferentie"] if language == "nl" else ["Trading line", "Fund", "ISIN", "Exchange", "Pricing date", "Close", "Currency", "Status", "Research reference"]
    pricing_rows = []
    for row in state["pricing"]["rows"]:
        key = row["verification_status"] if row["priced"] else "fetch_failed"
        proxy = row.get("research_reference") or "—"
        if proxy != "—":
            proxy += " · " + ("alleen onderzoek" if language == "nl" else "research only")
        pricing_rows.append([
            e(row["ticker"]), e(row["fund_name"]), e(row["isin"]), e(row["exchange"]), e(row["close_date"] or "n/a"),
            num(row["close_price"], language) if row["close_price"] is not None else "n/a", e(row["currency"]), e(STATUS[language].get(key, key)), e(proxy),
        ])
    pricing_note = "De prijzen zijn marktobservaties en geen zelfstandige basis voor waardering of aankoop." if language == "nl" else "Prices are market observations and not an independent basis for valuation or purchase."

    f = state["verification_funnel"]
    funnel_cards = [
        ("Geobserveerd" if language == "nl" else "Observed", f["observed_lines"]),
        ("Geprijsd" if language == "nl" else "Priced", f["priced_lines"]),
        ("Geverifieerd" if language == "nl" else "Verified", f["verified_lines"]),
        ("Onopgelost" if language == "nl" else "Unresolved", f["unresolved_lines"]),
        ("Gefinancierd" if language == "nl" else "Funded", f["funded_positions"]),
    ]
    funnel_body = '<div class="funnel-strip">' + "".join('<div class="funnel-card"><div class="funnel-value">' + e(value) + '</div><div class="funnel-label">' + e(label) + "</div></div>" for label, value in funnel_cards) + "</div>"
    funnel_body += '<div class="note-box">' + e(
        "Prijsbeschikbaarheid is niet hetzelfde als investeerbaarheid; investeerbaarheid is niet hetzelfde als een allocatiebesluit."
        if language == "nl" else
        "Price availability is not investability; investability is not an allocation decision."
    ) + "</div>"

    if state["portfolio"]["position_count"] == 0:
        positions_body = '<div class="inactive">' + e(
            "Niet actief: nog geen gefinancierde posities. Deze sectie wordt automatisch een positie-, rendement- en bijdrageanalyse zodra een gevalideerde positie bestaat."
            if language == "nl" else
            "Not active: no funded positions. This section automatically becomes a position, return and contribution review once a validated position exists."
        ) + "</div>"
    else:
        positions_body = "<p>Position analysis active.</p>"

    avoidance_headers = ["Vermijden / bewaken", "Reden"] if language == "nl" else ["Avoid / monitor", "Reason"]
    avoidance = [
        ["Inverse of leveraged producten" if language == "nl" else "Inverse or leveraged products", "Buiten het huidige productbeleid." if language == "nl" else "Outside the current product policy."],
        ["Ongeverifieerde handelslijnen" if language == "nl" else "Unverified trading lines", "Geen inzet vóór identiteit, KID, broker en lijn zijn bevestigd." if language == "nl" else "No allocation before identity, KID, broker and trading line are confirmed."],
        ["Goud-ETC’s" if language == "nl" else "Gold ETCs", "Geblokkeerd onder het huidige UCITS-only beleid." if language == "nl" else "Blocked under the current UCITS-only policy."],
        ["Smalle technologieconcentratie" if language == "nl" else "Narrow technology concentration", "Alleen als satellietblootstelling beoordelen." if language == "nl" else "Assess only as satellite exposure."],
    ]

    n = state["next_run_input"]
    next_items = [
        ("Portefeuillestaat" if language == "nl" else "Portfolio state") + ": " + n["portfolio_state"],
        ("Waarderingshistorie" if language == "nl" else "Valuation history") + ": " + n["valuation_history"],
        ("Prijsartifact" if language == "nl" else "Pricing artifact") + ": " + n["pricing_artifact"],
        ("Prioriteitskandidaten" if language == "nl" else "Priority candidates") + ": " + ", ".join(n["priority_candidates"]),
    ]
    next_body = "<ul>" + "".join("<li>" + e(item) + "</li>" for item in next_items) + "</ul><ol>" + "".join("<li>" + e(item) + "</li>" for item in n["required_actions"]) + "</ol>"

    disclaimer_text = (
        "Dit rapport is uitsluitend informatief en educatief en is geen beleggings-, juridisch, fiscaal of financieel advies. Het is geen aanbeveling om effecten te kopen, verkopen of aan te houden. Beleggen brengt risico’s met zich mee, waaronder verlies van inleg. Amerikaanse ETF-symbolen zijn uitsluitend onderzoeksreferenties; EU-productautoriteit blijft ISIN-first en UCITS-first."
        if language == "nl" else
        "This report is for informational and educational purposes only and is not investment, legal, tax or financial advice. It is not a recommendation to buy, sell or hold securities. Investing involves risk, including loss of principal. U.S. ETF symbols are research references only; EU product authority remains ISIN-first and UCITS-first."
    )

    return "".join([
        section(8, labels[7], table(allocation_headers, allocation_rows)),
        section(9, labels[8], table(effect_headers, effect_rows, "wide-table")),
        section(10, labels[9], '<div class="note-box">' + e(pricing_note) + "</div>" + table(pricing_headers, pricing_rows, "wide-table pricing-table"), "panel-wide"),
        section(11, labels[10], funnel_body),
        section(12, labels[11], positions_body),
        section(13, labels[12], table(avoidance_headers, [[e(a), e(b)] for a, b in avoidance])),
        section(14, labels[13], next_body),
        section(15, labels[14], "<p>" + e(disclaimer_text) + "</p>"),
    ])


def css() -> str:
    return """
@page { size: A4 portrait; margin: 13mm 12mm 15mm; @bottom-left { content: "Weekly ETF EU · client-grade preview"; color: #74818a; font-size: 7.5pt; } @bottom-right { content: "Page " counter(page) " of " counter(pages); color: #74818a; font-size: 7.5pt; } }
* { box-sizing: border-box; }
body { margin: 0; background: #F6F2EC; color: #2B3742; font-family: Arial, Helvetica, sans-serif; font-size: 9pt; line-height: 1.4; }
.hero { background: #607887; color: #FBFAF7; padding: 17px 20px; border-radius: 12px 12px 0 0; }
.hero-secondary { break-before: page; page-break-before: always; }
.hero-row { display: table; width: 100%; }
.hero-row > div { display: table-cell; vertical-align: middle; }
.hero-row > div:last-child { text-align: right; }
.masthead { font-family: Georgia, serif; font-size: 22pt; font-weight: 700; letter-spacing: .04em; }
.hero-date { margin-top: 3px; font-size: 9pt; }
.hero-type { font-size: 12pt; font-weight: 700; }
.hero-rule { height: 4px; background: #D4B483; margin: 5px 0 12px; border-radius: 99px; }
.notice, .note-box, .inactive { background: #F8F4EE; border: 1px solid #D9D3CB; border-radius: 9px; padding: 8px 10px; margin: 0 0 10px; color: #596872; }
.summary-strip, .funnel-strip { display: table; width: 100%; table-layout: fixed; border-spacing: 7px 0; margin: 0 -7px 11px; }
.mini-card, .funnel-card { display: table-cell; background: #FCFAF7; border: 1px solid #D9D3CB; border-radius: 11px; padding: 10px; vertical-align: top; }
.mini-label, .funnel-label { font-size: 7.5pt; color: #6B7882; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; }
.mini-value { font-family: Georgia, serif; font-size: 13pt; font-weight: 700; line-height: 1.2; margin-top: 5px; }
.funnel-card { text-align: center; }
.funnel-value { font-family: Georgia, serif; color: #2A5384; font-size: 17pt; font-weight: 700; }
.panel { background: #FCFAF7; border: 1px solid #D9D3CB; border-radius: 11px; padding: 11px 13px; margin-bottom: 10px; }
.section-head { display: table; width: 100%; border-bottom: 1px solid #DDD7CE; padding-bottom: 6px; margin-bottom: 8px; break-after: avoid; }
.badge { display: table-cell; width: 30px; height: 30px; border-radius: 50%; background: #2A5384; color: white; text-align: center; vertical-align: middle; font-weight: 700; }
.section-title { display: table-cell; vertical-align: middle; padding-left: 9px; color: #6B7882; font-size: 10pt; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
ul, ol { margin: 0 0 8px 17px; padding: 0; }
li { margin-bottom: 4px; }
.takeaway { background: #F4EEE4; border: 1px solid #E7D7BB; border-radius: 8px; padding: 8px 10px; }
.freshness.warning { background: #FFF4DF; border: 1px solid #E6C98C; color: #6C5423; border-radius: 8px; padding: 8px 10px; margin-bottom: 8px; font-weight: 700; }
table { width: 100%; border-collapse: collapse; margin: 5px 0 8px; font-size: 7.5pt; }
thead { display: table-header-group; }
tr { break-inside: avoid; page-break-inside: avoid; }
th, td { border: .5pt solid #D8D5CE; padding: 5px; vertical-align: top; overflow-wrap: anywhere; }
th { background: #F1EBDD; text-align: left; }
tbody tr:nth-child(even) td { background: #FEFCF9; }
.wide-table { font-size: 6.6pt; }
.pricing-table { font-size: 6.2pt; }
.summary-table { max-width: 72%; }
.cash-callout { display: table; width: 100%; background: #F4EEE4; border: 1px solid #E7D7BB; border-radius: 10px; padding: 13px; margin-bottom: 9px; }
.cash-value, .cash-text { display: table-cell; vertical-align: middle; }
.cash-value { width: 34%; font-family: Georgia, serif; color: #2A5384; font-size: 21pt; font-weight: 700; }
.cash-text { padding-left: 10px; font-size: 10pt; font-weight: 700; }
.equity-curve-svg { display: block; width: 100%; height: auto; }
"""


def build_html(state: dict[str, Any], language: str) -> str:
    if language not in {"nl", "en"}:
        raise ValueError("language must be nl or en")
    body = hero(state, language, "investor")
    body += investor_sections(state, language)
    body += hero(state, language, "analyst")
    body += analyst_sections(state, language)
    title = "Weekly ETF EU Review – Nederlands" if language == "nl" else "Weekly ETF EU Review – English"
    return '<!doctype html><html lang="' + language + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>' + e(title) + "</title><style>" + css() + "</style></head><body><main>" + body + "</main></body></html>"


def render(state_path: Path, language: str, html_output: Path, pdf_output: Path) -> None:
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("state_valid") is not True:
        raise RuntimeError("Invalid report state: " + str(state.get("blockers")))
    rendered = build_html(state, language)
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
    print("ETF_EU_CLIENT_GRADE_V2_RENDER_OK | language=" + args.language)


if __name__ == "__main__":
    main()
