from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, NavigableString, Tag
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def euro(value: Any, lang: str, decimals: int = 2) -> str:
    amount = float(value or 0)
    rendered = f"{amount:,.{decimals}f}"
    if lang == "nl":
        rendered = rendered.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"€ {rendered}"


def pct(value: Any, lang: str) -> str:
    rendered = f"{float(value or 0):.2f}%"
    return rendered.replace(".", ",") if lang == "nl" else rendered


def preferred_variant(allocator: dict[str, Any]) -> dict[str, Any]:
    preferred = str(allocator.get("preferred_shadow_variant") or "staged_policy_driven_v1")
    for variant in allocator.get("variants") or []:
        if isinstance(variant, dict) and variant.get("variant_id") == preferred:
            return variant
    raise RuntimeError(f"Preferred variant missing: {preferred}")


def selected_rows(variant: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for row in variant.get("allocation_rows") or []
        if isinstance(row, dict) and row.get("selected") is True and row.get("eligible") is True
    ]


def replace_text(soup: BeautifulSoup, replacements: dict[str, str]) -> None:
    for node in list(soup.find_all(string=True)):
        if not isinstance(node, NavigableString):
            continue
        text = str(node)
        updated = text
        for old, new in replacements.items():
            updated = updated.replace(old, new)
        if updated != text:
            node.replace_with(updated)


def add_proposal_surface(
    soup: BeautifulSoup,
    *,
    variant: dict[str, Any],
    rows: list[dict[str, Any]],
    lang: str,
) -> None:
    section = soup.find("section", id="section-2")
    if not isinstance(section, Tag):
        raise RuntimeError("Section 2 missing")
    summary = variant.get("summary") or {}
    box = soup.new_tag("div", attrs={"class": "shadow-expansion-proposal"})
    title = soup.new_tag("strong")
    title.string = "Shadow-uitbreidingsvoorstel - niet uitgevoerd" if lang == "nl" else "Shadow expansion proposal - not executed"
    box.append(title)
    intro = soup.new_tag("p")
    intro.string = (
        "Actuele slotkoers- en liquiditeitspoorten zijn geslaagd voor de twee fase-1-kandidaten. De officiële portefeuille blijft ongewijzigd totdat quote-, donor- en expliciete activeringspoorten slagen."
        if lang == "nl"
        else "Current close and liquidity gates passed for both Stage-1 candidates. The official portfolio remains unchanged until quote, donor and explicit activation gates pass."
    )
    box.append(intro)
    table = soup.new_tag("table", attrs={"class": "shadow-proposal-table"})
    thead = soup.new_tag("thead")
    tr = soup.new_tag("tr")
    headings = (
        ["ETF", "Voorstel", "Koers", "Doelgewicht", "Brutowaarde", "Status"]
        if lang == "nl"
        else ["ETF", "Proposal", "Close", "Target weight", "Gross value", "Status"]
    )
    for heading in headings:
        th = soup.new_tag("th")
        th.string = heading
        tr.append(th)
    thead.append(tr)
    table.append(thead)
    tbody = soup.new_tag("tbody")
    for row in rows:
        candidate = row.get("candidate") or {}
        order = row.get("order") or {}
        ticker = "L0CK" if candidate.get("ticker") == "LOCK" else str(candidate.get("ticker") or "—")
        values = [
            ticker,
            (f"Koop {int(order.get('target_shares') or 0)} stuks" if lang == "nl" else f"Buy {int(order.get('target_shares') or 0)} shares"),
            euro(candidate.get("price_eur"), lang, 4 if float(candidate.get("price_eur") or 0) < 20 else 2),
            pct(row.get("variant_target_weight_pct"), lang),
            euro(order.get("gross_trade_value_eur"), lang),
            ("Niet geactiveerd / niet uitgevoerd" if lang == "nl" else "Not activated / not executed"),
        ]
        tr = soup.new_tag("tr")
        for value in values:
            td = soup.new_tag("td")
            td.string = value
            tr.append(td)
        tbody.append(tr)
    table.append(tbody)
    box.append(table)
    footer = soup.new_tag("p", attrs={"class": "shadow-proposal-summary"})
    footer.string = (
        f"Projectie: {int(summary.get('position_count') or 0)} posities; cash {euro(summary.get('projected_cash_eur'), lang)} ({pct(summary.get('projected_cash_weight_pct'), lang)}); brutoturnover {pct(summary.get('gross_turnover_pct_nav'), lang)}. Geen brokeruitvoering en geen mutatie van officiële stukken of cash."
        if lang == "nl"
        else f"Projection: {int(summary.get('position_count') or 0)} positions; cash {euro(summary.get('projected_cash_eur'), lang)} ({pct(summary.get('projected_cash_weight_pct'), lang)}); gross turnover {pct(summary.get('gross_turnover_pct_nav'), lang)}. No broker execution and no mutation of official shares or cash."
    )
    box.append(footer)
    existing = section.find(class_="shadow-expansion-proposal")
    if isinstance(existing, Tag):
        existing.replace_with(box)
    else:
        section.append(box)


def add_style(soup: BeautifulSoup) -> None:
    style = soup.new_tag("style")
    style.string = """
.shadow-expansion-proposal{margin:.45rem 0 0;padding:.55rem .65rem;border:1px solid #9fb6c7;border-radius:7px;background:#f3f7fa;font-size:8.1pt;line-height:1.25;break-inside:avoid}
.shadow-expansion-proposal p{margin:.25rem 0}
.shadow-proposal-table{width:100%;border-collapse:collapse;margin:.35rem 0;font-size:7.7pt}
.shadow-proposal-table th,.shadow-proposal-table td{border:1px solid #ccd6df;padding:.22rem .28rem;vertical-align:top}
.shadow-proposal-table th{background:#e7eef3}
.shadow-proposal-summary{font-weight:600}
"""
    soup.head.append(style)


def patch_language(
    html_path: Path,
    pdf_path: Path,
    *,
    variant: dict[str, Any],
    rows: list[dict[str, Any]],
    lang: str,
) -> None:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    add_style(soup)
    replacements = (
        {
            "nieuwe inzet blijft geblokkeerd totdat actuele markt- en donorpoorten slagen": "nieuwe inzet is technisch voorbereid, maar blijft geblokkeerd totdat quote-, donor- en expliciete activeringspoorten slagen",
            "Actuele uitkomst: geen wijziging; geblokkeerde ruimte blijft cash.": "Actuele uitkomst: officiële portefeuille ongewijzigd; shadow allocator stelt uitbreiding naar vijf posities voor.",
            "VVSM niet actueel gepromoveerd; L0CK gepromoveerd maar geblokkeerd.": "VVSM en L0CK zijn prijs- en liquiditeitsgeschikt in de shadow allocator; officiële activering blijft geblokkeerd.",
            "Actueel gepromoveerd, maar actuele bewijs- en donorpoorten slagen niet.": "Actueel gepromoveerd; prijs- en liquiditeitspoorten slagen. Uitvoering blijft geblokkeerd door quote-, donor- en activeringsbevoegdheid.",
            "Activering blijft geblokkeerd: actuele afgeronde Xetra-slotkoers ontbreekt; geaccepteerde 20-daagse liquiditeitsmeting ontbreekt; timestamped bied-, laat- en quote-sizebewijs ontbreekt; de donor geeft geen nieuwe kooprichting.": "Actuele Xetra-slotkoers en 20-daagse liquiditeit zijn bevestigd. Uitvoering blijft geblokkeerd: timestamped bied-, laat- en quote-sizebewijs ontbreekt; de donor geeft geen nieuwe kooprichting; expliciete modelactivatie ontbreekt.",
            "actuele prijsbasis ontbreekt": "actuele prijs is beschikbaar, maar de uitvoerings- of beleidsset blijft onvolledig",
        }
        if lang == "nl"
        else {
            "new deployment remains blocked until current market and donor gates pass": "new deployment is technically prepared but remains blocked until quote, donor and explicit activation gates pass",
            "Current outcome: no change; blocked capacity remains cash.": "Current outcome: official portfolio unchanged; the shadow allocator proposes expansion to five positions.",
            "VVSM is not currently promoted; L0CK is promoted but blocked.": "VVSM and L0CK pass price and liquidity gates in the shadow allocator; official activation remains blocked.",
            "Currently promoted, but current evidence and donor gates do not pass.": "Currently promoted; price and liquidity gates pass. Execution remains blocked by quote, donor and activation authority.",
            "Activation remains blocked: accepted current completed Xetra close is unavailable; accepted 20-session liquidity measurement is unavailable; timestamped bid, ask and quote-size evidence is unavailable; the donor does not emit a fresh-add direction.": "The current Xetra close and 20-session liquidity measurement are confirmed. Execution remains blocked: timestamped bid, ask and quote-size evidence is unavailable; the donor does not emit a fresh-add direction; explicit model activation is absent.",
            "current price basis is unavailable": "a current price is available, but the execution or policy set remains incomplete",
        }
    )
    replace_text(soup, replacements)
    add_proposal_surface(soup, variant=variant, rows=rows, lang=lang)
    html_path.write_text(str(soup), encoding="utf-8")
    HTML(filename=str(html_path), base_url=str(html_path.parent.resolve())).write_pdf(str(pdf_path))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--pricing", type=Path, required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--allocator", type=Path, default=Path("output/routine_preview/sync/etf_eu_target_allocator_shadow.json"))
    args = parser.parse_args()

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "runtime/add_etf_eu_current_close_monitor.py"),
            str(args.manifest),
            "--pricing",
            str(args.pricing),
            "--report-date",
            args.report_date,
        ],
        cwd=str(ROOT),
        check=True,
    )

    manifest = load_object(args.manifest)
    allocator = load_object(args.allocator)
    variant = preferred_variant(allocator)
    rows = selected_rows(variant)
    if len(rows) < 2:
        raise RuntimeError("Expected two selected Stage-1 shadow proposals")
    for lang in ("nl", "en"):
        record = manifest.get("languages", {}).get(lang, {})
        patch_language(
            Path(record["html"]),
            Path(record["pdf"]),
            variant=variant,
            rows=rows,
            lang=lang,
        )
        record["expanded_shadow_allocation_surface"] = "evidence_qualified_unexecuted_v1"
    manifest["expanded_shadow_allocation_surface"] = {
        "applied": True,
        "variant_id": variant.get("variant_id"),
        "selected_exposure_count": len(rows),
        "proposed_position_count": variant.get("summary", {}).get("position_count"),
        "portfolio_mutation": False,
        "real_broker_execution": False,
        "activation_authority": False,
    }
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "ETF_EU_EXPANDED_ALLOCATION_MONITOR_OK"
        f" | proposals={len(rows)}"
        f" | positions={variant.get('summary', {}).get('position_count')}"
        f" | official_state_applied=false"
    )


if __name__ == "__main__":
    main()
