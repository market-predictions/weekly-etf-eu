#!/usr/bin/env python3
"""Finalize Weekly ETF EU generation artifacts after deterministic quality gates.

PRE_SEND_READY means generation and machine/client-quality validation passed. It does
not grant merge, delivery, funding, portfolio-mutation, or transport authority.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PRE_SEND_READY = "PRE_SEND_READY"
NEXT_ACTION = "INDEPENDENT_RELEASE_ASSURANCE"


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _identity(payload: dict[str, Any]) -> tuple[str, str]:
    return str(payload.get("run_id") or payload.get("source_run_id") or ""), str(payload.get("report_date") or "")


def finalize_pre_send_ready(
    package_manifest_path: Path,
    ready_artifact_path: Path,
    routine_manifest_path: Path,
    strict_validation_path: Path,
    machine_gate_path: Path,
) -> None:
    package = _load(package_manifest_path)
    ready = _load(ready_artifact_path)
    routine = _load(routine_manifest_path)
    strict = _load(strict_validation_path)
    machine = _load(machine_gate_path)

    run_id = str(ready.get("run_id") or "")
    report_date = str(ready.get("report_date") or "")
    _require(bool(run_id and report_date), "PRE_SEND_READY_IDENTITY_MISSING")

    for name, payload in (("package", package), ("routine", routine), ("strict", strict), ("machine", machine)):
        payload_run_id, payload_report_date = _identity(payload)
        _require(payload_run_id == run_id, f"PRE_SEND_READY_RUN_ID_MISMATCH:{name}")
        if payload_report_date:
            _require(payload_report_date == report_date, f"PRE_SEND_READY_REPORT_DATE_MISMATCH:{name}")

    _require(strict.get("client_grade_v2_passed") is True, "PRE_SEND_READY_STRICT_GATE_FAILED")
    _require(not strict.get("blockers"), "PRE_SEND_READY_STRICT_BLOCKERS_PRESENT")
    _require(strict.get("funded_state_consistency_passed") is True, "PRE_SEND_READY_FUNDED_STATE_FAILED")
    for language in ("dutch", "english"):
        language_result = strict.get(language)
        _require(isinstance(language_result, dict) and language_result.get("passed") is True, f"PRE_SEND_READY_{language.upper()}_FAILED")
        _require(not language_result.get("blockers"), f"PRE_SEND_READY_{language.upper()}_BLOCKERS_PRESENT")

    _require(machine.get("pdf_client_grade_passed") is True, "PRE_SEND_READY_MACHINE_GATE_FAILED")
    _require(machine.get("client_surface_clean") is True, "PRE_SEND_READY_CLIENT_SURFACE_NOT_CLEAN")
    _require(machine.get("authority_metadata_absent") is True, "PRE_SEND_READY_AUTHORITY_METADATA_PRESENT")
    _require(machine.get("raw_status_enums_absent") is True, "PRE_SEND_READY_RAW_STATUS_ENUMS_PRESENT")
    _require(not machine.get("blockers"), "PRE_SEND_READY_MACHINE_BLOCKERS_PRESENT")

    for name, payload in (("package", package), ("ready", ready), ("routine", routine)):
        for field in ("funding_authority", "portfolio_mutation", "production_delivery_authority", "send_executed", "transport_attempted"):
            _require(payload.get(field) is not True, f"PRE_SEND_READY_UNSAFE_{field.upper()}:{name}")

    finalized_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    package.update(
        {
            "client_output_valid": True,
            "client_surface_clean": True,
            "full_generation_status": PRE_SEND_READY,
            "next_action": NEXT_ACTION,
            "next_package": NEXT_ACTION,
            "pdf_generation_status": PRE_SEND_READY,
            "pdf_machine_gate_passed": True,
            "pre_send_ready": True,
            "pre_send_ready_finalized_at_utc": finalized_at,
            "ready_for_controlled_delivery": False,
            "delivery_authorized": False,
        }
    )
    ready.update(
        {
            "authority_metadata_absent": True,
            "client_output_valid": True,
            "client_surface_clean": True,
            "full_generation_status": PRE_SEND_READY,
            "next_action": NEXT_ACTION,
            "pdf_machine_gate_passed": True,
            "pre_send_ready": True,
            "pre_send_ready_finalized_at_utc": finalized_at,
            "raw_status_enums_absent": True,
            "ready_for_controlled_delivery": False,
            "delivery_authorized": False,
        }
    )
    routine.update(
        {
            "full_generation_status": PRE_SEND_READY,
            "next_package": NEXT_ACTION,
            "pre_send_ready": True,
            "pre_send_ready_finalized_at_utc": finalized_at,
            "routine_stage": PRE_SEND_READY,
            "valuation_grade": True,
            "workflow_conclusion": "PASS",
            "workflow_status": PRE_SEND_READY,
        }
    )

    _write(package_manifest_path, package)
    _write(ready_artifact_path, ready)
    _write(routine_manifest_path, routine)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-manifest", required=True, type=Path)
    parser.add_argument("--ready-artifact", required=True, type=Path)
    parser.add_argument("--routine-manifest", required=True, type=Path)
    parser.add_argument("--strict-validation", required=True, type=Path)
    parser.add_argument("--machine-gate", required=True, type=Path)
    args = parser.parse_args()
    finalize_pre_send_ready(
        args.package_manifest,
        args.ready_artifact,
        args.routine_manifest,
        args.strict_validation,
        args.machine_gate,
    )
    print(f"ETF_EU_PRE_SEND_READY=PASS | ready={args.ready_artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
