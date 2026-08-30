from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def _money(value: Any) -> str:
    try:
        return f"€{float(value):,.2f}"
    except (TypeError, ValueError):
        return "—"


def _pct(value: Any, digits: int = 2) -> str:
    try:
        return f"{float(value):.{digits}f}%"
    except (TypeError, ValueError):
        return "—"


def _pp(value: Any) -> str:
    try:
        number = float(value)
        sign = "+" if number > 0 else ""
        return f"{sign}{number:.2f} pp"
    except (TypeError, ValueError):
        return "—"


def _text(value: Any) -> str:
    return str(value or "—").strip() or "—"


def _labels(language: str) -> dict[str, str]:
    if language == "nl":
        return {
            "title": "Weekly ETF EU Review",
            "subtitle": "Kapitaalbesluit & accountability",
            "date": "Rapportdatum",
            "decision": "Besluit deze week",
            "portfolio": "Portefeuille",
            "nav": "NAV",
            "invested": "Belegd",
            "cash": "Cash",
            "performance": "Accountability",
            "portfolio_return": "Portefeuille",
            "comparator_return": "VWCE comparator",
            "active_return": "Actief resultaat",
            "drawdown": "Drawdown",
            "contributors": "Bijdrage",
            "top_contributor": "Beste bijdrage",
            "top_detractor": "Grootste tegenvaller",
            "cash_rationale": "Cashbesluit",
            "positions": "Gefunde posities — actuele kapitaalbeslissing",
            "ticker": "Ticker",
            "action": "Actie",
            "weight": "Gewicht",
            "value": "Waarde",
            "fresh_cash": "Fresh-cash view",
            "rationale": "Kernrationale",
            "alternative": "Beste alternatief",
            "trigger": "Invalidering / volgende trigger",
            "confidence": "Confidence",
            "evidence": "Evidence & onzekerheid",
            "unresolved": "Onopgelost",
            "method": "Methodiek",
            "appendix": "Methodiek & pricing provenance",
            "pricing": "Pricing contract",
            "disclaimer": "Modelportefeuille; geen brokerorder. Rapporttekst creëert geen allocatie-, trading- of delivery-authority.",
        }
    return {
        "title": "Weekly ETF EU Review",
        "subtitle": "Capital decision & accountability",
        "date": "Report date",
        "decision": "Decision this week",
        "portfolio": "Portfolio",
        "nav": "NAV",
        "invested": "Invested",
        "cash": "Cash",
        "performance": "Accountability",
        "portfolio_return": "Portfolio",
        "comparator_return": "VWCE comparator",
        "active_return": "Active return",
        "drawdown": "Drawdown",
        "contributors": "Contribution",
        "top_contributor": "Top contributor",
        "top_detractor": "Top detractor",
        "cash_rationale": "Cash decision",
        "positions": "Funded positions — current capital decision",
        "ticker": "Ticker",
        "action": "Action",
        "weight": "Weight",
        "value": "Value",
        "fresh_cash": "Fresh-cash view",
        "rationale": "Core rationale",
        "alternative": "Best alternative",
        "trigger": "Invalidation / next trigger",
        "confidence": "Confidence",
        "evidence": "Evidence & uncertainty",
        "unresolved": "Unresolved",
        "method": "Method",
        "appendix": "Method & pricing provenance",
        "pricing": "Pricing contract",
        "disclaimer": "Model portfolio; no broker order. Report text creates no allocation, trading or delivery authority.",
    }


def _position_rows_md(state: dict[str, Any]) -> str:
    rows = []
    for row in state.get("funded_position_decisions") or []:
        rows.append(
            "| {ticker} | {action} | {weight} | {value} | {fresh} | {confidence} |".format(
                ticker=_text(row.get("ticker")),
                action=_text(row.get("action")),
                weight=_pct(row.get("weight_pct")),
                value=_money(row.get("value_eur")),
                fresh=_text(row.get("fresh_cash_view")).replace("|", "/"),
                confidence=_text(row.get("confidence")),
            )
        )
    return "\n".join(rows)


def render_markdown(state: dict[str, Any], language: str) -> str:
    if language not in {"nl", "en"}:
        raise ValueError("language must be nl or en")
    if state.get("semantic_state_frozen") is not True or state.get("semantic_mutation_allowed_downstream") is not False:
        raise RuntimeError("Renderer accepts frozen review state only")
    if state.get("state_valid") is not True:
        raise RuntimeError(f"Cannot render invalid review state: {state.get('blockers')}")

    l = _labels(language)
    portfolio = state.get("portfolio") or {}
    account = state.get("accountability") or {}
    weekly = state.get("weekly_decision") or {}
    contributor = account.get("top_contributor") or {}
    detractor = account.get("top_detractor") or {}
    unresolved = (state.get("epistemics") or {}).get("unresolved") or []

    lines = [
        f"# {l['title']}",
        f"**{l['subtitle']} · {state.get('report_date')}**",
        "",
        f"> {l['disclaimer']}",
        "",
        f"## {l['decision']}",
        f"**{_text(weekly.get('action'))}**",
        "",
        f"## {l['portfolio']}",
        f"- {l['nav']}: **{_money(portfolio.get('nav_eur'))}**",
        f"- {l['invested']}: **{_money(portfolio.get('invested_market_value_eur'))}**",
        f"- {l['cash']}: **{_money(portfolio.get('cash_eur'))}** ({_pct(account.get('cash_weight_pct'))})",
        "",
        f"## {l['performance']}",
        f"- {l['portfolio_return']}: **{_pct(account.get('portfolio_period_return_pct'))}**",
        f"- {l['comparator_return']}: **{_pct(account.get('comparator_period_return_pct'))}**",
        f"- {l['active_return']}: **{_pp(account.get('active_return_pp'))}**",
        f"- {l['drawdown']}: {_pct(account.get('portfolio_drawdown_pct'))} vs VWCE {_pct(account.get('comparator_drawdown_pct'))}",
        f"- {l['top_contributor']}: {_text(contributor.get('ticker'))} ({_money(contributor.get('contribution_eur'))})",
        f"- {l['top_detractor']}: {_text(detractor.get('ticker'))} ({_money(detractor.get('contribution_eur'))})",
        "",
        f"### {l['cash_rationale']}",
        _text(account.get("cash_rationale")),
        "",
        f"## {l['positions']}",
        f"| {l['ticker']} | {l['action']} | {l['weight']} | {l['value']} | {l['fresh_cash']} | {l['confidence']} |",
        "|---|---:|---:|---:|---|---|",
        _position_rows_md(state),
        "",
    ]
    for row in state.get("funded_position_decisions") or []:
        lines.extend(
            [
                f"### {_text(row.get('ticker'))} — {_text(row.get('action'))}",
                f"- {l['rationale']}: {_text(row.get('rationale'))}",
                f"- {l['alternative']}: {_text(row.get('best_alternative'))}",
                f"- {l['trigger']}: {_text(row.get('invalidation_or_next_trigger'))}",
                f"- {l['confidence']}: {_text(row.get('confidence'))}",
                "",
            ]
        )
    lines.extend(
        [
            f"## {l['evidence']}",
            f"- {l['unresolved']}: " + (", ".join(map(str, unresolved)) if unresolved else "none"),
            f"- {l['method']}: one frozen `review_state` is the sole client-semantic source; renderers do not recalculate NAV, pricing, actions or comparator performance.",
            "",
            f"## {l['appendix']}",
            f"- {l['pricing']}: `{_text((state.get('sources') or {}).get('pricing_artifact'))}`",
            f"- Comparator: `{_text(account.get('comparator_id'))}` / {_text(account.get('comparator_ticker'))} / {_text(account.get('comparator_isin'))}",
            f"- Review state schema: `{_text(state.get('schema_version'))}`",
            "",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def render_html(state: dict[str, Any], language: str) -> str:
    markdown = render_markdown(state, language)
    # Intentionally tiny deterministic renderer: semantic facts are already frozen.
    # It handles the constrained Markdown generated above rather than accepting arbitrary Markdown.
    l = _labels(language)
    portfolio = state.get("portfolio") or {}
    account = state.get("accountability") or {}
    weekly = state.get("weekly_decision") or {}
    contributor = account.get("top_contributor") or {}
    detractor = account.get("top_detractor") or {}

    position_cards = []
    for row in state.get("funded_position_decisions") or []:
        position_cards.append(
            f"""<article class=\"position\"><header><strong>{html.escape(_text(row.get('ticker')))}</strong><span>{html.escape(_text(row.get('action')))}</span></header>
            <div class=\"metrics\"><b>{_pct(row.get('weight_pct'))}</b><b>{_money(row.get('value_eur'))}</b><b>{html.escape(_text(row.get('confidence')))}</b></div>
            <p>{html.escape(_text(row.get('rationale')))}</p>
            <small><b>{html.escape(l['alternative'])}:</b> {html.escape(_text(row.get('best_alternative')))}<br><b>{html.escape(l['trigger'])}:</b> {html.escape(_text(row.get('invalidation_or_next_trigger')))}</small></article>"""
        )

    unresolved = (state.get("epistemics") or {}).get("unresolved") or []
    unresolved_text = ", ".join(map(str, unresolved)) if unresolved else "none"
    return f"""<!doctype html><html lang=\"{language}\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{html.escape(l['title'])}</title>
<style>
@page {{ size:A4; margin:15mm; }}
*{{box-sizing:border-box}} body{{font-family:Arial,Helvetica,sans-serif;margin:0;color:#111827;background:#fff;font-size:12px;line-height:1.45}} main{{max-width:1120px;margin:auto;padding:26px}} .eyebrow{{font-size:11px;text-transform:uppercase;letter-spacing:.12em;color:#667085}} h1{{font-size:30px;margin:4px 0}} h2{{font-size:17px;margin:22px 0 10px;border-bottom:1px solid #d0d5dd;padding-bottom:6px}} .hero{{border:1px solid #d0d5dd;border-radius:14px;padding:18px;margin:18px 0}} .decision{{font-size:20px;font-weight:700;margin:6px 0 18px}} .grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}} .metric{{border:1px solid #e4e7ec;border-radius:10px;padding:10px}} .metric span{{display:block;color:#667085;font-size:10px;text-transform:uppercase}} .metric strong{{font-size:18px}} .positions{{display:grid;grid-template-columns:1fr 1fr;gap:10px}} .position{{border:1px solid #e4e7ec;border-radius:10px;padding:12px;break-inside:avoid}} .position header{{display:flex;justify-content:space-between;font-size:15px}} .position header span{{font-size:11px;border:1px solid #98a2b3;border-radius:99px;padding:2px 7px}} .metrics{{display:flex;gap:14px;margin:8px 0}} .metrics b{{font-size:11px}} small{{color:#475467}} .foot{{margin-top:22px;border-top:1px solid #d0d5dd;padding-top:10px;color:#667085}} @media(max-width:720px){{.grid,.positions{{grid-template-columns:1fr}}main{{padding:16px}}}}
</style></head><body><main>
<div class=\"eyebrow\">{html.escape(l['subtitle'])} · {html.escape(_text(state.get('report_date')))}</div><h1>{html.escape(l['title'])}</h1>
<div class=\"hero\"><div class=\"eyebrow\">{html.escape(l['decision'])}</div><div class=\"decision\">{html.escape(_text(weekly.get('action')))}</div>
<div class=\"grid\"><div class=\"metric\"><span>{html.escape(l['nav'])}</span><strong>{_money(portfolio.get('nav_eur'))}</strong></div><div class=\"metric\"><span>{html.escape(l['cash'])}</span><strong>{_money(portfolio.get('cash_eur'))}</strong></div><div class=\"metric\"><span>{html.escape(l['active_return'])}</span><strong>{_pp(account.get('active_return_pp'))}</strong></div></div></div>
<h2>{html.escape(l['performance'])}</h2><div class=\"grid\"><div class=\"metric\"><span>{html.escape(l['portfolio_return'])}</span><strong>{_pct(account.get('portfolio_period_return_pct'))}</strong></div><div class=\"metric\"><span>{html.escape(l['comparator_return'])}</span><strong>{_pct(account.get('comparator_period_return_pct'))}</strong></div><div class=\"metric\"><span>{html.escape(l['drawdown'])}</span><strong>{_pct(account.get('portfolio_drawdown_pct'))}</strong><small> vs VWCE {_pct(account.get('comparator_drawdown_pct'))}</small></div><div class=\"metric\"><span>{html.escape(l['top_contributor'])}</span><strong>{html.escape(_text(contributor.get('ticker')))}</strong><small>{_money(contributor.get('contribution_eur'))}</small></div><div class=\"metric\"><span>{html.escape(l['top_detractor'])}</span><strong>{html.escape(_text(detractor.get('ticker')))}</strong><small>{_money(detractor.get('contribution_eur'))}</small></div><div class=\"metric\"><span>{html.escape(l['cash'])}</span><strong>{_pct(account.get('cash_weight_pct'))}</strong><small>{html.escape(_text(account.get('cash_drag_status')))}</small></div></div>
<h2>{html.escape(l['cash_rationale'])}</h2><p>{html.escape(_text(account.get('cash_rationale')))}</p>
<h2>{html.escape(l['positions'])}</h2><section class=\"positions\">{''.join(position_cards)}</section>
<h2>{html.escape(l['evidence'])}</h2><p><b>{html.escape(l['unresolved'])}:</b> {html.escape(unresolved_text)}</p><p><b>{html.escape(l['pricing'])}:</b> {html.escape(_text((state.get('sources') or {}).get('pricing_artifact')))}</p>
<p class=\"foot\">{html.escape(l['disclaimer'])}<br>Schema: {html.escape(_text(state.get('schema_version')))} · frozen semantic state: true.</p>
<!-- deterministic-source-markdown-sha-input-length:{len(markdown)} -->
</main></body></html>"""


def render_to_paths(state: dict[str, Any], *, language: str, markdown_path: Path, html_path: Path) -> None:
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_markdown(state, language), encoding="utf-8")
    html_path.write_text(render_html(state, language), encoding="utf-8")


def load_review_state(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Review state must be a JSON object")
    return payload
