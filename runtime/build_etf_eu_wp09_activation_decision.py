from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build(evidence: dict[str, Any], evidence_path: Path, output: Path, manifest_path: Path) -> None:
    rows = evidence.get("candidates") if isinstance(evidence.get("candidates"), list) else []
    gate_rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    for row in rows:
        symbol = str(row.get("symbol") or "UNKNOWN")
        identity_pass = bool((row.get("identity") or {}).get("pass"))
        kid_pass = bool((row.get("kid") or {}).get("pass"))
        close_pass = (row.get("market_evidence") or {}).get("accepted_completed_close") is not None
        quote_pass = (row.get("market_evidence") or {}).get("accepted_timestamped_bid_ask_size") is not None
        liquidity_pass = bool((row.get("liquidity") or {}).get("pass"))
        gates = {
            "exact_line_identity": identity_pass,
            "exact_current_official_kid": kid_pass,
            "accepted_current_eur_completed_close": close_pass,
            "timestamped_bid_ask_quote_size": quote_pass,
            "accepted_liquidity_measurement": liquidity_pass,
        }
        failed = [name for name, passed in gates.items() if not passed]
        blockers.extend(f"{symbol}:{name}" for name in failed)
        gate_rows.append({
            "symbol": symbol,
            "isin": row.get("isin"),
            "gates": gates,
            "all_evidence_gates_pass": not failed,
            "source_blockers": row.get("blockers") or [],
        })

    donor = evidence.get("donor_reunderwriting") if isinstance(evidence.get("donor_reunderwriting"), dict) else {}
    donor_current = bool(donor.get("both_exposures_present") and donor.get("current_report_date"))
    donor_fresh_add = bool(donor.get("any_fresh_add_direction"))
    if not donor_current:
        blockers.append("donor_reunderwriting_not_current_or_complete")
    if not donor_fresh_add:
        blockers.append("donor_fresh_add_direction_absent")

    all_evidence = bool(gate_rows) and all(row["all_evidence_gates_pass"] for row in gate_rows)
    evidence_decision = "authorize" if all_evidence and donor_current and donor_fresh_add else "blocked"
    evidence_passed = evidence_decision == "authorize"
    payload = {
        "schema_version": "etf_eu_wp09_stage_1_activation_decision_v1",
        "artifact_type": "etf_eu_wp09_stage_1_activation_decision",
        "run_id": evidence.get("run_id"),
        "generated_at_utc": utc_now(),
        "evidence_path": str(evidence_path),
        "evidence_sha256": sha256_file(evidence_path),
        "decision": evidence_decision,
        "decision_reason": "all evidence and donor fresh-add gates passed" if evidence_passed else "required activation evidence and/or donor fresh-add authority is incomplete",
        "gate_rows": gate_rows,
        "donor_gate": {
            "current_reunderwriting_present": donor_current,
            "fresh_add_direction_present": donor_fresh_add,
            "donor_report_date": donor.get("current_report_date"),
            "rows": donor.get("rows"),
        },
        "blockers": sorted(set(blockers)),
        "stage_1_activation_authorized": False,
        "authorization_package_required_after_evidence_pass": True,
        "official_state_applied": False,
        "executable_trade_intents": [],
        "authority": {
            "portfolio_mutation": False,
            "ledger_write": False,
            "funding_authority": False,
            "execution_authority": False,
            "activation_authority": False,
            "production_delivery_authority": False,
        },
        "protected_state": evidence.get("protected_state"),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    manifest = {
        "schema_version": "etf_eu_wp09_cutover_readiness_manifest_v1",
        "artifact_type": "etf_eu_wp09_cutover_readiness_manifest",
        "run_id": evidence.get("run_id"),
        "generated_at_utc": utc_now(),
        "status": "blocked_not_activation_ready" if not evidence_passed else "evidence_passed_pending_separate_authorization_package",
        "evidence_artifact": str(evidence_path),
        "evidence_sha256": sha256_file(evidence_path),
        "decision_artifact": str(output),
        "decision_sha256": sha256_file(output),
        "activation_ready": False,
        "stage_1_activation_authorized": False,
        "blocker_count": len(payload["blockers"]),
        "blockers": payload["blockers"],
        "protected_state": evidence.get("protected_state"),
        "portfolio_mutation": False,
        "ledger_write": False,
        "funding_authority": False,
        "execution_authority": False,
        "production_delivery_authority": False,
        "executable_trade_intents": [],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    build(load(args.evidence), args.evidence, args.output, args.manifest)
    print(args.output)
    print(args.manifest)


if __name__ == "__main__":
    main()
