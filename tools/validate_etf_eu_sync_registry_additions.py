from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml


ISIN_RE = re.compile(r"^[A-Z]{2}[A-Z0-9]{10}$")
KID_AVAILABILITY = {"available", "unverified"}
KID_ARTIFACT_STATUS = {"captured", "available_not_captured", "unverified"}


def load(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def validate(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "ucits_symbol_registry_sync_additions_v1":
        blockers.append("unexpected schema_version")
    if payload.get("status") != "shadow_only":
        blockers.append("supplemental registry must remain shadow_only")
    rules = payload.get("rules") if isinstance(payload.get("rules"), dict) else {}
    if rules.get("production_registry_overwrite") is not False:
        blockers.append("production registry overwrite must be false")
    if rules.get("mapping_does_not_authorize_allocation") is not True:
        blockers.append("allocation-authority boundary is missing")
    if rules.get("official_issuer_identity_required") is not True:
        blockers.append("official issuer identity rule is missing")
    if rules.get("exact_trading_line_required") is not True:
        blockers.append("exact trading-line rule is missing")
    if rules.get("exact_kid_artifact_required_for_cutover") is not True:
        blockers.append("exact KID artifact cutover rule is missing")

    funds = [row for row in (payload.get("funds") or []) if isinstance(row, dict)]
    if not funds:
        blockers.append("no supplemental funds")
        return blockers
    ids = [str(row.get("registry_id") or "") for row in funds]
    duplicates = sorted({value for value in ids if value and ids.count(value) > 1})
    if duplicates:
        blockers.append("duplicate registry IDs: " + ", ".join(duplicates))
    isins = [str(row.get("isin") or "").upper() for row in funds]
    duplicate_isins = sorted({value for value in isins if value and isins.count(value) > 1})
    if duplicate_isins:
        blockers.append("duplicate ISINs: " + ", ".join(duplicate_isins))

    for fund in funds:
        registry_id = str(fund.get("registry_id") or "")
        if not registry_id:
            blockers.append("fund without registry_id")
            continue
        isin = str(fund.get("isin") or "").upper()
        if not ISIN_RE.fullmatch(isin):
            blockers.append(f"{registry_id}: invalid ISIN")
        if fund.get("instrument_type") != "UCITS ETF":
            blockers.append(f"{registry_id}: only UCITS ETF is accepted in this supplemental layer")
        if fund.get("ucits_status") != "confirmed":
            blockers.append(f"{registry_id}: UCITS status is not confirmed")
        if fund.get("priips_kid_status") not in KID_AVAILABILITY:
            blockers.append(f"{registry_id}: invalid PRIIPs KID availability status")
        artifact_status = fund.get("kid_artifact_status")
        if artifact_status not in KID_ARTIFACT_STATUS:
            blockers.append(f"{registry_id}: invalid KID artifact status")
        if artifact_status == "captured" and not fund.get("kid_artifact_url"):
            blockers.append(f"{registry_id}: captured KID artifact URL missing")
        if artifact_status == "captured" and not fund.get("kid_document_date"):
            blockers.append(f"{registry_id}: captured KID document date missing")
        if artifact_status == "available_not_captured" and fund.get("priips_kid_status") != "available":
            blockers.append(f"{registry_id}: KID cannot be available-not-captured when availability is unverified")

        evidence = fund.get("evidence") if isinstance(fund.get("evidence"), dict) else {}
        if not evidence.get("issuer_product_page"):
            blockers.append(f"{registry_id}: issuer product-page evidence missing")
        if not evidence.get("exchange_reference"):
            blockers.append(f"{registry_id}: exchange reference missing")
        if "verified" not in str(evidence.get("identity_status") or ""):
            blockers.append(f"{registry_id}: identity evidence is not verified")

        lines = [line for line in (fund.get("trading_lines") or []) if isinstance(line, dict)]
        if not lines:
            blockers.append(f"{registry_id}: no trading line")
            continue
        primary = [line for line in lines if line.get("primary_line") is True]
        if len(primary) != 1:
            blockers.append(f"{registry_id}: exactly one primary line is required")
        for line in lines:
            if not line.get("exchange") or not line.get("venue_code") or not line.get("exchange_ticker") or not line.get("trading_currency"):
                blockers.append(f"{registry_id}: incomplete trading line")
            if not str(line.get("line_verification_status") or "").startswith("verified_ucits_trading_line"):
                blockers.append(f"{registry_id}: trading line is not verified")

    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate shadow UCITS synchronization registry additions")
    parser.add_argument("path", type=Path, nargs="?", default=Path("config/ucits_symbol_registry_sync_additions.yml"))
    args = parser.parse_args()
    payload = load(args.path)
    blockers = validate(payload)
    print(json.dumps({
        "artifact_type": "etf_eu_sync_registry_additions_validation",
        "path": str(args.path),
        "valid": not blockers,
        "blockers": blockers,
        "fund_count": len(payload.get("funds") or []),
        "captured_kid_count": sum(
            1 for row in (payload.get("funds") or [])
            if isinstance(row, dict) and row.get("kid_artifact_status") == "captured"
        ),
    }, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
