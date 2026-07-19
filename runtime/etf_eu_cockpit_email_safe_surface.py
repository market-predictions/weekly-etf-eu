from __future__ import annotations

from html import escape
from typing import Any

from runtime.render_etf_eu_cockpit_front_page import FRONT_PAGE_MARKER, build_snapshot


def _style(**items: str) -> str:
    return ";".join(f"{key.replace('_', '-')}:{value}" for key, value in items.items() if value)


def _attr(value: str) -> str:
    return escape(value, quote=True)


def _money(value: float, language: str) -> str:
    text = f"{value:,.0f}"
    return "€" + (text.replace(",", ".") if language == "nl" else text)


def _pct(value: float, language: str, signed: bool = False) -> str:
    sign = "+" if signed and value > 0 else ""
    text = f"{sign}{value:.1f}%"
    return text.replace(".", ",") if language == "nl" else text


def _metric(label: str, value: str, sub: str) -> str:
    return (
        '<td style="width:33.33%;vertical-align:top;padding:11px 12px;border:1px solid #D8CDB8;background:#FFFFFF">'
        '<div style="font-family:Courier New,monospace;font-size:9px;font-weight:700;letter-spacing:1px;'
        f'text-transform:uppercase;color:#5A5043">{escape(label)}</div>'
        '<div style="font-family:Georgia,Times New Roman,serif;font-size:21px;font-weight:700;line-height:1.1;'
        f'color:#211C16;padding-top:6px">{escape(value)}</div>'
        '<div style="font-family:Courier New,monospace;font-size:9px;line-height:1.35;color:#5A5043;'
        f'padding-top:4px">{escape(sub)}</div></td>'
    )


def _sparkline_text(state: dict[str, Any]) -> str:
    values = [float(row.get("nav_eur")) for row in (state.get("equity_curve") or {}).get("points") or [] if row.get("nav_eur")]
    if not values:
        return "—"
    low, high = min(values), max(values)
    bars = "▁▂▃▄▅▆▇█"
    if high <= low:
        return bars[3] * len(values)
    return "".join(bars[min(7, max(0, round((value - low) / (high - low) * 7)))] for value in values)


def render_email_safe_front_page(state: dict[str, Any], language: str) -> str:
    snap = build_snapshot(state, language)
    is_nl = language == "nl"
    title = "De ETF EU-Review" if is_nl else "The ETF EU Review"
    kicker = "Beleggersrapport · EU/UCITS-strategie" if is_nl else "Investor report · EU/UCITS strategy"
    model = "Modelportefeuille · EUR" if is_nl else "Model portfolio · EUR"
    climate = "Marktklimaat" if is_nl else "Market climate"
    action = "Actie deze week" if is_nl else "This week's action"
    discipline = "Disciplinepunt" if is_nl else "Discipline point"
    verified_label = "Gefinancierde ISIN's" if is_nl else "Funded ISINs"
    outer = _style(max_width="780px", margin="0 auto 28px auto", background_color="#F6F1E7", color="#211C16", border="1px solid #D8CDB8", font_family="Arial,Helvetica,sans-serif")
    inner = _style(padding="28px 34px 26px 34px")
    section = _style(font_family="Courier New,monospace", font_size="10px", font_weight="700", letter_spacing="2px", text_transform="uppercase", color="#0F4438", border_bottom="1px solid #D8CDB8", padding_bottom="6px", margin_top="20px", margin_bottom="9px")
    evidence = [
        "Portefeuillestatus gereconcilieerd" if is_nl else "Portfolio state reconciled",
        "Waarderingshistorie gereconcilieerd" if is_nl else "Valuation history reconciled",
        f"{snap.verified_funded_count}/{snap.funded_count} gefinancierde ISIN's geverifieerd" if is_nl else f"{snap.verified_funded_count}/{snap.funded_count} funded ISINs verified",
        "Prijsbewijs gekoppeld" if is_nl else "Pricing evidence linked",
        "Macrobeeld gekoppeld" if is_nl else "Macro context linked",
        "Runregistratie gekoppeld" if is_nl else "Run record linked",
    ]
    evidence_cells = "".join(
        '<td style="width:50%;vertical-align:top;border-top:1px solid #D8CDB8;padding:7px 8px 6px 0;'
        f'font-family:Courier New,monospace;font-size:9px;line-height:1.35;color:#211C16">{escape(item)}</td>'
        for item in evidence
    )
    evidence_rows = "".join(
        "<tr>" + evidence_cells[index : index + 2 * 1] + "</tr>" for index in []
    )
    # Build rows explicitly because each cell is an HTML fragment rather than a scalar.
    cells = [
        '<td style="width:50%;vertical-align:top;border-top:1px solid #D8CDB8;padding:7px 8px 6px 0;'
        f'font-family:Courier New,monospace;font-size:9px;line-height:1.35;color:#211C16">{escape(item)}</td>'
        for item in evidence
    ]
    evidence_rows = "".join("<tr>" + cells[i] + cells[i + 1] + "</tr>" for i in range(0, len(cells), 2))
    metrics = [
        _metric("Rendement sinds start" if is_nl else "Return since inception", _pct(snap.since_inception_pct, language, True), f"€100.000 → {_money(snap.nav_eur, language)}" if is_nl else f"€100,000 → {_money(snap.nav_eur, language)}"),
        _metric("Grootste terugval" if is_nl else "Max drawdown", _pct(snap.max_drawdown_pct, language), "sinds start" if is_nl else "since inception"),
        _metric("Cash", _pct(snap.cash_pct, language), _money(snap.cash_eur, language)),
        _metric("Posities" if is_nl else "Positions", str(snap.position_count), "actieve posities" if is_nl else "active positions"),
        _metric("Grootste positie" if is_nl else "Largest position", snap.largest_ticker, _pct(snap.largest_weight_pct, language)),
        _metric(verified_label, f"{snap.verified_funded_count}/{snap.funded_count}", "ISIN-first"),
    ]
    return f'''<section class="etf-eu-cockpit-page" {FRONT_PAGE_MARKER} data-language="{language}" data-render-mode="email" style="{_attr(outer)}">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="width:100%;border-collapse:collapse"><tr><td style="{_attr(inner)}">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0"><tr><td style="vertical-align:top"><div style="font-family:Courier New,monospace;font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#B07D2B;padding-bottom:7px">{escape(kicker)}</div><div style="font-family:Georgia,Times New Roman,serif;font-size:36px;font-weight:700;line-height:1.05">{escape(title)}</div></td><td style="vertical-align:top;text-align:right;font-family:Courier New,monospace;font-size:10px;line-height:1.65;color:#5A5043;padding-left:18px">{escape(model)}<br>{escape(snap.report_date)}<br><strong>{'Rapportvoorpagina' if is_nl else 'Report front page'}</strong></td></tr></table>
<div style="border-top:2px solid #211C16;padding-top:9px;margin-top:9px;font-family:Courier New,monospace;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#5A5043">{'Wekelijks · ISIN-first · geen beleggingsadvies' if is_nl else 'Weekly · ISIN-first · not investment advice'}</div>
<div style="{_attr(section)}">{'In het kort' if is_nl else 'In brief'}</div><p style="font-family:Georgia,Times New Roman,serif;font-size:18px;line-height:1.48;color:#211C16;margin:0">{escape(snap.summary)}</p>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="width:100%;border-collapse:separate;border-spacing:10px 0;margin-top:18px"><tr><td style="width:50%;vertical-align:top;border:1px solid #D8CDB8;background:#EFE8D9;padding:14px 16px"><div style="font-family:Courier New,monospace;font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#5A5043">{escape(climate)}</div><div style="font-family:Georgia,Times New Roman,serif;font-size:18px;font-weight:700;padding-top:7px">{escape(snap.regime)}</div><div style="font-size:11px;color:#5A5043;padding-top:7px">{snap.confidence_pct}% {'vertrouwen' if is_nl else 'confidence'}</div></td><td style="width:50%;vertical-align:top;border:1px solid #D8CDB8;background:#EFE8D9;padding:14px 16px"><div style="font-family:Courier New,monospace;font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#5A5043">{escape(action)}</div><div style="font-family:Georgia,Times New Roman,serif;font-size:18px;font-weight:700;padding-top:7px">{escape(snap.action_title)}</div><div style="font-size:11px;line-height:1.45;color:#5A5043;padding-top:7px">{escape(snap.action_note)}</div></td></tr></table>
<div style="{_attr(section)}">{'Prestatie, risico en verificatie' if is_nl else 'Performance, risk and verification'}</div><div style="border:1px solid #D8CDB8;background:#FFFFFF;padding:13px 14px"><div style="font-family:Courier New,monospace;font-size:9px;color:#5A5043">{'PORTEFEUILLEWAARDE' if is_nl else 'PORTFOLIO VALUE'} · EUR</div><div style="font-family:Courier New,monospace;font-size:19px;letter-spacing:1px;line-height:1.2;color:#0F4438;white-space:nowrap;overflow:hidden;padding:10px 0 3px">{escape(_sparkline_text(state))}</div><div style="font-family:Georgia,Times New Roman,serif;font-size:20px;font-weight:700">{escape(_money(snap.nav_eur, language))}</div></div>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="width:100%;border-collapse:collapse"><tr>{''.join(metrics[:3])}</tr><tr>{''.join(metrics[3:])}</tr></table>
<div style="{_attr(section)}">{escape(discipline)}</div><div style="border-left:4px solid #B07D2B;background:#F0E5D0;padding:12px 14px;font-size:12px;line-height:1.48">{escape(snap.discipline)}</div><div style="margin-top:7px;border:1px solid #D8CDB8;background:#FFFFFF;padding:10px 12px;font-size:11px;line-height:1.45;color:#5A5043">{escape(snap.next_trigger)}</div>
<div style="{_attr(section)}">{'Bronnen en controle' if is_nl else 'Sources and controls'}</div><table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="width:100%;border-collapse:collapse;background:#FFFFFF;border:1px solid #D8CDB8">{evidence_rows}</table>
<div style="border-top:1px solid #D8CDB8;padding-top:10px;margin-top:14px;font-family:Courier New,monospace;font-size:9px;color:#5A5043">{'Beleggersrapport en analistenrapport volgen hierna.' if is_nl else 'Investor report and analyst report follow below.'}</div>
</td></tr></table></section>'''
