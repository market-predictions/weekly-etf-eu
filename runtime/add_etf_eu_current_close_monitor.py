from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from weasyprint import HTML

PROMOTED_TICKERS = {"L0CK", "CBUF", "ISAE", "XMLC", "IQQQ", "DFEN"}
WATCHLIST_TICKER = "VVSM"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected object: {path}")
    return payload


def format_price(value: Any, currency: str, language: str) -> str:
    if value is None:
        return "Niet beschikbaar" if language == "nl" else "Unavailable"
    amount = float(value)
    if currency == "EUR":
        rendered = f"€{amount:,.4f}" if amount < 20 else f"€{amount:,.2f}"
    else:
        rendered = f"{currency} {amount:,.2f}"
    if language == "nl":
        rendered = rendered.replace(",", "X").replace(".", ",").replace("X", ".")
    return rendered


def status_text(row: dict[str, Any], language: str) -> str:
    status = str(row.get("source_agreement_status") or "")
    providers = row.get("agreeing_providers") or []
    if status == "qualified_development_consensus":
        return "Börse + Yahoo akkoord" if language == "nl" else "Börse + Yahoo agreement"
    if providers:
        return "Enkele bron; alleen monitoring" if language == "nl" else "Single source; monitoring only"
    return "Geen bruikbare slotkoers" if language == "nl" else "No usable close"


def add_style(soup: BeautifulSoup) -> None:
    style = soup.new_tag("style")
    style.string = """
.current-close-note{margin:.45rem 0 .3rem;padding:.45rem .6rem;border:1px solid #d8dee8;border-radius:6px;font-size:8.1pt;line-height:1.25;background:#f8fafc}
.current-close-watch{margin:.35rem 0 0;font-size:8.1pt;line-height:1.25}
.promoted-mapping-table .current-close-cell{white-space:nowrap;font-variant-numeric:tabular-nums}
"""
    soup.head.append(style)


def patch_language(html_path: Path, pdf_path: Path, rows: dict[str, dict[str, Any]], language: str, report_date: str) -> None:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    add_style(soup)
    section = soup.find("section", id="section-4")
    if section is None:
        raise RuntimeError(f"Section 4 missing: {html_path}")
    table = section.find("table", class_="promoted-mapping-table")
    if table is None:
        raise RuntimeError(f"Promoted mapping table missing: {html_path}")
    header = table.find("thead").find("tr")
    for text in (("Slotkoers", "Datum / bewijs") if language == "nl" else ("Close", "Date / evidence")):
        cell = soup.new_tag("th")
        cell.string = text
        header.append(cell)
    seen: set[str] = set()
    for tr in table.find("tbody").find_all("tr", recursive=False):
        candidate = tr.find(attrs={"data-ticker": True})
        ticker = str(candidate.get("data-ticker") if candidate else "").upper()
        if ticker == "LOCK":
            ticker = "L0CK"
        row = rows.get(ticker)
        price_cell = soup.new_tag("td", attrs={"class": "current-close-cell"})
        evidence_cell = soup.new_tag("td")
        if row:
            price_cell.string = format_price(row.get("close_price"), str(row.get("currency") or ""), language)
            evidence_cell.string = f"{row.get('close_date') or '—'} · {status_text(row, language)}"
            seen.add(ticker)
        else:
            price_cell.string = "—"
            evidence_cell.string = "Niet geprijsd" if language == "nl" else "Unpriced"
        tr.append(price_cell)
        tr.append(evidence_cell)
    note = soup.new_tag("div", attrs={"class": "current-close-note"})
    note.string = (
        f"Slotkoersen per {report_date}. Prijsbewijs en mapping zijn geen allocatie- of uitvoeringsbevoegdheid."
        if language == "nl"
        else f"Closing prices as of {report_date}. Pricing evidence and mapping do not create allocation or execution authority."
    )
    table.insert_after(note)
    watch = rows.get(WATCHLIST_TICKER)
    if watch:
        paragraph = soup.new_tag("div", attrs={"class": "current-close-watch"})
        label = "Behouden fase-1-watchlist" if language == "nl" else "Retained Stage-1 watchlist"
        no_funding = "niet gefinancierd" if language == "nl" else "not funded"
        paragraph.string = (
            f"{label}: VVSM · {format_price(watch.get('close_price'), str(watch.get('currency') or ''), language)}"
            f" · {watch.get('close_date')} · {status_text(watch, language)} · {no_funding}."
        )
        note.insert_after(paragraph)
    html_path.write_text(str(soup), encoding="utf-8")
    HTML(filename=str(html_path), base_url=str(html_path.parent)).write_pdf(str(pdf_path))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--pricing", type=Path, required=True)
    parser.add_argument("--report-date", required=True)
    args = parser.parse_args()
    manifest = load_json(args.manifest)
    pricing = load_json(args.pricing)
    by_ticker = {
        str(row.get("ticker") or "").upper(): row
        for row in pricing.get("rows", [])
        if isinstance(row, dict) and str(row.get("ticker") or "").upper() in PROMOTED_TICKERS | {WATCHLIST_TICKER}
    }
    for language in ("nl", "en"):
        details = manifest.get("languages", {}).get(language, {})
        html_path = Path(details["html"])
        pdf_path = Path(details["pdf"])
        patch_language(html_path, pdf_path, by_ticker, language, args.report_date)
        details["current_close_monitor"] = "promoted_six_plus_vvsm_watchlist_v1"
    manifest["current_close_monitor"] = {
        "applied": True,
        "report_date": args.report_date,
        "promoted_ticker_count": len(PROMOTED_TICKERS),
        "watchlist_tickers": [WATCHLIST_TICKER],
        "pricing_artifact": str(args.pricing),
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
    }
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"ETF_EU_CURRENT_CLOSE_MONITOR_OK | manifest={args.manifest} | priced={len(by_ticker)}")


if __name__ == "__main__":
    main()
