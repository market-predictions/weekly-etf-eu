from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_SECTIONS = ["1", "2", "2A", "3", "4", "4A", "5", "6", "7", "7A", "8", "9", "10", "11", "12", "13", "14", "15", "16"]
REQUIRED_TABLE_TERMS = {
    "nl": [
        "Portefeuille-acties",
        "Structurele kansenradar",
        "Rendement huidige ETF-posities",
        "Allocatiekaart",
        "Tweede-orde-effectenkaart",
        "Review huidige posities",
        "Definitieve actietabel",
        "Huidige posities en cash",
        "Exacte donor-exposuredekking",
    ],
    "en": [
        "Portfolio actions",
        "Structural opportunity radar",
        "Current ETF position performance",
        "Allocation map",
        "Second-order effects map",
        "Current-position review",
        "Final action table",
        "Current positions and cash",
        "Exact donor-exposure coverage",
    ],
}
INTERNAL_CLIENT_TOKENS = re.compile(
    r"\b(?:trading_line_unverified|ucits_identity_unverified|product_type_blocked|"
    r"existing_position_transition|pricing_missing_or_stale|shadow_candidate|"
    r"ai_compute_infrastructure|non_us_developed_equities|cyber_security|"
    r"broad_commodities|grid_power|biotech_innovation|healthcare_quality|"
    r"uranium_nuclear|power_utilities_capex|aggregate_bonds|core_us_equity|"
    r"global_equity_core)\b"
)
FORBIDDEN_DUTCH_PHRASES = [
    "VWCE is incumbent",
    "SXR8 is incumbent",
    "EUNA remains separate",
    "promoted exposures are not yet implemented",
    "Promoted exposures pending implementation",
    "Shadow only",
]


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Manifest must be a JSON object")
    return payload


def _client_surface(text: str) -> str:
    marker = '<section id="section-16"'
    if marker not in text:
        return text
    return text.split(marker, 1)[0]


def validate(manifest: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if manifest.get("artifact_type") != "etf_eu_sister_report_shadow_manifest":
        blockers.append("unexpected artifact_type")
    if manifest.get("portfolio_mutation") is not False:
        blockers.append("portfolio_mutation must be false")
    if manifest.get("production_delivery_authority") is not False:
        blockers.append("production_delivery_authority must be false")
    alignment_surface = manifest.get("portfolio_alignment_surface") if isinstance(manifest.get("portfolio_alignment_surface"), dict) else {}
    if alignment_surface.get("applied") is not True:
        blockers.append("portfolio alignment surface was not applied")
    if int(alignment_surface.get("row_count") or 0) <= 0:
        blockers.append("portfolio alignment surface has no rows")
    if alignment_surface.get("portfolio_mutation") is not False:
        blockers.append("portfolio alignment surface mutation boundary is missing")
    if alignment_surface.get("recommendation_authority") is not False:
        blockers.append("portfolio alignment surface must not have recommendation authority")
    client_polish = manifest.get("client_surface_polish") if isinstance(manifest.get("client_surface_polish"), dict) else {}
    if client_polish.get("applied") is not True:
        blockers.append("client-surface polish was not applied")
    if client_polish.get("canonical_section_16_ids_preserved") is not True:
        blockers.append("canonical Section 16 identifier boundary is missing")
    for key in ("portfolio_mutation", "recommendation_change", "valuation_change"):
        if client_polish.get(key) is not False:
            blockers.append(f"client-surface polish {key} must be false")

    languages = manifest.get("languages") if isinstance(manifest.get("languages"), dict) else {}
    if set(languages) != {"nl", "en"}:
        blockers.append("both Dutch and English outputs are required")
        return blockers

    section_sets: dict[str, set[str]] = {}
    for language, files in languages.items():
        if not isinstance(files, dict):
            blockers.append(f"invalid language manifest for {language}")
            continue
        html_path = Path(str(files.get("html") or ""))
        pdf_path = Path(str(files.get("pdf") or ""))
        png_path = Path(str(files.get("equity_png") or ""))
        for path, label in ((html_path, "html"), (pdf_path, "pdf"), (png_path, "png")):
            if not path.is_file() or path.stat().st_size <= 0:
                blockers.append(f"missing or empty {language} {label}: {path}")
        if not html_path.is_file():
            continue
        text = html_path.read_text(encoding="utf-8")
        lowered = text.lower()
        client_text = html.unescape(_client_surface(text))
        if "data:image/png;base64," not in lowered:
            blockers.append(f"{language} HTML has no embedded PNG chart")
        if "<svg" in lowered:
            blockers.append(f"{language} HTML still contains inline SVG")
        if "cid:" in lowered:
            blockers.append(f"{language} standalone HTML incorrectly depends on CID")
        if files.get("html_image_mode") != "embedded_data_uri_png":
            blockers.append(f"{language} image mode is not embedded_data_uri_png")
        if files.get("portfolio_alignment_surface") != "donor_target_vs_eu_actual":
            blockers.append(f"{language} portfolio alignment surface marker is missing")
        if files.get("client_surface_polish") != "bilingual_exposure_reason_and_phrase_normalization":
            blockers.append(f"{language} client-surface polish marker is missing")
        if 'class="wide-table alignment-table"' not in text:
            blockers.append(f"{language} donor-to-EU allocation table is missing")
        if 'class="wide-table final-alignment-table"' not in text:
            blockers.append(f"{language} final action table is not driven by portfolio alignment")
        leaked_tokens = sorted(set(INTERNAL_CLIENT_TOKENS.findall(client_text)))
        if leaked_tokens:
            blockers.append(f"{language} client surface leaks internal tokens: {', '.join(leaked_tokens)}")
        if language == "nl":
            for phrase in FORBIDDEN_DUTCH_PHRASES:
                if phrase in client_text:
                    blockers.append(f"Dutch client surface contains untranslated phrase: {phrase}")
        sections = {number for number in REQUIRED_SECTIONS if f'id="section-{number}"' in text}
        section_sets[language] = sections
        missing = [number for number in REQUIRED_SECTIONS if number not in sections]
        if missing:
            blockers.append(f"{language} missing sections: {', '.join(missing)}")
        for term in REQUIRED_TABLE_TERMS[language]:
            if term not in text:
                blockers.append(f"{language} missing donor surface term: {term}")
        if text.count("<table") < 16:
            blockers.append(f"{language} report has too few tables after alignment integration")
        if "Schaduwoutput" not in text and "Shadow output" not in text:
            blockers.append(f"{language} shadow authority notice is missing")

    if section_sets.get("nl") != section_sets.get("en"):
        blockers.append("Dutch and English section sets differ")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate synchronized EU sister-report shadow")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()

    manifest = _load(args.manifest)
    blockers = validate(manifest)
    result = {
        "artifact_type": "etf_eu_sister_report_shadow_validation",
        "manifest": str(args.manifest),
        "valid": not blockers,
        "blockers": blockers,
        "required_section_count": len(REQUIRED_SECTIONS),
        "language_count": len(manifest.get("languages") or {}),
        "portfolio_alignment_row_count": int((manifest.get("portfolio_alignment_surface") or {}).get("row_count") or 0),
    }
    print(json.dumps(result, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
