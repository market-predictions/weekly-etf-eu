from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag

from tools import validate_etf_eu_production_converged_report as legacy


MONITORED_LITERAL_BLOCKER = "monitored Stage-1 row is not visibly blocked"


def monitored_row_is_non_actionable(language: str, row: Tag) -> tuple[bool, list[str]]:
    text = " ".join(row.get_text(" ", strip=True).split())
    folded = text.casefold()
    zero_weights = re.findall(r"\b0[,.]00%", text)
    blockers: list[str] = []

    if len(zero_weights) < 3:
        blockers.append("current/target/delta are not all zero")

    if language == "nl":
        required_groups = (
            ("bewaken", "gemonitord"),
            ("geen allocatie", "geen toewijzing"),
            ("niet gefinancierd",),
            ("geen uitvoering",),
        )
    else:
        required_groups = (
            ("monitor", "monitored"),
            ("no allocation",),
            ("unfunded",),
            ("no execution",),
        )

    for alternatives in required_groups:
        if not any(value in folded for value in alternatives):
            blockers.append(f"missing non-actionable semantic: {'/'.join(alternatives)}")

    prohibited = (
        "buy",
        "increase",
        "fund now",
        "execute",
        "kopen",
        "verhogen",
        "nu financieren",
        "uitvoeren",
    )
    for token in prohibited:
        if token in folded and not (
            token == "execute" and "no execution" in folded
        ) and not (
            token == "uitvoeren" and "geen uitvoering" in folded
        ):
            blockers.append(f"monitored row contains actionable token: {token}")

    return not blockers, blockers


def validate_language(
    language: str,
    record: dict[str, Any],
    state: dict[str, Any],
    contract: dict[str, Any],
) -> tuple[list[str], dict[str, Any]]:
    blockers, details = legacy.validate_language(language, record, state, contract)
    literal_blocker = f"{language}: monitored Stage-1 row is not visibly blocked for VVSM"
    if literal_blocker not in blockers:
        return blockers, details

    html_path = Path(str(record.get("html") or ""))
    if not html_path.is_file():
        return blockers, details

    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    section_13 = soup.find("section", id="section-13")
    if not isinstance(section_13, Tag):
        return blockers, details
    row = legacy.find_row(section_13, "IE00BMC38736")
    if not isinstance(row, Tag):
        return blockers, details

    valid, semantic_blockers = monitored_row_is_non_actionable(language, row)
    if valid:
        blockers = [blocker for blocker in blockers if blocker != literal_blocker]
    else:
        blockers = [blocker for blocker in blockers if blocker != literal_blocker]
        blockers.append(
            f"{language}: monitored Stage-1 row is not semantically non-actionable for VVSM: "
            + "; ".join(semantic_blockers)
        )
    return blockers, details


def validate(manifest: dict[str, Any], state: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    blockers, contract = legacy.validate_manifest_state(manifest, state)
    details: dict[str, Any] = {
        "contract": {
            "position_count": contract.get("position_count"),
            "stage_1_decision": contract.get("stage_value"),
            "renderer_mode": contract.get("renderer_mode"),
            "funded_tickers": sorted(contract.get("funded_tickers") or []),
            "activated_tickers": sorted(contract.get("activated_tickers") or []),
            "monitored_tickers": sorted(contract.get("monitored_tickers") or []),
        }
    }
    languages = manifest.get("languages") if isinstance(manifest.get("languages"), dict) else {}
    for language in ("nl", "en"):
        record = languages.get(language)
        if not isinstance(record, dict):
            blockers.append(f"manifest language missing: {language}")
            continue
        language_blockers, language_details = validate_language(language, record, state, contract)
        blockers.extend(language_blockers)
        details[language] = language_details
    return blockers, details


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = legacy.load(args.manifest)
    state = legacy.load(args.state)
    blockers, details = validate(manifest, state)
    contract = details.get("contract", {})
    result = {
        "artifact_type": "etf_eu_production_converged_report_validation",
        "validator_contract": "monitored_stage1_semantic_non_actionable_v2",
        "valid": not blockers,
        "blockers": blockers,
        "languages": {key: value for key, value in details.items() if key in {"nl", "en"}},
        "funded_position_count": contract.get("position_count"),
        "funded_tickers": contract.get("funded_tickers"),
        "activated_tickers": contract.get("activated_tickers"),
        "remaining_monitored_tickers": contract.get("monitored_tickers"),
        "stage_1_decision": contract.get("stage_1_decision"),
        "renderer_mode": contract.get("renderer_mode"),
        "promoted_exposure_count": len(state.get("promoted_exposures") or []),
    }
    text = json.dumps(result, indent=2, ensure_ascii=False)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
