"""AI commentary for the report — narrates facts, never computes or decides.

The model receives the facts JSON and returns commentary sections. Every number
in its text must already exist in the facts (same rounding); otherwise the text
is rejected, retried once, and replaced by deterministic fallback text. The
report therefore never depends on the AI being available or correct.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

import requests

LANGS = ("en", "nl")
SECTIONS = ("headline", "summary", "trades", "markets", "watch")
BANNED = {
    "en": ["you should", "we recommend", "guaranteed", "will rise", "will fall", "certain to", "buy now", "sell now"],
    "nl": ["u moet", "je moet", "wij raden", "we raden", "gegarandeerd", "zal stijgen", "zal dalen", "nu kopen", "nu verkopen"],
}

SYSTEM = """You write the commentary for a premium weekly model-portfolio report on European UCITS ETFs.

Hard rules:
1. Use ONLY the facts in the JSON you receive. Do not add any number, date, price, rate, event or name that is not in it.
2. Copy every number exactly as it appears in the facts (same rounding). You may drop a minus sign when the sentence already says "fell"/"daalde".
3. Explain trades mechanically from their "why" and "detail" fields: what rule triggered, with its numbers.
4. No forecasts, no personal advice, no "you should". This is a model portfolio run by fixed rules.
5. Tone: calm, precise, plain language for private investors. No jargon, no hype, no exclamation marks.
6. Name funds by a short form of their name (e.g. "Vanguard FTSE All-World"), with the ticker in brackets the first time.
7. Macro items with "stale": true or "available": false must be described as not current / unavailable, or left out.

Return a JSON object with exactly these keys, written in the requested language:
- "headline": one sentence, at most 14 words, the main news of the week.
- "summary": 3-4 sentences: this week's and since-start return of the portfolio vs the benchmark, the market state (regime, breadth), and what changed in the portfolio.
- "trades": a list with one object {"id": <ticker>, "text": <one or two sentences>} per trade, then one per deferred change (say it is planned for a later week and why).
- "markets": 3-4 sentences on the market panel and the macro indicators.
- "watch": a list of 2-3 short sentences on what the rules are watching next (e.g. held funds whose rank or trend is close to a threshold, deferred changes).
"""


# ── Number check ─────────────────────────────────────────────────────────────
NUM_RE = re.compile(r"(?<![\w])-?\d[\d.,]*")


def _parse(token: str, lang: str) -> float | None:
    t = token.strip(".,")
    if not t or not re.search(r"\d", t):
        return None
    if lang == "nl":
        t = t.replace(".", "").replace(",", ".") if "," in t else (t.replace(".", "") if re.fullmatch(r"-?\d{1,3}(\.\d{3})+", t) else t)
    else:
        t = t.replace(",", "")
    try:
        return float(t)
    except ValueError:
        return None


def allowed_numbers(facts: Any) -> set[float]:
    out: set[float] = set()

    def walk(x):
        if isinstance(x, bool):
            return
        if isinstance(x, (int, float)):
            out.add(round(abs(float(x)), 2))  # exact displayed value only
        elif isinstance(x, str):
            for tok in NUM_RE.findall(x):
                v = _parse(tok, "en")
                if v is not None:
                    out.add(round(abs(v), 2))
            for part in re.findall(r"\d+", x):  # dates and codes: 2026, 11, 14
                out.add(float(int(part)))
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(facts)
    return out


def unknown_numbers(text: str, lang: str, allowed: set[float]) -> list[str]:
    bad = []
    for tok in NUM_RE.findall(text):
        v = _parse(tok, lang)
        if v is None:
            continue
        a = abs(v)
        if round(a, 2) != a or a not in allowed:
            bad.append(tok)
    return bad


def check(sections: dict, lang: str, facts: dict) -> list[str]:
    problems = []
    for k in SECTIONS:
        if k not in sections:
            problems.append(f"missing section {k}")
    allowed = allowed_numbers(facts)
    texts = []
    for k in ("headline", "summary", "markets"):
        texts.append(str(sections.get(k, "")))
    texts += [str(t.get("text", "")) for t in sections.get("trades", []) if isinstance(t, dict)]
    texts += [str(t) for t in sections.get("watch", [])]
    blob = "\n".join(texts)
    for tok in unknown_numbers(blob, lang, allowed):
        problems.append(f"number not in facts: {tok}")
    low = blob.lower()
    for b in BANNED[lang]:
        if b in low:
            problems.append(f"banned phrase: {b}")
    return problems


# ── Model call ───────────────────────────────────────────────────────────────
def _call_openai(facts: dict, lang: str, feedback: str | None) -> dict:
    key = os.environ["OPENAI_API_KEY"]
    model = os.environ.get("V2_OPENAI_MODEL", "gpt-4o")
    lang_name = {"en": "English", "nl": "Dutch (Netherlands; use comma as decimal separator, e.g. 0,49%)"}[lang]
    user = f"Language: {lang_name}.\n\nFacts JSON:\n{json.dumps(facts, ensure_ascii=False)}"
    if feedback:
        user += f"\n\nYour previous answer was rejected: {feedback}. Fix it; use only numbers that appear in the facts."
    r = requests.post("https://api.openai.com/v1/chat/completions", timeout=120,
                      headers={"Authorization": f"Bearer {key}"},
                      json={"model": model, "response_format": {"type": "json_object"},
                            "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]})
    r.raise_for_status()
    return json.loads(r.json()["choices"][0]["message"]["content"])


def _facts_for_model(facts: dict) -> dict:
    slim = {k: v for k, v in facts.items() if k not in ("chart",)}
    return slim


# ── Deterministic fallback ───────────────────────────────────────────────────
def _fmt(v: float, lang: str, nd: int = 2) -> str:
    s = f"{v:,.{nd}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".") if lang == "nl" else s


def reason_text(t: dict, lang: str) -> str:
    """One sentence per trade, from the structured reason — both languages."""
    p, w, nl = t.get("params") or {}, t.get("why"), lang == "nl"
    f = lambda v, nd=1: _fmt(v, lang, nd)
    if w == "trend_down":
        return (f"Koers {f(p['close'], 2)} staat twee weken op rij onder het 200-daags gemiddelde ({f(p['sma200'], 2)}): de trend is gekeerd, de positie wordt gesloten." if nl
                else f"Price {f(p['close'], 2)} has been below its 200-day average ({f(p['sma200'], 2)}) for two weeks running: the trend has turned, so the position is closed.")
    if w == "rank_dropped":
        return (f"Gezakt naar plaats {p['rank']} van {p['n']}; een positie blijft alleen zolang ze in de top {p['keep_limit']} staat." if nl
                else f"Dropped to rank {p['rank']} of {p['n']}; a holding stays only while it ranks in the top {p['keep_limit']}.")
    if w == "replaced":
        return (f"Vervangen door {p['new_id']}: score {p['new_score']} tegen {p['old_score']}, meer dan de vereiste {p['margin']} punten verschil." if nl
                else f"Replaced by {p['new_id']}: score {p['new_score']} against {p['old_score']}, more than the required {p['margin']}-point margin.")
    if w == "slots_reduced":
        return (f"Defensieve stand: nog {p['slots']} satellieten; dit is de zwakste positie (plaats {p['rank']})." if nl
                else f"Defensive mode allows {p['slots']} satellites; this is the weakest holding (rank {p['rank']}).")
    if w == "not_in_target":
        return (f"Geen onderdeel van de doelportefeuille: de kern bestaat uit {p['core_equity']} en {p['core_bonds']}." if nl
                else f"Not part of the target portfolio: the core is {p['core_equity']} plus {p['core_bonds']}.")
    if w == "selected":
        return (f"Nieuw: plaats {p['rank']} van {p['n']} in de scan, score {p['score']}, opwaartse trend." if nl
                else f"New: rank {p['rank']} of {p['n']} in the scan, score {p['score']}, in an uptrend.")
    if w == "resize":
        return (f"Gewicht {f(p['weight_pct'])}% tegen doel {f(p['target_pct'])}%; bijgesteld omdat het verschil groter is dan {p['band_pts']} procentpunt." if nl
                else f"Weight {f(p['weight_pct'])}% against a target of {f(p['target_pct'])}%; resized because the gap exceeds {p['band_pts']} percentage points.")
    if w == "deploy_cash":
        return (f"Kas {f(p['cash_pct'])}% ligt boven het plafond van {p['ceiling_pct']}%; aangevuld richting doel {f(p['target_pct'])}%." if nl
                else f"Cash {f(p['cash_pct'])}% is above the {p['ceiling_pct']}% ceiling; topped up toward the {f(p['target_pct'])}% target.")
    if w == "core_or_defensive":
        return (f"Kern- of defensieve positie, doelgewicht {f(p['target_pct'])}%." if nl else f"Core or defensive position, target weight {f(p['target_pct'])}%.")
    return t.get("detail", "")


def short(name: str) -> str:
    from v2.render import short_name
    return short_name(name)


def _long(d: str, lang: str) -> str:
    from v2.render import long_date
    return long_date(d, lang)


def fallback(facts: dict, lang: str) -> dict:
    p, rg = facts["portfolio"], facts["regime"]
    nl = lang == "nl"
    up_dn = lambda v: (("steeg" if v >= 0 else "daalde") if nl else ("rose" if v >= 0 else "fell"))
    headline = ("Portefeuille " + up_dn(p["week_return_pct"]) + f" {_fmt(abs(p['week_return_pct']), lang)}% deze week" if nl
                else f"Portfolio {up_dn(p['week_return_pct'])} {_fmt(abs(p['week_return_pct']), lang)}% this week")
    regime = {"risk_on": ("risicobereid" if nl else "risk-on"), "risk_off": ("defensief" if nl else "risk-off")}[rg["state"]]
    if nl:
        summary = (f"De modelportefeuille {up_dn(p['week_return_pct'])} deze week {_fmt(abs(p['week_return_pct']), lang)}%, tegen {_fmt(p['benchmark_week_return_pct'], lang)}% voor de benchmark. "
                   f"Sinds {_long(facts['track_record_start'], lang)} is het rendement {_fmt(p['since_start_return_pct'], lang)}% tegen {_fmt(p['benchmark_since_start_return_pct'], lang)}% voor de benchmark. "
                   f"De markttoestand is {regime}: {_fmt(rg['breadth_pct'], lang, 1)}% van de gerangschikte fondsen staat boven het 200-daags gemiddelde. "
                   f"Er zijn deze week {len(facts['trades'])} transacties.")
    else:
        summary = (f"The model portfolio {up_dn(p['week_return_pct'])} {_fmt(abs(p['week_return_pct']), lang)}% this week, against {_fmt(p['benchmark_week_return_pct'], lang)}% for the benchmark. "
                   f"Since {_long(facts['track_record_start'], lang)} the return is {_fmt(p['since_start_return_pct'], lang)}% against {_fmt(p['benchmark_since_start_return_pct'], lang)}% for the benchmark. "
                   f"The market state is {regime}: {_fmt(rg['breadth_pct'], lang, 1)}% of ranked funds trade above their 200-day average. "
                   f"There are {len(facts['trades'])} trades this week.")
    trades = [{"id": t["id"], "text": reason_text(t, lang)} for t in facts["trades"]]
    trades += [{"id": x["id"], "text": reason_text(x, lang) + (f" Gepland voor een volgende week: maximaal {facts['rules']['max_changes_per_week']} fondswissels per week." if nl
                                        else f" Planned for a later week: at most {facts['rules']['max_changes_per_week']} fund changes per week.")} for x in facts["deferred"]]
    mk = facts["market"]
    best = max(mk, key=lambda m: m["week_pct"] or -99)
    worst = min(mk, key=lambda m: m["week_pct"] or 99)
    markets = (f"Sterkste categorie deze week: {best['label_nl']} ({_fmt(best['week_pct'], lang)}%); zwakste: {worst['label_nl']} ({_fmt(worst['week_pct'], lang)}%)." if nl
               else f"Strongest asset class this week: {best['label_en']} ({_fmt(best['week_pct'], lang)}%); weakest: {worst['label_en']} ({_fmt(worst['week_pct'], lang)}%).")
    watch = [(f"Gepland: {('koop' if x['kind'] == 'entry' else 'verkoop')} {x['id']} ({short(x['name'])})." if nl
              else f"Planned: {('buy' if x['kind'] == 'entry' else 'sell')} {x['id']} ({short(x['name'])}).") for x in facts["deferred"][:3]] or [
        "Geen geplande wijzigingen." if nl else "No planned changes."]
    return {"headline": headline, "summary": summary, "trades": trades, "markets": markets, "watch": watch}


def narrate(facts: dict) -> dict:
    """Return {"en": sections, "nl": sections, "source": {...}, "problems": {...}}."""
    out: dict[str, Any] = {"source": {}, "problems": {}}
    model_facts = _facts_for_model(facts)
    for lang in LANGS:
        sections, problems = None, []
        if os.environ.get("OPENAI_API_KEY"):
            feedback = None
            for attempt in (1, 2):
                try:
                    cand = _call_openai(model_facts, lang, feedback)
                    problems = check(cand, lang, facts)
                    if not problems:
                        sections = cand
                        out["source"][lang] = f"ai:{os.environ.get('V2_OPENAI_MODEL', 'gpt-4o')}:attempt{attempt}"
                        break
                    feedback = "; ".join(problems[:10])
                except Exception as exc:
                    problems = [f"api_error: {type(exc).__name__}: {str(exc)[:120]}"]
                    break
        else:
            problems = ["no OPENAI_API_KEY"]
        if sections is None:
            sections = fallback(facts, lang)
            out["source"][lang] = "fallback"
            fb_problems = check(sections, lang, facts)
            if fb_problems:
                raise SystemExit(f"fallback text failed its own number check ({lang}): {fb_problems}")
        out[lang] = sections
        out["problems"][lang] = problems
    return out
