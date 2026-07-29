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
    surface = manifest.get("incumbent_overlap_surface") if isinstance(manifest.get("incumbent_overlap_surface"), dict) else {}
    if surface.get("applied") is not True:
        blockers.append("incumbent overlap surface not applied")
    if surface.get("lower_bound_only") is not True:
        blockers.append("lower-bound evidence marker missing")
    for key in ("portfolio_mutation", "funding_authority", "execution_authority"):
        if surface.get(key) is not False:
            blockers.append(f"incumbent overlap surface {key} must be false")
    required = {
        "nl": ["Overlap- en dispositiebeoordeling", "Prioritaire bron voor fase-2 overlapreductie", "geen bewijs van nul werkelijke overlap"],
        "en": ["Overlap and disposition review", "Priority source for stage-2 overlap reduction", "does not prove zero actual overlap"],
    }
    for language, files in (manifest.get("languages") or {}).items():
        if language not in required or not isinstance(files, dict):
            continue
        html_path = Path(str(files.get("html") or ""))
        if not html_path.is_file():
            blockers.append(f"missing {language} HTML")
            continue
        text = html_path.read_text(encoding="utf-8")
        if files.get("incumbent_overlap_surface") != "documented_lower_bound_and_disposition_v1":
            blockers.append(f"{language} overlap surface marker missing")
        if 'class="wide-table incumbent-overlap-table"' not in text:
            blockers.append(f"{language} overlap table missing")
        for term in required[language]:
            if term not in text:
                blockers.append(f"{language} overlap surface missing: {term}")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    blockers = validate(load(args.manifest))
    print(json.dumps({"valid": not blockers, "blockers": blockers}, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
