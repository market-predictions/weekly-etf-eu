from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Overlap review must be a JSON object")
    return payload


def num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def validate(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_eu_incumbent_overlap_review_v1":
        blockers.append("unexpected schema_version")
    for key in ("portfolio_mutation", "funding_authority", "execution_authority", "production_delivery_authority"):
        if payload.get(key) is not False:
            blockers.append(f"{key} must be false")
    methodology = payload.get("methodology") if isinstance(payload.get("methodology"), dict) else {}
    if methodology.get("lower_bound_only") is not True:
        blockers.append("lower-bound methodology marker missing")
    if "zero_measured_overlap_is_not_zero_actual_overlap" not in str(methodology.get("zero_overlap_guard") or ""):
        blockers.append("zero-overlap guard missing")

    pairs = [row for row in payload.get("pairwise_overlap_rows") or [] if isinstance(row, dict)]
    required_pairs = {("VWCE", "SXR8"), ("VWCE", "VVSM"), ("SXR8", "VVSM"), ("VWCE", "LOCK"), ("SXR8", "LOCK")}
    actual_pairs = {(str(row.get("left_fund")), str(row.get("right_fund"))) for row in pairs}
    if not required_pairs.issubset(actual_pairs):
        blockers.append("required pairwise overlap rows missing")
    for row in pairs:
        if num(row.get("measured_overlap_lower_bound_pct")) < 0:
            blockers.append(f"negative overlap: {row.get('left_fund')}:{row.get('right_fund')}")
        if row.get("full_holdings_coverage") is not True and row.get("zero_measured_overlap_means_zero_actual_overlap") is True:
            blockers.append(f"false zero-overlap claim: {row.get('left_fund')}:{row.get('right_fund')}")
        if row.get("full_holdings_coverage") is not True and "lower_bound_only" not in str(row.get("interpretation") or ""):
            blockers.append(f"incomplete pair not labeled lower-bound: {row.get('left_fund')}:{row.get('right_fund')}")

    embedded = payload.get("portfolio_embedded_exposure_lower_bounds") if isinstance(payload.get("portfolio_embedded_exposure_lower_bounds"), dict) else {}
    if num(embedded.get("semiconductor_pct_nav")) <= 0:
        blockers.append("documented embedded semiconductor exposure was not measured")
    if not str(embedded.get("cybersecurity_measurement_warning") or ""):
        blockers.append("cybersecurity coverage warning missing")

    dispositions = {str(row.get("ticker")): row for row in payload.get("incumbent_dispositions") or [] if isinstance(row, dict)}
    if set(dispositions) != {"VWCE", "SXR8", "EUNA"}:
        blockers.append("incumbent disposition set must be VWCE, SXR8 and EUNA")
    for ticker, row in dispositions.items():
        if row.get("stage_1_action") != "hold":
            blockers.append(f"{ticker} stage-one action must remain hold in shadow review")
    if dispositions.get("SXR8", {}).get("shadow_disposition") != "retain_stage_1_then_prioritize_for_overlap_reduction_review":
        blockers.append("SXR8 overlap-reduction disposition missing")
    if dispositions.get("EUNA", {}).get("shadow_disposition") != "retain_pending_explicit_risk_budget_decision":
        blockers.append("EUNA risk-budget disposition missing")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    payload = load(args.artifact)
    blockers = validate(payload)
    print(json.dumps({"valid": not blockers, "blockers": blockers}, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
