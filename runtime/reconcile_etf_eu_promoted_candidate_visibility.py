from __future__ import annotations

import argparse
import html
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
    blocker_text,
    e,
    exposure_name,
    lane_index,
    money,
    num,
    pct,
    preferred_variant,
    promoted_rows,
    replace_section,
    selected_explanation,
    status_badge,
    table,
)


SECTIONS = ("2", "4", "11", "13")


def target_index(sync: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("exposure_id")): row
        for row in sync.get("portfolio_alignment_rows") or []
        if isinstance(row, dict)
    }


def primary_candidate(row: dict[str, Any]) -> dict[str, str]:
    candidate = row.get("preferred_ucits_candidate") if isinstance(row.get("preferred_ucits_candidate"), dict) else {}
    lines = [line for line in (candidate.get("trading_lines") or []) if isinstance(line, dict)]
    preferred = [
        line for line in lines
        if str(line.get("trading_currency") or "").upper() == "EUR"
        and str(line.get("exchange") or "") in {"Xetra", "Euronext Amsterdam", "Borsa Italiana"}
    ]
    line = (preferred or lines or [{}])[0]
    return {
        "ticker": str(line.get("exchange_ticker") or "").strip(),
        "isin": str(candidate.get("isin") or "").strip(),
        "fund_name": str(candidate.get("fund_name") or "").strip(),
        "exchange": str(line.get("exchange") or "").strip(),
    }


def candidate_marker(exposure_id: str, row: dict[str, Any]) -> str:
    candidate = primary_candidate(row)
    parts = [candidate["ticker"], candidate["fund_name"], candidate["isin"]]
    label = " · ".join(part for part in parts if part) or "—"
    return (
        '<span class="ucits-candidate" '
        f'data-exposure-id="{html.escape(exposure_id, quote=True)}" '
        f'data-ticker="{html.escape(candidate["ticker"], quote=True)}" '
        f'data-isin="{html.escape(candidate["isin"], quote=True)}">'
        f'{html.escape(label)}</span>'
    )


def mapped(row: dict[str, Any]) -> bool:
    candidate = primary_candidate(row)
    return bool(candidate["ticker"] and candidate["isin"])


def stage_state(
    exposure_id: str,
    sync_row: dict[str, Any],
    allocation: dict[str, Any],
    donor_target: float,
    language: str,
) -> tuple[str, str, str]:
    if allocation.get("selected") is True:
        status = "Beleidsgestuurd geschaald" if language == "nl" else "Policy-sized"
        action = "Afzonderlijke fase-1 activatie beoordelen" if language == "nl" else "Review separate Stage-1 activation"
        detail = "Schaduwpoort geslaagd; officiële portefeuille ongewijzigd" if language == "nl" else "Shadow gate passed; official portfolio unchanged"
        return status, action, detail

    blockers = [str(code) for code in allocation.get("blockers") or []]
    if allocation:
        if "stage_1_candidate_not_allowlisted" in blockers:
            status = "Gekoppeld; niet toegelaten tot fase 1" if language == "nl" else "Mapped; not Stage-1 allowlisted"
            action = "Alleen na expliciete beleidswijziging" if language == "nl" else "Only after explicit policy change"
        else:
            status = "Gekoppeld; bewijs onvolledig" if language == "nl" else "Mapped; evidence incomplete"
            action = "Document-, prijs- en liquiditeitspoorten voltooien" if language == "nl" else "Complete document, price and liquidity gates"
        detail = blocker_text(allocation, language)
        return status, action, detail

    if mapped(sync_row):
        status = "Gekoppelde kans; geen huidig portefeuilledoel" if language == "nl" else "Mapped opportunity; no current portfolio target"
        action = "Volgen; geen allocatie zonder nieuw doelbesluit" if language == "nl" else "Monitor; no allocation without a new target decision"
        detail = (
            "Gepromoveerde donor-kans, maar huidig donordoel is 0%"
            if language == "nl" else
            "Promoted donor opportunity, but current donor target is 0%"
        )
        return status, action, detail

    status = "UCITS-koppeling ontbreekt" if language == "nl" else "UCITS mapping unresolved"
    action = "Exact product en handelslijn identificeren" if language == "nl" else "Identify exact product and trading line"
    detail = str(sync_row.get("research_required") or sync_row.get("mapping_note") or "—")
    return status, action, detail


def section_2(sync: dict[str, Any], preferred: dict[str, Any], language: str) -> str:
    allocations = allocation_index(preferred)
    targets = target_index(sync)
    headers = (
        ["Exposure", "UCITS-implementatie", "Donordoel", "Fase-1-status", "Huidig gewicht", "Volgende actie"]
        if language == "nl" else
        ["Exposure", "UCITS implementation", "Donor target", "Stage-1 status", "Current weight", "Next action"]
    )
    rows: list[list[str]] = []
    for promoted in promoted_rows(sync):
        exposure_id = str(promoted.get("exposure_id"))
        allocation = allocations.get(exposure_id, {})
        donor_target = num((targets.get(exposure_id) or {}).get("donor_target_weight_pct"))
        status, action, _ = stage_state(exposure_id, promoted, allocation, donor_target, language)
        rows.append([
            e(exposure_name(exposure_id, language, promoted.get("lane_name"))),
            candidate_marker(exposure_id, promoted),
            e(pct(donor_target, language)),
            e(status),
            e(pct(promoted.get("current_eu_weight_pct"), language)),
            e(action),
        ])
    return table(headers, rows, "wide-table promoted-mapping-table")


def section_4(sync: dict[str, Any], preferred: dict[str, Any], language: str) -> str:
    allocations = allocation_index(preferred)
    targets = target_index(sync)
    headers = (
        ["Rang", "Thema", "UCITS-kandidaat", "Donorscore", "Donordoel", "Mappingstatus", "Fase-1-status"]
        if language == "nl" else
        ["Rank", "Theme", "UCITS candidate", "Donor score", "Donor target", "Mapping status", "Stage-1 status"]
    )
    rows: list[list[str]] = []
    for promoted in promoted_rows(sync):
        exposure_id = str(promoted.get("exposure_id"))
        allocation = allocations.get(exposure_id, {})
        donor_target = num((targets.get(exposure_id) or {}).get("donor_target_weight_pct"))
        status, _, _ = stage_state(exposure_id, promoted, allocation, donor_target, language)
        mapping_status = (
            "Exacte UCITS-identiteit gekoppeld" if language == "nl" else "Exact UCITS identity mapped"
        ) if mapped(promoted) else (
            "Exacte UCITS-identiteit ontbreekt" if language == "nl" else "Exact UCITS identity unresolved"
        )
        rows.append([
            e(promoted.get("shared_rank")),
            e(exposure_name(exposure_id, language, promoted.get("lane_name"))),
            candidate_marker(exposure_id, promoted),
            e(f"{num(promoted.get('shared_score')):.2f}"),
            e(pct(donor_target, language)),
            e(mapping_status),
            e(status),
        ])
    return table(headers, rows, "wide-table promoted-mapping-table")


def section_11(sync: dict[str, Any], preferred: dict[str, Any], language: str) -> str:
    allocations = allocation_index(preferred)
    targets = target_index(sync)
    headers = (
        ["Gedeelde kans", "UCITS-alternatief", "Mapping", "Donordoel", "Allocatiestatus", "Bewijs / vervolgstap"]
        if language == "nl" else
        ["Shared opportunity", "UCITS alternative", "Mapping", "Donor target", "Allocation status", "Evidence / next step"]
    )
    rows: list[list[str]] = []
    for promoted in promoted_rows(sync):
        exposure_id = str(promoted.get("exposure_id"))
        allocation = allocations.get(exposure_id, {})
        donor_target = num((targets.get(exposure_id) or {}).get("donor_target_weight_pct"))
        status, action, detail = stage_state(exposure_id, promoted, allocation, donor_target, language)
        mapping_label = ("Gekoppeld" if language == "nl" else "Mapped") if mapped(promoted) else ("Onopgelost" if language == "nl" else "Unresolved")
        if allocation.get("selected") is True:
            detail = selected_explanation(allocation, language)
        rows.append([
            e(exposure_name(exposure_id, language, promoted.get("lane_name"))),
            candidate_marker(exposure_id, promoted),
            e(mapping_label),
            e(pct(donor_target, language)),
            e(status),
            e(f"{detail}; {action}"),
        ])
    return table(headers, rows, "wide-table promoted-mapping-table")


def section_13(sync: dict[str, Any], preferred: dict[str, Any], allocator: dict[str, Any], language: str) -> str:
    allocations = allocation_index(preferred)
    lanes = lane_index(sync)
    targets = target_index(sync)
    headers = (
        ["Exposure", "ETF", "Huidig", "Donordoel", "Fase-1-doel", "Status", "Actie", "Toelichting"]
        if language == "nl" else
        ["Exposure", "ETF", "Current", "Donor target", "Stage-1 target", "Status", "Action", "Explanation"]
    )
    rows: list[list[str]] = []
    ordered_ids: list[str] = []
    for allocation in preferred.get("allocation_rows") or []:
        if isinstance(allocation, dict):
            ordered_ids.append(str(allocation.get("exposure_id")))
    for promoted in promoted_rows(sync):
        exposure_id = str(promoted.get("exposure_id"))
        if exposure_id not in ordered_ids:
            ordered_ids.append(exposure_id)

    for exposure_id in ordered_ids:
        sync_row = lanes.get(exposure_id, {})
        allocation = allocations.get(exposure_id, {})
        donor_target = num((targets.get(exposure_id) or {}).get("donor_target_weight_pct"))
        stage_target = num(allocation.get("variant_target_weight_pct"))
        status, action, detail = stage_state(exposure_id, sync_row, allocation, donor_target, language)
        rows.append([
            e(exposure_name(exposure_id, language, sync_row.get("lane_name"))),
            candidate_marker(exposure_id, sync_row),
            e(pct(sync_row.get("current_eu_weight_pct"), language)),
            e(pct(donor_target, language)),
            e(pct(stage_target, language)),
            e(status),
            e(action),
            e(detail),
        ])

    summary = preferred.get("summary") if isinstance(preferred.get("summary"), dict) else {}
    current = allocator.get("current_portfolio") if isinstance(allocator.get("current_portfolio"), dict) else {}
    nav = num(current.get("nav_eur"), 1.0)
    current_cash = num(current.get("cash_eur")) / nav * 100.0
    target_cash = num(summary.get("projected_cash_weight_pct"))
    rows.append([
        e("Cash"), e("CASH"), e(pct(current_cash, language)), e("—"), e(pct(target_cash, language)),
        e("Reserve na fase 1" if language == "nl" else "Post-Stage-1 reserve"),
        e("Alleen na afzonderlijke activatie" if language == "nl" else "Only after separate activation"),
        e((f"Bruto schaduwaankopen {money(summary.get('gross_buy_value_eur'), language)}." if language == "nl" else f"Gross shadow purchases {money(summary.get('gross_buy_value_eur'), language)}.")),
    ])
    return table(headers, rows, "wide-table promoted-mapping-final-table")


def apply(manifest_path: Path, allocator_path: Path, sync_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    allocator = json.loads(allocator_path.read_text(encoding="utf-8"))
    sync = json.loads(sync_path.read_text(encoding="utf-8"))
    preferred = preferred_variant(allocator)

    mapped_count = sum(1 for row in promoted_rows(sync) if mapped(row))
    promoted_count = len(promoted_rows(sync))
    for language, files in (manifest.get("languages") or {}).items():
        if language not in {"nl", "en"} or not isinstance(files, dict):
            continue
        html_path = Path(str(files.get("html") or ""))
        pdf_path = Path(str(files.get("pdf") or ""))
        text = html_path.read_text(encoding="utf-8")
        replacements = {
            "2": section_2(sync, preferred, language),
            "4": section_4(sync, preferred, language),
            "11": section_11(sync, preferred, language),
            "13": section_13(sync, preferred, allocator, language),
        }
        for section_id, content in replacements.items():
            text = replace_section(text, section_id, content)
        html_path.write_text(text, encoding="utf-8")
        HTML(string=text, base_url=str(html_path.parent.resolve())).write_pdf(pdf_path)
        files["promoted_candidate_visibility"] = "registry_identity_allocator_status_separated_v1"

    manifest["promoted_candidate_visibility"] = {
        "applied": True,
        "source_allocator": str(allocator_path),
        "source_sync_shadow": str(sync_path),
        "sections_reconciled": list(SECTIONS),
        "promoted_exposure_count": promoted_count,
        "mapped_promoted_exposure_count": mapped_count,
        "unmapped_promoted_exposure_count": promoted_count - mapped_count,
        "candidate_identity_source": "synchronization_registry",
        "target_and_stage_source": "policy_allocator",
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Keep mapped promoted UCITS candidates visible independently of allocator selection")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--allocator", type=Path, required=True)
    parser.add_argument("--sync-shadow", type=Path, required=True)
    args = parser.parse_args()
    apply(args.manifest, args.allocator, args.sync_shadow)
    print(args.manifest)


if __name__ == "__main__":
    main()
