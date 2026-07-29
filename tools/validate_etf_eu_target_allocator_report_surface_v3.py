from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import validate_etf_eu_target_allocator_report_surface_v2 as base


COMPACT_TERMS = {
    "nl": (
        "Beleidsgestuurd",
        "Voorgestelde fase-1 allocatie",
        "Bestaande posities blijven ongewijzigd",
        "Halfgeleiderlimiet",
    ),
    "en": (
        "Policy-driven cash-first migration",
        "Proposed policy-driven stage-1 allocation",
        "Current positions remain unchanged",
        "Effective semiconductor cap",
    ),
}

REMOVED_BY_COMPACTION = {
    "nl allocator surface missing: Beleidsgestuurde cash-first migratie",
    "nl allocator surface missing: Voorgestelde beleidsgestuurde fase-1 allocatie",
    "nl allocator surface missing: Behandeling huidige posities",
    "nl allocator surface missing: Effectieve halfgeleiderlimiet",
    "en allocator surface missing: Treatment of current positions",
    'nl allocator table missing: class="data-table allocator-legacy-table"',
    'en allocator table missing: class="data-table allocator-legacy-table"',
}


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Manifest must be a JSON object")
    return payload


def validate(manifest: dict[str, Any]) -> list[str]:
    blockers = [blocker for blocker in base.validate(manifest) if blocker not in REMOVED_BY_COMPACTION]

    compaction = manifest.get("policy_transition_compaction") if isinstance(manifest.get("policy_transition_compaction"), dict) else {}
    if compaction.get("applied") is not True:
        blockers.append("policy transition compaction marker missing")
    if compaction.get("incumbent_evidence_remains_in_sections") != ["10", "13", "15"]:
        blockers.append("compacted incumbent evidence lineage is incomplete")
    removed = compaction.get("duplicate_incumbent_block_removed_by_language") if isinstance(compaction.get("duplicate_incumbent_block_removed_by_language"), dict) else {}
    for language in ("nl", "en"):
        if removed.get(language) is not True:
            blockers.append(f"{language} duplicate incumbent block was not explicitly compacted")
        files = (manifest.get("languages") or {}).get(language) if isinstance((manifest.get("languages") or {}).get(language), dict) else {}
        path = Path(str(files.get("html") or ""))
        if not path.is_file():
            blockers.append(f"missing {language} HTML for compact allocator validation")
            continue
        text = path.read_text(encoding="utf-8")
        for term in COMPACT_TERMS[language]:
            if term not in text:
                blockers.append(f"{language} compact allocator surface missing: {term}")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    blockers = validate(load(args.manifest))
    print(json.dumps({"valid": not blockers, "blockers": blockers}, indent=2, ensure_ascii=False))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
