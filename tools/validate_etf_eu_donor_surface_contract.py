from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

import yaml


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def validate(manifest: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    required_sections = [item for item in (contract.get("required_sections") or []) if isinstance(item, dict)]
    headers = contract.get("required_table_headers") if isinstance(contract.get("required_table_headers"), dict) else {}
    visual = contract.get("visual_contract") if isinstance(contract.get("visual_contract"), dict) else {}
    languages = manifest.get("languages") if isinstance(manifest.get("languages"), dict) else {}

    for language in ("nl", "en"):
        files = languages.get(language) if isinstance(languages.get(language), dict) else {}
        path = Path(str(files.get("html") or ""))
        if not path.is_file():
            blockers.append(f"{language} HTML missing")
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()

        for item in required_sections:
            section_id = str(item.get("id") or "")
            title = str(item.get(language) or "")
            if f'id="section-{section_id}"' not in text:
                blockers.append(f"{language} section {section_id} missing")
            if title and html.escape(title) not in text:
                blockers.append(f"{language} section title missing: {title}")

        language_headers = headers.get(language) if isinstance(headers.get(language), dict) else {}
        for table_id, values in language_headers.items():
            for value in values or []:
                escaped = html.escape(str(value))
                if f"<th>{escaped}</th>" not in text:
                    blockers.append(f"{language} missing {table_id} header: {value}")

        if visual.get("executive_hero") == "required" and 'class="hero"' not in text:
            blockers.append(f"{language} executive hero missing")
        if visual.get("summary_cards") == "required" and 'class="summary-strip"' not in text:
            blockers.append(f"{language} summary cards missing")
        if visual.get("numbered_section_badges") == "required" and text.count('class="section-badge"') < len(required_sections):
            blockers.append(f"{language} section badges incomplete")
        if visual.get("investor_to_analyst_page_break") == "required" and 'class="analyst-divider"' not in text:
            blockers.append(f"{language} investor/analyst divider missing")
        if visual.get("functional_status_badges") == "required" and 'class="status ' not in text:
            blockers.append(f"{language} status badges missing")
        if visual.get("standalone_html_chart_mode") == "embedded_data_uri_png" and "data:image/png;base64," not in lowered:
            blockers.append(f"{language} embedded PNG chart missing")
        if visual.get("inline_svg_in_email") == "forbidden" and "<svg" in lowered:
            blockers.append(f"{language} inline SVG is forbidden")
        minimum_tables = int(visual.get("minimum_table_count") or 0)
        if text.count("<table") < minimum_tables:
            blockers.append(f"{language} table count below donor contract")

    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Weekly ETF EU sister report against donor surface contract")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--contract", type=Path, default=Path("config/weekly_etf_donor_surface_contract.yml"))
    args = parser.parse_args()

    manifest = _load_json(args.manifest)
    contract = _load_yaml(args.contract)
    blockers = validate(manifest, contract)
    result = {
        "artifact_type": "etf_eu_donor_surface_contract_validation",
        "valid": not blockers,
        "blockers": blockers,
        "section_count": len(contract.get("required_sections") or []),
        "contract": str(args.contract),
    }
    print(json.dumps(result, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
