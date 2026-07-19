from __future__ import annotations

import html
import math
from dataclasses import dataclass
from datetime import datetime
from typing import Any

FRONT_PAGE_MARKER = 'data-etf-eu-cockpit-front-page="preview"'
STYLE_ID = "etf-eu-cockpit-front-page-style"


@dataclass(frozen=True)
class CockpitSnapshot:
    language: str
    report_date: str
    regime: str
    confidence_pct: int
    action_title: str
    action_note: str
    summary: str
    nav_eur: float
    since_inception_pct: float
    max_drawdown_pct: float
    cash_eur: float
    cash_pct: float
    position_count: int
    largest_ticker: str
    largest_weight_pct: float
    verified_funded_count: int
    funded_count: int
    pricing_date: str
    discipline: str
    next_trigger: str


@dataclass(frozen=True)
class CockpitFragment:
    css: str
    html: str
    language: str


def _e(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def _f(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
        return number if math.isfinite(number) else default
    except (TypeError, ValueError):
        return default


def _money(value: float, language: str, decimals: int = 0) -> str:
    text = f"{value:,.{decimals}f}"
    if language == "nl":
        text = text.replace(",", "X").replace(".", ",").replace("X", ".")
    return "€" + text


def _pct(value: float, language: str, *, signed: bool = False) -> str:
    sign = "+" if signed and value > 0 else ""
    text = f"{sign}{value:.1f}%"
    return text.replace(".", ",") if language == "nl" else text


def _date(value: str, language: str) -> str:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return value
    if language == "nl":
        months = "januari februari maart april mei juni juli augustus september oktober november december".split()
        return f"{parsed.day} {months[parsed.month - 1]} {parsed.year}"
    return parsed.strftime("%d %b %Y")


def _positions(state: dict[str, Any]) -> list[dict[str, Any]]:
    portfolio = state.get("portfolio") or {}
    return [dict(row) for row in portfolio.get("positions") or [] if isinstance(row, dict)]


def _ticker(row: dict[str, Any]) -> str:
    return str(row.get("exchange_ticker") or row.get("ticker") or "-").strip().upper()


def _equity_points(state: dict[str, Any]) -> list[tuple[str, float]]:
    points: list[tuple[str, float]] = []
    for row in (state.get("equity_curve") or {}).get("points") or []:
        if not isinstance(row, dict):
            continue
        date = str(row.get("date") or "").strip()
        nav = _f(row.get("nav_eur"))
        if date and nav > 0:
            points.append((date, nav))
    return sorted(points)


def _max_drawdown(points: list[tuple[str, float]]) -> float:
    peak = 0.0
    worst = 0.0
    for _, value in points:
        peak = max(peak, value)
        if peak > 0:
            worst = min(worst, (value / peak - 1.0) * 100.0)
    return worst


def _sparkline(points: list[tuple[str, float]]) -> str:
    if len(points) < 2:
        return ""
    width, height = 620, 118
    left, right, top, bottom = 18, 18, 10, 18
    values = [value for _, value in points]
    low, high = min(values), max(values)
    span = max(high - low, 1.0)
    plot_width = width - left - right
    plot_height = height - top - bottom
    coords = [
        (
            left + index / max(len(points) - 1, 1) * plot_width,
            top + (1.0 - (value - low) / span) * plot_height,
        )
        for index, (_, value) in enumerate(points)
    ]
    polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    return (
        f'<svg class="etf-eu-cockpit-spark" viewBox="0 0 {width} {height}" role="img" '
        'aria-label="Portfolio development">'
        f'<polyline points="{polyline}" fill="none" stroke="#0F4438" stroke-width="3" '
        'stroke-linejoin="round" stroke-linecap="round"/>'
        f'<circle cx="{coords[-1][0]:.1f}" cy="{coords[-1][1]:.1f}" r="4" fill="#0F4438"/>'
        "</svg>"
    )


def build_snapshot(state: dict[str, Any], language: str) -> CockpitSnapshot:
    if language not in {"nl", "en"}:
        raise ValueError("language must be nl or en")
    if state.get("state_valid") is not True:
        raise RuntimeError("cockpit requires a valid normalized report state")

    portfolio = state.get("portfolio") or {}
    positions = _positions(state)
    nav = _f(portfolio.get("nav_eur"))
    cash = _f(portfolio.get("cash_eur"))
    starting = _f(portfolio.get("starting_capital_eur"), 100000.0)
    since = (nav / starting - 1.0) * 100.0 if starting else 0.0
    cash_pct = cash / nav * 100.0 if nav else 0.0
    points = _equity_points(state)
    drawdown = _max_drawdown(points)
    largest = max(positions, key=lambda row: _f(row.get("current_weight_pct")), default={})
    largest_ticker = _ticker(largest) if largest else "-"
    largest_weight = _f(largest.get("current_weight_pct")) if largest else 0.0
    verified = sum(
        1
        for row in positions
        if row.get("isin") and str(row.get("verification_status") or "") == "verified_ucits_trading_line"
    )
    pricing_date = str((state.get("pricing") or {}).get("as_of") or state.get("report_date") or "")
    macro = state.get("macro") or {}
    regime = str(macro.get("regime_nl") if language == "nl" else macro.get("regime") or "-")
    confidence = int(round(_f(macro.get("confidence_pct"))))

    added = [row for row in positions if _f(row.get("shares_delta_this_run")) > 0]
    held = [row for row in positions if _f(row.get("shares_delta_this_run")) == 0]
    if language == "nl":
        if added:
            added_text = " en ".join(f"{int(_f(row.get('shares'))):,}".replace(",", ".") + f" {_ticker(row)}" for row in added)
            held_text = ", ".join(_ticker(row) for row in held)
            action_title = "Eerste tranches toegevoegd"
            action_note = f"{added_text} toegevoegd" + (f"; {held_text} aangehouden." if held_text else ".")
        else:
            action_title = "Geen portefeuillewijziging"
            action_note = "VWCE, EUNA en SXR8 blijven actief; een tweede SXR8-tranche is niet geautoriseerd."
        summary = (
            f"De EU-modelportefeuille telt {len(positions)} gefinancierde UCITS-posities en staat sinds de start op "
            f"{_pct(since, 'nl', signed=True)}. {_money(cash, 'nl')} blijft cash; dat is beschikbare capaciteit, "
            "geen automatische allocatiebevoegdheid."
        )
        discipline = (
            "Resterende cash wordt niet automatisch ingezet. Meet de overlap tussen VWCE en SXR8, behandel EUNA als "
            "stabilisator en niet als gegarandeerde bescherming, en vereis voor iedere volgende tranche een afzonderlijk besluit."
        )
        trigger = (
            "Volgende-actietrigger: verse slotprijzen voor de exacte handelslijnen, bevestigde rol en bijdrage, "
            "concentratie- en overlapcontrole en een afzonderlijk allocatiebesluit."
        )
    else:
        if added:
            added_text = " and ".join(f"{int(_f(row.get('shares'))):,} {_ticker(row)}" for row in added)
            held_text = ", ".join(_ticker(row) for row in held)
            action_title = "First tranches added"
            action_note = f"Added {added_text}" + (f"; maintained {held_text}." if held_text else ".")
        else:
            action_title = "No portfolio change"
            action_note = "VWCE, EUNA and SXR8 remain active; a second SXR8 tranche is not authorised."
        summary = (
            f"The EU model portfolio holds {len(positions)} funded UCITS positions and is {_pct(since, 'en', signed=True)} "
            f"since inception. {_money(cash, 'en')} remains in cash; this is available capacity, not automatic allocation authority."
        )
        discipline = (
            "Remaining cash is not deployed automatically. Measure VWCE/SXR8 overlap, treat EUNA as a stabiliser rather than "
            "guaranteed protection, and require a separate decision for every later tranche."
        )
        trigger = (
            "Next-action trigger: fresh closes for the exact trading lines, confirmed role and contribution, concentration and "
            "overlap review, and a separate allocation decision."
        )

    return CockpitSnapshot(
        language=language,
        report_date=str(state.get("report_date") or ""),
        regime=regime,
        confidence_pct=max(0, min(confidence, 100)),
        action_title=action_title,
        action_note=action_note,
        summary=summary,
        nav_eur=nav,
        since_inception_pct=since,
        max_drawdown_pct=drawdown,
        cash_eur=cash,
        cash_pct=cash_pct,
        position_count=len(positions),
        largest_ticker=largest_ticker,
        largest_weight_pct=largest_weight,
        verified_funded_count=verified,
        funded_count=len(positions),
        pricing_date=pricing_date,
        discipline=discipline,
        next_trigger=trigger,
    )


def browser_css() -> str:
    return f"""<style id="{STYLE_ID}">
.etf-eu-cockpit-page{{background:#F6F1E7;color:#211C16;border:1px solid #D8CDB8;max-width:780px;margin:0 auto 24px;font-family:Arial,Helvetica,sans-serif;box-sizing:border-box;break-after:page;page-break-after:always}}
.etf-eu-cockpit-page *{{box-sizing:border-box}}
.etf-eu-cockpit-inner{{padding:34px 40px 26px}}
.etf-eu-cockpit-header{{display:flex;justify-content:space-between;gap:20px;border-bottom:2px solid #211C16;padding-bottom:13px}}
.etf-eu-cockpit-kicker,.etf-eu-cockpit-meta,.etf-eu-cockpit-label,.etf-eu-cockpit-section-title,.etf-eu-cockpit-footer{{font-family:'Courier New',monospace}}
.etf-eu-cockpit-kicker{{font-size:10px;letter-spacing:.17em;text-transform:uppercase;color:#B07D2B}}
.etf-eu-cockpit-title{{font-family:Georgia,'Times New Roman',serif;font-size:36px;font-weight:700;line-height:1.02;margin-top:7px}}
.etf-eu-cockpit-title em{{font-weight:400;font-style:italic;color:#0F4438}}
.etf-eu-cockpit-meta{{text-align:right;font-size:10px;line-height:1.65;color:#5A5043}}
.etf-eu-cockpit-strap{{margin-top:10px;font:700 10px 'Courier New',monospace;letter-spacing:.12em;text-transform:uppercase;color:#5A5043}}
.etf-eu-cockpit-section-title{{margin:24px 0 10px;color:#0F4438;font-size:10px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;border-bottom:1px solid #D8CDB8;padding-bottom:7px}}
.etf-eu-cockpit-lede{{font:20px/1.45 Georgia,'Times New Roman',serif;margin:0}}
.etf-eu-cockpit-row{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:20px}}
.etf-eu-cockpit-card{{border:1px solid #D8CDB8;background:#EFE8D9;padding:15px 17px}}
.etf-eu-cockpit-label{{font-size:9px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#5A5043;margin-bottom:8px}}
.etf-eu-cockpit-value{{font:700 19px/1.2 Georgia,'Times New Roman',serif}}
.etf-eu-cockpit-note{{font-size:12px;line-height:1.45;color:#5A5043;margin-top:7px}}
.etf-eu-cockpit-bar{{height:6px;background:#E2D9C6;margin-top:10px;overflow:hidden}}
.etf-eu-cockpit-bar i{{display:block;height:100%;background:#0F4438}}
.etf-eu-cockpit-performance{{border:1px solid #D8CDB8;background:#fff}}
.etf-eu-cockpit-chart{{padding:14px 16px 4px}}
.etf-eu-cockpit-chart-caption{{display:flex;justify-content:space-between;gap:14px;font-size:11px;color:#5A5043}}
.etf-eu-cockpit-spark{{width:100%;height:92px;display:block}}
.etf-eu-cockpit-metrics{{display:grid;grid-template-columns:repeat(3,1fr)}}
.etf-eu-cockpit-metric{{padding:12px 14px;border-top:1px solid #D8CDB8;border-right:1px solid #D8CDB8}}
.etf-eu-cockpit-metric:nth-child(3n){{border-right:none}}
.etf-eu-cockpit-metric-value{{font:700 21px Georgia,'Times New Roman',serif;margin-top:6px}}
.etf-eu-cockpit-metric-sub{{font:9px/1.35 'Courier New',monospace;color:#5A5043;margin-top:4px}}
.etf-eu-cockpit-discipline{{border-left:4px solid #B07D2B;background:#F0E5D0;padding:13px 15px;font-size:12px;line-height:1.48}}
.etf-eu-cockpit-trigger{{margin-top:8px;border:1px solid #D8CDB8;background:#fff;padding:11px 13px;color:#5A5043;font-size:11px;line-height:1.45}}
.etf-eu-cockpit-evidence{{display:grid;grid-template-columns:repeat(3,1fr);gap:7px 10px;border:1px solid #D8CDB8;background:#fff;padding:12px 14px}}
.etf-eu-cockpit-evidence div{{border-top:1px solid #D8CDB8;padding-top:6px;font:9px/1.35 'Courier New',monospace}}
.etf-eu-cockpit-footer{{display:flex;justify-content:space-between;margin-top:16px;padding-top:10px;border-top:1px solid #D8CDB8;color:#5A5043;font-size:9px}}
@media print{{.etf-eu-cockpit-page{{border:none;margin:0;max-width:none;break-inside:avoid;page-break-inside:avoid}}.etf-eu-cockpit-inner{{padding:12px 20px 10px}}.etf-eu-cockpit-title{{font-size:27px}}.etf-eu-cockpit-lede{{font-size:13px;line-height:1.28}}.etf-eu-cockpit-section-title{{margin:8px 0 4px;font-size:7.5px;padding-bottom:3px}}.etf-eu-cockpit-row{{gap:7px;margin-top:7px}}.etf-eu-cockpit-card{{padding:7px 9px}}.etf-eu-cockpit-value{{font-size:13px}}.etf-eu-cockpit-note{{font-size:8px;margin-top:3px}}.etf-eu-cockpit-spark{{height:54px}}.etf-eu-cockpit-chart{{padding:6px 8px 1px}}.etf-eu-cockpit-metric{{padding:5px 7px}}.etf-eu-cockpit-metric-value{{font-size:14px;margin-top:2px}}.etf-eu-cockpit-label,.etf-eu-cockpit-metric-sub{{font-size:6.8px}}.etf-eu-cockpit-discipline{{padding:6px 8px;font-size:8px;line-height:1.25}}.etf-eu-cockpit-trigger{{margin-top:3px;padding:5px 7px;font-size:7.5px}}.etf-eu-cockpit-evidence{{padding:5px 7px;gap:3px 7px}}.etf-eu-cockpit-evidence div{{padding-top:2px;font-size:6.5px}}.etf-eu-cockpit-footer{{margin-top:4px;padding-top:3px;font-size:6.5px}}}}
</style>"""


def render_browser_fragment(state: dict[str, Any], language: str) -> CockpitFragment:
    snap = build_snapshot(state, language)
    is_nl = language == "nl"
    labels = {
        "kicker": "Beleggersrapport · EU/UCITS-strategie" if is_nl else "Investor report · EU/UCITS strategy",
        "title": "De ETF EU-Review" if is_nl else "The ETF EU Review",
        "model": "Modelportefeuille · EUR" if is_nl else "Model portfolio · EUR",
        "issue": "Rapportvoorpagina" if is_nl else "Report front page",
        "strap": "Wekelijks · ISIN-first · geen beleggingsadvies" if is_nl else "Weekly · ISIN-first · not investment advice",
        "brief": "In het kort" if is_nl else "In brief",
        "climate": "Marktklimaat" if is_nl else "Market climate",
        "action": "Actie deze week" if is_nl else "This week's action",
        "performance": "Prestatie, risico en verificatie" if is_nl else "Performance, risk and verification",
        "nav": "Portefeuillewaarde" if is_nl else "Portfolio value",
        "return": "Rendement sinds start" if is_nl else "Return since inception",
        "drawdown": "Grootste terugval" if is_nl else "Max drawdown",
        "cash": "Cash",
        "positions": "Posities" if is_nl else "Positions",
        "largest": "Grootste positie" if is_nl else "Largest position",
        "verified": "Gefinancierde ISIN's" if is_nl else "Funded ISINs",
        "discipline": "Disciplinepunt" if is_nl else "Discipline point",
        "sources": "Bronnen en controle" if is_nl else "Sources and controls",
        "footer": "Beleggersrapport en analistenrapport volgen hierna." if is_nl else "Investor report and analyst report follow below.",
    }
    evidence = [
        "Portefeuillestatus gereconcilieerd" if is_nl else "Portfolio state reconciled",
        "Waarderingshistorie gereconcilieerd" if is_nl else "Valuation history reconciled",
        f"{snap.verified_funded_count}/{snap.funded_count} gefinancierde ISIN's geverifieerd" if is_nl else f"{snap.verified_funded_count}/{snap.funded_count} funded ISINs verified",
        "Prijsbewijs gekoppeld" if is_nl else "Pricing evidence linked",
        "Macrobeeld gekoppeld" if is_nl else "Macro context linked",
        "Runregistratie gekoppeld" if is_nl else "Run record linked",
    ]
    metrics = [
        (labels["return"], _pct(snap.since_inception_pct, language, signed=True), f"{_money(100000, language)} → {_money(snap.nav_eur, language)}"),
        (labels["drawdown"], _pct(snap.max_drawdown_pct, language), "sinds start" if is_nl else "since inception"),
        (labels["cash"], _pct(snap.cash_pct, language), _money(snap.cash_eur, language)),
        (labels["positions"], str(snap.position_count), "actieve posities" if is_nl else "active positions"),
        (labels["largest"], snap.largest_ticker, _pct(snap.largest_weight_pct, language)),
        (labels["verified"], f"{snap.verified_funded_count}/{snap.funded_count}", f"peildatum {_date(snap.pricing_date, language)}" if is_nl else f"as of {_date(snap.pricing_date, language)}"),
    ]
    metric_html = "".join(
        '<div class="etf-eu-cockpit-metric"><div class="etf-eu-cockpit-label">'
        + _e(label)
        + '</div><div class="etf-eu-cockpit-metric-value">'
        + _e(value)
        + '</div><div class="etf-eu-cockpit-metric-sub">'
        + _e(sub)
        + "</div></div>"
        for label, value, sub in metrics
    )
    html_text = f'''<section class="etf-eu-cockpit-page" {FRONT_PAGE_MARKER} data-language="{language}" data-render-mode="browser">
<div class="etf-eu-cockpit-inner">
<header class="etf-eu-cockpit-header"><div><div class="etf-eu-cockpit-kicker">{_e(labels['kicker'])}</div><div class="etf-eu-cockpit-title">{_e(labels['title']).replace('ETF', '<em>ETF</em>', 1)}</div></div><div class="etf-eu-cockpit-meta">{_e(labels['model'])}<br>{_e(_date(snap.report_date, language))}<br><strong>{_e(labels['issue'])}</strong></div></header>
<div class="etf-eu-cockpit-strap">{_e(labels['strap'])}</div>
<div class="etf-eu-cockpit-section-title">{_e(labels['brief'])}</div><p class="etf-eu-cockpit-lede">{_e(snap.summary)}</p>
<div class="etf-eu-cockpit-row"><div class="etf-eu-cockpit-card"><div class="etf-eu-cockpit-label">{_e(labels['climate'])}</div><div class="etf-eu-cockpit-value">{_e(snap.regime)}</div><div class="etf-eu-cockpit-bar"><i style="width:{snap.confidence_pct}%"></i></div><div class="etf-eu-cockpit-note">{snap.confidence_pct}% {'vertrouwen' if is_nl else 'confidence'}</div></div><div class="etf-eu-cockpit-card"><div class="etf-eu-cockpit-label">{_e(labels['action'])}</div><div class="etf-eu-cockpit-value">{_e(snap.action_title)}</div><div class="etf-eu-cockpit-note">{_e(snap.action_note)}</div></div></div>
<div class="etf-eu-cockpit-section-title">{_e(labels['performance'])}</div><div class="etf-eu-cockpit-performance"><div class="etf-eu-cockpit-chart"><div class="etf-eu-cockpit-chart-caption"><span>{_e(labels['nav'])} · EUR</span><span>{_e(_money(snap.nav_eur, language))} · <strong>{_e(_pct(snap.since_inception_pct, language, signed=True))}</strong></span></div>{_sparkline(_equity_points(state))}</div><div class="etf-eu-cockpit-metrics">{metric_html}</div></div>
<div class="etf-eu-cockpit-section-title">{_e(labels['discipline'])}</div><div class="etf-eu-cockpit-discipline">{_e(snap.discipline)}</div><div class="etf-eu-cockpit-trigger">{_e(snap.next_trigger)}</div>
<div class="etf-eu-cockpit-section-title">{_e(labels['sources'])}</div><div class="etf-eu-cockpit-evidence">{''.join('<div>'+_e(item)+'</div>' for item in evidence)}</div>
<div class="etf-eu-cockpit-footer"><span>{_e(labels['footer'])}</span><span>01</span></div>
</div></section>'''
    return CockpitFragment(css=browser_css(), html=html_text, language=language)
