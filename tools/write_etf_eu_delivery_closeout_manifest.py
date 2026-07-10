from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_delivery_closeout_manifest_v1"
ARTIFACT_TYPE = "etf_eu_delivery_closeout_manifest"
DEFAULT_RECEIPT = "output/delivery/etf_eu_manual_receipt_confirmation_20260710_1755.json"
DEFAULT_PACKAGE = "output/delivery_package/etf_eu_delivery_package_manifest_20260709_000000.json"
DEFAULT_READY = "output/client_surface/etf_eu_mvp19_fix2_ready_for_controlled_resend_20260709_000000.json"
DEFAULT_OUTPUT = "output/run_manifests/etf_eu_delivery_closeout_manifest_20260710_1755.json"
LATEST_POINTER = "latest_etf_eu_delivery_closeout_manifest_path.txt"
UPSTREAM_PATTERN = (
    "weekly-etf delivery manifest and run manifest closeout pattern; adapted for EU manual Gmail receipt "
    "and UCITS authority boundaries"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Required input is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def build_manifest(
    *,
    manual_receipt_path: Path,
    delivery_package_manifest_path: Path,
    ready_artifact_path: Path,
    generated_at_utc: str | None = None,
    next_package: str = "ETF-EU-MVP22_ROUTINE_WEEKLY_EU_REPORT_OPERATING_LOOP",
) -> dict[str, Any]:
    receipt = _load_json(manual_receipt_path)
    package = _load_json(delivery_package_manifest_path)
    ready = _load_json(ready_artifact_path)

    _require(receipt.get("schema_version") == "etf_eu_manual_receipt_confirmation_v1", "manual receipt schema mismatch")
    _require(receipt.get("artifact_type") == "manual_inbox_receipt_confirmation", "manual receipt artifact type mismatch")
    _require(package.get("schema_version") == "etf_eu_delivery_package_manifest_v1", "delivery package schema mismatch")
    _require(ready.get("schema_version") == "etf_eu_mvp19_fix2_ready_for_controlled_resend_v1", "ready artifact schema mismatch")
    _require(receipt.get("receipt_confirmed") is True, "manual receipt must confirm receipt")
    _require(receipt.get("transport_attempted") is True, "manual receipt must show attempted transport")
    _require(receipt.get("transport_success") is True, "manual receipt must show transport success")
    _require(receipt.get("raw_receipt_pdf_stored_in_github") is False, "raw receipt PDF must not be stored in GitHub")
    _require(receipt.get("recipient_plaintext_values_exposed_in_artifact") is False, "manual receipt artifact exposes plaintext recipient")
    _require(receipt.get("secret_values_exposed") is False, "manual receipt artifact exposes secrets")
    _require(package.get("client_grade_package_ready") is True, "package must be client-grade ready")
    _require(package.get("dutch_primary") is True, "Dutch primary flag missing")
    _require(package.get("english_companion") is True, "English companion flag missing")
    _require(ready.get("transport_guard", {}).get("ready_for_controlled_resend") is True, "ready artifact is not ready for controlled resend")

    for key in ["valuation_grade", "funding_authority", "portfolio_mutation", "production_delivery_authority"]:
        _require(receipt.get(key) is False, f"manual receipt must preserve {key}=false")
    for key in ["valuation_grade", "funding_authority", "portfolio_mutation"]:
        _require(package.get(key) is False, f"delivery package must preserve {key}=false")

    attachments = receipt.get("attachments_observed") or []
    _require(isinstance(attachments, list), "attachments_observed must be a list")

    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "generated_at_utc": generated_at_utc or _utc_now(),
        "work_package_id": "ETF-EU-MVP21_POST_DELIVERY_HARDENING",
        "source_work_package": "ETF-EU-MVP20B_GUARDED_CONTROLLED_RESEND_EXECUTION",
        "status": "completed_guarded_resend_with_receipt_confirmed",
        "workflow_run_id": str(receipt.get("workflow_run_id")),
        "workflow_job_id": str(receipt.get("workflow_job_id")),
        "delivery_package_manifest": str(delivery_package_manifest_path),
        "ready_artifact": str(ready_artifact_path),
        "manual_receipt_confirmation_artifact": str(manual_receipt_path),
        "transport_attempted": True,
        "transport_success": True,
        "resend_performed": True,
        "send_executed": True,
        "delivery_success_closed": True,
        "receipt_confirmed": True,
        "completion_claimed": True,
        "attachment_count": int(receipt.get("attachment_count") or len(attachments)),
        "attachments_observed": attachments,
        "raw_receipt_pdf_stored_in_github": False,
        "recipient_plaintext_values_exposed": False,
        "secret_values_exposed": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "upstream_pattern_adapted": UPSTREAM_PATTERN,
        "delivery_package_summary": {
            "run_id": package.get("run_id"),
            "report_suffix": package.get("report_suffix"),
            "dutch_primary_pdf": package.get("dutch_primary_pdf"),
            "english_companion_pdf": package.get("english_companion_pdf"),
            "dutch_primary_html": package.get("dutch_primary_html"),
            "english_companion_html": package.get("english_companion_html"),
        },
        "receipt_summary": {
            "receipt_confirmation_source": receipt.get("receipt_confirmation_source"),
            "receipt_confirmation_file_title": receipt.get("receipt_confirmation_file_title"),
            "gmail_message_subject_observed": receipt.get("gmail_message_subject_observed"),
            "gmail_received_local_display": receipt.get("gmail_received_local_display"),
            "gmail_sender_redacted": receipt.get("gmail_sender_redacted"),
            "gmail_recipient_redacted": receipt.get("gmail_recipient_redacted"),
            "raw_receipt_pdf_storage_note": receipt.get("raw_receipt_pdf_storage_note"),
        },
        "next_package": next_package,
    }
    return manifest


def write_manifest(manifest: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_path.parent / LATEST_POINTER).write_text(str(output_path) + "\n", encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Write ETF EU delivery closeout manifest from redacted receipt evidence.")
    parser.add_argument("--manual-receipt", default=DEFAULT_RECEIPT)
    parser.add_argument("--delivery-package-manifest", default=DEFAULT_PACKAGE)
    parser.add_argument("--ready-artifact", default=DEFAULT_READY)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--generated-at-utc", default=None)
    parser.add_argument("--next-package", default="ETF-EU-MVP22_ROUTINE_WEEKLY_EU_REPORT_OPERATING_LOOP")
    args = parser.parse_args()

    manifest = build_manifest(
        manual_receipt_path=Path(args.manual_receipt),
        delivery_package_manifest_path=Path(args.delivery_package_manifest),
        ready_artifact_path=Path(args.ready_artifact),
        generated_at_utc=args.generated_at_utc,
        next_package=args.next_package,
    )
    path = write_manifest(manifest, Path(args.output))
    print(
        "ETF_EU_DELIVERY_CLOSEOUT_MANIFEST_OK | "
        f"status={manifest['status']} | receipt_confirmed={manifest['receipt_confirmed']} | manifest={path}"
    )


if __name__ == "__main__":
    main()
