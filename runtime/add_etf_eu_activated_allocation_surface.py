from __future__ import annotations

import argparse
import json
import re
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


def euro(value: Any, language: str, decimals: int = 2) -> str:
    amount = float(value or 0)
    rendered = f"{amount:,.{decimals}f}"
    if language == "nl":
        rendered = rendered.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"€ {rendered}"


def pct(value: Any, language: str) -> str:
    rendered = f"{float(value or 0):.2f}%"
    return rendered.replace(".", ",") if language == "nl" else rendered


def normalize_ticker(value: Any) -> str:
    ticker = str(value or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def replace_visible_text(soup: BeautifulSoup, language: str) -> None:
    stale_regime = (
        "The regime changed versus the prior review from Risk-on groei to Policy transition / mixed regime; market breadth is improving and cross-asset confirmation is mixed."
        if language == "nl"
        else "The regime changed versus the prior review from Risk-on growth to Policy transition / mixed regime; market breadth is improving and cross-asset confirmation is mixed."
    )
    current_regime = (
        "Het regime-label is historische strategiecontext uit de donorbeoordeling van 29 juli. Fed- en ECB-besluiten zijn actueel geverifieerd; er is geen nieuwe EU-regimeberekening uitgevoerd."
        if language == "nl"
        else "The regime label is historical strategy context from the 29 July donor review. Fed and ECB decisions are current; no new EU regime calculation was performed."
    )
    replacements = (
        {
            "Actuele uitkomst: officiële portefeuille ongewijzigd; shadow allocator stelt uitbreiding naar vijf posities voor.": "Actuele uitkomst: L0CK is toegevoegd aan de modelportefeuille; VVSM blijft gemonitord en niet gefinancierd.",
            "VVSM en L0CK zijn prijs- en liquiditeitsgeschikt in de shadow allocator; officiële activering blijft geblokkeerd.": "L0CK is als vierde modelpositie geactiveerd. VVSM heeft actuele prijs- en liquiditeitsinformatie, maar wordt niet actueel gepromoveerd door de donorstrategie.",
            "Shadow-uitbreidingsvoorstel": "Modelstatus",
            "shadow allocator": "modelallocator",
            "shadow proposals": "modelvoorstellen",
            "shadow proposal": "modelvoorstel",
        }
        if language == "nl"
        else {
            "Current outcome: official portfolio unchanged; the shadow allocator proposes expansion to five positions.": "Current outcome: L0CK has been added to the model portfolio; VVSM remains monitored and unfunded.",
            "VVSM and L0CK pass price and liquidity gates in the shadow allocator; official activation remains blocked.": "L0CK has been activated as the fourth model position. VVSM has current price and liquidity evidence but is not currently promoted by the donor strategy.",
            "Shadow expansion proposal": "Model status",
            "the shadow allocator": "the model allocator",
            "shadow proposals": "model proposals",
            "shadow proposal": "model proposal",
        }
    )
    for node in list(soup.find_all(string=True)):
        if not isinstance(node, NavigableString):
            continue
        original = str(node)
        updated = original.replace(stale_regime, current_regime)
        updated = re.sub(r"\bLOCK\b", "L0CK", updated)
        for old, new in replacements.items():
            updated = updated.replace(old, new)
        if updated != original:
            node.replace_with(updated)


def compact_opportunity_table(soup: BeautifulSoup, language: str) -> None:
    table = soup.find("table", class_="promoted-mapping-table")
    if not isinstance(table, Tag):
        raise RuntimeError("Promoted mapping table missing")
    header_cells = table.select("thead tr th")
    if len(header_cells) >= 2:
        header_cells[-2].string = "Slot / bewijs" if language == "nl" else "Close / evidence"
        header_cells[-1].decompose()
    for row in table.select("tbody > tr"):
        cells = row.find_all("td", recursive=False)
        if len(cells) < 2:
            continue
        price_text = cells[-2].get_text(" ", strip=True)
        evidence_text = cells[-1].get_text(" ", strip=True)
        for old, new in (
            (("Börse + Yahoo akkoord", "2-bron akkoord"), ("Enkele bron; alleen monitoring", "1 bron · monitoring"))
            if language == "nl"
            else (("Börse + Yahoo agreement", "2-source agreement"), ("Single source; monitoring only", "1 source · monitoring"))
        ):
            evidence_text = evidence_text.replace(old, new)
        combined = cells[-2]
        combined.clear()
        price = soup.new_tag("div", attrs={"class": "compact-close-price"})
        price.string = price_text
        proof = soup.new_tag("div", attrs={"class": "compact-close-proof"})
        proof.string = evidence_text
        combined.append(price)
        combined.append(proof)
        cells[-1].decompose()


def activated_status_box(soup: BeautifulSoup, state: dict[str, Any], language: str) -> None:
    section = soup.find("section", id="section-2")
    if not isinstance(section, Tag):
        raise RuntimeError("Section 2 missing")
    portfolio = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    positions = {
        normalize_ticker(row.get("ticker") or row.get("exchange_ticker")): row
        for row in portfolio.get("positions") or []
        if isinstance(row, dict)
    }
    l0ck = positions.get("L0CK")
    vvsm = next(
        (
            row
            for row in state.get("stage_1_review_candidates") or []
            if isinstance(row, dict) and normalize_ticker(row.get("exchange_symbol")) == "VVSM"
        ),
        {},
    )
    if l0ck is None:
        raise RuntimeError("Activated L0CK position missing from final state")

    box = soup.new_tag("div", attrs={"class": "activated-allocation-status"})
    heading = soup.new_tag("strong")
    heading.string = (
        "Modelportefeuille uitgebreid naar vier posities"
        if language == "nl"
        else "Model portfolio expanded to four positions"
    )
    box.append(heading)

    l0ck_line = soup.new_tag("div", attrs={"class": "activated-allocation-line"})
    l0ck_price = l0ck.get("current_price_eur") or l0ck.get("current_price_local")
    if language == "nl":
        l0ck_line.string = (
            f"L0CK: {int(float(l0ck.get('shares') or 0))} stuks · slot {euro(l0ck_price, language, 4)} · "
            f"gewicht {pct(l0ck.get('current_weight_pct') or l0ck.get('weight_pct'), language)} · modelpositie actief."
        )
    else:
        l0ck_line.string = (
            f"L0CK: {int(float(l0ck.get('shares') or 0))} shares · close {euro(l0ck_price, language, 4)} · "
            f"weight {pct(l0ck.get('current_weight_pct') or l0ck.get('weight_pct'), language)} · model position active."
        )
    box.append(l0ck_line)

    vvsm_line = soup.new_tag("div", attrs={"class": "activated-allocation-line"})
    vvsm_price = vvsm.get("current_price_eur")
    if language == "nl":
        vvsm_line.string = (
            f"VVSM: slot {euro(vvsm_price, language)} · niet gefinancierd; blijft op de watchlist omdat de donorstrategie deze lijn niet actueel promoveert."
        )
    else:
        vvsm_line.string = (
            f"VVSM: close {euro(vvsm_price, language)} · unfunded; remains on the watchlist because the donor strategy does not currently promote this line."
        )
    box.append(vvsm_line)

    footer = soup.new_tag("div", attrs={"class": "activated-allocation-footer"})
    nav = portfolio.get("nav_eur")
    cash = portfolio.get("cash_eur")
    cash_weight = float(cash or 0) / float(nav or 1) * 100.0
    if language == "nl":
        footer.string = (
            f"Actuele modelstatus: {len(positions)} posities · NAV {euro(nav, language)} · cash {euro(cash, language)} "
            f"({pct(cash_weight, language)}). Geen echte brokerorder uitgevoerd."
        )
    else:
        footer.string = (
            f"Current model status: {len(positions)} positions · NAV {euro(nav, language)} · cash {euro(cash, language)} "
            f"({pct(cash_weight, language)}). No real broker order was placed."
        )
    box.append(footer)

    existing = section.find(class_="shadow-expansion-proposal") or section.find(class_="model-expansion-proposal")
    if isinstance(existing, Tag):
        existing.replace_with(box)
    else:
        section.append(box)


def add_style(soup: BeautifulSoup) -> None:
    style = soup.new_tag("style")
    style.string = """
.activated-allocation-status{margin:.3rem 0 0;padding:.42rem .55rem;border:1px solid #84a796;border-radius:7px;background:#f1f7f3;font-size:7.45pt;line-height:1.18;break-inside:avoid}
.activated-allocation-line{margin:.14rem 0;font-variant-numeric:tabular-nums}
.activated-allocation-footer{margin-top:.2rem;font-weight:600}
.promoted-mapping-table{font-size:6.55pt!important;line-height:1.08!important;table-layout:fixed!important}
.promoted-mapping-table th,.promoted-mapping-table td{padding:.12rem .16rem!important;vertical-align:top!important;overflow-wrap:anywhere}
.promoted-mapping-table th:last-child,.promoted-mapping-table td:last-child{width:15.5%!important;white-space:normal!important}
.compact-close-price{font-weight:700;white-space:nowrap}.compact-close-proof{font-size:6.05pt;line-height:1.03;margin-top:.05rem}
.current-close-note{font-size:7.25pt!important;padding:.28rem .42rem!important;margin:.25rem 0 .15rem!important;line-height:1.12!important}
.current-close-watch{font-size:7.2pt!important;line-height:1.12!important;margin:.2rem 0 0!important}
"""
    soup.head.append(style)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--pricing", type=Path, required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--state", type=Path, default=None)
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

    state_path = args.state
    if state_path is None:
        matches = sorted(Path("output/routine_preview").glob("etf_eu_production_convergence_state_*.json"))
        if not matches:
            raise RuntimeError("Final convergence state missing")
        state_path = matches[-1]
    state = load_object(state_path)
    manifest = load_object(args.manifest)
    for language in ("nl", "en"):
        record = manifest.get("languages", {}).get(language, {})
        html_path = Path(record["html"])
        pdf_path = Path(record["pdf"])
        soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
        replace_visible_text(soup, language)
        compact_opportunity_table(soup, language)
        activated_status_box(soup, state, language)
        add_style(soup)
        html_path.write_text(str(soup), encoding="utf-8")
        HTML(filename=str(html_path), base_url=str(html_path.parent.resolve())).write_pdf(str(pdf_path))
        record["activated_allocation_surface"] = "l0ck_funded_vvsm_monitored_v1"
    manifest["activated_allocation_surface"] = {
        "applied": True,
        "funded_stage1_tickers": ["L0CK"],
        "remaining_monitored_tickers": ["VVSM"],
        "current_position_count": 4,
        "portfolio_mutation_this_report_run": False,
        "real_broker_execution": False,
        "production_delivery_authority": False,
    }
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("ETF_EU_ACTIVATED_ALLOCATION_SURFACE_OK | funded=L0CK | monitored=VVSM | positions=4")


if __name__ == "__main__":
    main()
