from __future__ import annotations

import argparse
import json
import math
from datetime import date
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Expected JSON object")
    return payload


def _num(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
        return result if math.isfinite(result) else default
    except (TypeError, ValueError):
        return default


def validate(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_eu_allocator_market_evidence_v1":
        blockers.append("unexpected schema_version")
    if payload.get("valuation_grade") is not False:
        blockers.append("market evidence must not claim valuation grade")
    if payload.get("funding_authority") is not False:
        blockers.append("market evidence must not have funding authority")
    if payload.get("portfolio_mutation") is not False:
        blockers.append("market evidence must not mutate portfolio")

    try:
        report_date = date.fromisoformat(str(payload.get("report_date")))
    except ValueError:
        blockers.append("invalid report_date")
        return blockers

    rows = [row for row in (payload.get("target_rows") or []) if isinstance(row, dict)]
    if len(rows) != 9:
        blockers.append(f"expected 9 donor target rows, found {len(rows)}")
    ids = [str(row.get("exposure_id") or "") for row in rows]
    if len(set(ids)) != len(ids):
        blockers.append("duplicate exposure IDs")

    priced_count = 0
    liquidity_pass_count = 0
    for row in rows:
        exposure_id = str(row.get("exposure_id") or "missing")
        if row.get("identity_gate_passed") is not True:
            blockers.append(f"{exposure_id}: identity gate failed")
        if not row.get("isin") or not row.get("exchange_ticker"):
            blockers.append(f"{exposure_id}: incomplete security identity")
        market = row.get("market") if isinstance(row.get("market"), dict) else {}
        if market.get("status") == "priced_completed_close":
            priced_count += 1
            try:
                close_date = date.fromisoformat(str(market.get("completed_close_date")))
                if close_date >= report_date:
                    blockers.append(f"{exposure_id}: close is not completed before report date")
            except ValueError:
                blockers.append(f"{exposure_id}: invalid completed-close date")
            if _num(market.get("completed_close_price_eur")) <= 0:
                blockers.append(f"{exposure_id}: invalid completed-close price")
            if int(_num(market.get("liquidity_session_count"))) < 10:
                blockers.append(f"{exposure_id}: insufficient liquidity observations")
            if _num(market.get("nonzero_volume_session_ratio")) <= 0:
                blockers.append(f"{exposure_id}: no nonzero-volume evidence")
        else:
            blockers.append(f"{exposure_id}: completed-close price missing")
        if row.get("liquidity_gate_passed") is True:
            liquidity_pass_count += 1
            if _num(market.get("median_daily_traded_value_eur")) < _num(row.get("liquidity_threshold_eur_per_day")):
                blockers.append(f"{exposure_id}: liquidity pass does not reconcile")
        if row.get("spread_status") == "fail" and "quote_spread_above_threshold" not in (row.get("blockers") or []):
            blockers.append(f"{exposure_id}: spread failure lacks blocker")
        if row.get("allocator_market_status") == "eligible_shadow_allocator" and (row.get("liquidity_gate_passed") is not True or row.get("spread_status") != "pass"):
            blockers.append(f"{exposure_id}: eligible status is inconsistent")

    if priced_count != len(rows):
        blockers.append(f"not all target rows priced: {priced_count}/{len(rows)}")
    if liquidity_pass_count < 7:
        blockers.append(f"fewer than 7 exposures pass preliminary liquidity: {liquidity_pass_count}")

    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    if int(_num(summary.get("target_count"))) != len(rows):
        blockers.append("summary target count mismatch")
    if int(_num(summary.get("priced_count"))) != priced_count:
        blockers.append("summary priced count mismatch")
    if int(_num(summary.get("liquidity_pass_count"))) != liquidity_pass_count:
        blockers.append("summary liquidity count mismatch")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate EU allocator market evidence")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    payload = _load(args.path)
    blockers = validate(payload)
    result = {
        "artifact_type": "etf_eu_allocator_market_evidence_validation",
        "path": str(args.path),
        "valid": not blockers,
        "blockers": blockers,
        "target_count": len(payload.get("target_rows") or []),
        "summary": payload.get("summary"),
    }
    print(json.dumps(result, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
