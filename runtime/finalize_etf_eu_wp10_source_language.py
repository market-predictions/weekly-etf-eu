from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from weasyprint import HTML


REPLACEMENTS = {
    "Water infrastructure / treatment": "Waterinfrastructuur / waterbehandeling",
    "Water utilities / defensive infrastructure": "Waternutsbedrijven / defensieve infrastructuur",
}


def apply(manifest_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = (manifest.get("languages") or {}).get("nl")
    if not isinstance(files, dict):
        raise RuntimeError("Dutch report output is missing")
    html_path = Path(str(files.get("html") or ""))
    pdf_path = Path(str(files.get("pdf") or ""))
    text = html_path.read_text(encoding="utf-8")
    for raw, replacement in REPLACEMENTS.items():
        text = text.replace(raw, html.escape(replacement)).replace(html.escape(raw), html.escape(replacement))
    visible = html.unescape(text)
    leaked = [raw for raw in REPLACEMENTS if raw in visible]
    if leaked:
        raise RuntimeError("Post-overlay Dutch water-lane localization failed: " + ", ".join(leaked))
    html_path.write_text(text, encoding="utf-8")
    HTML(string=text, base_url=str(html_path.parent.resolve())).write_pdf(str(pdf_path))
    files["wp10_post_overlay_language_finalization"] = "water_lane_exact_phrase_v1"
    manifest["wp10_post_overlay_language_finalization"] = {
        "applied": True,
        "replacements": REPLACEMENTS,
        "portfolio_mutation": False,
        "allocation_change": False,
        "production_delivery_authority": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    apply(args.manifest)
    print(args.manifest)


if __name__ == "__main__":
    main()
