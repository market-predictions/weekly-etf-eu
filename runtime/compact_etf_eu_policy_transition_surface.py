from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from weasyprint import HTML


SECTION_RE = re.compile(r'(<section id="section-14"[^>]*>)(.*?)(</section>)', re.DOTALL)
TABLE_RE = re.compile(r'(<table class="wide-table allocator-order-table">.*?<tbody>)(.*?)(</tbody></table>)', re.DOTALL)
ROW_RE = re.compile(r'<tr>.*?</tr>', re.DOTALL)


def compact_section(body: str, language: str) -> tuple[str, int]:
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
    return updated, removed


def main() -> None:
    parser = argparse.ArgumentParser(description="Compact policy transition table to actionable intents")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    removed_by_language: dict[str, int] = {}
    for language, files in (manifest.get("languages") or {}).items():
        if language not in {"nl", "en"} or not isinstance(files, dict):
            continue
        html_path = Path(str(files.get("html") or ""))
        pdf_path = Path(str(files.get("pdf") or ""))
        text = html_path.read_text(encoding="utf-8")

        def replace(match: re.Match[str]) -> str:
            compacted, removed = compact_section(match.group(2), language)
            removed_by_language[language] = removed
            return match.group(1) + compacted + match.group(3)

        updated, count = SECTION_RE.subn(replace, text, count=1)
        if count != 1:
            raise RuntimeError(f"Could not compact Section 14 for {language}")
        html_path.write_text(updated, encoding="utf-8")
        HTML(string=updated, base_url=str(html_path.parent.resolve())).write_pdf(pdf_path)
        files["policy_transition_compaction"] = "actionable_intents_only_v1"

    manifest["policy_transition_compaction"] = {
        "applied": True,
        "removed_deferred_row_count_by_language": removed_by_language,
        "deferred_exposures_remain_in_sections": ["11", "13"],
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
    }
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.manifest)


if __name__ == "__main__":
    main()
