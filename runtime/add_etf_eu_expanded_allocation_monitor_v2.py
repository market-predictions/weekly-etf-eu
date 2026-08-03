from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]


VISIBLE_REPLACEMENTS = {
    "Shadow-uitbreidingsvoorstel": "Modeluitbreidingsvoorstel",
    "shadow allocator": "modelallocator",
    "Shadow expansion proposal": "Model expansion proposal",
    "the shadow allocator": "the model allocator",
    "shadow proposals": "model proposals",
    "shadow proposal": "model proposal",
}


def replace_visible_text(html_path: Path, pdf_path: Path) -> None:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    for node in list(soup.find_all(string=True)):
        if not isinstance(node, NavigableString):
            continue
        original = str(node)
        updated = original
        for old, new in VISIBLE_REPLACEMENTS.items():
            updated = updated.replace(old, new)
        if updated != original:
            node.replace_with(updated)
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
            str(ROOT / "runtime/add_etf_eu_expanded_allocation_monitor.py"),
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
        replace_visible_text(Path(record["html"]), Path(record["pdf"]))
        record["client_terminology_cleanup"] = "model_proposal_v1"
    manifest["client_terminology_cleanup"] = {
        "applied": True,
        "internal_shadow_language_visible": False,
        "portfolio_mutation": False,
        "activation_authority": False,
    }
    args.manifest.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("ETF_EU_EXPANDED_ALLOCATION_CLIENT_TERMINOLOGY_OK | visible_shadow_language=false")


if __name__ == "__main__":
    main()
