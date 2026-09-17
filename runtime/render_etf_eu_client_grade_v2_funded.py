from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any, Iterable

from weasyprint import HTML

from pricing.ucits_close_price_validation_contract_v2 import AUTHORIZED_EXACT_STATUSES
from runtime.equity_curve_eu_contract import render_equity_curve_svg
from runtime.render_etf_eu_client_grade_v2 import css


SECTIONS = {
    "nl": [
        "Besliscockpit",
        "Portefeuille en kapitaal",
        "Regime- en beleidsdashboard",
        "Structurele UCITS-kansenradar",
        "Belangrijkste risico’s en invalidaties",
        "Portefeuilleontwikkeling",
        "Conclusie",
        "Allocatiekaart",
        "Tweede-orde-effecten",
        "UCITS-kandidaten en prijsbewijs",
        "Verificatiefunnel",
        "Review huidige posities",
        "Vervanging, rotatie en vermijdingsradar",
        "Input voor de volgende run",
        "Disclaimer",
    ],
    "en": [
        "Decision cockpit",
        "Portfolio and capital",
        "Regime and policy dashboard",
        "Structural UCITS opportunity radar",
        "Key risks and invalidations",
        "Portfolio development",
        "Conclusion",
        "Allocation map",
        "Second-order effects",
        "UCITS candidates and pricing evidence",
        "Verification funnel",
        "Current-position review",
        "Replacement, rotation and avoidance radar",
        "Input for the next run",
        "Disclaimer",
    ],
}


FORBIDDEN_CLIENT_PHRASES = (
    "two-provider completed-close consensus",
    "two-provider exact-line consensus",
    "valuation-grade two-provider",
    "qualified_development_consensus",
    "single_source_only",
    "funded_model_position_active",
    "priced_non_authoritative",
    "verified_ucits_trading_line",
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


def whole(value: Any, language: str) -> str:
    try:
        amount = int(float(value))
    except (TypeError, ValueError):
        return "0"
    return f"{amount:,}".replace(",", ".") if language == "nl" else f"{amount:,}"


def table(headers: Iterable[str], rows: Iterable[Iterable[str]], css_class: str = "data-table") -> str:
    head = "".join("<th>" + e(item) + "</th>" for item in headers)
    body = "".join(
        "<tr>" + "".join("<td>" + str(value) + "</td>" for value in row) + "</tr>"
        for row in rows
    )
    return '<table class="' + css_class + '"><thead><tr>' + head + "</tr></thead><tbody>" + body + "</tbody></table>"


def section(number: int, title: str, body: str, extra: str = "") -> str:
    head = (
        '<div class="section-head"><span class="badge">'
        + str(number)
        + '</span><span class="section-title">'
        + e(title)
        + "</span></div>"
    )
    return '<section class="panel ' + extra + '">' + head + body + "</section>"


def ticker_of(row: dict[str, Any]) -> str:
    ticker = str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def joined(items: list[str], language: str) -> str:
    clean = [item for item in items if item]
    if not clean:
        return ""
    if len(clean) == 1:
        return clean[0]
    conjunction = " en " if language == "nl" else " and "
    return ", ".join(clean[:-1]) + conjunction + clean[-1]


def _current_run_change_authorized(state: dict[str, Any]) -> bool:
    authority = state.get("authority") if isinstance(state.get("authority"), dict) else {}
    return bool(authority.get("portfolio_mutation") is True or authority.get("trade_ledger_mutation") is True)


def funded_overlay(state: dict[str, Any]) -> dict[str, Any]:
    state = dict(state)
    portfolio = dict(state.get("portfolio") or {})
    positions = [dict(row) for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    portfolio["positions"] = positions
    portfolio["position_count"] = len(positions)
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
    state["verification_funnel"] = funnel

    next_run = dict(state.get("next_run_input") or {})
    existing_priority = [str(item).strip().upper() for item in next_run.get("priority_candidates") or []]
    next_run["priority_candidates"] = list(dict.fromkeys([*funded_tickers, *existing_priority]))
    next_run["required_actions"] = [
        f"re-underwrite every funded position ({', '.join(funded_tickers)}) from current evidence rather than historical target metadata",
        "obtain fresh exact-line completed closes before any add, reduction or new position",
        "run direct replacement duels for any replaceable or weakening holding",
        "classify material cash and deploy only when a distinct lane is fully fundable and separately approved",
    ]
    state["next_run_input"] = next_run

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
        "allocation_map_source": "normalized_current_state",
        "historical_target_copy_rendered": False,
        "allocation_map_reconciled": True,
        "opportunity_radar_reconciled": True,
        "broker_neutral_model_language": True,
        "normalized_state_authority": True,
    }
    return state


def _status_label(status: str, language: str) -> str:
    mapping = {
        "nl": {
            "fresh_exact_verified": "Exacte slotkoers · onafhankelijk geverifieerd",
            "fresh_exact_unverified": "Exacte slotkoers · geen actuele onafhankelijke verifier",
            "provider_disagreement": "Geblokkeerd · prijsconflict tussen bronnen",
            "no_exact_close": "Geblokkeerd · exacte slotkoers ontbreekt",
            "identity_binding_failed": "Geblokkeerd · handelslijnidentiteit niet gebonden",
        },
        "en": {
            "fresh_exact_verified": "Exact close · independently verified",
            "fresh_exact_unverified": "Exact close · no current independent verifier",
            "provider_disagreement": "Blocked · provider price disagreement",
            "no_exact_close": "Blocked · exact close unavailable",
            "identity_binding_failed": "Blocked · trading-line identity not bound",
        },
    }
    return mapping[language].get(status, "Geen prijsautoriteit" if language == "nl" else "No pricing authority")


def _pricing_counts(state: dict[str, Any]) -> tuple[int, int, int]:
    rows = [row for row in (state.get("pricing") or {}).get("rows") or [] if isinstance(row, dict)]
    verified = sum(str(row.get("authority_status") or row.get("verification_status") or "") == "fresh_exact_verified" for row in rows)
    primary_only = sum(str(row.get("authority_status") or row.get("verification_status") or "") == "fresh_exact_unverified" for row in rows)
    authorized = verified + primary_only
    return authorized, verified, primary_only


def _hero(state: dict[str, Any], language: str, report_type: str) -> str:
    macro = state.get("macro") or {}
    regime = macro.get("regime_nl") if language == "nl" else macro.get("regime")
    if macro.get("fresh_for_report") is not True:
        regime = "Macro-refresh vereist" if language == "nl" else "Macro refresh required"
    portfolio = state.get("portfolio") or {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    tickers = [ticker_of(row) for row in positions]
    label = "Beleggersrapport" if language == "nl" else "Investor report"
    if report_type == "analyst":
        label = "Analistenrapport" if language == "nl" else "Analyst report"
    class_name = "hero hero-secondary" if report_type == "analyst" else "hero"
    brand = "WEKELIJKSE ETF EU-REVIEW" if language == "nl" else "WEEKLY ETF EU REVIEW"
    result = (
        f'<header class="{class_name}"><div class="hero-row"><div><div class="masthead">{e(brand)}</div>'
        f'<div class="hero-date">{e(state.get("report_date"))}</div></div><div class="hero-type">{e(label)}</div></div></header>'
        '<div class="hero-rule"></div>'
    )
    if report_type == "investor":
        funded_label = (
            f"{len(positions)} modelposities actief"
            if language == "nl"
            else f"{len(positions)} model positions active"
        )
        takeaway = (
            f"Beschermde modelportefeuille: {joined(tickers, 'nl')}; iedere wijziging vereist actuele re-underwriting en een afzonderlijk allocatiebesluit."
            if language == "nl"
            else f"Protected model portfolio: {joined(tickers, 'en')}; every change requires current re-underwriting and a separate allocation decision."
        )
        result += '<div class="notice">' + e(
            "Dit rapport is uitsluitend informatief en educatief. UCITS-identiteit en actuele canonical pricing state zijn leidend."
            if language == "nl"
            else "This report is for informational and educational purposes only. UCITS identity and current canonical pricing state are authoritative."
        ) + "</div>"
        cards = [
            ("Primair regime" if language == "nl" else "Primary regime", regime or "n/a"),
            ("Portefeuilleactie" if language == "nl" else "Portfolio action", funded_label),
            ("Kernconclusie" if language == "nl" else "Main conclusion", takeaway),
        ]
        result += '<div class="summary-strip">' + "".join(
            '<div class="mini-card"><div class="mini-label">' + e(key) + '</div><div class="mini-value">' + e(value) + "</div></div>"
            for key, value in cards
        ) + "</div>"
    return result


def _investor_sections(state: dict[str, Any], language: str) -> str:
    titles = SECTIONS[language]
    portfolio = state.get("portfolio") or {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    tickers = [ticker_of(row) for row in positions]
    authorized, verified, primary_only = _pricing_counts(state)
    mutation = _current_run_change_authorized(state)

    if language == "nl":
        cockpit = [
            f"Deze run: {'een modelportefeuillewijziging is geautoriseerd' if mutation else 'geen modelportefeuillewijziging is geautoriseerd'}; {len(positions)} beschermde modelposities actief — {joined(tickers, 'nl')}.",
            f"Gefinancierde prijsautoriteit: {len(positions)} van {len(positions)} funded lijnen moeten exact-date canonical pricing authority hebben; confidence wordt per lijn afzonderlijk getoond.",
            f"Totale prijslaag: {authorized} geautoriseerde lijnen, waarvan {verified} onafhankelijk geverifieerd en {primary_only} zonder actuele verifier.",
            "Prijsautoriteit creëert nooit zelfstandig funding-, allocatie-, broker- of delivery-authority.",
        ]
        portfolio_headers = ["Component", "Waarde"]
        decision_rule = "Wijzig alleen vanuit actuele re-underwriting, canonical exact-close pricing authority, fundability en een afzonderlijk allocatiebesluit."
        portfolio_note = f"De modelportefeuille heeft {money(portfolio.get('invested_market_value_eur'), language)} belegd en {money(portfolio.get('cash_eur'), language)} cash; geen echte brokeruitvoering."
    else:
        cockpit = [
            f"This run: {'a model-portfolio change is authorized' if mutation else 'no model-portfolio change is authorized'}; {len(positions)} protected model positions are active — {joined(tickers, 'en')}.",
            f"Funded pricing authority: all {len(positions)} funded lines must carry exact-date canonical pricing authority; confidence is shown separately per line.",
            f"Full pricing layer: {authorized} authorized lines, of which {verified} independently verified and {primary_only} without a current verifier.",
            "Pricing authority never independently creates funding, allocation, broker or delivery authority.",
        ]
        portfolio_headers = ["Component", "Value"]
        decision_rule = "Change only from current re-underwriting, canonical exact-close pricing authority, fundability and a separate allocation decision."
        portfolio_note = f"The model portfolio has {money(portfolio.get('invested_market_value_eur'), language)} invested and {money(portfolio.get('cash_eur'), language)} in cash; no real broker execution."

    cockpit_body = "<ul>" + "".join("<li>" + e(item) + "</li>" for item in cockpit) + "</ul>"
    cockpit_body += '<div class="takeaway"><strong>' + ("Beslisregel: " if language == "nl" else "Decision rule: ") + "</strong>" + e(decision_rule) + "</div>"
    portfolio_rows = [
        ["Startkapitaal" if language == "nl" else "Starting capital", money(portfolio.get("starting_capital_eur"), language)],
        ["Cash", money(portfolio.get("cash_eur"), language)],
        ["Belegde marktwaarde" if language == "nl" else "Invested market value", money(portfolio.get("invested_market_value_eur"), language)],
        ["Totale portefeuillewaarde" if language == "nl" else "Total portfolio value", money(portfolio.get("nav_eur"), language)],
        ["Rendement sinds start" if language == "nl" else "Return since inception", num(portfolio.get("since_inception_return_pct"), language) + "%"],
        ["Gefinancierde posities" if language == "nl" else "Funded positions", e(len(positions))],
    ]
    portfolio_body = table(portfolio_headers, portfolio_rows, "summary-table") + '<div class="note-box">' + e(portfolio_note) + "</div>"

    macro = state.get("macro") or {}
    stale = macro.get("fresh_for_report") is not True
    freshness = (
        f"Historische macrocontext van {macro.get('source_report_date')}; macro-refresh vereist vóór een actuele macroclaim."
        if language == "nl" and stale
        else f"Historical macro context dated {macro.get('source_report_date')}; macro refresh required before a current macro claim."
        if stale
        else "Macro-pack is voldoende actueel."
        if language == "nl"
        else "Macro pack is sufficiently current."
    )
    macro_rows = [
        ["Regime", e(macro.get("regime_nl") if language == "nl" else macro.get("regime")), e("Context, geen allocatiebevoegdheid." if language == "nl" else "Context, not allocation authority.")],
        ["Federal Reserve", e((macro.get("fed") or {}).get("stance_nl") if language == "nl" else (macro.get("fed") or {}).get("stance")), e((macro.get("fed") or {}).get("implication") or "n/a")],
        ["ECB", e((macro.get("ecb") or {}).get("stance_nl") if language == "nl" else (macro.get("ecb") or {}).get("stance")), e((macro.get("ecb") or {}).get("implication") or "n/a")],
    ]
    macro_body = '<div class="freshness warning">' + e(freshness) + "</div>" + table(
        ["Onderdeel", "Lezing", "Implicatie"] if language == "nl" else ["Component", "Reading", "Implication"],
        macro_rows,
    )

    radar_rows: list[list[str]] = []
    funded_set = set(tickers)
    for lane in state.get("opportunity_radar") or []:
        if not isinstance(lane, dict):
            continue
        candidates = [str(value).strip().upper() for value in lane.get("candidate_tickers") or lane.get("tickers") or []]
        active = sorted(funded_set & set(candidates))
        status = (
            ("Actieve modelpositie: " if language == "nl" else "Active model position: ") + joined(active, language)
            if active
            else ("Research / fundability nog niet afgerond" if language == "nl" else "Research / fundability not yet complete")
        )
        radar_rows.append(
            [
                e(lane.get("name_nl") if language == "nl" else lane.get("name_en") or lane.get("lane_name")),
                e(", ".join(candidates)),
                e((lane.get("research_reference") or "—") + (" · alleen onderzoek" if language == "nl" else " · research only")),
                e(status),
                e(lane.get("horizon") or "n/a"),
            ]
        )
    radar_body = table(
        ["Thema", "UCITS-lijnen", "Onderzoeksreferentie", "Actuele status", "Horizon"] if language == "nl" else ["Theme", "UCITS lines", "Research reference", "Current status", "Horizon"],
        radar_rows,
        "wide-table",
    )

    unresolved = max(int((state.get("verification_funnel") or {}).get("unresolved_lines") or 0), 0)
    risk_items = [
        (
            "Same-date prijsconflict blokkeert valuation-grade pricing authority."
            if language == "nl"
            else "Same-date provider disagreement blocks valuation-grade pricing authority."
        ),
        (
            f"{unresolved} prijsregels hebben geen canonical pricing authority en blijven buiten fundingbesluiten."
            if language == "nl"
            else f"{unresolved} pricing rows lack canonical pricing authority and remain outside funding decisions."
        ),
        (
            "Factoroverlap tussen VWCE en SXR8 moet als expliciete concentratie worden beoordeeld."
            if language == "nl"
            else "Factor overlap between VWCE and SXR8 must be treated as explicit concentration."
        ),
        (
            "Materiële cash blijft deploy-or-explain: alleen inzetten als een distincte lane volledig fundable is."
            if language == "nl"
            else "Material cash remains deploy-or-explain: deploy only when a distinct lane is fully fundable."
        ),
    ]
    risk_body = "<ul>" + "".join("<li>" + e(item) + "</li>" for item in risk_items) + "</ul>"

    curve = render_equity_curve_svg(state, language=language)
    if curve:
        development_body = curve
    else:
        fallback = (state.get("equity_curve") or {}).get("fallback_nl" if language == "nl" else "fallback_en") or (
            "Nog onvoldoende gevalideerde NAV-historie voor een betekenisvolle curve."
            if language == "nl"
            else "Insufficient validated NAV history for a meaningful curve."
        )
        development_body = '<div class="cash-callout"><div class="cash-value">' + money(portfolio.get("cash_eur"), language) + '</div><div class="cash-text">' + e(fallback) + "</div></div>"

    conclusion = (
        f"Behoud de beschermde modelportefeuille ({joined(tickers, 'nl')}) onder actuele re-underwriting. Gebruik canonical pricing authority voor waardering, en behandel onafhankelijke verificatie uitsluitend als confidence-evidence."
        if language == "nl"
        else f"Preserve the protected model portfolio ({joined(tickers, 'en')}) under current re-underwriting. Use canonical pricing authority for valuation and treat independent verification only as confidence evidence."
    )
    return "".join(
        [
            section(1, titles[0], cockpit_body),
            section(2, titles[1], portfolio_body),
            section(3, titles[2], macro_body),
            section(4, titles[3], radar_body, "panel-wide"),
            section(5, titles[4], risk_body),
            section(6, titles[5], development_body),
            section(7, titles[6], "<p>" + e(conclusion) + "</p>"),
        ]
    )


def _analyst_sections(state: dict[str, Any], language: str) -> str:
    titles = SECTIONS[language]
    portfolio = state.get("portfolio") or {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    funded_set = {ticker_of(row) for row in positions}

    allocation_rows = [
        [
            e(ticker_of(row)),
            e((row.get("portfolio_role") or "Funded model position")),
            num(row.get("current_weight_pct"), language) + "%",
            e(row.get("current_allocation_decision") or "hold"),
        ]
        for row in positions
    ]
    allocation_rows.append(
        [
            "Cash",
            e((portfolio.get("cash_classification") or "Tactical reserve")),
            num((float(portfolio.get("cash_eur") or 0) / float(portfolio.get("nav_eur") or 1)) * 100.0, language) + "%",
            e("Deploy-or-explain"),
        ]
    )
    allocation_body = table(
        ["Segment", "Rol", "Gewicht", "Actueel besluit"] if language == "nl" else ["Segment", "Role", "Weight", "Current decision"],
        allocation_rows,
    )

    effects = state.get("second_order_effects") or []
    effect_rows = [
        [
            e(item.get("driver_nl") if language == "nl" else item.get("driver_en")),
            e(item.get("first_nl") if language == "nl" else item.get("first_en")),
            e(item.get("second_nl") if language == "nl" else item.get("second_en")),
            e(item.get("implication_nl") if language == "nl" else item.get("implication_en")),
        ]
        for item in effects
        if isinstance(item, dict)
    ]
    effect_body = table(
        ["Drijver", "Eerste orde", "Tweede orde", "ETF EU-implicatie"] if language == "nl" else ["Driver", "First order", "Second order", "ETF EU implication"],
        effect_rows,
        "wide-table",
    )

    pricing_rows: list[list[str]] = []
    for row in (state.get("pricing") or {}).get("rows") or []:
        if not isinstance(row, dict):
            continue
        ticker = str(row.get("ticker") or "").strip().upper()
        status = str(row.get("authority_status") or row.get("verification_status") or "")
        role = "Gefinancierd" if ticker in funded_set and language == "nl" else "Funded" if ticker in funded_set else "Alleen onderzoek" if language == "nl" else "Research only"
        verification = ", ".join(str(value) for value in row.get("verification_providers") or []) or ("geen actuele verifier" if language == "nl" else "no current verifier")
        pricing_rows.append(
            [
                e(ticker),
                e(row.get("fund_name")),
                e(row.get("isin")),
                e(row.get("exchange")),
                e(row.get("close_date") or "n/a"),
                num(row.get("close_price"), language),
                e(row.get("currency")),
                e(_status_label(status, language)),
                e(row.get("primary_provider") or "n/a"),
                e(verification),
                e(role),
            ]
        )
    pricing_note = (
        "Iedere prijsclaim in deze tabel is rechtstreeks afgeleid van canonical pricing state. Exact primary pricing kan waarderingsautoriteit dragen; een verifier verhoogt confidence en same-date disagreement blokkeert."
        if language == "nl"
        else "Every pricing claim in this table is derived directly from canonical pricing state. Exact primary pricing can carry valuation authority; a verifier increases confidence and same-date disagreement blocks."
    )
    pricing_body = '<div class="note-box">' + e(pricing_note) + "</div>" + table(
        ["Handelslijn", "Fonds", "ISIN", "Beurs", "Peildatum", "Slot", "Valuta", "Prijsautoriteit", "Primary", "Verifier", "Rol"]
        if language == "nl"
        else ["Trading line", "Fund", "ISIN", "Exchange", "Pricing date", "Close", "Currency", "Pricing authority", "Primary", "Verifier", "Role"],
        pricing_rows,
        "wide-table pricing-table",
    )

    funnel = state.get("verification_funnel") or {}
    cards = [
        ("Geobserveerd" if language == "nl" else "Observed", funnel.get("observed_lines", 0)),
        ("Geprijsd" if language == "nl" else "Priced", funnel.get("priced_lines", 0)),
        ("Prijsautoriteit" if language == "nl" else "Authorized", funnel.get("authorized_lines", 0)),
        ("Geverifieerd" if language == "nl" else "Verified", funnel.get("verified_lines", 0)),
        ("Primary-only", funnel.get("primary_only_lines", 0)),
        ("Gefinancierd" if language == "nl" else "Funded", len(positions)),
    ]
    funnel_body = '<div class="funnel-strip">' + "".join(
        '<div class="funnel-card"><div class="funnel-value">' + e(value) + '</div><div class="funnel-label">' + e(label) + "</div></div>"
        for label, value in cards
    ) + "</div>"
    funnel_body += '<div class="note-box">' + e(
        "Prijsautoriteit is een waarderingsinput; fundability en allocatie blijven afzonderlijke gates."
        if language == "nl"
        else "Pricing authority is a valuation input; fundability and allocation remain separate gates."
    ) + "</div>"

    valuation_lines = {
        str(row.get("ticker") or "").strip().upper(): row
        for row in (portfolio.get("derived_valuation") or {}).get("lines") or []
        if isinstance(row, dict)
    }
    position_rows: list[list[str]] = []
    for row in positions:
        ticker = ticker_of(row)
        evidence = valuation_lines.get(ticker, {})
        status = str(row.get("verification_status") or evidence.get("source_agreement_status") or "")
        position_rows.append(
            [
                e(ticker),
                e(row.get("isin")),
                e(whole(row.get("shares"), language)),
                money(row.get("current_price_local"), language),
                e(row.get("price_date")),
                money(row.get("market_value_eur"), language),
                num(row.get("current_weight_pct"), language) + "%",
                e(_status_label(status, language)),
                e(row.get("implementation_assessment") or "n/a"),
                e(row.get("required_next_action") or "n/a"),
            ]
        )
    positions_body = table(
        ["Handelslijn", "ISIN", "Stukken", "Prijs", "Peildatum", "Marktwaarde", "Gewicht", "Prijsautoriteit", "Implementation", "Volgende actie"]
        if language == "nl"
        else ["Trading line", "ISIN", "Shares", "Price", "Pricing date", "Market value", "Weight", "Pricing authority", "Implementation", "Next action"],
        position_rows,
        "wide-table",
    )

    replacement_rows = [
        [
            e(ticker_of(row)),
            e(row.get("replaceable_status") or "n/a"),
            e(row.get("best_alternative") or "n/a"),
            e(row.get("replacement_duel_status") or "n/a"),
            e(row.get("next_review_trigger") or "n/a"),
        ]
        for row in positions
    ]
    replacement_body = table(
        ["Positie", "Vervangbaar", "Beste alternatief", "Duelstatus", "Reviewtrigger"]
        if language == "nl"
        else ["Position", "Replaceable", "Best alternative", "Duel status", "Review trigger"],
        replacement_rows,
        "wide-table",
    )

    next_run = state.get("next_run_input") or {}
    next_items = [
        ("Portefeuillestaat" if language == "nl" else "Portfolio state") + ": " + str(next_run.get("portfolio_state") or "n/a"),
        ("Waarderingshistorie" if language == "nl" else "Valuation history") + ": " + str(next_run.get("valuation_history") or "n/a"),
        ("Prijsartifact" if language == "nl" else "Pricing artifact") + ": " + str(next_run.get("pricing_artifact") or "n/a"),
        ("Prioriteitskandidaten" if language == "nl" else "Priority candidates") + ": " + ", ".join(str(value) for value in next_run.get("priority_candidates") or []),
    ]
    next_body = "<ul>" + "".join("<li>" + e(item) + "</li>" for item in next_items) + "</ul><ol>" + "".join(
        "<li>" + e(item) + "</li>" for item in next_run.get("required_actions") or []
    ) + "</ol>"

    disclaimer = (
        "Dit rapport is uitsluitend informatief en educatief en is geen beleggings-, juridisch, fiscaal of financieel advies. Amerikaanse ETF-symbolen zijn uitsluitend onderzoeksreferenties; EU-productautoriteit blijft ISIN-first en UCITS-first. Geen echte brokeruitvoering of e-maildelivery is door deze rapportgeneratie geautoriseerd."
        if language == "nl"
        else "This report is for informational and educational purposes only and is not investment, legal, tax or financial advice. U.S. ETF symbols are research references only; EU product authority remains ISIN-first and UCITS-first. No real broker execution or email delivery is authorized by this report generation."
    )

    return "".join(
        [
            section(8, titles[7], allocation_body),
            section(9, titles[8], effect_body, "panel-wide"),
            section(10, titles[9], pricing_body, "panel-wide"),
            section(11, titles[10], funnel_body),
            section(12, titles[11], positions_body, "panel-wide"),
            section(13, titles[12], replacement_body, "panel-wide"),
            section(14, titles[13], next_body),
            section(15, titles[14], "<p>" + e(disclaimer) + "</p>"),
        ]
    )


def build_html(state: dict[str, Any], language: str) -> str:
    if language not in {"nl", "en"}:
        raise ValueError("language must be nl or en")
    if state.get("state_valid") is not True:
        raise RuntimeError("Invalid report state: " + str(state.get("blockers")))
    state = funded_overlay(state)
    body = _hero(state, language, "investor")
    body += _investor_sections(state, language)
    body += _hero(state, language, "analyst")
    body += _analyst_sections(state, language)
    title = "Weekly ETF EU Review – Nederlands" if language == "nl" else "Weekly ETF EU Review – English"
    rendered = (
        '<!doctype html><html lang="'
        + language
        + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'
        + e(title)
        + "</title><style>"
        + css()
        + "</style></head><body><main>"
        + body
        + "</main></body></html>"
    )
    validate_client_surface(rendered, state)
    return rendered


def validate_client_surface(rendered: str, state: dict[str, Any]) -> None:
    folded = rendered.casefold()
    for phrase in FORBIDDEN_CLIENT_PHRASES:
        if phrase.casefold() in folded:
            raise RuntimeError(f"ETF_EU_RETIRED_CLIENT_COPY_LEAK={phrase}")
    positions = [row for row in (state.get("portfolio") or {}).get("positions") or [] if isinstance(row, dict)]
    count = len(positions)
    for language_token in (f"{count} modelposities actief", f"{count} model positions active"):
        if language_token.casefold() in folded:
            break
    else:
        raise RuntimeError("ETF_EU_FUNDED_POSITION_COUNT_SUMMARY_MISSING")
    for row in positions:
        ticker = ticker_of(row)
        if ticker and ticker.casefold() not in folded:
            raise RuntimeError(f"ETF_EU_FUNDED_TICKER_MISSING_FROM_CLIENT_SURFACE={ticker}")


def render(state_path: Path, language: str, html_output: Path, pdf_output: Path) -> None:
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state = funded_overlay(state)
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
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
    print("ETF_EU_CLIENT_GRADE_V3_NATIVE_RENDER_OK | language=" + args.language)


if __name__ == "__main__":
    main()
