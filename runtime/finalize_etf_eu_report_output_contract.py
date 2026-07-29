from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.reconcile_etf_eu_report_with_policy_allocator import (  # noqa: E402
    allocation_index,
    e,
    exposure_name,
    num,
    pct,
    preferred_variant,
    promoted_rows,
    replace_section,
    selected_explanation,
    table,
)
from runtime.reconcile_etf_eu_promoted_candidate_visibility import (  # noqa: E402
    candidate_marker,
    mapped,
    stage_state,
    target_index,
)


BLOCKER_LABELS = {
    "kid_missing": {"nl": "KID ontbreekt", "en": "KID missing"},
    "liquidity_below_threshold": {"nl": "liquiditeit onder de beleidsdrempel", "en": "liquidity below the policy threshold"},
    "product_structure_review_required": {"nl": "product- en tegenpartijstructuur vereist beoordeling", "en": "product and counterparty structure requires review"},
    "pricing_missing_or_stale": {"nl": "actuele prijsbasis ontbreekt", "en": "current price basis unavailable"},
    "trading_line_unverified": {"nl": "handelslijn niet geverifieerd", "en": "trading line unverified"},
    "no_ucits_equivalent": {"nl": "geen geschikt UCITS-equivalent", "en": "no suitable UCITS equivalent"},
    "product_type_blocked": {"nl": "producttype geblokkeerd", "en": "product type blocked"},
    "position_limit": {"nl": "positielimiet bereikt", "en": "position limit reached"},
    "stage_turnover_or_cash_budget": {"nl": "omzet- of cashbudget bereikt", "en": "turnover or cash budget reached"},
    "minimum_trade_size": {"nl": "onder minimale transactiegrootte", "en": "below minimum trade size"},
    "stage_1_candidate_not_allowlisted": {"nl": "niet toegelaten tot fase 1", "en": "not Stage-1 allowlisted"},
}


def clean_detail(value: Any, language: str) -> str:
    text = str(value or "—")
    for code, labels in BLOCKER_LABELS.items():
        text = text.replace(code, labels[language])
    while "; ;" in text:
        text = text.replace("; ;", ";")
    return text


def section_2(sync: dict[str, Any], preferred: dict[str, Any], language: str) -> str:
    allocations = allocation_index(preferred)
    targets = target_index(sync)
    headers = (
        ["Exposure", "Actie", "UCITS-implementatie", "Huidig gewicht", "Afwijkingsreden"]
        if language == "nl"
        else ["Exposure", "Action", "UCITS implementation", "Current weight", "Divergence reason"]
    )
    rows: list[list[str]] = []
    for promoted in promoted_rows(sync):
        exposure_id = str(promoted.get("exposure_id") or "")
        allocation = allocations.get(exposure_id, {})
        donor_target = num((targets.get(exposure_id) or {}).get("donor_target_weight_pct"))
        status, action, detail = stage_state(exposure_id, promoted, allocation, donor_target, language)
        if allocation.get("selected") is True:
            detail = selected_explanation(allocation, language)
        reason = (
            f"Donordoel {pct(donor_target, language)}; {status}; {clean_detail(detail, language)}"
            if language == "nl"
            else f"Donor target {pct(donor_target, language)}; {status}; {clean_detail(detail, language)}"
        )
        rows.append([
            e(exposure_name(exposure_id, language, promoted.get("lane_name"))),
            e(action),
            candidate_marker(exposure_id, promoted),
            e(pct(promoted.get("current_eu_weight_pct"), language)),
            e(reason),
        ])
    return table(headers, rows, "wide-table promoted-mapping-table")


def section_4(sync: dict[str, Any], preferred: dict[str, Any], language: str) -> str:
    allocations = allocation_index(preferred)
    targets = target_index(sync)
    headers = (
        ["Rang", "Thema", "UCITS-kandidaat", "Donorscore", "Implementatiestatus", "Benodigde actie", "Blokkade"]
        if language == "nl"
        else ["Rank", "Theme", "UCITS candidate", "Donor score", "Implementation status", "Required action", "Blocker"]
    )
    rows: list[list[str]] = []
    for promoted in promoted_rows(sync):
        exposure_id = str(promoted.get("exposure_id") or "")
        allocation = allocations.get(exposure_id, {})
        donor_target = num((targets.get(exposure_id) or {}).get("donor_target_weight_pct"))
        status, action, detail = stage_state(exposure_id, promoted, allocation, donor_target, language)
        mapping_status = (
            "Exacte UCITS-identiteit gekoppeld" if language == "nl" else "Exact UCITS identity mapped"
        ) if mapped(promoted) else (
            "Exacte UCITS-identiteit ontbreekt" if language == "nl" else "Exact UCITS identity unresolved"
        )
        if allocation.get("selected") is True:
            blocker = (
                f"Geen schaduwblokker; afzonderlijke activatie vereist. Donordoel {pct(donor_target, language)}."
                if language == "nl"
                else f"No shadow-gate blocker; separate activation required. Donor target {pct(donor_target, language)}."
            )
        else:
            blocker = (
                f"Donordoel {pct(donor_target, language)}; {mapping_status}; {clean_detail(detail, language)}"
                if language == "nl"
                else f"Donor target {pct(donor_target, language)}; {mapping_status}; {clean_detail(detail, language)}"
            )
        rows.append([
            e(promoted.get("shared_rank")),
            e(exposure_name(exposure_id, language, promoted.get("lane_name"))),
            candidate_marker(exposure_id, promoted),
            e(f"{num(promoted.get('shared_score')):.2f}"),
            e(status),
            e(action),
            e(blocker),
        ])
    return table(headers, rows, "wide-table promoted-mapping-table")


def section_11(sync: dict[str, Any], preferred: dict[str, Any], language: str) -> str:
    allocations = allocation_index(preferred)
    targets = target_index(sync)
    headers = (
        ["Gedeelde kans", "UCITS-alternatief", "Status", "Prijs-/productbasis", "Beslisimplicatie"]
        if language == "nl"
        else ["Shared opportunity", "UCITS alternative", "Status", "Pricing/product basis", "Decision implication"]
    )
    rows: list[list[str]] = []
    for promoted in promoted_rows(sync):
        exposure_id = str(promoted.get("exposure_id") or "")
        allocation = allocations.get(exposure_id, {})
        donor_target = num((targets.get(exposure_id) or {}).get("donor_target_weight_pct"))
        status, action, detail = stage_state(exposure_id, promoted, allocation, donor_target, language)
        basis = selected_explanation(allocation, language) if allocation.get("selected") is True else detail
        rows.append([
            e(exposure_name(exposure_id, language, promoted.get("lane_name"))),
            candidate_marker(exposure_id, promoted),
            e(status),
            e(clean_detail(basis, language)),
            e(action),
        ])
    return table(headers, rows, "wide-table promoted-mapping-table")


def apply(manifest_path: Path, allocator_path: Path, sync_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    allocator = json.loads(allocator_path.read_text(encoding="utf-8"))
    sync = json.loads(sync_path.read_text(encoding="utf-8"))
    preferred = preferred_variant(allocator)

    for language, files in (manifest.get("languages") or {}).items():
        if language not in {"nl", "en"} or not isinstance(files, dict):
            continue
        html_path = Path(str(files.get("html") or ""))
        pdf_path = Path(str(files.get("pdf") or ""))
        text = html_path.read_text(encoding="utf-8")
        text = replace_section(text, "2", section_2(sync, preferred, language))
        text = replace_section(text, "4", section_4(sync, preferred, language))
        text = replace_section(text, "11", section_11(sync, preferred, language))

        multi_class = 'class="wide-table final-alignment-table promoted-mapping-final-table"'
        if multi_class in text:
            text = text.replace(multi_class, 'class="wide-table final-alignment-table"', 1)
        if 'class="wide-table final-alignment-table"' not in text:
            raise RuntimeError(f"Final alignment table class missing for {language}")

        for code, labels in BLOCKER_LABELS.items():
            text = text.replace(code, labels[language])

        html_path.write_text(text, encoding="utf-8")
        HTML(string=text, base_url=str(html_path.parent.resolve())).write_pdf(pdf_path)
        files["report_output_contract_finalization"] = "donor_headers_visible_labels_and_alignment_class_v1"

    manifest["report_output_contract_finalization"] = {
        "applied": True,
        "sections_restored": ["2", "4", "11", "13"],
        "donor_table_headers_preserved": True,
        "visible_internal_blocker_codes_removed": True,
        "portfolio_alignment_class_preserved": True,
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Finalize the client-visible ETF EU donor output contract")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--allocator", type=Path, required=True)
    parser.add_argument("--sync-shadow", type=Path, required=True)
    args = parser.parse_args()
    apply(args.manifest, args.allocator, args.sync_shadow)
    print(args.manifest)


if __name__ == "__main__":
    main()
