from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def _money(value: Any) -> str:
    try: return f"€{float(value):,.2f}"
    except (TypeError, ValueError): return "—"


def _pct(value: Any) -> str:
    try: return f"{float(value):.2f}%"
    except (TypeError, ValueError): return "—"


def _pp(value: Any) -> str:
    try:
        n = float(value); return f"{'+' if n > 0 else ''}{n:.2f} pp"
    except (TypeError, ValueError): return "—"


def _text(value: Any) -> str:
    return str(value or "—").strip() or "—"


def _labels(language: str) -> dict[str, str]:
    if language == "nl":
        return {"title":"Weekly ETF EU Review","subtitle":"Kapitaalbesluit & accountability","decision":"Besluit deze week","nav":"NAV","invested":"Belegd","cash":"Cash","active":"Actief resultaat","portfolio_return":"Portefeuille","comparator":"VWCE comparator","drawdown":"Drawdown","contributor":"Beste bijdrage","detractor":"Grootste tegenvaller","candidate":"Beste nieuwe/vervangingskandidaat","risk":"Grootste actuele risico","cash_decision":"Cashbesluit","positions":"Gefunde posities — actuele kapitaalbeslissing","action":"Actie","weight":"Gewicht","value":"Waarde","fresh":"Fresh-cash view","confidence":"Confidence","rationale":"Kernrationale","alternative":"Beste alternatief","trigger":"Invalidering / volgende trigger","evidence":"Evidence & onzekerheid","unresolved":"Onopgelost","appendix":"Methodiek & pricing provenance","disclaimer":"Modelportefeuille; geen brokerorder. Rapporttekst creëert geen allocatie-, trading- of delivery-authority."}
    return {"title":"Weekly ETF EU Review","subtitle":"Capital decision & accountability","decision":"Decision this week","nav":"NAV","invested":"Invested","cash":"Cash","active":"Active return","portfolio_return":"Portfolio","comparator":"VWCE comparator","drawdown":"Drawdown","contributor":"Top contributor","detractor":"Top detractor","candidate":"Best new/replacement candidate","risk":"Biggest current risk","cash_decision":"Cash decision","positions":"Funded positions — current capital decision","action":"Action","weight":"Weight","value":"Value","fresh":"Fresh-cash view","confidence":"Confidence","rationale":"Core rationale","alternative":"Best alternative","trigger":"Invalidation / next trigger","evidence":"Evidence & uncertainty","unresolved":"Unresolved","appendix":"Method & pricing provenance","disclaimer":"Model portfolio; no broker order. Report text creates no allocation, trading or delivery authority."}


def _check(state: dict[str, Any], language: str) -> None:
    if language not in {"nl", "en"}: raise ValueError("language must be nl or en")
    if state.get("semantic_state_frozen") is not True or state.get("semantic_mutation_allowed_downstream") is not False: raise RuntimeError("Renderer accepts frozen review state only")
    if state.get("state_valid") is not True: raise RuntimeError(f"Cannot render invalid review state: {state.get('blockers')}")


def _candidate_text(weekly: dict[str, Any]) -> str:
    candidate = weekly.get("best_new_or_replace_candidate") or {}
    return f"{_text(candidate.get('ticker'))} — {_text(candidate.get('fund_name') or candidate.get('lane_name'))}" if candidate else "None established"


def render_markdown(state: dict[str, Any], language: str) -> str:
    _check(state, language)
    l, p, a, w = _labels(language), state.get("portfolio") or {}, state.get("accountability") or {}, state.get("weekly_decision") or {}
    contributor, detractor, risk = a.get("top_contributor") or {}, a.get("top_detractor") or {}, w.get("biggest_current_risk") or {}
    lines = [f"# {l['title']}", f"**{l['subtitle']} · {state.get('report_date')}**", "", f"> {l['disclaimer']}", "", f"## {l['decision']}", f"**{_text(w.get('action'))}**", "", f"- {l['nav']}: **{_money(p.get('nav_eur'))}**", f"- {l['invested']}: **{_money(p.get('invested_market_value_eur'))}**", f"- {l['cash']}: **{_money(p.get('cash_eur'))}** ({_pct(a.get('cash_weight_pct'))})", f"- {l['portfolio_return']}: **{_pct(a.get('portfolio_period_return_pct'))}**", f"- {l['comparator']}: **{_pct(a.get('comparator_period_return_pct'))}**", f"- {l['active']}: **{_pp(a.get('active_return_pp'))}**", f"- {l['drawdown']}: {_pct(a.get('portfolio_drawdown_pct'))} vs VWCE {_pct(a.get('comparator_drawdown_pct'))}", f"- {l['contributor']}: {_text(contributor.get('ticker'))} ({_money(contributor.get('contribution_eur'))})", f"- {l['detractor']}: {_text(detractor.get('ticker'))} ({_money(detractor.get('contribution_eur'))})", f"- {l['candidate']}: {_candidate_text(w)}", f"- {l['risk']}: {_text(risk.get('summary'))}", "", f"### {l['cash_decision']}", _text(a.get("cash_rationale")), "", f"## {l['positions']}", f"| Ticker | {l['action']} | {l['weight']} | {l['value']} | {l['fresh']} | {l['confidence']} |", "|---|---|---:|---:|---|---|"]
    for row in state.get("funded_position_decisions") or []:
        lines.append(f"| {_text(row.get('ticker'))} | {_text(row.get('action'))} | {_pct(row.get('weight_pct'))} | {_money(row.get('value_eur'))} | {_text(row.get('fresh_cash_view')).replace('|','/')} | {_text(row.get('confidence'))} |")
    for row in state.get("funded_position_decisions") or []:
        lines += ["", f"### {_text(row.get('ticker'))} — {_text(row.get('action'))}", f"- {l['rationale']}: {_text(row.get('rationale'))}", f"- {l['alternative']}: {_text(row.get('best_alternative'))}", f"- {l['trigger']}: {_text(row.get('invalidation_or_next_trigger'))}", f"- {l['confidence']}: {_text(row.get('confidence'))}"]
    unresolved = (state.get("epistemics") or {}).get("unresolved") or []
    lines += ["", f"## {l['evidence']}", f"- {l['unresolved']}: {', '.join(map(str, unresolved)) if unresolved else 'none'}", "- Method: one frozen `review_state` is the sole client-semantic source; renderers do not recalculate NAV, pricing, actions or comparator performance.", "", f"## {l['appendix']}", f"- Pricing: `{_text((state.get('sources') or {}).get('pricing_artifact'))}`", f"- Comparator: `{_text(a.get('comparator_id'))}` / {_text(a.get('comparator_ticker'))} / {_text(a.get('comparator_isin'))}", f"- Review state schema: `{_text(state.get('schema_version'))}`", ""]
    return "\n".join(lines)


def render_html(state: dict[str, Any], language: str) -> str:
    _check(state, language)
    l, p, a, w = _labels(language), state.get("portfolio") or {}, state.get("accountability") or {}, state.get("weekly_decision") or {}
    contributor, detractor, risk = a.get("top_contributor") or {}, a.get("top_detractor") or {}, w.get("biggest_current_risk") or {}
    def card(label: str, value: str, small: str = "") -> str:
        return f'<div class="metric"><span>{html.escape(label)}</span><strong>{html.escape(value)}</strong>{f"<small>{html.escape(small)}</small>" if small else ""}</div>'
    positions = "".join(f'<article class="position"><header><strong>{html.escape(_text(r.get("ticker")))}</strong><span>{html.escape(_text(r.get("action")))}</span></header><div class="mini">{_pct(r.get("weight_pct"))} · {_money(r.get("value_eur"))} · {html.escape(_text(r.get("confidence")))}</div><p>{html.escape(_text(r.get("rationale")))}</p><small><b>{html.escape(l["alternative"])}:</b> {html.escape(_text(r.get("best_alternative")))}<br><b>{html.escape(l["trigger"])}:</b> {html.escape(_text(r.get("invalidation_or_next_trigger")))}</small></article>' for r in state.get("funded_position_decisions") or [])
    unresolved = (state.get("epistemics") or {}).get("unresolved") or []
    cockpit = "".join([card(l["nav"], _money(p.get("nav_eur"))), card(l["cash"], _money(p.get("cash_eur")), _pct(a.get("cash_weight_pct"))), card(l["active"], _pp(a.get("active_return_pp"))), card(l["portfolio_return"], _pct(a.get("portfolio_period_return_pct"))), card(l["comparator"], _pct(a.get("comparator_period_return_pct"))), card(l["drawdown"], _pct(a.get("portfolio_drawdown_pct")), f'VWCE {_pct(a.get("comparator_drawdown_pct"))}'), card(l["contributor"], _text(contributor.get("ticker")), _money(contributor.get("contribution_eur"))), card(l["detractor"], _text(detractor.get("ticker")), _money(detractor.get("contribution_eur"))), card(l["candidate"], _candidate_text(w)), card(l["risk"], _text(risk.get("ticker")), _text(risk.get("summary")))])
    return f'''<!doctype html><html lang="{language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(l['title'])}</title><style>@page{{size:A4;margin:14mm}}*{{box-sizing:border-box}}body{{font-family:Arial,Helvetica,sans-serif;margin:0;color:#111827;font-size:12px;line-height:1.45}}main{{max-width:1120px;margin:auto;padding:24px}}.eyebrow{{font-size:10px;text-transform:uppercase;letter-spacing:.12em;color:#667085}}h1{{font-size:29px;margin:4px 0}}h2{{font-size:17px;margin:22px 0 10px;border-bottom:1px solid #d0d5dd;padding-bottom:6px}}.hero{{border:1px solid #d0d5dd;border-radius:14px;padding:16px;margin:16px 0}}.decision{{font-size:20px;font-weight:700;margin:5px 0 14px}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}}.metric{{border:1px solid #e4e7ec;border-radius:9px;padding:9px;min-height:70px}}.metric span{{display:block;color:#667085;font-size:9px;text-transform:uppercase}}.metric strong{{display:block;font-size:16px;margin-top:3px}}small{{display:block;color:#475467;margin-top:3px}}.positions{{display:grid;grid-template-columns:1fr 1fr;gap:9px}}.position{{border:1px solid #e4e7ec;border-radius:9px;padding:11px;break-inside:avoid}}.position header{{display:flex;justify-content:space-between;font-size:14px}}.position header span{{font-size:10px;border:1px solid #98a2b3;border-radius:99px;padding:2px 7px}}.mini{{font-size:10px;color:#475467;margin:6px 0}}.foot{{margin-top:20px;border-top:1px solid #d0d5dd;padding-top:9px;color:#667085}}@media(max-width:720px){{.grid,.positions{{grid-template-columns:1fr}}main{{padding:14px}}}}</style></head><body><main><div class="eyebrow">{html.escape(l['subtitle'])} · {html.escape(_text(state.get('report_date')))}</div><h1>{html.escape(l['title'])}</h1><div class="hero"><div class="eyebrow">{html.escape(l['decision'])}</div><div class="decision">{html.escape(_text(w.get('action')))}</div><div class="grid">{cockpit}</div></div><h2>{html.escape(l['cash_decision'])}</h2><p>{html.escape(_text(a.get('cash_rationale')))}</p><h2>{html.escape(l['positions'])}</h2><section class="positions">{positions}</section><h2>{html.escape(l['evidence'])}</h2><p><b>{html.escape(l['unresolved'])}:</b> {html.escape(', '.join(map(str, unresolved)) if unresolved else 'none')}</p><p>Pricing: {html.escape(_text((state.get('sources') or {}).get('pricing_artifact')))}</p><p class="foot">{html.escape(l['disclaimer'])}<br>Schema: {html.escape(_text(state.get('schema_version')))} · frozen semantic state: true.</p></main></body></html>'''


def render_to_paths(state: dict[str, Any], *, language: str, markdown_path: Path, html_path: Path) -> None:
    markdown_path.parent.mkdir(parents=True, exist_ok=True); html_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_markdown(state, language), encoding="utf-8")
    html_path.write_text(render_html(state, language), encoding="utf-8")


def load_review_state(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict): raise RuntimeError("Review state must be a JSON object")
    return payload
