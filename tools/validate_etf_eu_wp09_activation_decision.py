from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Decision must be a JSON object")
    return payload


def validate(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_eu_wp09_stage_1_activation_decision_v1":
        blockers.append("unexpected decision schema")
    if payload.get("decision") not in {"authorize", "withhold", "blocked"}:
        blockers.append("invalid decision value")
    gate_rows = payload.get("gate_rows") if isinstance(payload.get("gate_rows"), list) else []
    if {row.get("symbol") for row in gate_rows if isinstance(row, dict)} != {"VVSM", "LOCK"}:
        blockers.append("decision candidate set mismatch")
    all_gates = bool(gate_rows) and all(row.get("all_evidence_gates_pass") is True for row in gate_rows)
    donor = payload.get("donor_gate") if isinstance(payload.get("donor_gate"), dict) else {}
    should_authorize_evidence = all_gates and donor.get("current_reunderwriting_present") is True and donor.get("fresh_add_direction_present") is True
    if payload.get("decision") == "authorize" and not should_authorize_evidence:
        blockers.append("authorize decision lacks all evidence and donor gates")
    if not should_authorize_evidence and payload.get("decision") != "blocked":
        blockers.append("incomplete gates must produce blocked decision")
    if payload.get("stage_1_activation_authorized") is not False:
        blockers.append("WP09 decision package may not authorize Stage 1 directly")
    if payload.get("official_state_applied") is not False:
        blockers.append("official state was applied")
    if payload.get("executable_trade_intents") not in ([], None):
        blockers.append("decision contains executable trade intents")
    authority = payload.get("authority") if isinstance(payload.get("authority"), dict) else {}
    for key in ("portfolio_mutation", "ledger_write", "funding_authority", "execution_authority", "activation_authority", "production_delivery_authority"):
        if authority.get(key) is not False:
            blockers.append(f"authority {key} must be false")
    if payload.get("decision") == "blocked" and not payload.get("blockers"):
        blockers.append("blocked decision has no blockers")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    payload = load(args.path)
    blockers = validate(payload)
    print(json.dumps({
        "artifact_type": "etf_eu_wp09_stage_1_activation_decision_validation",
        "valid": not blockers,
        "decision": payload.get("decision"),
        "blockers": blockers,
        "decision_blocker_count": len(payload.get("blockers") or []),
    }, indent=2, ensure_ascii=False))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
