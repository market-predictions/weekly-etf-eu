from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "yahoo_fallback_gate_shadow_evidence_v1"
REQUIRED_KINDS = {
    "yahoo_ucits_close_diagnostics",
    "yahoo_fallback_gate_evaluation",
    "yahoo_completed_session_gate",
    "twelve_data_symbol_discovery",
    "yahoo_cross_source_gate",
    "issuer_reference_sanity_gate",
    "ishares_reference_endpoint_discovery",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(path: Path) -> None:
    payload = load_json(path)
    errors: list[str] = []
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version_mismatch")
    if payload.get("validation_status") != "passed":
        errors.append("validation_status_must_be_passed")
    if payload.get("all_rows_blocked_until_contract_gates_pass") is not True:
        errors.append("all_rows_blocked_flag_required")
    for flag in [
        "completed_session_gate_evidence_present",
        "cross_source_gate_evidence_present",
        "issuer_reference_sanity_gate_evidence_present",
        "ishares_reference_endpoint_discovery_evidence_present",
    ]:
        if payload.get(flag) is not True:
            errors.append(f"{flag}_required")
    for field in ["valuation_authority", "funding_authority", "portfolio_mutation", "production_delivery"]:
        if payload.get(field) is not False:
            errors.append(f"{field}_must_be_false")
    artifacts = payload.get("required_artifacts") if isinstance(payload.get("required_artifacts"), list) else []
    kinds = {str(item.get("kind")) for item in artifacts if isinstance(item, dict)}
    missing = REQUIRED_KINDS - kinds
    if missing:
        errors.append("missing_required_kinds:" + ",".join(sorted(missing)))
    for idx, item in enumerate(artifacts):
        if not isinstance(item, dict):
            errors.append(f"artifact_{idx}_must_be_object")
            continue
        if item.get("exists") is not True:
            errors.append(f"artifact_{idx}_exists_must_be_true")
        if not item.get("path"):
            errors.append(f"artifact_{idx}_path_required")
        if not item.get("sha256") or len(str(item.get("sha256"))) != 64:
            errors.append(f"artifact_{idx}_sha256_required")
        if int(item.get("size_bytes") or 0) <= 0:
            errors.append(f"artifact_{idx}_size_positive_required")
    if errors:
        raise RuntimeError("YAHOO_FALLBACK_GATE_SHADOW_EVIDENCE_VALIDATION_FAILED: " + "; ".join(sorted(set(errors))))
    print(f"YAHOO_FALLBACK_GATE_SHADOW_EVIDENCE_VALIDATION_OK | artifact={path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()
    validate(Path(args.artifact))


if __name__ == "__main__":
    main()
