from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any


RECONCILED_SECTIONS = ("1", "2", "2A", "4", "11", "12", "13")
STALE_PHRASES = (
    "current pricing basis missing",
    "Mapped, not yet fundable",
    "Prepare pricing and allocation review",
    "Promoted exposures pending implementation",
    "huidige prijsbasis ontbreekt",
    "Gemapt, nog niet financierbaar",
    "Prijs- en allocatiebeoordeling voorbereiden",
    "Gepromoveerde exposures wachten op implementatie",
)


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Manifest must be a JSON object")
    return payload


def section_text(text: str, section_id: str) -> str:
    match = re.search(fr'<section id="section-{re.escape(section_id)}"[^>]*>(.*?)</section>', text, re.DOTALL)
    return html.unescape(match.group(1)) if match else ""


def normalized(value: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", value).split())


def validate(manifest: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    reconciliation = manifest.get("policy_allocator_reconciliation") if isinstance(manifest.get("policy_allocator_reconciliation"), dict) else {}
    if reconciliation.get("applied") is not True:
        blockers.append("policy allocator reconciliation not applied")
    if reconciliation.get("preferred_variant") != "staged_policy_driven_v1":
        blockers.append("unexpected reconciled preferred variant")
    if set(reconciliation.get("sections_reconciled") or []) != set(RECONCILED_SECTIONS):
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
            "section-1": ["VVSM, LOCK", "24.99% turnover", "35.57% remaining cash", "official EU portfolio remains unchanged"],
            "section-2": ["Stage-1 shadow buy ready: 156 shares, target 14.80%", "Stage-1 shadow buy ready: 995 shares, target 10.19%"],
            "section-2A": ["2 exact UCITS implementations are policy-sized for Stage 1", "No portfolio change or order"],
            "section-4": ["Policy-sized", "Shadow target 14.80%; 156 shares", "Shadow target 10.19%; 995 shares"],
            "section-11": ["156 whole shares", "995 whole shares", "price date 2026-07-24", "shadow gate passed"],
            "section-12": ["156 VVSM, 995 LOCK", "None in Stage 1", "Re-underwrite SXR8 first in Stage 2"],
            "section-13": [
                "AI compute and semiconductors VanEck Semiconductor UCITS ETF 0.00% 14.80% +14.80%",
                "Cybersecurity resilience iShares Digital Security UCITS ETF USD (Acc) 0.00% 10.19% +10.19%",
                "Cash CASH 60.59% 35.57% -25.02%",
                "VWCE Vanguard FTSE All-World UCITS ETF USD Acc 24.87% 24.87% 0.00%",
                "EUNA iShares Core Global Aggregate Bond UCITS ETF EUR Hedged Acc 7.48% 7.48% 0.00%",
                "SXR8 iShares Core S&amp;P 500 UCITS ETF USD (Acc) 7.06% 7.06% 0.00%",
            ],
        },
        "nl": {
            "section-1": ["VVSM, LOCK", "24,99% omzet", "35,57% resterende cash", "officiële EU-portefeuille blijft ongewijzigd"],
            "section-2": ["Fase-1 schaduwkoop gereed: 156 aandelen, doel 14,80%", "Fase-1 schaduwkoop gereed: 995 aandelen, doel 10,19%"],
            "section-2A": ["2 exacte UCITS-implementaties zijn beleidsgestuurd geschaald voor fase 1", "Geen portefeuillewijziging of order"],
            "section-4": ["Beleidsgestuurd geschaald", "Schaduwdoel 14,80%; 156 aandelen", "Schaduwdoel 10,19%; 995 aandelen"],
            "section-11": ["156 hele aandelen", "995 hele aandelen", "koersdatum 2026-07-24", "Schaduwpoort geslaagd"],
            "section-12": ["156 VVSM, 995 LOCK", "Geen in fase 1", "SXR8 eerst herbeoordelen in fase 2"],
            "section-13": [
                "AI-rekenkracht en halfgeleiders VanEck Semiconductor UCITS ETF 0,00% 14,80% +14,80%",
                "Cybersecurityweerbaarheid iShares Digital Security UCITS ETF USD (Acc) 0,00% 10,19% +10,19%",
                "Cash CASH 60,59% 35,57% -25,02%",
                "VWCE Vanguard FTSE All-World UCITS ETF USD Acc 24,87% 24,87% 0,00%",
                "EUNA iShares Core Global Aggregate Bond UCITS ETF EUR Hedged Acc 7,48% 7,48% 0,00%",
                "SXR8 iShares Core S&amp;P 500 UCITS ETF USD (Acc) 7,06% 7,06% 0,00%",
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
        reconciled_text = " ".join(section_text(text, section_id) for section_id in RECONCILED_SECTIONS)
        for phrase in STALE_PHRASES:
            if phrase.lower() in reconciled_text.lower():
                blockers.append(f"{language} reconciled surface still contains stale phrase: {phrase}")
        if "No technical blocker; official activation is pending" in reconciled_text or "Geen technische blokkade; officiële activatie ontbreekt" in reconciled_text:
            blockers.append(f"{language} promoted unmapped exposure has false unblocked status")
        for section_key, terms in requirements[language].items():
            section_id = section_key.split("-", 1)[1]
            body = normalized(section_text(text, section_id))
            for term in terms:
                expected = html.unescape(term)
                if expected not in body:
                    blockers.append(f"{language} {section_key} missing reconciled term: {expected}")
        section13 = normalized(section_text(text, "13"))
        if "0.00% 27.16% +27.16%" in section13 or "0,00% 27,16% +27,16%" in section13:
            blockers.append(f"{language} Section 13 still presents full donor semiconductor weight as Stage-1 target")
        if "0.00% 18.35% +18.35%" in section13 or "0,00% 18,35% +18,35%" in section13:
            blockers.append(f"{language} Section 13 still presents full donor cybersecurity weight as Stage-1 target")
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
