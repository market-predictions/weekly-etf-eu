from __future__ import annotations

import argparse
import base64
import csv
import html
import json
from pathlib import Path
from typing import Any, Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from weasyprint import HTML


SECTION_TITLES = {
    "nl": {
        "brand": "WEKELIJKSE ETF EU-REVIEW",
        "report_type": "Gesynchroniseerd schaduwrapport",
        "sections": {
            "1": "Kernsamenvatting",
            "2": "Portefeuille-acties",
            "2A": "Besliscockpit",
            "3": "Regime-dashboard",
            "4": "Structurele kansenradar",
            "4A": "Vermijdings- en shortkansenradar",
            "5": "Belangrijkste risico’s / invalidaties",
            "6": "Conclusie",
            "7": "Portefeuillecurve en portefeuilleontwikkeling",
            "7A": "Rendement huidige ETF-posities",
            "8": "Allocatiekaart",
            "9": "Tweede-orde-effectenkaart",
            "10": "Review huidige posities",
            "11": "Beste nieuwe kansen en vervangingsanalyse",
            "12": "Rotatieplan portefeuille",
            "13": "Definitieve actietabel",
            "14": "Voorgestelde positiewijzigingen / rotatie-intenties",
            "15": "Huidige posities en cash",
            "16": "Input voor de volgende run",
        },
    },
    "en": {
        "brand": "WEEKLY ETF EU REVIEW",
        "report_type": "Synchronized shadow report",
        "sections": {
            "1": "Executive summary",
            "2": "Portfolio actions",
            "2A": "Decision cockpit",
            "3": "Regime dashboard",
            "4": "Structural opportunity radar",
            "4A": "Avoidance and short-opportunity radar",
            "5": "Key risks / invalidations",
            "6": "Bottom line",
            "7": "Portfolio curve and development",
            "7A": "Current ETF position performance",
            "8": "Allocation map",
            "9": "Second-order effects map",
            "10": "Current-position review",
            "11": "Best new opportunities and replacement analysis",
            "12": "Portfolio rotation plan",
            "13": "Final action table",
            "14": "Proposed position changes / rotation intents",
            "15": "Current positions and cash",
            "16": "Input for the next run",
        },
    },
}


def e(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def num(value: Any, language: str, decimals: int = 2) -> str:
    try:
        raw = f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return "n/a"
    if language == "nl":
        return raw.replace(",", "X").replace(".", ",").replace("X", ".")
    return raw


def money(value: Any, language: str) -> str:
    return "€ " + num(value, language)


def pct(value: Any, language: str, decimals: int = 2, signed: bool = False) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "n/a"
    prefix = "+" if signed and number > 0 else ""
    return prefix + num(number, language, decimals) + "%"


def table(headers: Iterable[str], rows: Iterable[Iterable[Any]], css_class: str = "data-table") -> str:
    head = "".join(f"<th>{e(item)}</th>" for item in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{value if isinstance(value, SafeHtml) else e(value)}</td>" for value in row) + "</tr>"
        for row in rows
    )
    return f'<table class="{css_class}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


class SafeHtml(str):
    pass


def badge(value: str, css_class: str = "status-neutral") -> SafeHtml:
    return SafeHtml(f'<span class="status {e(css_class)}">{e(value)}</span>')


def section(number: str, title: str, body: str, css_class: str = "") -> str:
    return (
        f'<section id="section-{e(number)}" class="panel {e(css_class)}">'
        f'<div class="section-head"><span class="section-badge">{e(number)}</span>'
        f'<h2>{e(title)}</h2></div>{body}</section>'
    )


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def load_history(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            try:
                rows.append(
                    {
                        "date": str(row.get("date") or ""),
                        "nav_eur": float(row.get("nav_eur") or 0),
                        "cash_eur": float(row.get("cash_eur") or 0),
                        "invested_market_value_eur": float(row.get("invested_market_value_eur") or 0),
                        "since_inception_return_pct": float(row.get("since_inception_return_pct") or 0),
                        "drawdown_pct": float(row.get("drawdown_pct") or 0),
                        "comment": str(row.get("comment") or ""),
                    }
                )
            except (TypeError, ValueError):
                continue
    return [row for row in rows if row["date"]]


def chart_png(history: list[dict[str, Any]], output: Path, language: str) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    dates = [row["date"] for row in history]
    values = [row["nav_eur"] for row in history]
    fig, ax = plt.subplots(figsize=(10.5, 4.2))
    ax.plot(dates, values, marker="o", linewidth=2.5)
    ax.set_title("Portefeuillecurve (EUR)" if language == "nl" else "Portfolio curve (EUR)")
    ax.set_ylabel("Portefeuillewaarde" if language == "nl" else "Portfolio value")
    ax.set_xlabel("Datum" if language == "nl" else "Date")
    ax.grid(True, alpha=0.25)
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(output, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return output


def data_uri(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def candidate_label(row: dict[str, Any]) -> str:
    candidate = row.get("preferred_ucits_candidate") if isinstance(row.get("preferred_ucits_candidate"), dict) else None
    if not candidate:
        return "—"
    lines = candidate.get("trading_lines") if isinstance(candidate.get("trading_lines"), list) else []
    tickers = [str(line.get("exchange_ticker") or "") for line in lines if isinstance(line, dict) and line.get("exchange_ticker")]
    ticker = "/".join(tickers) or "line pending"
    return f"{ticker} · {candidate.get('fund_name') or ''}".strip()


def status_label(row: dict[str, Any], language: str) -> SafeHtml:
    status = str(row.get("implementation_status") or "")
    labels = {
        "funded_current_position": ("Gefinancierd", "Funded", "status-good"),
        "mapped_pending_pricing_and_allocation": ("Gekoppeld, nog niet financierbaar", "Mapped, not yet fundable", "status-warn"),
        "trading_line_unverified": ("Handelslijn niet geverifieerd", "Trading line unverified", "status-warn"),
        "identity_unverified": ("Identiteit niet geverifieerd", "Identity unverified", "status-bad"),
        "unmapped": ("Geen UCITS-koppeling", "No UCITS mapping", "status-bad"),
        "policy_blocked": ("Beleidsmatig geblokkeerd", "Policy blocked", "status-bad"),
        "kid_missing": ("KID ontbreekt", "KID missing", "status-bad"),
    }
    nl, en, css = labels.get(status, (status or "Onbekend", status or "Unknown", "status-neutral"))
    return badge(nl if language == "nl" else en, css)


def action_label(value: Any, language: str) -> str:
    mapping = {
        "hold_and_reunderwrite": ("Aanhouden en opnieuw beoordelen", "Hold and re-underwrite"),
        "review_existing_position_opportunity_cost": ("Bestaande positie herbeoordelen", "Review incumbent opportunity cost"),
        "prepare_separate_pricing_and_allocation_review": ("Prijs- en allocatiereview voorbereiden", "Prepare pricing and allocation review"),
        "reserve_capacity_and_resolve_implementation": ("Capaciteit reserveren; implementatie oplossen", "Reserve capacity; resolve implementation"),
        "watch_only": ("Volgen", "Watch"),
    }
    pair = mapping.get(str(value), (str(value), str(value)))
    return pair[0] if language == "nl" else pair[1]


def hero(sync: dict[str, Any], language: str) -> str:
    labels = SECTION_TITLES[language]
    strategy = sync["shared_strategy"]
    portfolio = sync["eu_portfolio"]
    promoted = sync["promoted_exposure_comparison"]
    represented = sum(1 for row in promoted if float(row.get("current_eu_weight_pct") or 0) > 0)
    regime = ((strategy.get("regime") or {}).get("current") or "Unknown")
    summary = (
        f"Donorstrategie: {len(promoted)} kansrijke exposures; {represented} momenteel vertegenwoordigd in de EU-portefeuille."
        if language == "nl" else
        f"Donor strategy: {len(promoted)} promoted exposures; {represented} currently represented in the EU portfolio."
    )
    return f"""
<header class="hero">
  <div><div class="masthead">{e(labels['brand'])}</div><div class="hero-date">{e(strategy.get('report_date'))}</div></div>
  <div class="hero-type">{e(labels['report_type'])}</div>
</header>
<div class="hero-rule"></div>
<div class="notice">{e('Schaduwoutput: geen portefeuillewijziging of allocatiebevoegdheid.' if language == 'nl' else 'Shadow output: no portfolio mutation or allocation authority.')}</div>
<div class="summary-strip">
  <div class="mini-card"><span>{e('Primair regime' if language == 'nl' else 'Primary regime')}</span><strong>{e(regime)}</strong></div>
  <div class="mini-card"><span>{e('EU-portefeuille' if language == 'nl' else 'EU portfolio')}</span><strong>{money(portfolio.get('nav_eur'), language)}</strong></div>
  <div class="mini-card wide"><span>{e('Kernconclusie' if language == 'nl' else 'Main conclusion')}</span><strong>{e(summary)}</strong></div>
</div>
"""


def render_sections(sync: dict[str, Any], portfolio: dict[str, Any], history: list[dict[str, Any]], chart_uri: str, language: str) -> str:
    titles = SECTION_TITLES[language]["sections"]
    strategy = sync["shared_strategy"]
    regime = strategy.get("regime") if isinstance(strategy.get("regime"), dict) else {}
    promoted = sync.get("promoted_exposure_comparison") or []
    all_rows = sync.get("exposure_rows") or []
    legacy = sync.get("legacy_current_positions") or []
    positions = portfolio.get("positions") if isinstance(portfolio.get("positions"), list) else []

    top = promoted[0] if promoted else None
    summary_items = [
        ("Primair regime" if language == "nl" else "Primary regime", regime.get("current") or "Unknown"),
        ("Sterkste gedeelde exposure" if language == "nl" else "Top shared exposure", top.get("lane_name") if top else "n/a"),
        ("Huidige EU-positie" if language == "nl" else "Current EU posture", "Transitie en verificatie" if language == "nl" else "Transition and verification"),
        ("Belangrijkste conclusie" if language == "nl" else "Main conclusion", "De strategie is gedeeld; instrumenten en gewichten moeten via de UCITS-laag worden verklaard." if language == "nl" else "Strategy is shared; instruments and weights must be explained through the UCITS layer."),
    ]
    body1 = "<ul>" + "".join(f"<li><strong>{e(k)}:</strong> {e(v)}</li>" for k, v in summary_items) + "</ul>"

    action_rows = []
    for row in promoted:
        action_rows.append([
            row.get("lane_name"),
            action_label(row.get("action_candidate"), language),
            candidate_label(row),
            pct(row.get("current_eu_weight_pct"), language),
            ", ".join(row.get("divergence_reason_codes") or []) or "—",
        ])
    body2 = table(
        ["Exposure", "Actie", "UCITS-implementatie", "Huidig gewicht", "Afwijkingsreden"] if language == "nl" else ["Exposure", "Action", "UCITS implementation", "Current weight", "Divergence reason"],
        action_rows,
        "wide-table",
    )

    blocked_count = sum(1 for row in promoted if row.get("divergence_from_promoted_exposure"))
    cockpit = [
        f"{len(promoted)} " + ("donor-exposures zijn gepromoveerd." if language == "nl" else "donor exposures are promoted."),
        f"{blocked_count} " + ("daarvan ontbreken momenteel in de EU-portefeuille." if language == "nl" else "are currently absent from the EU portfolio."),
        ("Geen rotatie wordt uitgevoerd vanuit dit schaduwrapport." if language == "nl" else "No rotation is executed from this shadow report."),
        ("Volgende actie: productmapping, pricing en portefeuilleweging afzonderlijk valideren." if language == "nl" else "Next action: validate product mapping, pricing and portfolio weights separately."),
    ]
    body2a = "<div class=" + '"cockpit-grid">' + "".join(f'<div class="cockpit-card">{e(item)}</div>' for item in cockpit) + "</div>"

    body3 = table(
        ["Onderdeel", "Lezing", "Implicatie"] if language == "nl" else ["Component", "Reading", "Implication"],
        [
            ["Regime", regime.get("current"), "Gedeeld met Weekly ETF" if language == "nl" else "Shared with Weekly ETF"],
            ["Vertrouwen" if language == "nl" else "Confidence", pct(regime.get("confidence_pct"), language, 0), regime.get("decision_rule") or "—"],
            ["Wat veranderde" if language == "nl" else "What changed", "; ".join(regime.get("what_changed") or []) or "—", "Geen zelfstandige EU-regimeberekening" if language == "nl" else "No separate EU regime calculation"],
        ],
    )

    radar_rows = []
    for row in promoted:
        radar_rows.append([
            row.get("shared_rank"), row.get("lane_name"), candidate_label(row), num(row.get("shared_score"), language),
            status_label(row, language), action_label(row.get("action_candidate"), language),
            ", ".join(row.get("divergence_reason_codes") or []) or "—",
        ])
    body4 = table(
        ["Rang", "Thema", "UCITS-kandidaat", "Donorscore", "Implementatiestatus", "Benodigde actie", "Blokkade"] if language == "nl" else ["Rank", "Theme", "UCITS candidate", "Donor score", "Implementation status", "Required action", "Blocker"],
        radar_rows,
        "wide-table",
    )

    avoid_rows = []
    for row in all_rows:
        if row.get("promoted") is True:
            continue
        reasons = row.get("divergence_reason_codes") or []
        if reasons or row.get("shared_desired_direction") == "avoid_or_underweight":
            avoid_rows.append([row.get("lane_name"), row.get("shared_desired_direction"), ", ".join(reasons) or "lower donor rank", row.get("research_required") or "—"])
        if len(avoid_rows) >= 8:
            break
    body4a = table(
        ["Exposure", "Donorhouding", "Reden", "Wat moet veranderen"] if language == "nl" else ["Exposure", "Donor posture", "Reason", "What must change"],
        avoid_rows or [["—", "—", "—", "—"]],
    )

    risk_rows = [
        ["Strategische divergentie" if language == "nl" else "Strategic divergence", f"{blocked_count} promoted exposures are not represented"],
        ["Productmapping" if language == "nl" else "Product mapping", "Ongeverifieerde ISIN-/handelslijnen blijven geblokkeerd" if language == "nl" else "Unverified ISIN/trading lines remain blocked"],
        ["Legacy-portefeuille" if language == "nl" else "Legacy portfolio", f"{len(legacy)} current positions require re-underwriting"],
        ["Cash" if language == "nl" else "Cash", "Cash mag niet automatisch worden ingezet zonder allocator en uitvoeringstoets" if language == "nl" else "Cash may not be deployed without allocator and execution review"],
    ]
    body5 = table(["Risico", "Invalidatie / oplossing"] if language == "nl" else ["Risk", "Invalidation / resolution"], risk_rows)

    body6 = "<ul>" + "".join(
        f"<li>{e(item)}</li>" for item in (
            [
                "Weekly ETF is nu de gedeelde strategiebron voor deze schaduwrun.",
                "De EU-portefeuille is nog niet strategisch gesynchroniseerd; zij bevat voornamelijk bestaande kern- en stabilisatorposities.",
                "De volgende beslislaag moet doelgewichten en een gecontroleerd transitiepad bepalen.",
            ] if language == "nl" else [
                "Weekly ETF is now the shared strategy source for this shadow run.",
                "The EU portfolio is not yet strategically synchronized; it mainly contains incumbent core and stabilizer positions.",
                "The next decision layer must determine target weights and a controlled transition path.",
            ]
        )
    ) + "</ul>"

    history_rows = [[row["date"], money(row["nav_eur"], language), money(row["cash_eur"], language), money(row["invested_market_value_eur"], language), row["comment"]] for row in history]
    body7 = f'<img class="equity-chart" data-image-mode="embedded-data-uri" src="{chart_uri}" alt="Portfolio curve">' + table(
        ["Datum", "Portefeuillewaarde", "Cash", "Belegd", "Toelichting"] if language == "nl" else ["Date", "Portfolio value", "Cash", "Invested", "Comment"], history_rows)

    perf_rows = []
    for position in positions:
        perf_rows.append([
            position.get("portfolio_role"), position.get("fund_name"), position.get("ticker") or position.get("exchange_ticker"),
            pct(position.get("current_weight_pct"), language), "n/a", "n/a", "n/a",
            pct(position.get("unrealized_pnl_pct"), language, signed=True), money(position.get("unrealized_pnl_eur"), language),
            pct(position.get("portfolio_contribution_pct_nav"), language, signed=True),
        ])
    body7a = table(
        ["Portefeuillesegment", "Beleggingsthese", "ETF", "Gewicht %", "1w rendement", "1m rendement", "3m rendement", "Sinds instap", "P/L EUR", "Bijdrage %"] if language == "nl" else ["Portfolio segment", "Investment thesis", "ETF", "Weight %", "1w return", "1m return", "3m return", "Since entry", "P/L EUR", "Contribution %"],
        perf_rows,
        "wide-table",
    )

    allocation_rows = [
        ["Wereldwijde aandelen" if language == "nl" else "Global equity", "Overgang" if language == "nl" else "Transition", "VWCE is incumbent; shared-strategy fit must be re-underwritten."],
        ["Amerikaanse aandelen" if language == "nl" else "U.S. equity", "Overgang" if language == "nl" else "Transition", "SXR8 is incumbent and must be tested against promoted thematic exposures."],
        ["Obligaties" if language == "nl" else "Bonds", "Stabilisator onder review" if language == "nl" else "Stabilizer under review", "EUNA remains separate from donor opportunity ranking."],
        ["Thematische satellieten" if language == "nl" else "Thematic satellites", "Onderwogen / geblokkeerd" if language == "nl" else "Underweight / blocked", f"{blocked_count} promoted exposures are not yet implemented."],
        ["Cash", "Overwogen" if language == "nl" else "Overweight", money(sync['eu_portfolio'].get('cash_eur'), language)],
    ]
    body8 = table(["Segment", "Positionering", "Toelichting"] if language == "nl" else ["Segment", "Positioning", "Explanation"], allocation_rows)

    effect_rows = []
    for row in promoted[:5]:
        effect_rows.append([
            row.get("lane_name"), row.get("shared_why_now") or row.get("shared_evidence_summary") or "—",
            "UCITS product and portfolio-fit constraints determine implementation." if language == "en" else "UCITS-product- en portefeuillefit bepalen de implementatie.",
            candidate_label(row), action_label(row.get("action_candidate"), language),
            "Direct" if language == "nl" else "Immediate", "Hoog" if row.get("shared_rank", 99) <= 3 and language == "nl" else ("High" if row.get("shared_rank", 99) <= 3 else ("Gemiddeld" if language == "nl" else "Medium")),
        ])
    body9 = table(
        ["Drijver", "Eerste-orde-effect", "Tweede-orde-effect", "Waarschijnlijke winnaars", "ETF EU-implicatie", "Timing", "Vertrouwen"] if language == "nl" else ["Driver", "First-order effect", "Second-order effect", "Likely winners", "ETF EU implication", "Timing", "Confidence"],
        effect_rows,
        "wide-table",
    )

    review_rows = []
    for position in positions:
        review_rows.append([
            position.get("ticker") or position.get("exchange_ticker"), position.get("last_action") or "Hold",
            position.get("conviction_tier"), "Opnieuw beoordelen" if language == "nl" else "Re-underwrite",
            position.get("portfolio_role"), "Vergelijk met gedeelde top-exposures" if language == "nl" else "Compare with shared top exposures",
        ])
    body10 = table(
        ["Ticker", "Actie", "Score/tier", "Nieuw-kapitaaltoets", "Rol", "Volgende toets"] if language == "nl" else ["Ticker", "Action", "Score/tier", "Fresh-cash test", "Role", "Next test"],
        review_rows,
    )

    replacement_rows = [[row.get("lane_name"), candidate_label(row), status_label(row, language), ", ".join(row.get("divergence_reason_codes") or []) or "—", action_label(row.get("action_candidate"), language)] for row in promoted]
    body11 = table(
        ["Gedeelde kans", "UCITS-alternatief", "Status", "Prijs-/productbasis", "Beslisimplicatie"] if language == "nl" else ["Shared opportunity", "UCITS alternative", "Status", "Pricing/product basis", "Decision implication"],
        replacement_rows,
        "wide-table",
    )

    body12 = table(
        ["Sluiten", "Verlagen", "Aanhouden", "Toevoegen / bestemming", "Vervangen", "Status"] if language == "nl" else ["Close", "Reduce", "Hold", "Add / destination", "Replace", "Status"],
        [["Geen autorisatie" if language == "nl" else "Not authorized", "—", ", ".join(str(p.get("ticker") or p.get("exchange_ticker")) for p in positions), "Promoted exposures pending implementation", "—", "Shadow only"]],
    )

    final_rows = []
    for position in positions:
        final_rows.append([
            position.get("ticker") or position.get("exchange_ticker"), position.get("fund_name"), pct(position.get("current_weight_pct"), language),
            "Pending shared allocator", "n/a", "Review incumbent", "—", "—", "Existing position transition", "No",
        ])
    for row in promoted:
        final_rows.append([
            row.get("exposure_id"), candidate_label(row), pct(row.get("current_eu_weight_pct"), language), "Pending shared allocator", "n/a",
            action_label(row.get("action_candidate"), language), "Cash / rotation review", num(row.get("shared_score"), language),
            ", ".join(row.get("divergence_reason_codes") or []) or "Mapped", "Shadow",
        ])
    body13 = table(
        ["Ticker/exposure", "ETF", "Huidig gewicht", "Doelgewicht", "Delta gewicht", "Actie", "Kapitaalbestemming", "Score", "Toelichting", "Override-status"] if language == "nl" else ["Ticker/exposure", "ETF", "Current weight", "Target weight", "Weight delta", "Action", "Capital destination", "Score", "Explanation", "Override status"],
        final_rows,
        "wide-table",
    )

    intent_rows = [[row.get("exposure_id"), candidate_label(row), "n/a", "n/a", "n/a", "shadow_candidate", action_label(row.get("action_candidate"), language)] for row in promoted if row.get("divergence_from_promoted_exposure")]
    body14 = table(
        ["Bron", "Bestemming", "Delta bron %", "Delta bestemming %", "Geschatte waarde EUR", "Intentiestatus", "Toelichting"] if language == "nl" else ["Source", "Destination", "Source delta %", "Destination delta %", "Estimated value EUR", "Intent status", "Explanation"],
        intent_rows or [["—", "—", "—", "—", "—", "No intent", "No authorized changes"]],
    )

    holding_rows = [[
        position.get("ticker") or position.get("exchange_ticker"), position.get("shares"), num(position.get("current_price_local"), language), position.get("trading_currency"),
        num(position.get("market_value_local"), language), money(position.get("market_value_eur"), language), pct(position.get("current_weight_pct"), language), position.get("isin"),
    ] for position in positions]
    holding_rows.append(["CASH", "—", "1.00", "EUR", num(portfolio.get("cash_eur"), language), money(portfolio.get("cash_eur"), language), pct(float(portfolio.get("cash_eur") or 0) / float(portfolio.get("nav_eur") or 1) * 100, language), "—"])
    body15 = table(
        ["Ticker", "Aantal aandelen", "Prijs lokaal", "Valuta", "Marktwaarde lokaal", "Marktwaarde EUR", "Gewicht %", "ISIN"] if language == "nl" else ["Ticker", "Shares", "Local price", "Currency", "Local market value", "Market value EUR", "Weight %", "ISIN"],
        holding_rows,
        "wide-table",
    )

    priorities = [row.get("exposure_id") for row in promoted if row.get("divergence_from_promoted_exposure")]
    body16 = (
        "<div class=\"continuity-box\"><strong>" + e("Canonieke input" if language == "nl" else "Canonical input") + "</strong>"
        + "<ul>"
        + f"<li>shared_strategy_run_id: {e(strategy.get('source_run_id'))}</li>"
        + f"<li>shared_strategy_report_date: {e(strategy.get('report_date'))}</li>"
        + f"<li>eu_portfolio_state: output/etf_eu_portfolio_state.json</li>"
        + f"<li>priority_implementation_gaps: {e(', '.join(priorities) or 'none')}</li>"
        + f"<li>portfolio_mutation_authorized: false</li>"
        + "</ul></div>"
    )

    return "".join([
        section("1", titles["1"], body1),
        section("2", titles["2"], body2, "panel-wide"),
        section("2A", titles["2A"], body2a),
        section("3", titles["3"], body3),
        section("4", titles["4"], body4, "panel-wide"),
        section("4A", titles["4A"], body4a),
        section("5", titles["5"], body5),
        section("6", titles["6"], body6),
        section("7", titles["7"], body7, "panel-wide"),
        section("7A", titles["7A"], body7a, "panel-wide"),
        '<div class="analyst-divider"></div>',
        section("8", titles["8"], body8),
        section("9", titles["9"], body9, "panel-wide"),
        section("10", titles["10"], body10),
        section("11", titles["11"], body11, "panel-wide"),
        section("12", titles["12"], body12),
        section("13", titles["13"], body13, "panel-wide"),
        section("14", titles["14"], body14, "panel-wide"),
        section("15", titles["15"], body15, "panel-wide"),
        section("16", titles["16"], body16),
    ])


def css() -> str:
    return """
@page { size: A4 portrait; margin: 12mm 11mm 14mm; @bottom-left { content: "Weekly ETF EU · synchronized shadow"; color: #70808a; font-size: 7pt; } @bottom-right { content: "Page " counter(page) " of " counter(pages); color: #70808a; font-size: 7pt; } }
* { box-sizing: border-box; }
body { margin: 0; background: #ece8e1; color: #263641; font-family: Arial, Helvetica, sans-serif; font-size: 9pt; line-height: 1.42; }
.report { max-width: 1120px; margin: 0 auto; background: #fbfaf7; padding: 18px; }
.hero { background: #617a89; color: #fff; padding: 22px 25px; border-radius: 8px 8px 0 0; display: flex; justify-content: space-between; align-items: center; }
.masthead { font-family: Georgia, serif; font-size: 22px; font-weight: 700; letter-spacing: .4px; }
.hero-date { margin-top: 4px; opacity: .88; }
.hero-type { font-family: Georgia, serif; font-weight: 700; }
.hero-rule { height: 4px; background: #d7a45c; margin-bottom: 10px; }
.notice { background: #f6f1e9; border: 1px solid #ddd3c6; padding: 8px 12px; border-radius: 5px; color: #58656d; }
.summary-strip { display: grid; grid-template-columns: 1fr 1fr 2fr; gap: 9px; margin: 10px 0 14px; }
.mini-card { background: white; border: 1px solid #ddd7ce; padding: 11px; border-radius: 6px; }
.mini-card span { display: block; font-size: 7.5pt; text-transform: uppercase; color: #71808a; font-weight: 700; }
.mini-card strong { display: block; margin-top: 5px; font-family: Georgia, serif; font-size: 11pt; }
.panel { background: white; border: 1px solid #ddd8cf; border-radius: 7px; margin: 0 0 12px; padding: 12px 14px 14px; break-inside: avoid; }
.panel-wide { break-inside: auto; }
.section-head { display: flex; align-items: center; gap: 8px; margin-bottom: 9px; }
.section-head h2 { margin: 0; font-family: Georgia, serif; font-size: 13px; letter-spacing: .15px; }
.section-badge { display: inline-flex; width: 23px; height: 23px; border-radius: 50%; align-items: center; justify-content: center; background: #2d5d86; color: white; font-weight: 700; font-size: 8px; }
ul { margin: 7px 0 4px 18px; padding: 0; }
li { margin: 3px 0; }
table { width: 100%; border-collapse: collapse; margin-top: 7px; font-size: 7.8pt; }
th { background: #eee7d9; color: #344550; text-align: left; padding: 6px 6px; border: 1px solid #d7d0c4; font-weight: 700; }
td { padding: 5px 6px; border: 1px solid #dedad2; vertical-align: top; }
tbody tr:nth-child(even) { background: #faf8f4; }
.wide-table { font-size: 7.2pt; }
.status { display: inline-block; border-radius: 12px; padding: 2px 7px; font-size: 6.8pt; font-weight: 700; white-space: nowrap; }
.status-good { background: #e3f2e8; color: #24623a; }
.status-warn { background: #fff0cf; color: #805a0c; }
.status-bad { background: #f6dfdf; color: #842e2e; }
.status-neutral { background: #e8edf0; color: #40535e; }
.cockpit-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.cockpit-card { border-left: 4px solid #2d5d86; background: #f5f7f8; padding: 9px 11px; border-radius: 4px; }
.equity-chart { width: 100%; max-height: 330px; object-fit: contain; display: block; margin: 6px 0 10px; border: 1px solid #d6dce0; border-radius: 7px; background: white; }
.analyst-divider { break-before: page; page-break-before: always; height: 0; }
.continuity-box { background: #eef3f6; border: 1px solid #ccd9e0; padding: 11px; border-radius: 6px; }
@media (max-width: 760px) { .report { padding: 8px; } .summary-strip { grid-template-columns: 1fr; } .cockpit-grid { grid-template-columns: 1fr; } table { font-size: 7pt; } }
"""


def render(sync: dict[str, Any], portfolio: dict[str, Any], history: list[dict[str, Any]], chart_uri: str, language: str) -> str:
    return (
        "<!doctype html><html><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<title>{e(SECTION_TITLES[language]['brand'])}</title><style>{css()}</style></head><body><main class=\"report\">"
        + hero(sync, language)
        + render_sections(sync, portfolio, history, chart_uri, language)
        + "</main></body></html>"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Render synchronized Weekly ETF EU shadow sister report")
    parser.add_argument("--sync-shadow", type=Path, required=True)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--valuation-history", type=Path, default=Path("output/etf_eu_valuation_history.csv"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    sync = load_json(args.sync_shadow)
    portfolio = load_json(args.portfolio_state)
    history = load_history(args.valuation_history)
    if len(history) < 2:
        raise RuntimeError("At least two valuation-history points are required for the sister-report chart")

    report_date = str(sync.get("shared_strategy", {}).get("report_date") or "unknown")
    token = report_date.replace("-", "")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "artifact_type": "etf_eu_sister_report_shadow_manifest",
        "report_date": report_date,
        "source_sync_shadow": str(args.sync_shadow),
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "languages": {},
    }

    for language in ("nl", "en"):
        chart_path = args.output_dir / f"weekly_etf_eu_sister_shadow_{language}_{token}_equity.png"
        chart_png(history, chart_path, language)
        html_path = args.output_dir / f"weekly_etf_eu_sister_shadow_{language}_{token}.html"
        pdf_path = args.output_dir / f"weekly_etf_eu_sister_shadow_{language}_{token}.pdf"
        html_text = render(sync, portfolio, history, data_uri(chart_path), language)
        html_path.write_text(html_text, encoding="utf-8")
        HTML(string=html_text, base_url=str(args.output_dir.resolve())).write_pdf(pdf_path)
        manifest["languages"][language] = {
            "html": str(html_path),
            "pdf": str(pdf_path),
            "equity_png": str(chart_path),
            "html_image_mode": "embedded_data_uri_png",
        }

    manifest_path = args.output_dir / f"etf_eu_sister_report_shadow_manifest_{token}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
