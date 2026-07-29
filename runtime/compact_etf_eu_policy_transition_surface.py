from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from weasyprint import HTML


SECTION_RE = re.compile(r'(<section id="section-14"[^>]*>)(.*?)(</section>)', re.DOTALL)
TABLE_RE = re.compile(r'(<table class="wide-table allocator-order-table">.*?<tbody>)(.*?)(</tbody></table>)', re.DOTALL)
ROW_RE = re.compile(r'<tr>.*?</tr>', re.DOTALL)
LEGACY_BLOCK_RE = re.compile(
    r'<h3>(?:Behandeling huidige posities|Huidige posities|Treatment of current positions)</h3>'
    r'<table class="data-table allocator-legacy-table">.*?</table>'
    r'<div class="alignment-summary">.*?</div>',
    re.DOTALL,
)

NL_COMPACT_REPLACEMENTS = {
    "De allocator vergelijkt 4 schaduwvarianten. Geen variant heeft uitvoerings- of financieringsbevoegdheid.": "Vier schaduwvarianten; geen uitvoerings- of financieringsbevoegdheid.",
    "Strikte gemapte replicatie": "Strikte replicatie",
    "Efficiënte portefeuille, maximaal 8 posities": "Efficiënt, max. 8 posities",
    "Gefaseerde cash-first migratie (vaste 50%)": "Cash-first (vaste 50%)",
    "Beleidsgestuurde cash-first migratie": "Beleidsgestuurd",
    "De voorkeursvariant gebruikt geen vaste tranche. De ordergrootte volgt uit omzet-, cash-, positie-, liquiditeits- en effectieve exposurelimieten.": "Geen vaste tranche: beleidslimieten bepalen de ordergrootte.",
    "Effectieve halfgeleiderlimiet": "Halfgeleiderlimiet",
    "Ingebedde halfgeleiders, ondergrens": "Ingebedde semis (min.)",
    "Voorgestelde beleidsgestuurde fase-1 allocatie": "Voorgestelde fase-1 allocatie",
    "Beleidsgestuurde fase-1 schaduwintentie": "Fase-1 schaduwintentie",
    "Koop 156 hele aandelen VVSM. Effectieve exposure-ondergrens 17,91% versus limiet 18,00%. VanEck Semiconductor UCITS ETF": "156 VVSM; effectieve exposure 17,91% / limiet 18,00%.",
    "Koop 995 hele aandelen LOCK. Effectieve exposure-ondergrens 10,19% versus limiet 15,00%. iShares Digital Security UCITS ETF USD (Acc)": "995 LOCK; effectieve exposure 10,19% / limiet 15,00%.",
    "7 uitgestelde donor-exposures blijven volledig onderbouwd in secties 11 en 13; deze tabel toont uitsluitend de daadwerkelijke fase-1 schaduwintenties.": "7 uitgestelde exposures blijven volledig onderbouwd in secties 11 en 13; hier staan alleen de fase-1 intenties.",
}


def compact_section(body: str, language: str) -> tuple[str, int, bool]:
    match = TABLE_RE.search(body)
    if not match:
        raise RuntimeError(f"Allocator transition table not found for {language}")
    rows = ROW_RE.findall(match.group(2))
    blocked_markers = ("Blocked / deferred", "Geblokkeerd / uitgesteld")
    kept = [row for row in rows if not any(marker in row for marker in blocked_markers)]
    removed = len(rows) - len(kept)
    if len(kept) != 2:
        raise RuntimeError(f"Expected two actionable Stage-1 rows for {language}; found {len(kept)}")
    rebuilt = match.group(1) + "".join(kept) + match.group(3)
    note = (
        f'<div class="alignment-summary">{removed} uitgestelde donor-exposures blijven volledig onderbouwd in secties 11 en 13; deze tabel toont uitsluitend de daadwerkelijke fase-1 schaduwintenties.</div>'
        if language == "nl" else
        f'<div class="alignment-summary">{removed} deferred donor exposures remain fully documented in Sections 11 and 13; this table shows only the actual Stage-1 shadow intents.</div>'
    )
    updated = body[:match.start()] + rebuilt + note + body[match.end():]

    replacement = (
        '<div class="alignment-summary">Bestaande posities blijven ongewijzigd; zie secties 10, 13 en 15.</div>'
        if language == "nl" else
        '<div class="alignment-summary">Current positions remain unchanged; see Sections 10, 13 and 15.</div>'
    )
    updated, legacy_count = LEGACY_BLOCK_RE.subn(replacement, updated, count=1)
    if legacy_count != 1:
        raise RuntimeError(f"Expected one duplicate incumbent block in Section 14 for {language}")

    if language == "nl":
        for source, compact in NL_COMPACT_REPLACEMENTS.items():
            updated = updated.replace(source, compact)
    return updated, removed, True


def main() -> None:
    parser = argparse.ArgumentParser(description="Compact policy transition table to actionable intents")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    removed_by_language: dict[str, int] = {}
    duplicate_incumbent_block_removed: dict[str, bool] = {}
    for language, files in (manifest.get("languages") or {}).items():
        if language not in {"nl", "en"} or not isinstance(files, dict):
            continue
        html_path = Path(str(files.get("html") or ""))
        pdf_path = Path(str(files.get("pdf") or ""))
        text = html_path.read_text(encoding="utf-8")

        def replace(match: re.Match[str]) -> str:
            compacted, removed, legacy_removed = compact_section(match.group(2), language)
            removed_by_language[language] = removed
            duplicate_incumbent_block_removed[language] = legacy_removed
            return match.group(1) + compacted + match.group(3)

        updated, count = SECTION_RE.subn(replace, text, count=1)
        if count != 1:
            raise RuntimeError(f"Could not compact Section 14 for {language}")
        html_path.write_text(updated, encoding="utf-8")
        HTML(string=updated, base_url=str(html_path.parent.resolve())).write_pdf(pdf_path)
        files["policy_transition_compaction"] = "actionable_intents_without_duplicate_incumbents_v2"

    manifest["policy_transition_compaction"] = {
        "applied": True,
        "removed_deferred_row_count_by_language": removed_by_language,
        "duplicate_incumbent_block_removed_by_language": duplicate_incumbent_block_removed,
        "incumbent_evidence_remains_in_sections": ["10", "13", "15"],
        "deferred_exposures_remain_in_sections": ["11", "13"],
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
    }
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.manifest)


if __name__ == "__main__":
    main()
