from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Manifest must be a JSON object")
    return payload


def validate(manifest: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    compaction = manifest.get("policy_transition_compaction") if isinstance(manifest.get("policy_transition_compaction"), dict) else {}
    if compaction.get("applied") is not True:
        blockers.append("policy transition compaction not applied")
    for key in ("portfolio_mutation", "funding_authority", "execution_authority"):
        if compaction.get(key) is not False:
            blockers.append(f"policy transition compaction {key} must be false")
    if set(compaction.get("deferred_exposures_remain_in_sections") or []) != {"11", "13"}:
        blockers.append("deferred exposure evidence lineage is incomplete")
    for language, files in (manifest.get("languages") or {}).items():
        if language not in {"nl", "en"} or not isinstance(files, dict):
            continue
        path = Path(str(files.get("html") or ""))
        if not path.is_file():
            blockers.append(f"missing {language} HTML")
            continue
        if files.get("policy_transition_compaction") != "actionable_intents_only_v1":
            blockers.append(f"{language} compaction file marker missing")
        text = path.read_text(encoding="utf-8")
        section = re.search(r'<section id="section-14"[^>]*>(.*?)</section>', text, re.DOTALL)
        body = section.group(1) if section else ""
        table = re.search(r'<table class="wide-table allocator-order-table">.*?<tbody>(.*?)</tbody></table>', body, re.DOTALL)
        rows = re.findall(r'<tr>.*?</tr>', table.group(1), re.DOTALL) if table else []
        if len(rows) != 2:
            blockers.append(f"{language} Section 14 must contain exactly two actionable intent rows")
        if not all("VVSM" in body and "LOCK" in body for _ in [0]):
            blockers.append(f"{language} actionable intent tickers missing")
        for stale in ("Blocked / deferred", "Geblokkeerd / uitgesteld"):
            if stale in body:
                blockers.append(f"{language} Section 14 still repeats deferred rows")
        note = "remain fully documented in Sections 11 and 13" if language == "en" else "blijven volledig onderbouwd in secties 11 en 13"
        if note not in body:
            blockers.append(f"{language} deferred-evidence note missing")
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
