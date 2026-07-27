from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import validate_etf_eu_policy_report_reconciliation_v2 as base


ALTERNATE_SECTION_13_ROWS = {
    "en": [
        "AI compute and semiconductors VVSM · VanEck Semiconductor UCITS ETF 0.00% 14.80% +14.80%",
        "Cybersecurity resilience LOCK · iShares Digital Security UCITS ETF USD (Acc) 0.00% 10.19% +10.19%",
    ],
    "nl": [
        "AI-rekenkracht en halfgeleiders VVSM · VanEck Semiconductor UCITS ETF 0,00% 14,80% +14,80%",
        "Cybersecurityweerbaarheid LOCK · iShares Digital Security UCITS ETF USD (Acc) 0,00% 10,19% +10,19%",
    ],
}


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Manifest must be a JSON object")
    return payload


def section_plain(text: str, section_id: str) -> str:
    match = re.search(fr'<section id="section-{re.escape(section_id)}"[^>]*>(.*?)</section>', text, re.DOTALL)
    body = match.group(1) if match else ""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", body)).split())


def validate(manifest: dict[str, Any]) -> list[str]:
    original = base.validate(manifest)
    row_blockers = [blocker for blocker in original if "section 13 missing reconciled term" in blocker]
    blockers = [blocker for blocker in original if blocker not in row_blockers]
    languages = manifest.get("languages") if isinstance(manifest.get("languages"), dict) else {}
    for language, expected_rows in ALTERNATE_SECTION_13_ROWS.items():
        files = languages.get(language) if isinstance(languages.get(language), dict) else {}
        path = Path(str(files.get("html") or ""))
        if not path.is_file():
            blockers.append(f"missing {language} HTML for ticker-qualified reconciliation validation")
            continue
        body = section_plain(path.read_text(encoding="utf-8"), "13").casefold()
        for expected in expected_rows:
            if expected.casefold() not in body:
                blockers.append(f"{language} Section 13 missing ticker-qualified reconciled row: {expected}")
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
