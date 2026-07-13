from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def update_manifest(
    *,
    path: Path,
    correction_control_id: str,
    source_run_id: str,
    repair_run_id: str,
    report_date: str,
    report_suffix: str,
    status: str,
    result_path: Path | None,
) -> dict[str, Any]:
    manifest = _load(path)
    manifest.update(
        {
            "schema_version": "etf_eu_corrected_resend_manifest_v1",
            "artifact_type": "etf_eu_corrected_resend_manifest",
            "updated_at_utc": _utc_now(),
            "correction_control_id": correction_control_id,
            "source_run_id": source_run_id,
            "source_runtime_run_id": "20260712_182002",
            "repair_run_id": repair_run_id,
            "report_date": report_date,
            "report_suffix": report_suffix,
            "status": status,
            "corrected_package_manifest": f"output/delivery_control/etf_eu_corrected_resend_package_{correction_control_id}.json",
            "corrected_queue": f"control/run_queue/etf_eu_corrected_resend_request_{correction_control_id}.md",
            "corrected_client_output_valid": True,
            "receipt_confirmed": False,
        }
    )

    if result_path is None:
        manifest.update(
            {
                "runtime_run_id": None,
                "transport_result": None,
                "delivery_evidence": None,
                "corrected_resend_executed": False,
                "transport_attempted": False,
                "transport_success": False,
                "next_action": (
                    "EXPLICITLY_DISPATCH_CORRECTED_RESEND"
                    if status in {"corrected_resend_prepared", "corrected_resend_validate_only_completed"}
                    else "RUN_CORRECTED_RESEND_DRY_RUN"
                ),
            }
        )
    else:
        result = _load(result_path)
        manifest.update(
            {
                "runtime_run_id": result.get("run_id"),
                "transport_result": str(result_path),
                "delivery_evidence": result.get("delivery_evidence_path"),
                "corrected_resend_executed": result.get("send_executed") is True,
                "transport_attempted": result.get("transport_attempted") is True,
                "transport_success": result.get("transport_success") is True,
            }
        )
        if result.get("delivery_mode") == "dry_run":
            manifest["next_action"] = "EXPLICITLY_DISPATCH_CORRECTED_RESEND"
        elif result.get("transport_success") is True:
            manifest["next_action"] = "VERIFY_CORRECTED_RESEND_RECEIPT_AFTER_DELAY"
        else:
            manifest["next_action"] = "REPAIR_CORRECTED_RESEND_TRANSPORT_FAILURE"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ETF_EU_CORRECTED_RESEND_MANIFEST_OK | status={status} | path={path}")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Write or update the ETF EU corrected-resend run manifest.")
    parser.add_argument("--path", required=True)
    parser.add_argument("--correction-control-id", required=True)
    parser.add_argument("--source-run-id", required=True)
    parser.add_argument("--repair-run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--result", default=None)
    args = parser.parse_args()
    update_manifest(
        path=Path(args.path),
        correction_control_id=args.correction_control_id,
        source_run_id=args.source_run_id,
        repair_run_id=args.repair_run_id,
        report_date=args.report_date,
        report_suffix=args.report_suffix,
        status=args.status,
        result_path=Path(args.result) if args.result else None,
    )


if __name__ == "__main__":
    main()
