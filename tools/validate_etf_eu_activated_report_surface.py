from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def validate_language(language: str, html_path: Path) -> list[str]:
    blockers: list[str] = []
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    visible = soup.get_text(" ", strip=True)
    lowered = visible.lower()

    section = soup.find("section", id="section-14")
    if not isinstance(section, Tag):
        return [f"{language}: Section 14 missing"]
    table = section.find("table", class_=lambda value: value and "target-allocation-table" in value)
    if not isinstance(table, Tag):
        blockers.append(f"{language}: activated Stage-1 table missing")
    else:
        tbody = table.find("tbody")
        rows = tbody.find_all("tr", recursive=False) if isinstance(tbody, Tag) else []
        if len(rows) != 1:
            blockers.append(f"{language}: expected one remaining VVSM monitoring row; found {len(rows)}")
        elif rows:
            row_text = rows[0].get_text(" ", strip=True)
            row_lower = row_text.lower()
            if "vvsm" not in row_lower:
                blockers.append(f"{language}: remaining monitoring row is not VVSM")
            if re.search(r"\bl0ck\b|\block\b", row_lower):
                blockers.append(f"{language}: funded L0CK appears as a new Stage-1 intent")
            if any(marker in row_lower for marker in ("koop", "buy", "purchase", "aankoop")):
                blockers.append(f"{language}: VVSM row contains a buy instruction")
            if "monitor" not in row_lower:
                blockers.append(f"{language}: VVSM monitoring status missing")
            if rows[0].get("data-activated-stage1-status") != "remaining-vvsm-monitor":
                blockers.append(f"{language}: activated Stage-1 row marker missing")

    section_text = section.get_text(" ", strip=True).lower()
    if "l0ck" not in section_text or "funded" not in section_text and "gefinancierd" not in section_text:
        blockers.append(f"{language}: funded L0CK transition context missing")
    if "current positions remain unchanged" not in section_text and "bestaande posities blijven ongewijzigd" not in section_text:
        blockers.append(f"{language}: incumbent hold boundary missing")

    required_funded = ("vwce", "euna", "sxr8", "l0ck")
    for ticker in required_funded:
        if ticker not in lowered:
            blockers.append(f"{language}: funded ticker missing from report: {ticker.upper()}")
    if "model position active" not in lowered and "modelpositie actief" not in lowered:
        blockers.append(f"{language}: activated L0CK client status missing")
    if "no real broker order" not in lowered and "geen echte brokerorder" not in lowered:
        blockers.append(f"{language}: model-only broker boundary missing")
    if language == "nl":
        forbidden = (
            "promoted exposures are not represented",
            "promoted exposures are not yet implemented",
            "current positions remain unchanged",
            "remaining stage-1 monitoring",
        )
        for phrase in forbidden:
            if phrase in lowered:
                blockers.append(f"nl: untranslated internal phrase remains: {phrase}")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    manifest = load_object(args.manifest)
    blockers: list[str] = []
    compaction = manifest.get("policy_transition_compaction") or {}
    if compaction.get("mode") != "activated_l0ck_remaining_vvsm_monitor_v2":
        blockers.append("activated compaction mode missing")
    if compaction.get("remaining_actionable_row_count") != 1:
        blockers.append("activated compaction remaining-row count must be one")
    if set(compaction.get("funded_stage1_tickers") or []) != {"L0CK"}:
        blockers.append("activated compaction funded ticker must be L0CK")
    if set(compaction.get("remaining_monitored_tickers") or []) != {"VVSM"}:
        blockers.append("activated compaction monitored ticker must be VVSM")
    if compaction.get("current_position_count") != 4:
        blockers.append("activated compaction position count must be four")
    for language in ("nl", "en"):
        record = (manifest.get("languages") or {}).get(language) or {}
        html_path = Path(str(record.get("html") or ""))
        if not html_path.exists():
            blockers.append(f"{language}: HTML missing")
            continue
        if record.get("policy_transition_compaction") != "activated_l0ck_remaining_vvsm_monitor_v2":
            blockers.append(f"{language}: activated compaction file marker missing")
        blockers.extend(validate_language(language, html_path))
    result = {
        "schema_version": "etf_eu_activated_report_surface_validation_v1",
        "artifact_type": "etf_eu_activated_report_surface_validation",
        "valid": not blockers,
        "blockers": blockers,
        "funded_stage1_tickers": ["L0CK"],
        "remaining_monitored_tickers": ["VVSM"],
        "remaining_actionable_row_count": 1,
        "current_position_count": 4,
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
        "real_broker_execution": False,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
