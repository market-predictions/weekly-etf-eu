from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any


SECTION_IDS = ("1", "2", "2A", "4", "11", "12", "13")
STALE_PHRASES = (
    "current pricing basis missing",
    "mapped, not yet fundable",
    "prepare pricing and allocation review",
    "promoted exposures pending implementation",
    "huidige prijsbasis ontbreekt",
    "gemapt, nog niet financierbaar",
    "prijs- en allocatiebeoordeling voorbereiden",
    "gepromoveerde exposures wachten op implementatie",
    "no technical blocker; official activation is pending",
    "geen technische blokkade; officiële activatie ontbreekt",
)


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Manifest must be a JSON object")
    return payload


def section_html(text: str, section_id: str) -> str:
    match = re.search(fr'<section id="section-{re.escape(section_id)}"[^>]*>(.*?)</section>', text, re.DOTALL)
    return match.group(1) if match else ""


def plain(value: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value)).split())


def contains(body: str, expected: str) -> bool:
    return expected.casefold() in body.casefold()


def validate(manifest: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    reconciliation = manifest.get("policy_allocator_reconciliation") if isinstance(manifest.get("policy_allocator_reconciliation"), dict) else {}
    if reconciliation.get("applied") is not True:
        blockers.append("policy allocator reconciliation not applied")
    if reconciliation.get("preferred_variant") != "staged_policy_driven_v1":
        blockers.append("unexpected reconciled preferred variant")
    if set(reconciliation.get("sections_reconciled") or []) != set(SECTION_IDS):
        blockers.append("reconciled section set is incomplete")
    for key in ("official_portfolio_mutation", "funding_authority", "execution_authority", "production_delivery_authority"):
        if reconciliation.get(key) is not False:
            blockers.append(f"policy reconciliation {key} must be false")

    finalization = manifest.get("policy_reconciliation_finalization") if isinstance(manifest.get("policy_reconciliation_finalization"), dict) else {}
    if finalization.get("applied") is not True:
        blockers.append("policy reconciliation finalization not applied")
    for key in ("portfolio_mutation", "funding_authority", "execution_authority"):
        if finalization.get(key) is not False:
            blockers.append(f"policy reconciliation finalization {key} must be false")

    requirements = {
        "en": {
            "1": ["VVSM, LOCK", "24.99% turnover", "35.57% remaining cash", "official EU portfolio remains unchanged"],
            "2": ["Stage-1 shadow buy ready: 156 shares, target 14.80%", "Stage-1 shadow buy ready: 995 shares, target 10.19%"],
            "2A": ["2 exact UCITS implementations are policy-sized for Stage 1", "No portfolio change or order"],
            "4": ["Policy-sized", "Shadow target 14.80%; 156 shares", "Shadow target 10.19%; 995 shares"],
            "11": ["156 whole shares", "995 whole shares", "price date 2026-07-24", "Shadow gate passed"],
            "12": ["156 VVSM, 995 LOCK", "None in Stage 1", "Re-underwrite SXR8 first in Stage 2"],
            "13": [
                "AI compute and semiconductors VanEck Semiconductor UCITS ETF 0.00% 14.80% +14.80%",
                "Cybersecurity resilience iShares Digital Security UCITS ETF USD (Acc) 0.00% 10.19% +10.19%",
                "Cash CASH 60.59% 35.57% -25.02%",
                "VWCE Vanguard FTSE All-World UCITS ETF USD Acc 24.87% 24.87% 0.00%",
                "EUNA iShares Core Global Aggregate Bond UCITS ETF EUR Hedged Acc 7.48% 7.48% 0.00%",
                "SXR8 iShares Core S&P 500 UCITS ETF USD (Acc) 7.06% 7.06% 0.00%",
            ],
        },
        "nl": {
            "1": ["VVSM, LOCK", "24,99% omzet", "35,57% resterende cash", "officiële EU-portefeuille blijft ongewijzigd"],
            "2": ["Fase-1 schaduwkoop gereed: 156 aandelen, doel 14,80%", "Fase-1 schaduwkoop gereed: 995 aandelen, doel 10,19%"],
            "2A": ["2 exacte UCITS-implementaties zijn beleidsgestuurd geschaald voor fase 1", "Geen portefeuillewijziging of order"],
            "4": ["Beleidsgestuurd geschaald", "Schaduwdoel 14,80%; 156 aandelen", "Schaduwdoel 10,19%; 995 aandelen"],
            "11": ["156 hele aandelen", "995 hele aandelen", "koersdatum 2026-07-24", "Schaduwpoort geslaagd"],
            "12": ["156 VVSM, 995 LOCK", "Geen in fase 1", "SXR8 eerst herbeoordelen in fase 2"],
            "13": [
                "AI-rekenkracht en halfgeleiders VanEck Semiconductor UCITS ETF 0,00% 14,80% +14,80%",
                "Cybersecurityweerbaarheid iShares Digital Security UCITS ETF USD (Acc) 0,00% 10,19% +10,19%",
                "Cash CASH 60,59% 35,57% -25,02%",
                "VWCE Vanguard FTSE All-World UCITS ETF USD Acc 24,87% 24,87% 0,00%",
                "EUNA iShares Core Global Aggregate Bond UCITS ETF EUR Hedged Acc 7,48% 7,48% 0,00%",
                "SXR8 iShares Core S&P 500 UCITS ETF USD (Acc) 7,06% 7,06% 0,00%",
            ],
        },
    }

    for language, files in (manifest.get("languages") or {}).items():
        if language not in requirements or not isinstance(files, dict):
            continue
        path = Path(str(files.get("html") or ""))
        if not path.is_file():
            blockers.append(f"missing {language} HTML")
            continue
        text = path.read_text(encoding="utf-8")
        if files.get("policy_allocator_reconciliation") != "stage_1_status_and_feasible_target_contract_v1":
            blockers.append(f"{language} reconciliation file marker missing")
        if files.get("policy_reconciliation_finalization") != "unmapped_promoted_exposure_truthfulness_v1":
            blockers.append(f"{language} reconciliation finalization marker missing")
        bodies = {section_id: plain(section_html(text, section_id)) for section_id in SECTION_IDS}
        combined = " ".join(bodies.values()).casefold()
        for phrase in STALE_PHRASES:
            if phrase.casefold() in combined:
                blockers.append(f"{language} reconciled surface still contains stale phrase: {phrase}")
        for section_id, terms in requirements[language].items():
            body = bodies[section_id]
            for expected in terms:
                if not contains(body, expected):
                    blockers.append(f"{language} section {section_id} missing reconciled term: {expected}")
        section13 = bodies["13"]
        for stale_weight in ("0.00% 27.16% +27.16%", "0,00% 27,16% +27,16%", "0.00% 18.35% +18.35%", "0,00% 18,35% +18,35%"):
            if stale_weight in section13:
                blockers.append(f"{language} Section 13 still presents a full donor weight as the Stage-1 target: {stale_weight}")
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
