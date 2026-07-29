from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Evidence must be a JSON object")
    return payload


def validate(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_eu_wp09_fresh_product_evidence_v1":
        blockers.append("unexpected schema version")
    if payload.get("capture_attempted") is not True or payload.get("fresh_network_capture") is not True:
        blockers.append("fresh capture not attempted")
    if payload.get("cached_connectivity_promoted") is not False:
        blockers.append("cached connectivity was promoted")
    rows = payload.get("candidates") if isinstance(payload.get("candidates"), list) else []
    if {row.get("symbol") for row in rows if isinstance(row, dict)} != {"VVSM", "LOCK"}:
        blockers.append("candidate set must be exactly VVSM and LOCK")
    for row in rows:
        if not isinstance(row, dict):
            blockers.append("invalid candidate row")
            continue
        symbol = str(row.get("symbol") or "UNKNOWN")
        identity = row.get("identity") if isinstance(row.get("identity"), dict) else {}
        kid = row.get("kid") if isinstance(row.get("kid"), dict) else {}
        market = row.get("market_evidence") if isinstance(row.get("market_evidence"), dict) else {}
        liquidity = row.get("liquidity") if isinstance(row.get("liquidity"), dict) else {}
        if identity.get("pass") is not True:
            blockers.append(f"{symbol}: exact identity did not pass")
        if kid.get("pass") is not True:
            blockers.append(f"{symbol}: exact KID did not pass")
        if market.get("accepted_completed_close") is None and "accepted_current_xetra_eur_completed_close_not_captured" not in (row.get("blockers") or []):
            blockers.append(f"{symbol}: missing close lacks explicit blocker")
        if market.get("accepted_timestamped_bid_ask_size") is None and "timestamped_xetra_bid_ask_and_quote_size_not_captured" not in (row.get("blockers") or []):
            blockers.append(f"{symbol}: missing quote lacks explicit blocker")
        if liquidity.get("pass") is not True and not liquidity.get("blocker"):
            blockers.append(f"{symbol}: failed liquidity lacks blocker")
        if row.get("activation_evidence_pass") is True and row.get("blockers"):
            blockers.append(f"{symbol}: activation pass conflicts with blockers")
    donor = payload.get("donor_reunderwriting") if isinstance(payload.get("donor_reunderwriting"), dict) else {}
    if donor.get("both_exposures_present") is not True:
        blockers.append("donor re-underwriting does not contain both exposures")
    if not donor.get("current_report_date"):
        blockers.append("donor report date missing")
    protected = payload.get("protected_state") if isinstance(payload.get("protected_state"), dict) else {}
    for key in ("portfolio_sha256", "ledger_sha256"):
        if not protected.get(key):
            blockers.append(f"protected state {key} missing")
    if protected.get("portfolio_mutation") is not False or protected.get("ledger_write") is not False:
        blockers.append("protected state boundary violated")
    authority = payload.get("authority") if isinstance(payload.get("authority"), dict) else {}
    for key in ("funding_authority", "execution_authority", "activation_authority", "production_delivery_authority"):
        if authority.get(key) is not False:
            blockers.append(f"authority {key} must be false")
    if payload.get("executable_trade_intents") not in ([], None):
        blockers.append("evidence artifact contains executable trade intents")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    payload = load(args.path)
    blockers = validate(payload)
    result = {
        "artifact_type": "etf_eu_wp09_fresh_product_evidence_validation",
        "valid": not blockers,
        "blockers": blockers,
        "candidate_count": len(payload.get("candidates") or []),
        "evidence_summary": payload.get("summary"),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
