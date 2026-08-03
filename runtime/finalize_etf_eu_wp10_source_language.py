from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from weasyprint import HTML


LANGUAGE_REPLACEMENTS = {
    "nl": {
        "Water infrastructure / treatment": "Waterinfrastructuur / waterbehandeling",
        "Water utilities / defensive infrastructure": "Waternutsbedrijven / defensieve infrastructuur",
        "VVSM/SMH · VanEck Semiconductor UCITS ETF": "VVSM · VanEck Semiconductor UCITS ETF",
    },
    "en": {
        "VVSM/SMH · VanEck Semiconductor UCITS ETF": "VVSM · VanEck Semiconductor UCITS ETF",
    },
}


def apply(manifest_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    languages = manifest.get("languages") if isinstance(manifest.get("languages"), dict) else {}
    applied: dict[str, dict[str, str]] = {}
    for language, replacements in LANGUAGE_REPLACEMENTS.items():
        files = languages.get(language)
        if not isinstance(files, dict):
            raise RuntimeError(f"Report output is missing for language: {language}")
        html_path = Path(str(files.get("html") or ""))
        pdf_path = Path(str(files.get("pdf") or ""))
        text = html_path.read_text(encoding="utf-8")
        for raw, replacement in replacements.items():
            text = text.replace(raw, html.escape(replacement)).replace(html.escape(raw), html.escape(replacement))
        visible = html.unescape(text)
        leaked = [raw for raw in replacements if raw in visible]
        if leaked:
            raise RuntimeError(f"Post-overlay label finalization failed for {language}: " + ", ".join(leaked))
        html_path.write_text(text, encoding="utf-8")
        HTML(string=text, base_url=str(html_path.parent.resolve())).write_pdf(str(pdf_path))
        files["wp10_post_overlay_label_finalization"] = "exact_client_labels_v2"
        applied[language] = replacements
    manifest["wp10_post_overlay_label_finalization"] = {
        "applied": True,
        "replacements": applied,
        "official_state_changed": False,
        "allocation_change": False,
        "delivery_performed": False,
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
