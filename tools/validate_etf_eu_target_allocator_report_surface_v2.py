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
    if surface.get("preferred_variant") != "staged_policy_driven_v1":
        blockers.append("unexpected preferred allocator variant")
    if surface.get("policy_driven") is not True:
        blockers.append("policy-driven surface marker missing")
    if surface.get("overlap_review_applied") is not True:
        blockers.append("overlap-review surface marker missing")
    for key in ("portfolio_mutation", "funding_authority", "execution_authority"):
        if surface.get(key) is not False:
            blockers.append(f"target allocator surface {key} must be false")

    required = {
        "nl": [
            "Beleidsgestuurde cash-first migratie",
            "Voorgestelde beleidsgestuurde fase-1 allocatie",
            "Behandeling huidige posities",
            "Omzetplafond",
            "Effectieve halfgeleiderlimiet",
            "VVSM",
            "LOCK",
        ],
        "en": [
            "Policy-driven cash-first migration",
            "Proposed policy-driven stage-1 allocation",
            "Treatment of current positions",
            "Turnover ceiling",
            "Effective semiconductor cap",
            "VVSM",
            "LOCK",
        ],
    }
    required_classes = (
        'class="wide-table allocator-variant-table"',
        'class="data-table allocator-policy-table"',
        'class="wide-table allocator-order-table"',
        'class="data-table allocator-legacy-table"',
    )
    for language, files in (manifest.get("languages") or {}).items():
        if language not in required or not isinstance(files, dict):
            continue
        html_path = Path(str(files.get("html") or ""))
        if not html_path.is_file():
            blockers.append(f"missing {language} HTML")
            continue
        text = html_path.read_text(encoding="utf-8")
        if files.get("target_allocator_surface") != "wp_sync_04_policy_driven_variant_and_stage_orders_v2":
            blockers.append(f"{language} allocator surface marker missing")
        for term in required[language]:
            if term not in text:
                blockers.append(f"{language} allocator surface missing: {term}")
        for css_class in required_classes:
            if css_class not in text:
                blockers.append(f"{language} allocator table missing: {css_class}")
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
