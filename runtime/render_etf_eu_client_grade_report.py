from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any, Iterable

from weasyprint import HTML

from runtime.equity_curve_eu_contract import render_equity_curve_svg


STATUS_LABELS = {
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


COPY = {
    "nl": {
        "brand": "WEKELIJKSE ETF EU-REVIEW",
        "investor_report": "Beleggersrapport",
        "analyst_report": "Analistenrapport",
        "notice": "Dit rapport is uitsluitend informatief en educatief. UCITS-identiteit, handelslijn en productbeleid blijven leidend; zie de disclaimer aan het einde.",
        "primary_regime": "Primair regime",
        "portfolio_action": "Portefeuilleactie",
        "main_conclusion": "Kernconclusie",
        "macro_refresh": "Macro-refresh vereist",
        "cash_hold": "Cash behouden",
        "main_takeaway": "De S&P 500 UCITS-lijnen zijn operationeel het verst gevorderd, maar inzet van kapitaal vereist een afzonderlijk allocatiebesluit.",
        "section_1": "Besliscockpit",
        "section_2": "Portefeuille en kapitaal",
        "section_3": "Regime- en beleidsdashboard",
        "section_4": "Structurele UCITS-kansenradar",
        "section_5": "Belangrijkste risico’s en invalidaties",
        "section_6": "Portefeuilleontwikkeling",
        "section_7": "Conclusie",
        "section_8": "Allocatiekaart",
        "section_9": "Tweede-orde-effecten",
        "section_10": "UCITS-kandidaten en prijsbewijs",
        "section_11": "Verificatiefunnel",
        "section_12": "Review huidige posities",
        "section_13": "Vervanging, rotatie en vermijdingsradar",
        "section_14": "Input voor de volgende run",
        "section_15": "Disclaimer",
    },
    "en": {
        "brand": "WEEKLY ETF EU REVIEW",
        "investor_report": "Investor report",
        "analyst_report": "Analyst report",
        "notice": "This report is for informational and educational purposes only. UCITS identity, trading line and product policy remain authoritative; see the disclaimer at the end.",
        "primary_regime": "Primary regime",
        "portfolio_action": "Portfolio action",
        "main_conclusion": "Main conclusion",
        "macro_refresh": "Macro refresh required",
        "cash_hold": "Retain cash",
        "main_takeaway": "The S&P 500 UCITS lines are operationally most advanced, but capital deployment requires a separate allocation decision.",
        "section_1": "Decision cockpit",
        "section_2": "Portfolio and capital",
        "section_3": "Regime and policy dashboard",
        "section_4": "Structural UCITS opportunity radar",
        "section_5": "Key risks and invalidations",
        "section_6": "Portfolio development",
        "section_7": "Conclusion",
        "section_8": "Allocation map",
        "section_9": "Second-order effects",
        "section_10": "UCITS candidates and pricing evidence",
        "section_11": "Verification funnel",
        "section_12": "Current-position review",
        "section_13": "Replacement, rotation and avoidance radar",
        "section_14": "Input for the next run",
        "section_15": "Disclaimer",
    },
}


def _e(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def _money(value: Any, *, language: str) -> str:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if language == "nl":
        formatted = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        formatted = f"{amount:,.2f}"
    return f"€ {formatted}"


def _number(value: Any, *, decimals: int = 2, language: str = "nl") -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "n/a"
    formatted = f"{number:,.{decimals}f}"
    if language == "nl":
        return formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return formatted


def _pct(value: Any, *, language: str) -> str:
    return f"{_number(value, decimals=2, language=language)}%"


def _load_state(path: Path) -> dict[str, Any]:
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("state_valid") is not True:
        raise RuntimeError(f"Client-grade report state is not valid: {state.get('blockers')}")
    return state


def _section_header(number: int, title: str) -> str:
    return (
        '<div class="section-kicker">'
        f'<span class="section-badge">{number}</span>'
        f'<span class="section-title">{_e(title)}</span>'
        "</div>"
    )


def _panel(content: str, *, extra: str = "") -> str:
    return f'<section class="panel {extra}">{content}</section>'


def _rows_table(headers: Iterable[str], rows: Iterable[Iterable[str]], *, css_class: str = "data-table") -> str:
    head = "".join(f"<th>{_e(value)}</th>" for value in headers)
    body = "".join("<tr>" + "".join(f"<td>{value}</td>" for value in row) + "</tr>" for row in rows)
    return f'<table class="{css_class}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def _hero(state: dict[str, Any], *, language: str, report_type: str) -> str:
    c = COPY[language]
    macro = state["macro"]
    regime = macro["regime_nl"] if language == "nl" else macro["regime"]
    if not macro["fresh_for_report"]:
        regime = c["macro_refresh"]
    return f"""
<header class="hero {'hero-secondary' if report_type == 'analyst' else ''}">
  <div class="hero-row">
    <div>
      <div class="masthead">{_e(c['brand'])}</div>
      <div class="hero-date">{_e(state['report_date'])}</div>
    </div>
    <div class="hero-type">{_e(c['analyst_report'] if report_type == 'analyst' else c['investor_report'])}</div>
  </div>
</header>
<div class="hero-rule"></div>
{'' if report_type == 'analyst' else f'''<div class="notice">{_e(c['notice'])}</div>
<div class="summary-strip">
  <div class="mini-card"><div class="mini-label">{_e(c['primary_regime'])}</div><div class="mini-value">{_e(regime)}</div></div>
  <div class="mini-card"><div class="mini-label">{_e(c['portfolio_action'])}</div><div class="mini-value">{_e(c['cash_hold'])}</div></div>
  <div class="mini-card"><div class="mini-label">{_e(c['main_conclusion'])}</div><div class="mini-value mini-value-small">{_e(c['main_takeaway'])}</div></div>
</div>'''}
"""


def _decision_cockpit(state: dict[str, Any], language: str) -> str:
    funnel = state["verification_funnel"]
    macro = state["macro"]
    if language == "nl":
        bullets = [
            "Deze week: geen portefeuilletransactie; de EU-modelportefeuille blijft volledig in cash.",
            f"Meest volwassen implementatie: {funnel['verified_lines']} geverifieerde UCITS-handelslijnen, beide voor brede Amerikaanse kernaandelen.",
            f"Belangrijkste actieve blokkade: {funnel['observed_lines'] - funnel['verified_lines']} lijnen zijn nog niet volledig geverifieerd of geprijsd.",
            "Trigger voor volgende actie: brokerbeschikbaarheid, actuele prijsbasis, bronovereenkomst en een afzonderlijk allocatiebesluit moeten samen positief zijn.",
            "Macrocontext: verversing is vereist vóór productiepromotie." if not macro["fresh_for_report"] else "Macrocontext: actueel genoeg voor deze rapportdatum.",
        ]
        takeaway = "Versnel verificatie van SXR8/CSPX en de gewenste EUR-handelslijn, zonder het afzonderlijke allocatiebesluit over te slaan."
    else:
        bullets = [
            "This week: no portfolio transaction; the EU model portfolio remains fully in cash.",
            f"Most mature implementation: {funnel['verified_lines']} verified UCITS trading lines, both providing broad U.S. core equity exposure.",
            f"Main active blocker: {funnel['observed_lines'] - funnel['verified_lines']} lines are not yet fully verified or priced.",
            "Next-action trigger: broker availability, current pricing, source agreement and a separate allocation decision must all be positive.",
            "Macro context: refresh is required before production promotion." if not macro["fresh_for_report"] else "Macro context: sufficiently current for this report date.",
        ]
        takeaway = "Accelerate SXR8/CSPX and preferred EUR-line verification without bypassing the separate allocation decision."
    content = _section_header(1, COPY[language]["section_1"])
    content += '<ul class="cockpit-list">' + "".join(f"<li>{_e(item)}</li>" for item in bullets) + "</ul>"
    content += f'<div class="takeaway"><div class="takeaway-label">{"Beslisregel" if language == "nl" else "Decision rule"}</div><div class="takeaway-text">{_e(takeaway)}</div></div>'
    return _panel(content, extra="panel-cockpit")


def _portfolio_section(state: dict[str, Any], language: str) -> str:
    p = state["portfolio"]
    if language == "nl":
        headers = ["Component", "Waarde"]
        rows = [
            ["Startkapitaal", _money(p["starting_capital_eur"], language=language)],
            ["Cash", _money(p["cash_eur"], language=language)],
            ["Belegde marktwaarde", _money(p["invested_market_value_eur"], language=language)],
            ["Totale portefeuillewaarde", _money(p["nav_eur"], language=language)],
            ["Rendement sinds start", _pct(p["since_inception_return_pct"], language=language)],
            ["Gefinancierde posities", _e(p["position_count"])],
        ]
        note = "De portefeuille is nog niet belegd. Dit is een bewuste kapitaalbeschermingsstatus, geen ontbrekende portefeuillegegevens."
    else:
        headers = ["Component", "Value"]
        rows = [
            ["Starting capital", _money(p["starting_capital_eur"], language=language)],
            ["Cash", _money(p["cash_eur"], language=language)],
            ["Invested market value", _money(p["invested_market_value_eur"], language=language)],
            ["Total portfolio value", _money(p["nav_eur"], language=language)],
            ["Return since inception", _pct(p["since_inception_return_pct"], language=language)],
            ["Funded positions", _e(p["position_count"])],
        ]
        note = "The portfolio is not yet invested. This is a deliberate capital-preservation state, not missing portfolio data."
    content = _section_header(2, COPY[language]["section_2"])
    content += _rows_table(headers, rows, css_class="summary-table")
    content += f'<div class="note-box">{_e(note)}</div>'
    return _panel(content)


def _macro_section(state: dict[str, Any], language: str) -> str:
    m = state["macro"]
    stale = not m["fresh_for_report"]
    if language == "nl":
        freshness = (
            f"Historische context uit macro-pack van {m.get('source_report_date') or 'onbekende datum'}; {m.get('age_days')} dagen oud. Verversing vereist vóór productiepromotie."
            if stale else "Macro-pack is voldoende actueel voor deze rapportdatum."
        )
        regime = m["regime_nl"]
        fed_stance = m["fed"]["stance_nl"]
        ecb_stance = m["ecb"]["stance_nl"]
        headers = ["Onderdeel", "Lezing", "Portefeuille-implicatie"]
        rows = [
            ["Regime", _e(regime), _e("Alleen historische context; geen allocatiebevoegdheid." if stale else (m["decision_rule"] or "Behoud selectiviteit."))],
            ["Federal Reserve", _e(fed_stance), _e(m["fed"].get("implication") or "Geen actuele implicatie beschikbaar.")],
            ["ECB", _e(ecb_stance), _e(m["ecb"].get("implication") or "Geen actuele implicatie beschikbaar.")],
        ]
        changed_title = "Wat het beschikbare macrobeeld benadrukt"
        catalyst_title = "Beleidscatalysatoren"
    else:
        freshness = (
            f"Historical context from macro pack dated {m.get('source_report_date') or 'unknown'}; {m.get('age_days')} days old. Refresh required before production promotion."
            if stale else "Macro pack is sufficiently current for this report date."
        )
        regime = m["regime"]
        fed_stance = m["fed"]["stance"] or "Unavailable"
        ecb_stance = m["ecb"]["stance"] or "Unavailable"
        headers = ["Component", "Reading", "Portfolio implication"]
        rows = [
            ["Regime", _e(regime), _e("Historical context only; no allocation authority." if stale else (m["decision_rule"] or "Retain selectivity."))],
            ["Federal Reserve", _e(fed_stance), _e(m["fed"].get("implication") or "No current implication available.")],
            ["ECB", _e(ecb_stance), _e(m["ecb"].get("implication") or "No current implication available.")],
        ]
        changed_title = "What the available macro context highlights"
        catalyst_title = "Policy catalysts"
    content = _section_header(3, COPY[language]["section_3"])
    content += f'<div class="freshness-banner {"warning" if stale else "ok"}">{_e(freshness)}</div>'
    content += _rows_table(headers, rows)
    changed = m.get("what_changed") or []
    if changed:
        content += f'<h3>{_e(changed_title)}</h3><ul>' + "".join(f"<li>{_e(item)}</li>" for item in changed) + "</ul>"
    catalysts = m.get("catalysts") or []
    if catalysts:
        content += f'<h3>{_e(catalyst_title)}</h3><ul>' + "".join(f"<li><strong>{_e(item.get('area'))}:</strong> {_e(item.get('signal'))}</li>" for item in catalysts) + "</ul>"
    return _panel(content)


def _opportunity_section(state: dict[str, Any], language: str) -> str:
    lanes = state["opportunity_radar"]
    if language == "nl":
        headers = ["Thema", "UCITS-kandidaten", "Onderzoeksreferentie", "Waarom relevant", "Structureel", "Implementatie", "Status", "Benodigde bevestiging", "Horizon"]
    else:
        headers = ["Theme", "UCITS candidates", "Research reference", "Why relevant", "Structural", "Implementation", "Status", "Required confirmation", "Horizon"]
    rows = []
    for lane in lanes:
        status = STATUS_LABELS[language].get(lane["status"], lane["status"])
        rows.append(
            [
                _e(lane["name_nl"] if language == "nl" else lane["name_en"]),
                _e(", ".join(lane["candidate_tickers"])),
                _e(lane["research_reference"] + (" · alleen onderzoek" if language == "nl" else " · research only")),
                _e(lane["why_nl"] if language == "nl" else lane["why_en"]),
                _e(lane["structural_score"]),
                _e(lane["implementation_score"]),
                _e(status),
                _e(lane["next_confirmation_nl"] if language == "nl" else lane["next_confirmation_en"]),
                _e(lane["horizon"]),
            ]
        )
    content = _section_header(4, COPY[language]["section_4"])
    content += '<div class="note-box">' + _e(
        "Scores tonen structurele relevantie en implementatiematuriteit; zij geven geen allocatiebevoegdheid."
        if language == "nl" else
        "Scores show structural relevance and implementation maturity; they do not provide allocation authority."
    ) + "</div>"
    content += _rows_table(headers, rows, css_class="wide-table radar-table")
    return _panel(content, extra="panel-wide")


def _risk_section(state: dict[str, Any], language: str) -> str:
    if language == "nl":
        headers = ["Actief risico", "Wat het risico ongeldig maakt of oplost"]
    else:
        headers = ["Active risk", "What invalidates or resolves the risk"]
    rows = []
    for item in state["risks"]:
        rows.append([
            _e(item["risk_nl"] if language == "nl" else item["risk_en"]),
            _e(item["invalidation_nl"] if language == "nl" else item["invalidation_en"]),
        ])
    content = _section_header(5, COPY[language]["section_5"])
    content += _rows_table(headers, rows)
    return _panel(content)


def _portfolio_development(state: dict[str, Any], language: str) -> str:
    curve = state["equity_curve"]
    p = state["portfolio"]
    content = _section_header(6, COPY[language]["section_6"])
    svg = render_equity_curve_svg(state, language=language)
    if svg:
        content += svg
    else:
        fallback = curve["fallback_nl"] if language == "nl" else curve["fallback_en"]
        content += f'<div class="cash-callout"><div class="cash-value">{_money(p["cash_eur"], language=language)}</div><div class="cash-text">{_e(fallback)}</div></div>'
    history = state.get("valuation_history") or []
    if language == "nl":
        headers = ["Datum", "Portefeuillewaarde", "Cash", "Belegd", "Toelichting"]
    else:
        headers = ["Date", "Portfolio value", "Cash", "Invested", "Comment"]
    rows = [
        [
            _e(row["date"]),
            _money(row["nav_eur"], language=language),
            _money(row["cash_eur"], language=language),
            _money(row["invested_market_value_eur"], language=language),
            _e(row["comment"]),
        ]
        for row in history
    ]
    if rows:
        content += _rows_table(headers, rows)
    return _panel(content)


def _conclusion(state: dict[str, Any], language: str) -> str:
    verified = state["verification_funnel"]["verified_lines"]
    if language == "nl":
        bullets = [
            f"Portefeuillehouding: behoud EUR 100.000 cash totdat een afzonderlijk allocatiebesluit is genomen.",
            f"Best onderbouwde implementatie: {verified} geverifieerde S&P 500 UCITS-handelslijnen.",
            "Belangrijkste productstap: kies de gewenste broker- en valutalijn, versterk de prijsbasis en maak daarna pas de kapitaalbeslissing.",
            "Grootste analytische tekortkoming voor productiepromotie: macrodata moet worden ververst.",
        ]
    else:
        bullets = [
            "Portfolio stance: retain EUR 100,000 cash until a separate allocation decision is made.",
            f"Best-supported implementation: {verified} verified S&P 500 UCITS trading lines.",
            "Main product step: select the preferred broker and currency line, strengthen pricing evidence, and only then make the capital decision.",
            "Largest analytical gap before production promotion: macro data must be refreshed.",
        ]
    content = _section_header(7, COPY[language]["section_7"])
    content += "<ul>" + "".join(f"<li>{_e(item)}</li>" for item in bullets) + "</ul>"
    return _panel(content)


def _allocation_section(state: dict[str, Any], language: str) -> str:
    if language == "nl":
        headers = ["Segment", "Positionering", "Toelichting"]
    else:
        headers = ["Segment", "Positioning", "Explanation"]
    rows = [
        [
            _e(item["segment_nl"] if language == "nl" else item["segment_en"]),
            _e(item["stance_nl"] if language == "nl" else item["stance_en"]),
            _e(item["note_nl"] if language == "nl" else item["note_en"]),
        ]
        for item in state["allocation_map"]
    ]
    return _panel(_section_header(8, COPY[language]["section_8"]) + _rows_table(headers, rows))


def _second_order_section(state: dict[str, Any], language: str) -> str:
    if language == "nl":
        headers = ["Drijver", "Eerste-orde-effect", "Tweede-orde-effect", "ETF EU-implicatie"]
    else:
        headers = ["Driver", "First-order effect", "Second-order effect", "ETF EU implication"]
    rows = [
        [
            _e(item["driver_nl"] if language == "nl" else item["driver_en"]),
            _e(item["first_nl"] if language == "nl" else item["first_en"]),
            _e(item["second_nl"] if language == "nl" else item["second_en"]),
            _e(item["implication_nl"] if language == "nl" else item["implication_en"]),
        ]
        for item in state["second_order_effects"]
    ]
    return _panel(_section_header(9, COPY[language]["section_9"]) + _rows_table(headers, rows, css_class="wide-table"))


def _pricing_section(state: dict[str, Any], language: str) -> str:
    if language == "nl":
        headers = ["Handelslijn", "Fonds", "ISIN", "Beurs", "Peildatum", "Slot", "Valuta", "Status", "Onderzoeksreferentie"]
    else:
        headers = ["Trading line", "Fund", "ISIN", "Exchange", "Pricing date", "Close", "Currency", "Status", "Research reference"]
    rows = []
    for row in state["pricing"]["rows"]:
        status_key = row["verification_status"] if row["priced"] else "fetch_failed"
        status = STATUS_LABELS[language].get(status_key, status_key)
        proxy = row.get("research_reference") or "—"
        if proxy != "—":
            proxy += " · " + ("alleen onderzoek" if language == "nl" else "research only")
        rows.append(
            [
                _e(row["ticker"]),
                _e(row["fund_name"]),
                _e(row["isin"]),
                _e(row["exchange"]),
                _e(row["close_date"] or "n/a"),
                _number(row["close_price"], language=language) if row["close_price"] is not None else "n/a",
                _e(row["currency"]),
                _e(status),
                _e(proxy),
            ]
        )
    content = _section_header(10, COPY[language]["section_10"])
    content += '<div class="note-box">' + _e(
        "De prijzen zijn marktobservaties en geen zelfstandige basis voor waardering of aankoop."
        if language == "nl" else
        "Prices are market observations and not an independent basis for valuation or purchase."
    ) + "</div>"
    content += _rows_table(headers, rows, css_class="wide-table pricing-table")
    return _panel(content, extra="panel-wide")


def _funnel_section(state: dict[str, Any], language: str) -> str:
    f = state["verification_funnel"]
    if language == "nl":
        cards = [
            ("Geobserveerde lijnen", f["observed_lines"]),
            ("Geprijsd", f["priced_lines"]),
            ("Geverifieerd", f["verified_lines"]),
            ("Onopgelost", f["unresolved_lines"]),
            ("Gefinancierd", f["funded_positions"]),
        ]
        note = "Verificatie is een trechter: prijsbeschikbaarheid is niet hetzelfde als investeerbaarheid, en investeerbaarheid is niet hetzelfde als een allocatiebesluit."
    else:
        cards = [
            ("Observed lines", f["observed_lines"]),
            ("Priced", f["priced_lines"]),
            ("Verified", f["verified_lines"]),
            ("Unresolved", f["unresolved_lines"]),
            ("Funded", f["funded_positions"]),
        ]
        note = "Verification is a funnel: price availability is not investability, and investability is not an allocation decision."
    content = _section_header(11, COPY[language]["section_11"])
    content += '<div class="funnel-strip">' + "".join(f'<div class="funnel-card"><div class="funnel-value">{_e(value)}</div><div class="funnel-label">{_e(label)}</div></div>' for label, value in cards) + "</div>"
    content += f'<div class="note-box">{_e(note)}</div>'
    return _panel(content)


def _positions_section(state: dict[str, Any], language: str) -> str:
    p = state["portfolio"]
    content = _section_header(12, COPY[language]["section_12"])
    if p["position_count"] == 0:
        text = (
            "Niet actief: de EU-modelportefeuille bevat nog geen gefinancierde posities. Deze sectie wordt automatisch een positie-, rendement- en bijdrageanalyse zodra een gevalideerde positie bestaat."
            if language == "nl" else
            "Not active: the EU model portfolio has no funded positions. This section automatically becomes a position, return and contribution review once a validated position exists."
        )
        content += f'<div class="inactive-callout">{_e(text)}</div>'
    else:
        if language == "nl":
            headers = ["ISIN", "Handelslijn", "Aantal", "Marktwaarde EUR", "Gewicht", "Rol", "Volgende toets"]
        else:
            headers = ["ISIN", "Trading line", "Shares", "Market value EUR", "Weight", "Role", "Next review"]
        rows = []
        for position in p["positions"]:
            rows.append([
                _e(position.get("isin")),
                _e(position.get("ticker")),
                _number(position.get("shares"), language=language),
                _money(position.get("market_value_eur"), language=language),
                _pct(position.get("weight_pct"), language=language),
                _e(position.get("role")),
                _e(position.get("required_next_action")),
            ])
        content += _rows_table(headers, rows)
    return _panel(content)


def _rotation_section(state: dict[str, Any], language: str) -> str:
    p = state["portfolio"]
    content = _section_header(13, COPY[language]["section_13"])
    if p["position_count"] == 0:
        text = (
            "Vervangings- en rotatieanalyse is niet actief zonder gefinancierde posities. De relevante vermijdingsradar blijft wel actief."
            if language == "nl" else
            "Replacement and rotation analysis is not active without funded positions. The relevant avoidance radar remains active."
        )
        content += f'<div class="inactive-callout">{_e(text)}</div>'
    avoidance = [
        (
            "Inverse of leveraged producten" if language == "nl" else "Inverse or leveraged products",
            "Buiten het huidige productbeleid." if language == "nl" else "Outside the current product policy.",
        ),
        (
            "Ongeverifieerde handelslijnen" if language == "nl" else "Unverified trading lines",
            "Geen inzet van kapitaal vóór identiteit, KID, broker en lijn zijn bevestigd." if language == "nl" else "No allocation before identity, KID, broker and trading line are confirmed.",
        ),
        (
            "Goud-ETC’s" if language == "nl" else "Gold ETCs",
            "Geblokkeerd totdat het UCITS-only beleid expliciet wordt aangepast." if language == "nl" else "Blocked until the UCITS-only policy is explicitly changed.",
        ),
        (
            "Smalle technologieconcentratie" if language == "nl" else "Narrow technology concentration",
            "Alleen als satellietblootstelling beoordelen en vergelijken met brede kernblootstelling." if language == "nl" else "Assess only as satellite exposure and compare with broad core exposure.",
        ),
    ]
    headers = ["Vermijden / bewaken", "Reden"] if language == "nl" else ["Avoid / monitor", "Reason"]
    content += _rows_table(headers, [[_e(a), _e(b)] for a, b in avoidance])
    return _panel(content)


def _next_run_section(state: dict[str, Any], language: str) -> str:
    n = state["next_run_input"]
    if language == "nl":
        bullets = [
            f"Portefeuillestaat: {n['portfolio_state']}",
            f"Waarderingshistorie: {n['valuation_history']}",
            f"Prijsartifact: {n['pricing_artifact']}",
            "Macro-pack verversen vóór productiepromotie." if n["macro_refresh_required"] else "Macro-pack is voldoende actueel.",
            "Prioriteitskandidaten: " + ", ".join(n["priority_candidates"]),
        ]
        actions_title = "Vereiste acties voor de volgende run"
    else:
        bullets = [
            f"Portfolio state: {n['portfolio_state']}",
            f"Valuation history: {n['valuation_history']}",
            f"Pricing artifact: {n['pricing_artifact']}",
            "Refresh the macro pack before production promotion." if n["macro_refresh_required"] else "Macro pack is sufficiently current.",
            "Priority candidates: " + ", ".join(n["priority_candidates"]),
        ]
        actions_title = "Required actions for the next run"
    content = _section_header(14, COPY[language]["section_14"])
    content += "<ul>" + "".join(f"<li>{_e(item)}</li>" for item in bullets) + "</ul>"
    content += f'<h3>{_e(actions_title)}</h3><ol>' + "".join(f"<li>{_e(item)}</li>" for item in n["required_actions"]) + "</ol>"
    return _panel(content)


def _disclaimer(language: str) -> str:
    if language == "nl":
        text = (
            "Dit rapport wordt uitsluitend verstrekt voor informatieve en educatieve doeleinden. Het is geen beleggingsadvies, juridisch advies, fiscaal advies of financieel advies en vormt geen aanbeveling om effecten te kopen, te verkopen of aan te houden. Het rapport houdt geen rekening met individuele beleggingsdoelen, financiële situatie of specifieke behoeften. Beleggen brengt risico’s met zich mee, waaronder verlies van inleg. Amerikaanse ETF-symbolen zijn uitsluitend onderzoeksreferenties; de EU-productautoriteit blijft ISIN-first en UCITS-first."
        )
    else:
        text = (
            "This report is provided for informational and educational purposes only. It is not investment, legal, tax or financial advice and is not a recommendation to buy, sell or hold securities. It does not consider individual objectives, financial circumstances or needs. Investing involves risk, including loss of principal. U.S. ETF symbols are research references only; EU product authority remains ISIN-first and UCITS-first."
        )
    return _panel(_section_header(15, COPY[language]["section_15"]) + f"<p>{_e(text)}</p>")


def _css() -> str:
    return """
@page {
  size: A4 portrait;
  margin: 13mm 12mm 15mm 12mm;
  @bottom-left { content: "Weekly ETF EU · client-grade preview"; color: #74818a; font-size: 7.5pt; }
  @bottom-right { content: "Pagina " counter(page) " van " counter(pages); color: #74818a; font-size: 7.5pt; }
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { background: #F6F2EC; color: #2B3742; font-family: Arial, Helvetica, sans-serif; font-size: 9.2pt; line-height: 1.42; }
.report-shell { width: 100%; }
.hero { background: #607887; color: #FBFAF7; padding: 17px 20px 15px; border-radius: 12px 12px 0 0; }
.hero-secondary { margin-top: 8mm; break-before: page; page-break-before: always; }
.hero-row { display: table; width: 100%; }
.hero-row > div { display: table-cell; vertical-align: middle; }
.hero-row > div:last-child { text-align: right; }
.masthead { font-family: Georgia, 'Times New Roman', serif; font-weight: 700; font-size: 23pt; letter-spacing: .045em; }
.hero-date { color: #EFF4F6; font-size: 9pt; margin-top: 3px; }
.hero-type { font-size: 12pt; font-weight: 700; }
.hero-rule { height: 4px; background: #D4B483; margin: 5px 0 12px; border-radius: 999px; }
.notice { background: #F8F4EE; border: 1px solid #D9D3CB; color: #6B7882; border-radius: 10px; padding: 8px 11px; font-size: 8pt; margin-bottom: 12px; }
.summary-strip { display: table; width: 100%; table-layout: fixed; border-spacing: 8px 0; margin: 0 -8px 12px; }
.mini-card { display: table-cell; width: 33.33%; background: #FCFAF7; border: 1px solid #D9D3CB; border-radius: 12px; padding: 11px 12px; vertical-align: top; }
.mini-label { font-size: 7.5pt; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: #6B7882; margin-bottom: 6px; }
.mini-value { font-family: Georgia, 'Times New Roman', serif; font-size: 15pt; font-weight: 700; line-height: 1.18; }
.mini-value-small { font-size: 11.5pt; }
.panel { background: #FCFAF7; border: 1px solid #D9D3CB; border-radius: 12px; padding: 12px 14px; margin: 0 0 11px; break-inside: auto; }
.panel-cockpit, .panel-wide { break-inside: auto; }
.section-kicker { display: table; width: 100%; border-bottom: 1px solid #DDD7CE; padding-bottom: 7px; margin-bottom: 9px; break-after: avoid; }
.section-badge { display: table-cell; width: 31px; height: 31px; border-radius: 50%; background: #2A5384; color: #fff; font-size: 11pt; font-weight: 700; text-align: center; vertical-align: middle; }
.section-title { display: table-cell; vertical-align: middle; padding-left: 10px; color: #6B7882; font-size: 10pt; font-weight: 700; letter-spacing: .07em; text-transform: uppercase; }
h3 { color: #405562; font-size: 10pt; margin: 10px 0 5px; break-after: avoid; }
p { margin: 0 0 7px; }
ul, ol { margin: 0 0 8px 18px; padding: 0; }
li { margin-bottom: 4px; }
.cockpit-list li { margin-bottom: 6px; }
.takeaway { margin-top: 10px; padding: 10px 12px; background: #F4EEE4; border: 1px solid #E7D7BB; border-radius: 9px; }
.takeaway-label { color: #6B7882; text-transform: uppercase; font-size: 7.5pt; font-weight: 700; letter-spacing: .06em; margin-bottom: 4px; }
.takeaway-text { font-family: Georgia, 'Times New Roman', serif; font-size: 11pt; font-weight: 700; }
.note-box, .inactive-callout { background: #F8F4EE; border: 1px solid #DDD5C9; border-radius: 8px; padding: 8px 10px; margin: 7px 0 9px; color: #53616B; }
.inactive-callout { border-left: 4px solid #8DA0AD; }
.freshness-banner { border-radius: 8px; padding: 8px 10px; margin-bottom: 9px; font-weight: 700; }
.freshness-banner.warning { background: #FFF4DF; border: 1px solid #E6C98C; color: #6C5423; }
.freshness-banner.ok { background: #EAF4EC; border: 1px solid #AFC7B4; color: #31563A; }
table { width: 100%; border-collapse: collapse; table-layout: auto; margin: 5px 0 8px; font-size: 7.6pt; }
thead { display: table-header-group; }
tr { break-inside: avoid; page-break-inside: avoid; }
th, td { border: .5pt solid #D8D5CE; padding: 5px 6px; vertical-align: top; overflow-wrap: anywhere; }
th { background: #F1EBDD; color: #2B3742; font-weight: 700; text-align: left; }
tbody tr:nth-child(even) td { background: #FEFCF9; }
.summary-table { max-width: 70%; }
.wide-table { font-size: 6.8pt; }
.radar-table th:nth-child(1) { width: 13%; }
.radar-table th:nth-child(2) { width: 11%; }
.radar-table th:nth-child(4) { width: 18%; }
.radar-table th:nth-child(8) { width: 18%; }
.pricing-table { font-size: 6.4pt; }
.pricing-table th:nth-child(2) { width: 20%; }
.cash-callout { display: table; width: 100%; background: #F4EEE4; border: 1px solid #E7D7BB; border-radius: 11px; padding: 14px; margin: 8px 0 10px; }
.cash-value, .cash-text { display: table-cell; vertical-align: middle; }
.cash-value { width: 34%; font-family: Georgia, 'Times New Roman', serif; font-size: 22pt; font-weight: 700; color: #2A5384; }
.cash-text { font-size: 10pt; font-weight: 700; padding-left: 12px; }
.funnel-strip { display: table; width: 100%; table-layout: fixed; border-spacing: 6px 0; margin: 0 -6px 10px; }
.funnel-card { display: table-cell; background: #F8F4EE; border: 1px solid #DDD5C9; border-radius: 9px; padding: 10px; text-align: center; }
.funnel-value { font-family: Georgia, 'Times New Roman', serif; font-size: 18pt; font-weight: 700; color: #2A5384; }
.funnel-label { font-size: 7.5pt; text-transform: uppercase; color: #6B7882; font-weight: 700; }
.equity-curve-block { width: 100%; margin: 5px 0 8px; }
.equity-curve-svg { display: block; width: 100%; height: auto; }
@media print {
  .panel { box-shadow: none; }
}
"""


def build_html(state: dict[str, Any], *, language: str) -> str:
    if language not in {"nl", "en"}:
        raise ValueError("language must be nl or en")
    sections = [
        _hero(state, language=language, report_type="investor"),
        _decision_cockpit(state, language),
        _portfolio_section(state, language),
        _macro_section(state, language),
        _opportunity_section(state, language),
        _risk_section(state, language),
        _portfolio_development(state, language),
        _conclusion(state, language),
        _hero(state, language=language, report_type="analyst"),
        _allocation_section(state, language),
        _second_order_section(state, language),
        _pricing_section(state, language),
        _funnel_section(state, language),
        _positions_section(state, language),
        _rotation_section(state, language),
        _next_run_section(state, language),
        _disclaimer(language),
    ]
    title = "Weekly ETF EU Review – Nederlands" if language == "nl" else "Weekly ETF EU Review – English"
    return f"""<!doctype html>
<html lang="{language}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_e(title)}</title>
<style>{_css()}</style>
</head>
<body>
<main class="report-shell">
{''.join(sections)}
</main>
</body>
</html>
"""


def render_report(*, state_path: Path, language: str, html_output: Path, pdf_output: Path) -> None:
    state = _load_state(state_path)
    rendered = build_html(state, language=language)
    html_output.parent.mkdir(parents=True, exist_ok=True)
    pdf_output.parent.mkdir(parents=True, exist_ok=True)
    html_output.write_text(rendered, encoding="utf-8")
    HTML(string=rendered, base_url=str(state_path.parent.resolve())).write_pdf(str(pdf_output))
    if not pdf_output.exists() or pdf_output.stat().st_size <= 0:
        raise RuntimeError(f"PDF output was not created: {pdf_output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the Weekly ETF EU client-grade v2 preview report.")
    parser.add_argument("--state", required=True)
    parser.add_argument("--language", choices=["nl", "en"], required=True)
    parser.add_argument("--html-output", required=True)
    parser.add_argument("--pdf-output", required=True)
    args = parser.parse_args()
    render_report(
        state_path=Path(args.state),
        language=args.language,
        html_output=Path(args.html_output),
        pdf_output=Path(args.pdf_output),
    )
    print(f"ETF_EU_CLIENT_GRADE_RENDER_OK | language={args.language} | pdf={args.pdf_output}")


if __name__ == "__main__":
    main()
