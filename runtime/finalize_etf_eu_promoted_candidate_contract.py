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
    lane_index,
    money,
    num,
    pct,
    preferred_variant,
    promoted_rows,
    replace_section,
    table,
)
from runtime.reconcile_etf_eu_promoted_candidate_visibility import (  # noqa: E402
    candidate_marker,
    stage_state,
    target_index,
)


def section_9(sync: dict[str, Any], preferred: dict[str, Any], language: str) -> str:
    allocations = allocation_index(preferred)
    targets = target_index(sync)
    headers = (
        ["Drijver", "Eerste-orde-effect", "Tweede-orde-effect", "Waarschijnlijke winnaars", "ETF EU-implicatie", "Timing", "Vertrouwen"]
        if language == "nl" else
        ["Driver", "First-order effect", "Second-order effect", "Likely winners", "ETF EU implication", "Timing", "Confidence"]
    )
    rows: list[list[str]] = []
    for promoted in promoted_rows(sync):
        exposure_id = str(promoted.get("exposure_id"))
        allocation = allocations.get(exposure_id, {})
        donor_target = num((targets.get(exposure_id) or {}).get("donor_target_weight_pct"))
        status, action, _ = stage_state(exposure_id, promoted, allocation, donor_target, language)
        rows.append([
            e(exposure_name(exposure_id, language, promoted.get("lane_name"))),
            e(promoted.get("shared_why_now") or promoted.get("shared_evidence_summary") or "—"),
            e(status),
            candidate_marker(exposure_id, promoted),
            e(action),
            e("Direct" if language == "nl" else "Immediate"),
            e(("Hoog" if language == "nl" else "High") if num(promoted.get("shared_rank"), 99) <= 3 else ("Gemiddeld" if language == "nl" else "Medium")),
        ])
    return table(headers, rows, "wide-table promoted-mapping-table")


def section_13(sync: dict[str, Any], preferred: dict[str, Any], allocator: dict[str, Any], language: str) -> str:
    allocations = allocation_index(preferred)
    lanes = lane_index(sync)
    targets = target_index(sync)
    headers = (
        ["Ticker/exposure", "ETF", "Huidig gewicht", "Doelgewicht", "Delta gewicht", "Actie", "Kapitaalbestemming", "Score", "Toelichting", "Override-status"]
        if language == "nl" else
        ["Ticker/exposure", "ETF", "Current weight", "Target weight", "Weight delta", "Action", "Capital destination", "Score", "Explanation", "Override status"]
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
        current_weight = num(sync_row.get("current_eu_weight_pct"))
        stage_target = num(allocation.get("variant_target_weight_pct"))
        status, action, detail = stage_state(exposure_id, sync_row, allocation, donor_target, language)
        capital = ("Cash" if language == "nl" else "Cash") if allocation.get("selected") is True else ("Geen toewijzing" if language == "nl" else "No allocation")
        explanation = (
            f"Donordoel {pct(donor_target, language)}; {status}; {detail}"
            if language == "nl" else
            f"Donor target {pct(donor_target, language)}; {status}; {detail}"
        )
        rows.append([
            e(exposure_name(exposure_id, language, sync_row.get("lane_name"))),
            candidate_marker(exposure_id, sync_row),
            e(pct(current_weight, language)),
            e(pct(stage_target, language)),
            e(pct(stage_target - current_weight, language, signed=True)),
            e(action),
            e(capital),
            e(f"{num(sync_row.get('shared_score')):.2f}" if sync_row else "—"),
            e(explanation),
            e("Schaduw – geen uitvoering" if language == "nl" else "Shadow – no execution"),
        ])

    summary = preferred.get("summary") if isinstance(preferred.get("summary"), dict) else {}
    current = allocator.get("current_portfolio") if isinstance(allocator.get("current_portfolio"), dict) else {}
    nav = num(current.get("nav_eur"), 1.0)
    current_cash = num(current.get("cash_eur")) / nav * 100.0
    target_cash = num(summary.get("projected_cash_weight_pct"))
    rows.append([
        e("Cash"), e("CASH"), e(pct(current_cash, language)), e(pct(target_cash, language)), e(pct(target_cash - current_cash, language, signed=True)),
        e("Fase 1 financieren en reserve aanhouden" if language == "nl" else "Fund Stage 1 and retain reserve"),
        e("VVSM en LOCK" if language == "nl" else "VVSM and LOCK"), e("—"),
        e((f"Bruto schaduwaankopen {money(summary.get('gross_buy_value_eur'), language)}." if language == "nl" else f"Gross shadow purchases {money(summary.get('gross_buy_value_eur'), language)}.")),
        e("Schaduw – geen uitvoering" if language == "nl" else "Shadow – no execution"),
    ])

    dispositions = {
        str(row.get("ticker")): row
        for row in (allocator.get("incumbent_overlap_review") or {}).get("incumbent_dispositions") or []
        if isinstance(row, dict)
    }
    for legacy in preferred.get("legacy_rows") or []:
        if not isinstance(legacy, dict):
            continue
        ticker = str(legacy.get("ticker"))
        weight = num((dispositions.get(ticker) or {}).get("current_weight_pct"))
        rows.append([
            e(ticker), e(str(legacy.get("fund_name") or ticker)), e(pct(weight, language)), e(pct(weight, language)), e(pct(0, language)),
            e("Aanhouden in fase 1" if language == "nl" else "Hold in Stage 1"),
            e("Geen verkoop" if language == "nl" else "No sale"), e("—"),
            e("Bestaande positie blijft ongewijzigd; aparte herbeoordeling vereist." if language == "nl" else "Incumbent position remains unchanged; separate re-underwriting required."),
            e("Schaduw – geen uitvoering" if language == "nl" else "Shadow – no execution"),
        ])
    return table(headers, rows, "wide-table final-alignment-table promoted-mapping-final-table")


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
        text = replace_section(text, "9", section_9(sync, preferred, language))
        text = replace_section(text, "13", section_13(sync, preferred, allocator, language))
        html_path.write_text(text, encoding="utf-8")
        HTML(string=text, base_url=str(html_path.parent.resolve())).write_pdf(pdf_path)
        files["promoted_candidate_contract"] = "all_promoted_rows_plus_donor_final_action_headers_v1"
    manifest["promoted_candidate_contract"] = {
        "applied": True,
        "sections_finalized": ["9", "13"],
        "all_promoted_rows_visible": True,
        "donor_final_action_header_contract_preserved": True,
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Finalize promoted candidate visibility under the donor table contract")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--allocator", type=Path, required=True)
    parser.add_argument("--sync-shadow", type=Path, required=True)
    args = parser.parse_args()
    apply(args.manifest, args.allocator, args.sync_shadow)
    print(args.manifest)


if __name__ == "__main__":
    main()
