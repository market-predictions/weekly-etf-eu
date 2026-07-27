from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import validate_etf_eu_target_allocator_report_surface_v2 as base


COMPACT_NL_TERMS = (
    "Beleidsgestuurd",
    "Voorgestelde fase-1 allocatie",
    "Huidige posities",
    "Halfgeleiderlimiet",
)


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Manifest must be a JSON object")
    return payload


def validate(manifest: dict[str, Any]) -> list[str]:
    original = base.validate(manifest)
    compact_blocker_fragments = (
        "nl allocator surface missing: Beleidsgestuurde cash-first migratie",
        "nl allocator surface missing: Voorgestelde beleidsgestuurde fase-1 allocatie",
        "nl allocator surface missing: Behandeling huidige posities",
        "nl allocator surface missing: Effectieve halfgeleiderlimiet",
    )
    blockers = [blocker for blocker in original if blocker not in compact_blocker_fragments]
    files = (manifest.get("languages") or {}).get("nl") if isinstance((manifest.get("languages") or {}).get("nl"), dict) else {}
    path = Path(str(files.get("html") or ""))
    if not path.is_file():
        blockers.append("missing Dutch HTML for compact allocator validation")
    else:
        text = path.read_text(encoding="utf-8")
        for term in COMPACT_NL_TERMS:
            if term not in text:
                blockers.append(f"Dutch compact allocator surface missing: {term}")
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
