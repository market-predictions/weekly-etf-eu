from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Manifest must be a JSON object")
    return payload


def validate(manifest: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    surface = manifest.get("target_allocator_surface") if isinstance(manifest.get("target_allocator_surface"), dict) else {}
    if surface.get("applied") is not True:
        blockers.append("target allocator surface not applied")
    if surface.get("preferred_variant") != "staged_cash_first_50pct":
        blockers.append("unexpected preferred allocator variant")
    for key in ("portfolio_mutation", "funding_authority", "execution_authority"):
        if surface.get(key) is not False:
            blockers.append(f"target allocator surface {key} must be false")
    required = {
        "nl": ["Gefaseerde cash-first migratie", "Voorgestelde fase-1 allocatie", "Behandeling huidige posities", "VVSM", "LOCK"],
        "en": ["Staged cash-first migration", "Proposed stage-1 allocation", "Treatment of current positions", "VVSM", "LOCK"],
    }
    for language, files in (manifest.get("languages") or {}).items():
        if language not in required or not isinstance(files, dict):
            continue
        html_path = Path(str(files.get("html") or ""))
        if not html_path.is_file():
            blockers.append(f"missing {language} HTML")
            continue
        text = html_path.read_text(encoding="utf-8")
        if files.get("target_allocator_surface") != "wp_sync_04_variant_and_stage_orders_v1":
            blockers.append(f"{language} allocator surface marker missing")
        for term in required[language]:
            if term not in text:
                blockers.append(f"{language} allocator surface missing: {term}")
        if 'class="wide-table allocator-variant-table"' not in text:
            blockers.append(f"{language} allocator variant table missing")
        if 'class="wide-table allocator-order-table"' not in text:
            blockers.append(f"{language} allocator order table missing")
        if 'class="data-table allocator-legacy-table"' not in text:
            blockers.append(f"{language} allocator legacy table missing")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    manifest = load(args.manifest)
    blockers = validate(manifest)
    print(json.dumps({"valid": not blockers, "blockers": blockers}, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
