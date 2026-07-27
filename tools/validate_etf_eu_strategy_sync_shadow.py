from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class SyncShadowValidationError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise SyncShadowValidationError(f"Synchronization shadow is missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SyncShadowValidationError("Synchronization shadow must be a JSON object")
    return payload


def validate(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_eu_strategy_sync_shadow_v2":
        blockers.append("unexpected schema_version")
    if payload.get("artifact_type") != "etf_eu_strategy_synchronization_shadow":
        blockers.append("unexpected artifact_type")

    authority = payload.get("authority") if isinstance(payload.get("authority"), dict) else {}
    if authority.get("shadow_only") is not True:
        blockers.append("shadow_only must be true")
    for key in ("portfolio_mutation", "funding_authority", "execution_authority", "production_delivery_authority"):
        if authority.get(key) is not False:
            blockers.append(f"{key} must be false")

    shared = payload.get("shared_strategy") if isinstance(payload.get("shared_strategy"), dict) else {}
    target = payload.get("shared_portfolio_target") if isinstance(payload.get("shared_portfolio_target"), dict) else {}
    if shared.get("source_repository") != "market-predictions/weekly-etf":
        blockers.append("shared strategy source repository mismatch")
    if target.get("source_repository") != "market-predictions/weekly-etf":
        blockers.append("shared portfolio target source repository mismatch")
    if not shared.get("source_run_id") or not shared.get("report_date"):
        blockers.append("shared strategy lineage is incomplete")
    if str(shared.get("source_run_id")) != str(target.get("source_run_id")):
        blockers.append("strategy and portfolio target source run IDs differ")

    rows = payload.get("exposure_rows") if isinstance(payload.get("exposure_rows"), list) else []
    promoted = payload.get("promoted_exposure_comparison") if isinstance(payload.get("promoted_exposure_comparison"), list) else []
    alignment = payload.get("portfolio_alignment_rows") if isinstance(payload.get("portfolio_alignment_rows"), list) else []
    if not rows:
        blockers.append("exposure_rows is empty")
    if not alignment:
        blockers.append("portfolio_alignment_rows is empty")
    if len(promoted) != int(shared.get("promoted_count") or 0):
        blockers.append("promoted exposure count does not match shared strategy")

    allowed = set(payload.get("allowed_divergence_reason_codes") or [])
    exposure_ids: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            blockers.append("exposure row is not an object")
            continue
        exposure_id = str(row.get("exposure_id") or "")
        exposure_ids.append(exposure_id)
        if not exposure_id:
            blockers.append("exposure row has no exposure_id")
        if row.get("portfolio_mutation") is not False or row.get("allocation_authority") is not False:
            blockers.append(f"exposure {exposure_id} violates authority boundary")
        reasons = row.get("divergence_reason_codes") if isinstance(row.get("divergence_reason_codes"), list) else []
        invalid = sorted(set(reasons) - allowed)
        if invalid:
            blockers.append(f"exposure {exposure_id} has invalid reason codes: {', '.join(invalid)}")
        if row.get("promoted") is True and row.get("divergence_from_promoted_exposure") is True and not reasons:
            blockers.append(f"promoted exposure {exposure_id} has unexplained divergence")

    duplicates = sorted({value for value in exposure_ids if value and exposure_ids.count(value) > 1})
    if duplicates:
        blockers.append("duplicate exposure IDs: " + ", ".join(duplicates))

    donor_alignment_ids: set[str] = set()
    eu_alignment_tickers: set[str] = set()
    for row in alignment:
        if not isinstance(row, dict):
            blockers.append("portfolio alignment row is not an object")
            continue
        exposure_id = str(row.get("exposure_id") or "")
        if not exposure_id:
            blockers.append("portfolio alignment row has no exposure_id")
        if float(row.get("donor_target_weight_pct") or 0) > 0 and exposure_id != "cash":
            donor_alignment_ids.add(exposure_id)
        eu_alignment_tickers.update(str(ticker) for ticker in (row.get("eu_current_tickers") or []) if ticker and ticker != "CASH")
        if row.get("portfolio_mutation") is not False or row.get("allocation_authority") is not False:
            blockers.append(f"portfolio alignment {exposure_id} violates authority boundary")
        reasons = row.get("divergence_reason_codes") if isinstance(row.get("divergence_reason_codes"), list) else []
        invalid = sorted(set(reasons) - allowed)
        if invalid:
            blockers.append(f"portfolio alignment {exposure_id} has invalid reason codes: {', '.join(invalid)}")
        if row.get("alignment_status") != "aligned_within_one_percentage_point" and not reasons:
            blockers.append(f"portfolio alignment {exposure_id} has unexplained divergence")

    expected_target_count = int(target.get("exposure_target_count") or 0)
    if len(donor_alignment_ids) != expected_target_count:
        blockers.append("not every donor target exposure is represented in portfolio alignment")

    eu_portfolio = payload.get("eu_portfolio") if isinstance(payload.get("eu_portfolio"), dict) else {}
    if len(eu_alignment_tickers) != int(eu_portfolio.get("position_count") or 0):
        blockers.append("not every current EU position is represented in portfolio alignment")

    summary = payload.get("portfolio_alignment_summary") if isinstance(payload.get("portfolio_alignment_summary"), dict) else {}
    coverage = float(summary.get("exact_exposure_coverage_pct_of_donor_invested_target") or 0)
    if coverage < 0 or coverage > 100.0001:
        blockers.append("portfolio exposure coverage is outside 0-100%")
    if int(summary.get("aligned_row_count") or 0) + int(summary.get("divergent_row_count") or 0) != len(alignment):
        blockers.append("portfolio alignment row counts do not reconcile")

    validation = payload.get("validation") if isinstance(payload.get("validation"), dict) else {}
    if validation.get("unexplained_promoted_divergences") not in ([], None):
        blockers.append("validation reports unexplained promoted divergences")
    if validation.get("unexplained_portfolio_divergences") not in ([], None):
        blockers.append("validation reports unexplained portfolio divergences")
    if validation.get("invalid_reason_codes") not in ([], None):
        blockers.append("validation reports invalid reason codes")
    if validation.get("portfolio_target_exposure_count") != expected_target_count:
        blockers.append("validation portfolio target exposure count mismatch")
    if validation.get("portfolio_alignment_row_count") != len(alignment):
        blockers.append("validation portfolio alignment row count mismatch")
    if validation.get("portfolio_mutation") is not False:
        blockers.append("validation portfolio_mutation must be false")

    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate EU ETF strategy and portfolio synchronization shadow")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    payload = _load(args.path)
    blockers = validate(payload)
    result = {
        "artifact_type": "etf_eu_strategy_sync_shadow_validation",
        "path": str(args.path),
        "valid": not blockers,
        "blockers": blockers,
        "exposure_count": len(payload.get("exposure_rows") or []),
        "promoted_count": len(payload.get("promoted_exposure_comparison") or []),
        "portfolio_alignment_count": len(payload.get("portfolio_alignment_rows") or []),
        "legacy_position_count": len(payload.get("legacy_current_positions") or []),
    }
    print(json.dumps(result, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
