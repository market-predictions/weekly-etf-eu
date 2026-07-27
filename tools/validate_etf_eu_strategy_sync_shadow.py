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
    if payload.get("schema_version") != "etf_eu_strategy_sync_shadow_v1":
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
    if shared.get("source_repository") != "market-predictions/weekly-etf":
        blockers.append("shared strategy source repository mismatch")
    if not shared.get("source_run_id") or not shared.get("report_date"):
        blockers.append("shared strategy lineage is incomplete")

    rows = payload.get("exposure_rows") if isinstance(payload.get("exposure_rows"), list) else []
    promoted = payload.get("promoted_exposure_comparison") if isinstance(payload.get("promoted_exposure_comparison"), list) else []
    if not rows:
        blockers.append("exposure_rows is empty")
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

    legacy = payload.get("legacy_current_positions") if isinstance(payload.get("legacy_current_positions"), list) else []
    eu_portfolio = payload.get("eu_portfolio") if isinstance(payload.get("eu_portfolio"), dict) else {}
    represented_tickers = {
        ticker
        for row in rows
        if isinstance(row, dict)
        for ticker in (row.get("current_eu_tickers") or [])
    }
    represented_tickers.update(str(row.get("ticker") or "") for row in legacy if isinstance(row, dict))
    represented_tickers.discard("")
    if len(represented_tickers) != int(eu_portfolio.get("position_count") or 0):
        blockers.append("not every current EU position is represented exactly once")

    validation = payload.get("validation") if isinstance(payload.get("validation"), dict) else {}
    if validation.get("unexplained_promoted_divergences") not in ([], None):
        blockers.append("validation reports unexplained promoted divergences")
    if validation.get("invalid_reason_codes") not in ([], None):
        blockers.append("validation reports invalid reason codes")
    if validation.get("portfolio_mutation") is not False:
        blockers.append("validation portfolio_mutation must be false")

    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate EU ETF strategy synchronization shadow")
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
        "legacy_position_count": len(payload.get("legacy_current_positions") or []),
    }
    print(json.dumps(result, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
