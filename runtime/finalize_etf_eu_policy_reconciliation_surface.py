from __future__ import annotations

import argparse
import json
from pathlib import Path

from weasyprint import HTML


REPLACEMENTS = {
    "nl": {
        "Geen technische blokkade; officiële activatie ontbreekt": "Geen geschikt UCITS-equivalent geverifieerd",
    },
    "en": {
        "No technical blocker; official activation is pending": "No suitable UCITS equivalent verified",
    },
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Finalize policy reconciliation wording")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    counts: dict[str, int] = {}
    for language, files in (manifest.get("languages") or {}).items():
        if language not in REPLACEMENTS or not isinstance(files, dict):
            continue
        html_path = Path(str(files.get("html") or ""))
        pdf_path = Path(str(files.get("pdf") or ""))
        text = html_path.read_text(encoding="utf-8")
        count = 0
        for source, replacement in REPLACEMENTS[language].items():
            occurrences = text.count(source)
            text = text.replace(source, replacement)
            count += occurrences
        html_path.write_text(text, encoding="utf-8")
        HTML(string=text, base_url=str(html_path.parent.resolve())).write_pdf(pdf_path)
        files["policy_reconciliation_finalization"] = "unmapped_promoted_exposure_truthfulness_v1"
        counts[language] = count
    manifest["policy_reconciliation_finalization"] = {
        "applied": True,
        "replacement_counts": counts,
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
    }
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.manifest)


if __name__ == "__main__":
    main()
