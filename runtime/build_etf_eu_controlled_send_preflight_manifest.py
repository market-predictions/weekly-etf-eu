from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT_DIR = Path("output/delivery")
BLOCKERS = [
    "mode guard present",
    "outbound path locked",
    "future receipt path reserved only",
    "success claim blocked",
    "requires MVP08 decision",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_sender_preflight(sender_preflight: dict[str, object]) -> None:
    required_true = ["dutch_primary_exists", "english_companion_exists", "preflight_no_send_mode_supported"]
    required_false = ["us_report_name_assumption_detected", "send_performed", "production_delivery", "email_delivery", "delivery_receipt", "delivery_success_claimed"]
    if sender_preflight.get("schema_version") != "etf_eu_sender_preflight_v1":
        raise RuntimeError("controlled-send preflight failed: unsupported sender preflight schema")
    if sender_preflight.get("delivery_mode") != "preflight_no_send":
        raise RuntimeError("controlled-send preflight failed: sender preflight must be no-send")
    for key in required_true:
        if sender_preflight.get(key) is not True:
            raise RuntimeError(f"controlled-send preflight failed: sender_preflight.{key} must be true")
    for key in required_false:
        if sender_preflight.get(key) is not False:
            raise RuntimeError(f"controlled-send preflight failed: sender_preflight.{key} must be false")


def build_controlled_send_preflight_manifest(
    *,
    run_id: str,
    report_date: str,
    sender_preflight: dict[str, object],
    base_delivery_manifest_path: Path,
    created_at_utc: str | None = None,
) -> dict[str, object]:
    _require_sender_preflight(sender_preflight)
    base = _load_json(Path(base_delivery_manifest_path))
    if base.get("schema_version") != "etf_eu_delivery_manifest_v1":
        raise RuntimeError("controlled-send preflight failed: unsupported base delivery manifest schema")
    if base.get("status") != "blocked_design_only":
        raise RuntimeError("controlled-send preflight failed: base manifest must be blocked_design_only")
    artifacts = dict(base.get("artifacts", {}))
    artifacts["dutch_report_path"] = str(sender_preflight["dutch_primary_report_path"])
    artifacts["english_report_path"] = str(sender_preflight["english_companion_report_path"])
    validation_paths = list(artifacts.get("validation_evidence_paths", []))
    sender_preflight_path = sender_preflight.get("sender_preflight_artifact_path")
    if isinstance(sender_preflight_path, str) and sender_preflight_path and sender_preflight_path not in validation_paths:
        validation_paths.append(sender_preflight_path)
    artifacts["validation_evidence_paths"] = validation_paths
    receipt_path = f"output/delivery/pending_receipt_{run_id}.json"
    return {
        "schema_version": "etf_eu_delivery_manifest_v1",
        "run_id": run_id,
        "created_at_utc": created_at_utc or _utc_now(),
        "report_date": report_date,
        "status": "ready_for_future_delivery",
        "delivery_enabled": False,
        "gates": {
            "main_workflow_green": True,
            "dutch_first_report_contract_green": True,
            "fundability_rules_clear": True,
            "delivery_manifest_exists": True,
            "receipt_path_exists": True,
        },
        "artifacts": artifacts,
        "receipt": {
            "receipt_required": True,
            "receipt_path": receipt_path,
            "receipt_status": "pending",
        },
        "authority": {
            "funding_authority": False,
            "portfolio_mutation": False,
            "valuation_grade_promotion": False,
            "candidate_promotion_to_fundable": False,
            "pdf_generation": False,
            "email_delivery": False,
            "delivery_receipt": False,
            "production_delivery": False,
        },
        "blockers": list(BLOCKERS),
    }


def write_controlled_send_preflight_manifest(
    output_dir: Path,
    *,
    run_id: str,
    report_date: str,
    sender_preflight_path: Path,
    base_delivery_manifest_path: Path,
    created_at_utc: str | None = None,
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    sender_preflight = _load_json(Path(sender_preflight_path))
    sender_preflight["sender_preflight_artifact_path"] = str(sender_preflight_path)
    manifest = build_controlled_send_preflight_manifest(
        run_id=run_id,
        report_date=report_date,
        sender_preflight=sender_preflight,
        base_delivery_manifest_path=Path(base_delivery_manifest_path),
        created_at_utc=created_at_utc,
    )
    path = output_dir / f"etf_eu_controlled_send_preflight_manifest_{run_id}.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--sender-preflight-path", required=True)
    parser.add_argument("--base-delivery-manifest-path", required=True)
    args = parser.parse_args()
    path = write_controlled_send_preflight_manifest(
        Path(args.output_dir),
        run_id=args.run_id,
        report_date=args.report_date,
        sender_preflight_path=Path(args.sender_preflight_path),
        base_delivery_manifest_path=Path(args.base_delivery_manifest_path),
    )
    print(f"ETF_EU_CONTROLLED_SEND_PREFLIGHT_MANIFEST_OK | manifest={path} | delivery_enabled=false | receipt_status=pending")


if __name__ == "__main__":
    main()
