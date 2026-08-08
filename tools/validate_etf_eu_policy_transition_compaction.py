from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


LEGACY_MARKER = "actionable_intents_without_duplicate_incumbents_v2"
ACTIVATED_MARKER = "actionable_intents_state_aware_v3"


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
    if set(compaction.get("incumbent_evidence_remain_in_sections") or compaction.get("incumbent_evidence_remains_in_sections") or []) != {"10", "13", "15"}:
        blockers.append("incumbent evidence lineage is incomplete")
    removed_legacy = compaction.get("duplicate_incumbent_block_removed_by_language") if isinstance(compaction.get("duplicate_incumbent_block_removed_by_language"), dict) else {}
    funded_compaction = compaction.get("already_funded_candidate_compacted_by_language") if isinstance(compaction.get("already_funded_candidate_compacted_by_language"), dict) else {}

    for language, files in (manifest.get("languages") or {}).items():
        if language not in {"nl", "en"} or not isinstance(files, dict):
            continue
        path = Path(str(files.get("html") or ""))
        if not path.is_file():
            blockers.append(f"missing {language} HTML")
            continue
        marker = files.get("policy_transition_compaction")
        activated = marker == ACTIVATED_MARKER and funded_compaction.get(language) is True
        if marker not in {LEGACY_MARKER, ACTIVATED_MARKER}:
            blockers.append(f"{language} compaction file marker missing or unsupported")
        if marker == ACTIVATED_MARKER and funded_compaction.get(language) not in {True, False}:
            blockers.append(f"{language} activated compaction state marker missing")
        if removed_legacy.get(language) is not True:
            blockers.append(f"{language} duplicate incumbent block removal not recorded")

        text = path.read_text(encoding="utf-8")
        section = re.search(r'<section id="section-14"[^>]*>(.*?)</section>', text, re.DOTALL)
        body = section.group(1) if section else ""
        table = re.search(r'<table class="wide-table allocator-order-table">.*?<tbody>(.*?)</tbody></table>', body, re.DOTALL)
        rows = re.findall(r'<tr>.*?</tr>', table.group(1), re.DOTALL) if table else []
        actionable_html = "".join(rows)
        expected_rows = 1 if activated else 2
        if len(rows) != expected_rows:
            blockers.append(f"{language} Section 14 must contain exactly {expected_rows} actionable intent rows")
        if "VVSM" not in actionable_html:
            blockers.append(f"{language} VVSM actionable intent ticker missing")
        if activated:
            if "LOCK" in actionable_html or "L0CK" in actionable_html:
                blockers.append(f"{language} already-funded L0CK still appears as a new actionable intent")
            funded_note = "L0CK is already funded" if language == "en" else "L0CK is al gefinancierd"
            if funded_note not in body:
                blockers.append(f"{language} already-funded L0CK evidence note missing")
        elif "LOCK" not in actionable_html and "L0CK" not in actionable_html:
            blockers.append(f"{language} cybersecurity actionable intent ticker missing")

        for stale in ("Blocked / deferred", "Geblokkeerd / uitgesteld"):
            if stale in body:
                blockers.append(f"{language} Section 14 still repeats deferred rows")
        if activated:
            note = "deferred exposures remain documented in Sections 11 and 13" if language == "en" else "uitgestelde exposures blijven onderbouwd in secties 11 en 13"
        else:
            note = "remain fully documented in Sections 11 and 13" if language == "en" else "blijven volledig onderbouwd in secties 11 en 13"
        if note not in body:
            blockers.append(f"{language} deferred-evidence note missing")
        if "allocator-legacy-table" in body:
            blockers.append(f"{language} Section 14 still duplicates the incumbent holdings table")
        incumbent_note = "Current positions remain unchanged; see Sections 10, 13 and 15." if language == "en" else "Bestaande posities blijven ongewijzigd; zie secties 10, 13 en 15."
        if incumbent_note not in body:
            blockers.append(f"{language} incumbent evidence reference missing")
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
