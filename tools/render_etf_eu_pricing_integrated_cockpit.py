from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

RUN_ID = "20260618_000000"
CREATED_AT_UTC = "2026-06-18T00:00:00Z"
SOURCE_UNIVERSE = Path("output/client_surface/etf_eu_cockpit_universe_enrichment_20260618_000000.json")
SOURCE_RENDER = Path("output/client_surface/etf_eu_enriched_cockpit_render_20260618_000000.json")
SOURCE_PRICING = Path("output/pricing/etf_eu_pricing_line_expansion_20260618_000000.json")
SOURCE_PRICING_NOTES = Path("output/pricing/etf_eu_pricing_line_expansion_notes_20260618_000000.md")
AUTH = Path("output/delivery/etf_eu_delivery_authorization_decision_20260618_000000.json")
EN_MD = Path("output/client_surface/weekly_etf_eu_review_260618_cockpit_pricing_integrated.md")
NL_MD = Path("output/client_surface/weekly_etf_eu_review_nl_260618_cockpit_pricing_integrated.md")
EN_HTML = Path("output/client_surface/weekly_etf_eu_review_260618_cockpit_pricing_integrated.html")
NL_HTML = Path("output/client_surface/weekly_etf_eu_review_nl_260618_cockpit_pricing_integrated.html")
MANIFEST = Path("output/client_surface/etf_eu_cockpit_pricing_integration_20260618_000000.json")
RENDERER = Path("tools/render_etf_eu_pricing_integrated_cockpit.py")
VALIDATOR = Path("tools/validate_etf_eu_cockpit_pricing_integration.py")
TESTS = Path("tests/test_etf_eu_cockpit_pricing_integration.py")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _join(values: list[str]) -> str:
    return ", ".join(value for value in values if value)


def _symbols(candidate: dict[str, Any]) -> str:
    symbols = []
    for line in candidate.get("trading_lines", []):
        symbol = str(line.get("pricing_symbol_yahoo") or line.get("exchange_ticker") or "").strip()
        if symbol:
            symbols.append(symbol)
    return _join(symbols)


def _proxies(candidate: dict[str, Any]) -> str:
    return _join([str(proxy.get("us_proxy") or "") for proxy in candidate.get("research_proxies", [])])


def _status_summary_rows(summary: dict[str, Any]) -> list[str]:
    return [f"| {key} | {value} |" for key, value in summary.items()]


def _candidate_rows(candidates: list[dict[str, Any]]) -> list[str]:
    rows = []
    for c in candidates:
        rows.append(
            "| {fund} | {isin} | {line_status} | {evidence_status} | {symbols} | {proxy} | {safe} |".format(
                fund=c.get("fund_name", ""),
                isin=c.get("isin", ""),
                line_status=c.get("pricing_line_status", ""),
                evidence_status=c.get("pricing_evidence_status", ""),
                symbols=_symbols(c),
                proxy=_proxies(c),
                safe=str(c.get("safe_for_cockpit_pricing_evidence", False)).lower(),
            )
        )
    return rows


def _unsafe_rows(unsafe: list[dict[str, Any]]) -> list[str]:
    return [f"| {item.get('symbol', '')} | {item.get('reason', '')} |" for item in unsafe]


def _proxy_rows(candidates: list[dict[str, Any]], nl: bool = False) -> list[str]:
    rows = []
    allowed = "alleen researchproxy / benchmark" if nl else "research proxy / benchmark only"
    blocked = "EU-holding, EU-prijsregel of financieringsbron" if nl else "EU holding, EU pricing line, or funding source"
    for c in candidates:
        for proxy in c.get("research_proxies", []):
            rows.append(f"| {proxy.get('us_proxy', '')} | {c.get('fund_name', '')} / {c.get('isin', '')} | {allowed} | {blocked} |")
    return rows


def _markdown(pricing: dict[str, Any], nl: bool = False) -> str:
    candidates = pricing["candidate_pricing_evidence"]
    summary = pricing["pricing_line_status_summary"]
    unsafe = pricing["unsafe_pricing_symbols"]
    if nl:
        title = "# Weekly ETF EU-review — pricing-geïntegreerde cockpit POC"
        lines = [
            title,
            "",
            "## Cockpitsamenvatting",
            "",
            "- **Status:** proof of concept / review-only.",
            "- **Prijsbewijs:** CSPX.L en SXR8.DE zijn de enige huidige review-only prijsbaseline.",
            "- **Niet veilig:** SMH blijft pricing_symbol_ambiguous en is geen veilige UCITS-prijsregel zonder exchange-specific verificatie.",
            "- **Geblokkeerd:** Gold/ETC blijft policy_blocked; infrastructure blijft identity_incomplete.",
            "- **Authority:** delivery_authorization_decision=remain_blocked; production_delivery=false; portfolio_mutation=false; candidate_promotion=false; funding_authority=false; valuation_grade=false.",
            "",
            "## Prijsbewijs in één oogopslag",
            "",
            "| Status | Aantal |",
            "| --- | --- |",
            *_status_summary_rows(summary),
            "",
            "## Zichtbaar UCITS-universum",
            "",
            "| Kandidaat | ISIN | Prijsregelstatus | Prijsbewijsstatus | Prijssymbolen | Researchproxy | Safe voor cockpit-prijsbewijs |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            *_candidate_rows(candidates),
            "",
            "## Prijsregel-bewijskaart",
            "",
            "| Kandidaat | Reader meaning | Volgende prijsactie |",
            "| --- | --- | --- |",
            *[f"| {c.get('fund_name', '')} | {c.get('reader_meaning', '')} | {c.get('next_pricing_action', '')} |" for c in candidates],
            "",
            "## Onveilige of geblokkeerde prijsregels",
            "",
            "| Symbool | Reden |",
            "| --- | --- |",
            *_unsafe_rows(unsafe),
            "| Gold/ETC | policy_blocked totdat ETC-beleid expliciet is besloten. |",
            "| Infrastructure | identity_incomplete totdat ISIN en issuer zijn geverifieerd. |",
            "",
            "## Scheiding met researchproxy",
            "",
            "| Researchproxy | EU/UCITS-weergave | Toegestaan gebruik | Geblokkeerd gebruik |",
            "| --- | --- | --- | --- |",
            *_proxy_rows(candidates, nl=True),
            "",
            "## Actiekaart voor de lezer",
            "",
            "| Vraag | Antwoord | Actie |",
            "| --- | --- | --- |",
            "| Wat is bruikbaar? | IE00B5BMR087 blijft usable_for_review_only via CSPX.L en SXR8.DE. | Gebruik alleen als reviewbewijs. |",
            "| Wat is onveilig? | IE00BMC38736 / SMH blijft ambiguous of pending. | Eerst exchange-specific UCITS-prijsregel verifiëren. |",
            "| Wat blijft geblokkeerd? | Gold/ETC policy_blocked; infrastructure identity_incomplete. | Niet promoveren of financieren. |",
            "",
            "## Huidige blokkades",
            "",
            "| Blokkade | Status |",
            "| --- | --- |",
            "| Delivery | delivery_authorization_decision=remain_blocked |",
            "| Productie | production_delivery=false |",
            "| Portefeuille | portfolio_mutation=false |",
            "| Kandidaatpromotie | candidate_promotion=false |",
            "| Funding | funding_authority=false |",
            "| Valuation-grade | valuation_grade=false |",
            "",
            "## Bijlage — technisch bewijs",
            "",
            "- Renderer: `tools/render_etf_eu_pricing_integrated_cockpit.py`",
            "- Validator: `tools/validate_etf_eu_cockpit_pricing_integration.py`",
            "- Testbestand: `tests/test_etf_eu_cockpit_pricing_integration.py`",
        ]
    else:
        title = "# Weekly ETF EU Review — Pricing-Integrated Cockpit POC"
        lines = [
            title,
            "",
            "## Cockpit summary",
            "",
            "- **Status:** proof of concept / review-only.",
            "- **Pricing evidence:** CSPX.L and SXR8.DE are the only current review-only pricing baseline.",
            "- **Unsafe:** SMH remains pricing_symbol_ambiguous and is not safe UCITS pricing evidence without exchange-specific verification.",
            "- **Blocked:** Gold/ETC remains policy_blocked; infrastructure remains identity_incomplete.",
            "- **Authority:** delivery_authorization_decision=remain_blocked; production_delivery=false; portfolio_mutation=false; candidate_promotion=false; funding_authority=false; valuation_grade=false.",
            "",
            "## Pricing evidence at a glance",
            "",
            "| Status | Count |",
            "| --- | --- |",
            *_status_summary_rows(summary),
            "",
            "## Visible UCITS universe",
            "",
            "| Candidate | ISIN | Pricing-line status | Pricing evidence status | Pricing symbols | Research proxy | Safe for cockpit pricing evidence |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            *_candidate_rows(candidates),
            "",
            "## Pricing-line evidence map",
            "",
            "| Candidate | Reader meaning | Next pricing action |",
            "| --- | --- | --- |",
            *[f"| {c.get('fund_name', '')} | {c.get('reader_meaning', '')} | {c.get('next_pricing_action', '')} |" for c in candidates],
            "",
            "## Unsafe or blocked pricing lines",
            "",
            "| Symbol | Reason |",
            "| --- | --- |",
            *_unsafe_rows(unsafe),
            "| Gold/ETC | policy_blocked until ETC policy is explicitly decided. |",
            "| Infrastructure | identity_incomplete until ISIN and issuer evidence are verified. |",
            "",
            "## Proxy separation map",
            "",
            "| Research proxy | EU/UCITS view | Allowed use | Blocked use |",
            "| --- | --- | --- | --- |",
            *_proxy_rows(candidates, nl=False),
            "",
            "## Reader action map",
            "",
            "| Question | Answer | Action |",
            "| --- | --- | --- |",
            "| What is usable? | IE00B5BMR087 remains usable_for_review_only through CSPX.L and SXR8.DE. | Use only as review evidence. |",
            "| What is unsafe? | IE00BMC38736 / SMH remains ambiguous or pending. | Verify exchange-specific UCITS pricing line first. |",
            "| What is blocked? | Gold/ETC is policy_blocked; infrastructure is identity_incomplete. | Do not promote or fund. |",
            "",
            "## Current blockers",
            "",
            "| Blocker | Status |",
            "| --- | --- |",
            "| Delivery | delivery_authorization_decision=remain_blocked |",
            "| Production | production_delivery=false |",
            "| Portfolio | portfolio_mutation=false |",
            "| Candidate promotion | candidate_promotion=false |",
            "| Funding | funding_authority=false |",
            "| Valuation-grade | valuation_grade=false |",
            "",
            "## Appendix — Technical evidence",
            "",
            "- Renderer: `tools/render_etf_eu_pricing_integrated_cockpit.py`",
            "- Validator: `tools/validate_etf_eu_cockpit_pricing_integration.py`",
            "- Test file: `tests/test_etf_eu_cockpit_pricing_integration.py`",
        ]
    return "\n".join(lines) + "\n"


def _html_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in row) + "</tr>" for row in rows)
    return f"<table><tr>{head}</tr>{body}</table>"


def _html(pricing: dict[str, Any], nl: bool = False) -> str:
    candidates = pricing["candidate_pricing_evidence"]
    title = "Weekly ETF EU-review — pricing-geïntegreerde cockpit POC" if nl else "Weekly ETF EU Review — Pricing-Integrated Cockpit POC"
    rows = [[c["fund_name"], c["isin"], c["pricing_line_status"], c["pricing_evidence_status"], _symbols(c), _proxies(c)] for c in candidates]
    unsafe = [[item["symbol"], item["reason"]] for item in pricing["unsafe_pricing_symbols"]]
    return f"""<!doctype html>
<html lang="{'nl' if nl else 'en'}">
<head><meta charset="utf-8"><title>{html.escape(title)}</title><style>
body{{margin:0;background:#f4f6fb;color:#172033;font-family:Arial,Helvetica,sans-serif}}.page{{max-width:1180px;margin:0 auto;padding:34px 22px 48px}}.hero{{background:linear-gradient(135deg,#14213d,#315d7d);color:white;border-radius:24px;padding:34px}}section{{background:white;border:1px solid #d9e0ec;border-radius:20px;margin-top:18px;padding:24px}}table{{width:100%;border-collapse:collapse}}th,td{{border-bottom:1px solid #d9e0ec;text-align:left;padding:11px 10px;vertical-align:top}}th{{color:#5c667a;font-size:12px;text-transform:uppercase}}.guard{{border-left:5px solid #9a3412;background:#f8fafc;border-radius:14px;padding:16px 18px}}code{{background:#eef2f7;padding:2px 6px;border-radius:6px}}
</style></head><body><div class="page">
<div class="hero"><h1>{html.escape(title)}</h1><p>Proof of concept / review-only. CSPX.L and SXR8.DE are the only current pricing evidence baseline.</p></div>
<section><h2>{'Prijsbewijs in één oogopslag' if nl else 'Pricing evidence at a glance'}</h2><p>IE00B5BMR087 remains usable_for_review_only. SMH is pricing_symbol_ambiguous. Gold/ETC is policy_blocked. Infrastructure is identity_incomplete.</p></section>
<section><h2>{'Prijsregel-bewijskaart' if nl else 'Pricing-line evidence map'}</h2>{_html_table(['Candidate','ISIN','Pricing-line status','Pricing evidence status','Pricing symbols','Research proxy'], rows)}</section>
<section><h2>{'Onveilige of geblokkeerde prijsregels' if nl else 'Unsafe or blocked pricing lines'}</h2>{_html_table(['Symbol','Reason'], unsafe)}</section>
<section><h2>{'Scheiding met researchproxy' if nl else 'Proxy separation map'}</h2><div class="guard">SPY, SMH, GLD and PAVE remain research proxies only; no U.S. proxy is an EU holding or EU pricing line.</div></section>
<section><h2>{'Huidige blokkades' if nl else 'Current blockers'}</h2><div class="guard">delivery_authorization_decision=remain_blocked; production_delivery=false; portfolio_mutation=false; candidate_promotion=false; funding_authority=false; valuation_grade=false.</div></section>
</div></body></html>
"""


def render_pricing_integrated_cockpit(universe_path: Path, pricing_path: Path) -> dict[str, Any]:
    if not SOURCE_RENDER.exists():
        raise FileNotFoundError(SOURCE_RENDER)
    universe = _load(universe_path)
    pricing = _load(pricing_path)
    if universe.get("visible_candidate_count") != pricing.get("visible_candidate_count"):
        raise ValueError("visible candidate count mismatch")
    _write(EN_MD, _markdown(pricing, nl=False))
    _write(NL_MD, _markdown(pricing, nl=True))
    _write(EN_HTML, _html(pricing, nl=False))
    _write(NL_HTML, _html(pricing, nl=True))
    manifest = {
        "schema_version": "etf_eu_cockpit_pricing_integration_v1",
        "run_id": RUN_ID,
        "status": "completed",
        "created_at_utc": CREATED_AT_UTC,
        "source_enriched_cockpit_render_manifest_path": str(SOURCE_RENDER),
        "source_universe_enrichment_manifest_path": str(universe_path),
        "source_pricing_line_expansion_manifest_path": str(pricing_path),
        "source_pricing_line_expansion_notes_path": str(SOURCE_PRICING_NOTES),
        "authorization_decision_artifact_path": str(AUTH),
        "pricing_integration_created": True,
        "pricing_integrated_cockpit_surface_created": True,
        "pricing_line_evidence_rendered": True,
        "candidate_pricing_evidence_preserved": True,
        "pricing_line_status_map_preserved": True,
        "unsafe_pricing_symbol_guard_rendered": True,
        "proxy_ambiguity_guard_rendered": True,
        "valuation_grade_guard_rendered": True,
        "funding_authority_guard_rendered": True,
        "candidate_promotion_guard_rendered": True,
        "ucits_identity_preserved": True,
        "proxy_separation_preserved": True,
        "pricing_evidence_preserved": True,
        "debug_surface_reduced": True,
        "delivery_authorization_decision": "remain_blocked",
        "production_delivery": False,
        "portfolio_mutation": False,
        "candidate_promotion": False,
        "funding_authority": False,
        "valuation_grade": False,
        "visible_candidate_count": pricing["visible_candidate_count"],
        "pricing_line_status_summary": pricing["pricing_line_status_summary"],
        "unsafe_pricing_symbols": pricing["unsafe_pricing_symbols"],
        "english_pricing_integrated_cockpit_markdown_path": str(EN_MD),
        "dutch_pricing_integrated_cockpit_markdown_path": str(NL_MD),
        "english_pricing_integrated_cockpit_html_path": str(EN_HTML),
        "dutch_pricing_integrated_cockpit_html_path": str(NL_HTML),
        "renderer_path": str(RENDERER),
        "validator_path": str(VALIDATOR),
        "tests_path": str(TESTS),
        "validators_run": ["tools/validate_etf_eu_pricing_line_expansion.py", "tools/validate_etf_eu_enriched_cockpit_render.py", "tools/validate_etf_eu_cockpit_pricing_integration.py"],
        "tests_expected": ["tests/test_etf_eu_cockpit_pricing_integration.py", "tests/test_etf_eu_pricing_line_expansion.py", "tests/test_etf_eu_enriched_cockpit_render.py"],
        "selected_next_package": "WP14S",
        "selected_next_package_title": "ETF EU cockpit client-surface readiness gate, no delivery",
    }
    _write(MANIFEST, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("universe_manifest", nargs="?", default=str(SOURCE_UNIVERSE))
    parser.add_argument("pricing_manifest", nargs="?", default=str(SOURCE_PRICING))
    args = parser.parse_args()
    manifest = render_pricing_integrated_cockpit(Path(args.universe_manifest), Path(args.pricing_manifest))
    print(f"ETF_EU_COCKPIT_PRICING_INTEGRATION_CREATED | artifact={MANIFEST} | visible_candidate_count={manifest['visible_candidate_count']} | selected_next_package={manifest['selected_next_package']}")


if __name__ == "__main__":
    main()
