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
    pagination = manifest.get("policy_report_pagination") if isinstance(manifest.get("policy_report_pagination"), dict) else {}
    if pagination.get("applied") is not True:
        blockers.append("policy report pagination not applied")
    if pagination.get("page_break_before_section") != "15":
        blockers.append("operational appendix must start at Section 15")
    if set(pagination.get("appendix_sections") or []) != {"15", "16"}:
        blockers.append("operational appendix section set is incomplete")
    for key in ("portfolio_mutation", "funding_authority", "execution_authority"):
        if pagination.get(key) is not False:
            blockers.append(f"policy report pagination {key} must be false")
    for language, files in (manifest.get("languages") or {}).items():
        if language not in {"nl", "en"} or not isinstance(files, dict):
            continue
        path = Path(str(files.get("html") or ""))
        if not path.is_file():
            blockers.append(f"missing {language} HTML")
            continue
        text = path.read_text(encoding="utf-8")
        if files.get("policy_report_pagination") != "holdings_and_continuity_appendix_page_v1":
            blockers.append(f"{language} pagination file marker missing")
        if 'id="policy-operational-appendix-pagination"' not in text:
            blockers.append(f"{language} operational appendix pagination style missing")
        if "#section-15 { break-before: page; page-break-before: always; }" not in text:
            blockers.append(f"{language} Section 15 page-break rule missing")
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
