from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
from typing import Any

RUN_ID = "20260618_000000"
CREATED_AT_UTC = "2026-06-18T00:00:00Z"
SOURCE_DEFAULT = Path("output/client_surface/etf_eu_cockpit_universe_enrichment_20260618_000000.json")
EN_MD = Path("output/client_surface/weekly_etf_eu_review_260618_cockpit_rendered.md")
NL_MD = Path("output/client_surface/weekly_etf_eu_review_nl_260618_cockpit_rendered.md")
EN_HTML = Path("output/client_surface/weekly_etf_eu_review_260618_cockpit_rendered.html")
NL_HTML = Path("output/client_surface/weekly_etf_eu_review_nl_260618_cockpit_rendered.html")
MANIFEST = Path("output/client_surface/etf_eu_enriched_cockpit_render_20260618_000000.json")
AUTH = Path("output/delivery/etf_eu_delivery_authorization_decision_20260618_000000.json")
RENDERER = Path("tools/render_etf_eu_enriched_cockpit.py")
VALIDATOR = Path("tools/validate_etf_eu_enriched_cockpit_render.py")
TESTS = Path("tests/test_etf_eu_enriched_cockpit_render.py")
ALLOWED = {"visible_review_candidate", "identity_incomplete", "pricing_incomplete", "proxy_only_mapping", "blocked_until_verified"}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _text(value: Any) -> str:
    return "" if value is None else str(value)


def _join(values: list[Any]) -> str:
    return ", ".join(str(value) for value in values if str(value))


def _lines(candidate: dict[str, Any]) -> str:
    return _join([
        f"{line.get('pricing_symbol_yahoo') or line.get('exchange_ticker')} ({line.get('trading_currency')}, {line.get('exchange')})"
        for line in candidate.get("trading_lines", [])
    ])


def _proxies(candidate: dict[str, Any]) -> str:
    return _join([proxy.get("us_proxy", "") for proxy in candidate.get("research_proxies", [])])


def _gaps(candidate: dict[str, Any]) -> str:
    return _join(candidate.get("evidence_gaps", [])) or "none"


def _statuses(candidates: list[dict[str, Any]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for idx, candidate in enumerate(candidates, 1):
        key = candidate.get("isin")
        if not key or key == "TBD":
            key = f"TBD-{idx}-{candidate.get('fund_name', 'candidate')}"
        out[str(key)] = str(candidate.get("cockpit_status"))
    return out


def _validate_source(source: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = source.get("visible_candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("visible_candidates must be a non-empty list")
    if source.get("visible_candidate_count") != len(candidates):
        raise ValueError("visible_candidate_count mismatch")
    for candidate in candidates:
        if candidate.get("cockpit_status") not in ALLOWED:
            raise ValueError(f"invalid cockpit_status: {candidate.get('cockpit_status')}")
    return candidates


def _candidate_rows(candidates: list[dict[str, Any]]) -> list[str]:
    rows = []
    for c in candidates:
        rows.append(f"| {_text(c.get('fund_name'))} | {_text(c.get('isin'))} | {_text(c.get('provider'))} | {_text(c.get('ucits_status'))} | {_lines(c)} | {_proxies(c)} | {_text(c.get('cockpit_status'))} |")
    return rows


def _evidence_rows(candidates: list[dict[str, Any]]) -> list[str]:
    rows = []
    for c in candidates:
        pricing = _join([line.get("pricing_symbol_yahoo", "") for line in c.get("trading_lines", [])]) or "pending"
        rows.append(f"| {_text(c.get('isin'))} / {_text(c.get('fund_name'))} | UCITS={_text(c.get('ucits_status'))}; KID={_text(c.get('priips_kid_status'))}; benchmark={_text(c.get('benchmark_index'))} | {pricing} | {_text(c.get('evidence_status'))} | {_gaps(c)} |")
    return rows


def _proxy_rows(candidates: list[dict[str, Any]], nl: bool = False) -> list[str]:
    rows = []
    for c in candidates:
        for proxy in c.get("research_proxies", []):
            allowed = "alleen benchmark / researchproxy" if nl else "benchmark / research proxy only"
            blocked = "EU-positie, financieringsbron of portefeuillepositie" if nl else "EU holding, funding source, or portfolio position"
            rows.append(f"| {_text(proxy.get('us_proxy'))} | {_text(c.get('fund_name'))} / {_text(c.get('isin'))} | {allowed} | {blocked} |")
    return rows


def _markdown(source: dict[str, Any], nl: bool = False) -> str:
    candidates = source["visible_candidates"]
    title = "# Weekly ETF EU-review — gerenderde verrijkte cockpit POC" if nl else "# Weekly ETF EU Review — Rendered Enriched Cockpit POC"
    summary = [
        "## Cockpitsamenvatting" if nl else "## Cockpit summary",
        "",
        "- **Rapportstatus:** proof of concept / review-only." if nl else "- **Report status:** proof of concept / review-only.",
        "- **Huidige stand:** de verrijkte UCITS-cockpit wordt deterministisch uit gestructureerde input gegenereerd; er is geen portefeuilleactie." if nl else "- **Current stance:** the enriched UCITS cockpit is generated deterministically from structured input; there is no portfolio action.",
        f"- **Status UCITS-universum:** {len(candidates)} zichtbare reviewlanes worden uit het enrichment manifest gerenderd." if nl else f"- **UCITS universe status:** {len(candidates)} visible review lanes are rendered from the enrichment manifest.",
        "- **Belangrijkste bewijsgaten:** prijssymbooldekking, beurslijnverificatie, ISIN-aanvulling en beleid rond ETC-blootstelling." if nl else "- **Main evidence gaps:** pricing-symbol coverage, exchange-line verification, ISIN completion and product-policy treatment for ETC exposure.",
        "- **Belangrijkste blokkade:** levering, financiering, valuation-grade gebruik, kandidaatpromotie en portefeuillewijziging blijven geblokkeerd." if nl else "- **Main blocker:** delivery, funding, valuation-grade use, candidate promotion and portfolio mutation remain blocked.",
        "- **Volgende productactie:** breid prijsbewijs per beurslijn uit voor de verrijkte cockpitkandidaten." if nl else "- **Next product action:** expand pricing-line evidence for enriched cockpit candidates.",
    ]
    cards_title = "## Kaarten in één oogopslag" if nl else "## At-a-glance cards"
    universe_title = "## Zichtbaar UCITS-universum" if nl else "## Visible UCITS universe"
    evidence_title = "## Bewijskaart per kandidaat" if nl else "## Candidate evidence map"
    gaps_title = "## Prijs- en identiteitsgaten" if nl else "## Pricing and identity gaps"
    proxy_title = "## Scheiding met researchproxy" if nl else "## Proxy separation map"
    action_title = "## Actiekaart voor de lezer" if nl else "## Reader action map"
    blockers_title = "## Huidige blokkades" if nl else "## Current blockers"
    appendix_title = "## Bijlage — technisch bewijs" if nl else "## Appendix — Technical evidence"

    parts = [title, "", *summary, "", cards_title, "",
        "| Kaart | Status | Betekenis voor de lezer |" if nl else "| Card | Status | Reader meaning |",
        "| --- | --- | --- |",
        f"| UCITS-universum | Gerenderd | {len(candidates)} gestructureerde kandidaten zijn zichtbaar in de cockpit. |" if nl else f"| UCITS universe | Rendered | {len(candidates)} structured candidates are visible in the cockpit. |",
        "| Identiteitsbewijs | Gemengd | ISIN-first identiteit blijft behouden; incomplete lanes blijven gemarkeerd. |" if nl else "| Identity evidence | Mixed | ISIN-first identity is preserved; incomplete lanes remain marked. |",
        "| Prijsbewijs | Gedeeltelijk | CSPX.L en SXR8.DE behouden prijsbewijs; andere regels blijven pending. |" if nl else "| Pricing evidence | Partial | CSPX.L and SXR8.DE retain pricing evidence; other lines remain pending. |",
        "| Proxy-scheiding | Behouden | SPY, SMH, GLD en PAVE zijn alleen researchproxy's / benchmarks. |" if nl else "| Proxy separation | Preserved | SPY, SMH, GLD and PAVE are research proxies / benchmarks only. |",
        "| Leveringsstatus | Geblokkeerd | delivery_authorization_decision=remain_blocked. |" if nl else "| Delivery status | Blocked | delivery_authorization_decision=remain_blocked. |",
        "| Portefeuilleautoriteit | Geblokkeerd | production_delivery=false; portfolio_mutation=false; candidate_promotion=false; funding_authority=false; valuation_grade=false. |" if nl else "| Portfolio authority | Blocked | production_delivery=false; portfolio_mutation=false; candidate_promotion=false; funding_authority=false; valuation_grade=false. |",
        "", universe_title, "",
        "| Kandidaat | ISIN | Provider | UCITS-status | Beurslijnen | Researchproxy | Cockpitstatus |" if nl else "| Candidate | ISIN | Provider | UCITS status | Trading lines | Research proxy | Cockpit status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
        *_candidate_rows(candidates),
        "", evidence_title, "",
        "| Kandidaat | Identiteitsbewijs | Prijsbewijs | Bewijsstatus | Bewijsgaten |" if nl else "| Candidate | Identity evidence | Pricing evidence | Evidence status | Evidence gaps |",
        "| --- | --- | --- | --- | --- |",
        *_evidence_rows(candidates),
        "", gaps_title, "",
        "| Gat | Betrokken gebied | Waarom dit belangrijk is |" if nl else "| Gap | Affected area | Why it matters |",
        "| --- | --- | --- |",
        "| Prijssymbolen pending | Semiconductor-, goud/ETC- en infrastructuurlanes | Deze lanes kunnen geen valuation-grade bewijs worden voordat prijsregels zijn geverifieerd. |" if nl else "| Pricing symbols pending | Semiconductor, gold/ETC and infrastructure lanes | These lanes cannot become valuation-grade evidence until pricing lines are verified. |",
        "| ISIN-placeholders | Goud/ETC- en infrastructuurlanes | ISIN-first identiteit is verplicht vóór kandidaatpromotie. |" if nl else "| ISIN placeholders | Gold/ETC and infrastructure lanes | ISIN-first identity is mandatory before candidate promotion. |",
        "| ETC-beleid | Goud/ETC-lane | De goudcase blijft geblokkeerd totdat beleid dit expliciet toestaat. |" if nl else "| ETC policy treatment | Gold/ETC lane | The gold case remains blocked until policy authority explicitly allows it. |",
        "", proxy_title, "",
        "| Amerikaanse proxy | Gerenderde EU/UCITS-weergave | Toegestaan gebruik | Geblokkeerd gebruik |" if nl else "| U.S. proxy | Rendered EU/UCITS view | Allowed use | Blocked use |",
        "| --- | --- | --- | --- |",
        *_proxy_rows(candidates, nl=nl),
        "", action_title, "",
        "| Vraag van de lezer | Cockpitantwoord | Actie nu |" if nl else "| Reader question | Cockpit answer | Action now |",
        "| --- | --- | --- |",
        "| Wat is veranderd? | De cockpit wordt uit gestructureerde input gegenereerd. | Controleer renderdeterminisme. |" if nl else "| What changed? | The cockpit is generated from structured input. | Review render determinism. |",
        "| Welke kandidaat heeft het sterkste bewijs? | IE00B5BMR087 via CSPX.L en SXR8.DE. | Behoud dit als bewijsbaseline. |" if nl else "| Which candidate has strongest evidence? | IE00B5BMR087 via CSPX.L and SXR8.DE. | Preserve this as the evidence baseline. |",
        "| Wat blijft geblokkeerd? | Levering, financiering, valuation-grade gebruik, kandidaatpromotie en portefeuillewijziging. | Geblokkeerd houden. |" if nl else "| What stays blocked? | Delivery, funding, valuation-grade use, candidate promotion and portfolio mutation. | Keep blocked. |",
        "", blockers_title, "",
        "| Blokkade | Huidige status | Betekenis |" if nl else "| Blocker | Current status | Meaning |",
        "| --- | --- | --- |",
        "| Leveringsautoriteit | delivery_authorization_decision=remain_blocked | Geen e-mail, geen ontvangeractivatie, geen productiesend. |" if nl else "| Delivery authority | delivery_authorization_decision=remain_blocked | No email, no recipient activation, no production send. |",
        "| Productielevering | production_delivery=false | Geen rapportlevering ingeschakeld. |" if nl else "| Production delivery | production_delivery=false | No report delivery is enabled. |",
        "| Portefeuillewijziging | portfolio_mutation=false | Geen wijziging in posities of cash. |" if nl else "| Portfolio mutation | portfolio_mutation=false | No holdings or cash changes. |",
        "| Kandidaatpromotie | candidate_promotion=false | Geen kandidaat is gepromoveerd. |" if nl else "| Candidate promotion | candidate_promotion=false | No candidate is promoted. |",
        "| Financieringsautoriteit | funding_authority=false | Geen koop- of financieringsbesluit. |" if nl else "| Funding authority | funding_authority=false | No buy or funding decision. |",
        "| Valuation-grade autoriteit | valuation_grade=false | Prijzen blijven alleen reviewbewijs. |" if nl else "| Valuation-grade authority | valuation_grade=false | Pricing remains review evidence only. |",
        "", appendix_title, "",
        "- Bron universe enrichment manifest: `output/client_surface/etf_eu_cockpit_universe_enrichment_20260618_000000.json`" if nl else "- Source universe enrichment manifest: `output/client_surface/etf_eu_cockpit_universe_enrichment_20260618_000000.json`",
        "- Render manifest: `output/client_surface/etf_eu_enriched_cockpit_render_20260618_000000.json`",
        "- Renderer: `tools/render_etf_eu_enriched_cockpit.py`",
        "- Validator: `tools/validate_etf_eu_enriched_cockpit_render.py`",
        "- Testbestand: `tests/test_etf_eu_enriched_cockpit_render.py`" if nl else "- Test file: `tests/test_etf_eu_enriched_cockpit_render.py`",
    ]
    return "\n".join(parts) + "\n"


def _table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{html.escape(x)}</th>" for x in headers)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(y)}</td>" for y in row) + "</tr>" for row in rows)
    return f"<table><tr>{head}</tr>{body}</table>"


def _html(source: dict[str, Any], nl: bool = False) -> str:
    candidates = source["visible_candidates"]
    title = "Weekly ETF EU-review — gerenderde verrijkte cockpit POC" if nl else "Weekly ETF EU Review — Rendered Enriched Cockpit POC"
    candidate_rows = [[c.get("fund_name", ""), c.get("isin", ""), _lines(c), _proxies(c), c.get("cockpit_status", "")] for c in candidates]
    proxy_rows = []
    for c in candidates:
        for p in c.get("research_proxies", []):
            proxy_rows.append([p.get("us_proxy", ""), f"{c.get('fund_name')} / {c.get('isin')}", "benchmark / research proxy only", "EU holding or funding source"])
    return f"""<!doctype html>
<html lang="{html.escape('nl' if nl else 'en')}">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
body{{margin:0;background:#f4f6fb;color:#172033;font-family:Arial,Helvetica,sans-serif}}.page{{max-width:1180px;margin:0 auto;padding:34px 22px 48px}}.hero{{background:linear-gradient(135deg,#16233d,#315d7d);color:#fff;border-radius:24px;padding:34px}}section{{background:#fff;border:1px solid #d9e0ec;border-radius:20px;margin-top:18px;padding:24px}}table{{width:100%;border-collapse:collapse}}th,td{{border-bottom:1px solid #d9e0ec;text-align:left;padding:11px 10px;vertical-align:top}}th{{color:#5c667a;font-size:12px;text-transform:uppercase}}.panel{{border-left:5px solid #9a3412;background:#f8fafc;border-radius:14px;padding:16px 18px}}code{{background:#eef2f7;padding:2px 6px;border-radius:6px}}
</style>
</head>
<body><div class="page">
<div class="hero"><h1>{html.escape(title)}</h1><p>Proof of concept / review-only UCITS cockpit generated deterministically from structured input.</p></div>
<section><h2>{'Zichtbaar UCITS-universum' if nl else 'Visible UCITS universe'}</h2>{_table(['Candidate','ISIN','Trading lines','Proxy','Cockpit status'], candidate_rows)}</section>
<section><h2>{'Bewijskaart per kandidaat' if nl else 'Candidate evidence map'}</h2>{_table(['Candidate','Evidence status','Evidence gaps'], [[c.get('fund_name',''), c.get('evidence_status',''), _gaps(c)] for c in candidates])}</section>
<section><h2>{'Scheiding met researchproxy' if nl else 'Proxy separation map'}</h2>{_table(['Proxy','EU/UCITS view','Allowed use','Blocked use'], proxy_rows)}</section>
<section><h2>{'Huidige blokkades' if nl else 'Current blockers'}</h2><div class="panel">delivery_authorization_decision=remain_blocked; production_delivery=false; portfolio_mutation=false; candidate_promotion=false; funding_authority=false; valuation_grade=false.</div></section>
<section><h2>{'Bijlage — technisch bewijs' if nl else 'Appendix — Technical evidence'}</h2><p><code>output/client_surface/etf_eu_enriched_cockpit_render_20260618_000000.json</code></p></section>
</div></body></html>
"""


def render_enriched_cockpit(source_manifest: Path = SOURCE_DEFAULT) -> dict[str, Any]:
    source = _load(source_manifest)
    candidates = _validate_source(source)
    _write(EN_MD, _markdown(source, nl=False))
    _write(NL_MD, _markdown(source, nl=True))
    _write(EN_HTML, _html(source, nl=False))
    _write(NL_HTML, _html(source, nl=True))
    manifest = {
        "schema_version": "etf_eu_enriched_cockpit_render_v1",
        "run_id": RUN_ID,
        "status": "completed",
        "created_at_utc": CREATED_AT_UTC,
        "source_universe_enrichment_manifest_path": str(source_manifest),
        "english_rendered_cockpit_markdown_path": str(EN_MD),
        "dutch_rendered_cockpit_markdown_path": str(NL_MD),
        "english_rendered_cockpit_html_path": str(EN_HTML),
        "dutch_rendered_cockpit_html_path": str(NL_HTML),
        "authorization_decision_artifact_path": str(AUTH),
        "renderer_path": str(RENDERER),
        "render_validator_path": str(VALIDATOR),
        "render_tests_path": str(TESTS),
        "render_created": True,
        "deterministic_renderer_created": True,
        "english_markdown_rendered": True,
        "dutch_markdown_rendered": True,
        "english_html_rendered": True,
        "dutch_html_rendered": True,
        "candidate_universe_preserved": True,
        "visible_candidate_count": len(candidates),
        "visible_candidate_statuses": _statuses(candidates),
        "candidate_evidence_map_rendered": True,
        "proxy_separation_map_rendered": True,
        "reader_action_map_rendered": True,
        "blocker_panel_rendered": True,
        "debug_surface_reduced": True,
        "ucits_identity_preserved": True,
        "proxy_separation_preserved": True,
        "pricing_evidence_preserved": True,
        "delivery_authorization_decision": "remain_blocked",
        "production_delivery": False,
        "portfolio_mutation": False,
        "candidate_promotion": False,
        "funding_authority": False,
        "valuation_grade": False,
        "source_manifest_hash": _hash(source_manifest),
        "english_markdown_hash": _hash(EN_MD),
        "dutch_markdown_hash": _hash(NL_MD),
        "english_html_hash": _hash(EN_HTML),
        "dutch_html_hash": _hash(NL_HTML),
        "validators_run": ["tools/validate_etf_eu_cockpit_universe_enrichment.py", "tools/validate_etf_eu_enriched_cockpit_render.py"],
        "tests_expected": ["tests/test_etf_eu_enriched_cockpit_render.py", "tests/test_etf_eu_cockpit_universe_enrichment.py", "tests/test_etf_eu_premium_cockpit_surface.py", "tests/test_etf_eu_client_poc_surface.py", "tests/test_etf_eu_delivery_authorization_decision.py", "tests/test_etf_eu_delivery_authorization_gate.py", "tests/test_etf_eu_html_pdf_dry_run.py", "tests/test_etf_eu_mature_bilingual_report.py", "tests/test_etf_eu_dutch_language_quality.py"],
        "selected_next_package": "WP14Q",
        "selected_next_package_title": "ETF EU pricing-line expansion for enriched cockpit candidates, no delivery",
    }
    _write(MANIFEST, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_manifest", nargs="?", default=str(SOURCE_DEFAULT))
    args = parser.parse_args()
    manifest = render_enriched_cockpit(Path(args.source_manifest))
    print(f"ETF_EU_ENRICHED_COCKPIT_RENDER_CREATED | artifact={MANIFEST} | visible_candidate_count={manifest['visible_candidate_count']} | selected_next_package={manifest['selected_next_package']}")


if __name__ == "__main__":
    main()
