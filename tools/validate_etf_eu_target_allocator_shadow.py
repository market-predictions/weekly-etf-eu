from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Allocator artifact must be a JSON object")
    return payload


def num(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def validate(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_eu_target_allocator_shadow_v1":
        blockers.append("unexpected schema_version")
    authority = payload.get("authority") if isinstance(payload.get("authority"), dict) else {}
    for key in ("portfolio_mutation", "funding_authority", "execution_authority", "production_delivery_authority"):
        if authority.get(key) is not False:
            blockers.append(f"authority.{key} must be false")
    if authority.get("shadow_only") is not True:
        blockers.append("authority.shadow_only must be true")

    variants = [item for item in (payload.get("variants") or []) if isinstance(item, dict)]
    ids = {str(item.get("variant_id")) for item in variants}
    required = {"strict_mapped_replication", "efficient_max_eight_positions", "staged_cash_first_50pct"}
    if ids != required:
        blockers.append("required allocator variants missing or duplicated")

    by_id = {str(item.get("variant_id")): item for item in variants}
    for variant in variants:
        variant_id = str(variant.get("variant_id"))
        summary = variant.get("summary") if isinstance(variant.get("summary"), dict) else {}
        if summary.get("cash_nonnegative") is not True or num(summary.get("projected_cash_eur")) < -0.01:
            blockers.append(f"{variant_id}: projected cash is negative")
        if variant_id != "strict_mapped_replication" and summary.get("within_position_limit") is not True:
            blockers.append(f"{variant_id}: position limit exceeded")
        for row in variant.get("allocation_rows") or []:
            if not isinstance(row, dict):
                continue
            order = row.get("order") if isinstance(row.get("order"), dict) else {}
            target_shares = num(order.get("target_shares"))
            if target_shares != int(target_shares):
                blockers.append(f"{variant_id}:{row.get('exposure_id')}: non-whole target shares")
            if row.get("eligible") is not True and target_shares > 0:
                blockers.append(f"{variant_id}:{row.get('exposure_id')}: blocked exposure received shares")
            if row.get("selected") is True and not row.get("candidate"):
                blockers.append(f"{variant_id}:{row.get('exposure_id')}: selected without candidate")
        for row in variant.get("legacy_rows") or []:
            if isinstance(row, dict) and num(row.get("target_shares")) != int(num(row.get("target_shares"))):
                blockers.append(f"{variant_id}:{row.get('ticker')}: non-whole legacy shares")

    strict = by_id.get("strict_mapped_replication", {})
    staged = by_id.get("staged_cash_first_50pct", {})
    if num((staged.get("summary") or {}).get("gross_turnover_eur")) >= num((strict.get("summary") or {}).get("gross_turnover_eur")):
        blockers.append("staged variant does not reduce turnover versus strict replication")
    if staged.get("retain_legacy_positions") is not True:
        blockers.append("staged variant must retain legacy positions")
    if payload.get("preferred_shadow_variant") != "staged_cash_first_50pct":
        blockers.append("preferred shadow variant is not staged_cash_first_50pct")
    assumptions = payload.get("assumptions") if isinstance(payload.get("assumptions"), dict) else {}
    if assumptions.get("prices_non_authoritative_connectivity_only") is not True:
        blockers.append("non-authoritative price limitation missing")
    if assumptions.get("bid_ask_spread_not_directly_observed") is not True:
        blockers.append("spread limitation missing")
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
