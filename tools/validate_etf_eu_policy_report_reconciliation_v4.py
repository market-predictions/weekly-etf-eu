from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any


SECTION_RE = re.compile(r'<section id="section-(?P<id>2|4|11|13)"[^>]*>(?P<body>.*?)</section>', re.DOTALL)
CANONICAL_HEADERS = {
    "nl": ["Ticker/exposure", "ETF", "Huidig gewicht", "Doelgewicht", "Delta gewicht", "Actie", "Kapitaalbestemming", "Score", "Toelichting", "Override-status"],
    "en": ["Ticker/exposure", "ETF", "Current weight", "Target weight", "Weight delta", "Action", "Capital destination", "Score", "Explanation", "Override status"],
}


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def text_only(value: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value)).split())


def pct(value: Any, language: str, signed: bool = False) -> str:
    number = float(value or 0)
    prefix = "+" if signed and number > 0 else ""
    raw = f"{prefix}{number:,.2f}%"
    return raw.replace(",", "X").replace(".", ",").replace("X", ".") if language == "nl" else raw


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate separated mapping, donor-target and Stage-1 report reconciliation")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()

    manifest = load(args.manifest)
    visibility = manifest.get("promoted_candidate_visibility") if isinstance(manifest.get("promoted_candidate_visibility"), dict) else {}
    contract = manifest.get("promoted_candidate_contract") if isinstance(manifest.get("promoted_candidate_contract"), dict) else {}
    blockers: list[str] = []
    if visibility.get("applied") is not True:
        blockers.append("promoted candidate visibility overlay missing")
    if contract.get("applied") is not True:
        blockers.append("promoted candidate final contract missing")
    if contract.get("donor_final_action_header_contract_preserved") is not True:
        blockers.append("donor final-action header contract not preserved")

    allocator_path = Path(str(visibility.get("source_allocator") or ""))
    if not allocator_path.is_file():
        blockers.append("allocator source missing")
        allocator = {}
    else:
        allocator = load(allocator_path)
    preferred_id = str(allocator.get("preferred_shadow_variant") or "")
    preferred = next((row for row in allocator.get("variants") or [] if isinstance(row, dict) and str(row.get("variant_id")) == preferred_id), {})
    selected = [row for row in preferred.get("allocation_rows") or [] if isinstance(row, dict) and row.get("selected") is True]

    for language, files in (manifest.get("languages") or {}).items():
        if language not in {"nl", "en"} or not isinstance(files, dict):
            continue
        html_path = Path(str(files.get("html") or ""))
        if not html_path.is_file():
            blockers.append(f"{language}: report HTML missing")
            continue
        raw = html_path.read_text(encoding="utf-8")
        sections = {match.group("id"): match.group("body") for match in SECTION_RE.finditer(raw)}
        if set(sections) != {"2", "4", "11", "13"}:
            blockers.append(f"{language}: required reconciled sections missing")
            continue
        section13 = text_only(sections["13"])
        for header in CANONICAL_HEADERS[language]:
            if header not in section13:
                blockers.append(f"{language}: Section 13 missing canonical header {header}")
        for row in selected:
            candidate = row.get("candidate") if isinstance(row.get("candidate"), dict) else {}
            ticker = str(candidate.get("ticker") or "")
            target = float(row.get("variant_target_weight_pct") or 0)
            if ticker not in section13:
                blockers.append(f"{language}: Section 13 missing selected ticker {ticker}")
            if pct(target, language) not in section13:
                blockers.append(f"{language}: Section 13 missing selected target {ticker} {pct(target, language)}")
            if pct(target, language, signed=True) not in section13:
                blockers.append(f"{language}: Section 13 missing selected delta {ticker} {pct(target, language, signed=True)}")
        combined = " ".join(text_only(sections[key]).lower() for key in ("2", "4", "11"))
        required_selected_status = "beleidsgestuurd geschaald" if language == "nl" else "policy-sized"
        if required_selected_status not in combined:
            blockers.append(f"{language}: selected Stage-1 status missing")
        required_no_target = "geen huidig portefeuilledoel" if language == "nl" else "no current portfolio target"
        if required_no_target not in combined:
            blockers.append(f"{language}: mapped promoted no-target status missing")

    if allocator.get("official_portfolio_mutation") is True:
        blockers.append("allocator claims official portfolio mutation")
    for key in ("funding_authority", "execution_authority"):
        if allocator.get(key) is True:
            blockers.append(f"allocator claims {key}")

    payload = {
        "schema_version": "etf_eu_policy_report_reconciliation_validation_v4",
        "artifact_type": "etf_eu_policy_report_reconciliation_validation",
        "valid": not blockers,
        "blockers": blockers,
        "selected_stage_1_count": len(selected),
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
