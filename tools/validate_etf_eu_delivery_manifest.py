from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_delivery_manifest_v1"
ALLOWED_STATUS = {"blocked_design_only", "ready_for_future_delivery", "sent", "failed"}
ALLOWED_RECEIPT_STATUS = {"not_created", "pending", "created", "failed"}
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "run_id",
    "created_at_utc",
    "report_date",
    "status",
    "delivery_enabled",
    "gates",
    "artifacts",
    "receipt",
    "authority",
    "blockers",
}
REQUIRED_GATES = {
    "main_workflow_green",
    "dutch_first_report_contract_green",
    "fundability_rules_clear",
    "delivery_manifest_exists",
    "receipt_path_exists",
}
REQUIRED_ARTIFACTS = {
    "dutch_report_path",
    "english_report_path",
    "valuation_artifact_path",
    "validation_evidence_paths",
}
REQUIRED_RECEIPT = {"receipt_required", "receipt_path", "receipt_status"}
REQUIRED_AUTHORITY_FALSE = {
    "funding_authority",
    "portfolio_mutation",
    "valuation_grade_promotion",
    "candidate_promotion_to_fundable",
}
DELIVERY_AUTHORITY_FLAGS = {"pdf_generation", "email_delivery", "production_delivery"}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _missing(required: set[str], payload: dict[str, Any]) -> list[str]:
    return sorted(required - set(payload))


def _require_bool_mapping(name: str, payload: Any, required_keys: set[str]) -> dict[str, bool]:
    if not isinstance(payload, dict):
        raise RuntimeError(f"delivery manifest failed: {name} must be an object")
    missing = _missing(required_keys, payload)
    if missing:
        raise RuntimeError(f"delivery manifest failed: {name} missing required key(s): {', '.join(missing)}")
    for key in required_keys:
        if not isinstance(payload[key], bool):
            raise RuntimeError(f"delivery manifest failed: {name}.{key} must be boolean")
    return payload


def validate_manifest(path: Path) -> None:
    payload = _load(path)
    missing_top = _missing(REQUIRED_TOP_LEVEL, payload)
    if missing_top:
        raise RuntimeError(f"delivery manifest failed: missing top-level key(s): {', '.join(missing_top)}")

    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(f"delivery manifest failed: unsupported schema_version={payload['schema_version']}")

    status = payload["status"]
    if status not in ALLOWED_STATUS:
        raise RuntimeError(f"delivery manifest failed: unsupported status={status}")

    if not isinstance(payload["delivery_enabled"], bool):
        raise RuntimeError("delivery manifest failed: delivery_enabled must be boolean")

    gates = _require_bool_mapping("gates", payload["gates"], REQUIRED_GATES)

    artifacts = payload["artifacts"]
    if not isinstance(artifacts, dict):
        raise RuntimeError("delivery manifest failed: artifacts must be an object")
    missing_artifacts = _missing(REQUIRED_ARTIFACTS, artifacts)
    if missing_artifacts:
        raise RuntimeError(f"delivery manifest failed: artifacts missing required key(s): {', '.join(missing_artifacts)}")
    if not isinstance(artifacts["validation_evidence_paths"], list):
        raise RuntimeError("delivery manifest failed: artifacts.validation_evidence_paths must be a list")

    receipt = payload["receipt"]
    if not isinstance(receipt, dict):
        raise RuntimeError("delivery manifest failed: receipt must be an object")
    missing_receipt = _missing(REQUIRED_RECEIPT, receipt)
    if missing_receipt:
        raise RuntimeError(f"delivery manifest failed: receipt missing required key(s): {', '.join(missing_receipt)}")
    if not isinstance(receipt["receipt_required"], bool):
        raise RuntimeError("delivery manifest failed: receipt.receipt_required must be boolean")
    if receipt["receipt_status"] not in ALLOWED_RECEIPT_STATUS:
        raise RuntimeError(f"delivery manifest failed: unsupported receipt_status={receipt['receipt_status']}")

    authority = _require_bool_mapping("authority", payload["authority"], REQUIRED_AUTHORITY_FALSE | DELIVERY_AUTHORITY_FLAGS)
    for key in REQUIRED_AUTHORITY_FALSE:
        if authority[key] is not False:
            raise RuntimeError(f"delivery manifest failed: authority.{key} must remain false")

    all_gates_green = all(gates.values())
    if status == "blocked_design_only":
        if payload["delivery_enabled"] is not False:
            raise RuntimeError("delivery manifest failed: blocked_design_only requires delivery_enabled=false")
        for key in DELIVERY_AUTHORITY_FLAGS:
            if authority[key] is not False:
                raise RuntimeError(f"delivery manifest failed: blocked_design_only requires authority.{key}=false")
        if receipt["receipt_status"] != "not_created":
            raise RuntimeError("delivery manifest failed: blocked_design_only requires receipt_status=not_created")
        if not payload["blockers"]:
            raise RuntimeError("delivery manifest failed: blocked_design_only requires at least one blocker")

    if status == "ready_for_future_delivery":
        if not all_gates_green:
            raise RuntimeError("delivery manifest failed: ready_for_future_delivery requires all gates true")
        if payload["delivery_enabled"] is not False:
            raise RuntimeError("delivery manifest failed: design-only ready_for_future_delivery still requires delivery_enabled=false")
        if receipt["receipt_status"] != "pending":
            raise RuntimeError("delivery manifest failed: ready_for_future_delivery requires receipt_status=pending")

    if status == "sent":
        if payload["delivery_enabled"] is not True:
            raise RuntimeError("delivery manifest failed: sent requires delivery_enabled=true")
        if not all_gates_green:
            raise RuntimeError("delivery manifest failed: sent requires all gates true")
        if receipt["receipt_status"] != "created":
            raise RuntimeError("delivery manifest failed: sent requires receipt_status=created")
        if not str(receipt["receipt_path"]).strip():
            raise RuntimeError("delivery manifest failed: sent requires non-empty receipt_path")
        if authority["email_delivery"] is not True and authority["pdf_generation"] is not True:
            raise RuntimeError("delivery manifest failed: sent requires explicit future delivery authority")

    print(f"ETF_EU_DELIVERY_MANIFEST_OK | manifest={path} | status={status} | delivery_enabled={payload['delivery_enabled']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    args = parser.parse_args()
    validate_manifest(Path(args.manifest))


if __name__ == "__main__":
    main()
