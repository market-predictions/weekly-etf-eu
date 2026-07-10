from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_guarded_fresh_package_delivery_prep_v1"
ARTIFACT_TYPE = "etf_eu_guarded_fresh_package_delivery_prep"
SOURCE_OF_TRUTH_REPO = "market-predictions/weekly-etf-eu"
REFERENCE_ARCHITECTURE_REPO = "market-predictions/weekly-etf"
UPSTREAM_PATTERN = "weekly-etf guarded delivery and delivery-manifest concept; adapted for EU explicit delivery-prep without send authority"
NEXT_PACKAGE = "ETF-EU-MVP27_EXPLICIT_GUARDED_SEND_AUTHORIZATION"

FALSE_AUTHORITY_FLAGS = [
    "delivery_authorized",
    "send_executed",
    "transport_attempted",
    "transport_success",
    "receipt_confirmed",
    "valuation_grade",
    "funding_authority",
    "portfolio_mutation",
    "production_delivery_authority",
]

PACKAGE_PATH_FIELDS = [
    "dutch_primary_markdown",
    "english_companion_markdown",
    "dutch_primary_html",
    "english_companion_html",
    "dutch_primary_pdf",
    "english_companion_pdf",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Required JSON input not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def _path(value: object, label: str) -> str:
    raw = str(value or "").strip()
    _require(bool(raw), f"{label} missing")
    path = Path(raw)
    _require(path.exists(), f"{label} does not exist: {path}")
    return raw


def _require_false(data: dict[str, Any], key: str, context: str) -> None:
    _require(data.get(key) is False, f"{context}:{key} must be false")


def _validate_inputs(package: dict[str, Any], ready: dict[str, Any], gate: dict[str, Any], routine: dict[str, Any]) -> None:
    _require(package.get("source_of_truth_repo") == SOURCE_OF_TRUTH_REPO, "package source_of_truth_repo mismatch")
    _require(package.get("reference_architecture_repo") == REFERENCE_ARCHITECTURE_REPO, "package reference_architecture_repo mismatch")
    _require(package.get("ready_for_controlled_delivery") is True, "package must be readiness-gated before delivery prep")
    _require(ready.get("ready_for_controlled_delivery") is True, "ready artifact must be true before delivery prep")
    _require(gate.get("readiness_gate_passed") is True, "readiness gate must have passed before delivery prep")
    _require(gate.get("blockers") == [], "readiness gate blockers must be empty before delivery prep")

    for context, payload in [("package", package), ("ready", ready), ("gate", gate), ("routine", routine)]:
        for key in FALSE_AUTHORITY_FLAGS:
            if key in payload:
                _require_false(payload, key, context)

    for field in PACKAGE_PATH_FIELDS:
        _path(package.get(field), field)

    for label, payload in [
        ("package_manifest", package),
        ("ready_artifact", ready),
        ("package_readiness_gate", gate),
        ("routine_run_manifest", routine),
    ]:
        _require(payload, f"{label} payload missing")


def build(args: argparse.Namespace) -> Path:
    package_manifest = Path(args.package_manifest)
    ready_artifact = Path(args.ready_artifact)
    package_readiness_gate = Path(args.package_readiness_gate)
    routine_manifest_path = Path(args.routine_manifest)

    package = _load_json(package_manifest)
    ready = _load_json(ready_artifact)
    gate = _load_json(package_readiness_gate)
    routine = _load_json(routine_manifest_path)

    _validate_inputs(package, ready, gate, routine)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    prep = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "generated_at_utc": _utc_now(),
        "run_id": args.run_id,
        "report_date": args.report_date,
        "report_suffix": args.report_suffix,
        "source_of_truth_repo": SOURCE_OF_TRUTH_REPO,
        "reference_architecture_repo": REFERENCE_ARCHITECTURE_REPO,
        "upstream_pattern_adapted": UPSTREAM_PATTERN,
        "package_manifest": str(package_manifest),
        "ready_artifact": str(ready_artifact),
        "package_readiness_gate": str(package_readiness_gate),
        "routine_run_manifest": str(routine_manifest_path),
        "dutch_primary_markdown": _path(package.get("dutch_primary_markdown"), "dutch_primary_markdown"),
        "english_companion_markdown": _path(package.get("english_companion_markdown"), "english_companion_markdown"),
        "dutch_primary_html": _path(package.get("dutch_primary_html"), "dutch_primary_html"),
        "english_companion_html": _path(package.get("english_companion_html"), "english_companion_html"),
        "dutch_primary_pdf": _path(package.get("dutch_primary_pdf"), "dutch_primary_pdf"),
        "english_companion_pdf": _path(package.get("english_companion_pdf"), "english_companion_pdf"),
        "ready_for_controlled_delivery": True,
        "delivery_authorized": False,
        "delivery_prep_created": True,
        "delivery_prep_validated": False,
        "explicit_user_authorization_required": True,
        "guarded_send_confirmation_required": True,
        "send_command_allowed": False,
        "workflow_dispatch_allowed": False,
        "run_queue_allowed": False,
        "send_executed": False,
        "transport_attempted": False,
        "transport_success": False,
        "receipt_confirmed": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "recipient_plaintext_values_exposed": False,
        "secret_values_exposed": False,
        "raw_receipt_pdf_stored_in_github": False,
        "next_package": NEXT_PACKAGE,
    }
    output_path.write_text(json.dumps(prep, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    routine.update(
        {
            "generated_at_utc": prep["generated_at_utc"],
            "routine_stage": "guarded_fresh_package_delivery_prep_created",
            "workflow_status": "guarded_fresh_package_delivery_prep_created",
            "delivery_prep_artifact": str(output_path),
            "ready_for_controlled_delivery": True,
            "delivery_authorized": False,
            "explicit_user_authorization_required": True,
            "guarded_send_confirmation_required": True,
            "send_command_allowed": False,
            "workflow_dispatch_allowed": False,
            "run_queue_allowed": False,
            "transport_attempted": False,
            "transport_success": False,
            "receipt_confirmed": False,
            "next_package": NEXT_PACKAGE,
        }
    )
    routine_manifest_path.write_text(json.dumps(routine, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare guarded delivery metadata for the readiness-gated ETF EU fresh package without sending.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--package-manifest", required=True)
    parser.add_argument("--ready-artifact", required=True)
    parser.add_argument("--package-readiness-gate", required=True)
    parser.add_argument("--routine-manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    path = build(args)
    print(f"ETF_EU_GUARDED_DELIVERY_PREP_OK | prep={path} | send_executed=false | transport_attempted=false")


if __name__ == "__main__":
    main()
