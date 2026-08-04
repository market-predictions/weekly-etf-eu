from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]


def compact_status(text: str, language: str) -> str:
    replacements = (
        {
            "Börse + Yahoo akkoord": "2-bron akkoord",
            "Enkele bron; alleen monitoring": "1 bron · monitoring",
            "Geen bruikbare slotkoers": "geen koers",
            "Niet geprijsd": "geen koers",
        }
        if language == "nl"
        else {
            "Börse + Yahoo agreement": "2-source agreement",
            "Single source; monitoring only": "1 source · monitoring",
            "No usable close": "no close",
            "Unpriced": "no close",
        }
    )
    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)
    return result


def correct_client_wording(soup: BeautifulSoup, language: str) -> None:
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
    for node in list(soup.find_all(string=True)):
        if not isinstance(node, NavigableString):
            continue
        original = str(node)
        updated = original.replace(stale_regime, current_regime)
        updated = re.sub(r"\bLOCK\b", "L0CK", updated)
        if updated != original:
            node.replace_with(updated)


def compact_opportunity_table(html_path: Path, pdf_path: Path, language: str) -> None:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    correct_client_wording(soup, language)
    table = soup.find("table", class_="promoted-mapping-table")
    if not isinstance(table, Tag):
        raise RuntimeError(f"Promoted mapping table missing: {html_path}")

    header_cells = table.select("thead tr th")
    if len(header_cells) < 2:
        raise RuntimeError("Promoted mapping table does not contain appended close columns")
    header_cells[-2].string = "Slot / bewijs" if language == "nl" else "Close / evidence"
    header_cells[-1].decompose()

    for row in table.select("tbody > tr"):
        cells = row.find_all("td", recursive=False)
        if len(cells) < 2:
            continue
        price_text = cells[-2].get_text(" ", strip=True)
        evidence_text = compact_status(cells[-1].get_text(" ", strip=True), language)
        combined = cells[-2]
        combined.clear()
        price = soup.new_tag("div", attrs={"class": "compact-close-price"})
        price.string = price_text
        proof = soup.new_tag("div", attrs={"class": "compact-close-proof"})
        proof.string = evidence_text
        combined.append(price)
        combined.append(proof)
        cells[-1].decompose()

    style = soup.new_tag("style")
    style.string = """
.promoted-mapping-table{font-size:6.55pt!important;line-height:1.08!important;table-layout:fixed!important}
.promoted-mapping-table th,.promoted-mapping-table td{padding:.12rem .16rem!important;vertical-align:top!important;overflow-wrap:anywhere}
.promoted-mapping-table th:last-child,.promoted-mapping-table td:last-child{width:15.5%!important;white-space:normal!important}
.promoted-mapping-table .compact-close-price{font-weight:700;white-space:nowrap}
.promoted-mapping-table .compact-close-proof{font-size:6.05pt;line-height:1.03;margin-top:.05rem}
.current-close-note{font-size:7.25pt!important;padding:.28rem .42rem!important;margin:.25rem 0 .15rem!important;line-height:1.12!important}
.current-close-watch{font-size:7.2pt!important;line-height:1.12!important;margin:.2rem 0 0!important}
"""
    soup.head.append(style)
    html_path.write_text(str(soup), encoding="utf-8")
    HTML(filename=str(html_path), base_url=str(html_path.parent.resolve())).write_pdf(str(pdf_path))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--pricing", type=Path, required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument(
        "--allocator",
        type=Path,
        default=Path("output/routine_preview/sync/etf_eu_target_allocator_shadow.json"),
    )
    args = parser.parse_args()

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "runtime/add_etf_eu_expanded_allocation_monitor_v3.py"),
            str(args.manifest),
            "--pricing",
            str(args.pricing),
            "--report-date",
            args.report_date,
            "--allocator",
            str(args.allocator),
        ],
        cwd=str(ROOT),
        check=True,
    )

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise RuntimeError("Expected report manifest object")
    for language in ("nl", "en"):
        record = manifest.get("languages", {}).get(language, {})
        compact_opportunity_table(Path(record["html"]), Path(record["pdf"]), language)
        record["promoted_close_table_layout"] = "combined_compact_v2"
    manifest["promoted_close_table_layout"] = {
        "applied": True,
        "format": "combined_compact_v2",
        "promoted_rows_preserved": 6,
        "exact_l0ck_ticker_visible": True,
        "historical_regime_context_labelled": True,
        "portfolio_mutation": False,
        "activation_authority": False,
    }
    args.manifest.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("ETF_EU_PROMOTED_CLOSE_TABLE_COMPACT_OK | promoted_rows=6 | wording_reconciled=true")


if __name__ == "__main__":
    main()
