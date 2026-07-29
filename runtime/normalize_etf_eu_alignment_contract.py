from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


STATUS_REASON = {
    "trading_line_unverified": "trading_line_unverified",
    "identity_unverified": "ucits_identity_unverified",
    "unmapped": "ucits_identity_unverified",
    "policy_blocked": "product_type_blocked",
    "kid_missing": "kid_missing",
    "verified_product_line": "pricing_missing_or_stale",
}


def normalize(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Alignment shadow must be a JSON object")
    rows = payload.get("portfolio_alignment_rows") if isinstance(payload.get("portfolio_alignment_rows"), list) else []
    corrections: list[str] = []
    for row in rows:
        if not isinstance(row, dict) or row.get("exposure_id") == "cash":
            continue
        target = float(row.get("donor_target_weight_pct") or 0)
        current = float(row.get("eu_current_weight_pct") or 0)
        if target > 0 and current <= 0:
            if row.get("alignment_status") == "aligned_within_one_percentage_point":
                corrections.append(str(row.get("exposure_id")))
            row["alignment_status"] = "missing_donor_target_exposure"
            row["alignment_action"] = "resolve_ucits_implementation_then_review"
            reasons = list(row.get("divergence_reason_codes") or [])
            if not reasons:
                reasons = [STATUS_REASON.get(str(row.get("implementation_status") or ""), "existing_position_transition")]
            row["divergence_reason_codes"] = reasons

    summary = payload.get("portfolio_alignment_summary") if isinstance(payload.get("portfolio_alignment_summary"), dict) else {}
    summary["aligned_row_count"] = sum(1 for row in rows if isinstance(row, dict) and row.get("alignment_status") == "aligned_within_one_percentage_point")
    summary["divergent_row_count"] = len(rows) - int(summary["aligned_row_count"])
    payload["portfolio_alignment_summary"] = summary

    validation = payload.get("validation") if isinstance(payload.get("validation"), dict) else {}
    validation["unexplained_portfolio_divergences"] = [
        str(row.get("exposure_id"))
        for row in rows
        if isinstance(row, dict)
        and row.get("alignment_status") != "aligned_within_one_percentage_point"
        and not (row.get("divergence_reason_codes") or [])
    ]
    validation["zero_weight_alignment_corrections"] = corrections
    validation["zero_weight_exposure_alignment_rule"] = "target_positive_and_actual_zero_is_always_missing"
    payload["validation"] = validation
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize EU alignment semantics for absent donor exposures")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    normalize(args.path)
    print(args.path)


if __name__ == "__main__":
    main()
