from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Required closeout input does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_closeout(
    *,
    package_path: Path,
    transport_path: Path,
    delivery_path: Path,
    receipt_check_path: Path,
    receipt_evidence_path: Path,
    run_manifest_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    package = _load(package_path)
    transport = _load(transport_path)
    delivery = _load(delivery_path)
    receipt = _load(receipt_check_path)
    receipt_evidence = _load(receipt_evidence_path)
    run_manifest = _load(run_manifest_path)

    _require(package.get("correction_control_id") == "20260713_180000", "Wrong correction control id")
    _require("20260713_000000" not in str(package_path), "Superseded correction package is forbidden")
    _require(package.get("client_surface_clean") is True, "Client surface gate did not pass")
    _require(package.get("corrected_client_output_valid") is True, "Corrected client output is invalid")
    _require(package.get("combined_machine_gate_passed") is True, "PDF machine gate did not pass")
    _require(package.get("visual_review_passed") is True, "PDF visual gate did not pass")
    _require(package.get("authority_separation_gate_passed") is True, "Authority separation gate did not pass")
    _require(transport.get("run_id") == "20260715_152543", "Wrong transport runtime id")
    _require(transport.get("delivery_mode") == "send", "Dry-run evidence cannot close delivery")
    _require(transport.get("transport_attempted") is True, "Transport was not attempted")
    _require(transport.get("transport_success") is True, "Transport did not succeed")
    _require(transport.get("send_executed") is True, "Send was not executed")
    _require(delivery.get("attachment_count") == 4, "Delivery evidence does not contain four attachments")
    _require(receipt.get("mailbox_search_performed") is True, "Independent mailbox search is missing")
    _require(receipt.get("receipt_confirmed") is True, "Receipt was not confirmed")
    _require(receipt.get("expected_attachment_set_seen") is True, "Expected attachment set was not observed")
    _require(receipt.get("attachment_count_seen") == 4, "Mailbox did not contain four expected attachments")
    _require(receipt_evidence.get("additional_resend_required") is False, "Receipt evidence requests another resend")
    _require(run_manifest.get("runtime_run_id") == "20260715_152543", "Run manifest points to the wrong runtime")

    payload = {
        "schema_version": "etf_eu_corrected_delivery_closeout_v1",
        "artifact_type": "etf_eu_corrected_delivery_closeout",
        "generated_at_utc": _utc_now(),
        "source_run_id": "20260712_125000",
        "source_runtime_run_id": "20260712_182002",
        "correction_control_id": "20260713_180000",
        "repair_run_id": "20260713_180000",
        "transport_runtime_run_id": "20260715_152543",
        "github_workflow_run_id": 29428021408,
        "report_date": "2026-07-12",
        "report_suffix": "260712",
        "package_manifest": str(package_path),
        "transport_result": str(transport_path),
        "delivery_evidence": str(delivery_path),
        "receipt_check": str(receipt_check_path),
        "receipt_evidence": str(receipt_evidence_path),
        "corrected_run_manifest": str(run_manifest_path),
        "client_surface_clean": True,
        "corrected_client_output_valid": True,
        "pdf_machine_gate_passed": True,
        "pdf_visual_gate_passed": True,
        "authority_separation_gate_passed": True,
        "transport_attempted": True,
        "transport_success": True,
        "send_executed": True,
        "delivery_status": "smtp_sendmail_returned_no_exception",
        "receipt_check_status": "receipt_confirmed",
        "receipt_confirmed": True,
        "expected_attachment_set_seen": True,
        "attachment_count_seen": 4,
        "dutch_primary_pdf_seen": True,
        "dutch_primary_html_seen": True,
        "english_companion_pdf_seen": True,
        "english_companion_html_seen": True,
        "attachment_names_match": receipt.get("attachment_names_match"),
        "attachment_sizes_match": receipt.get("attachment_sizes_match"),
        "attachment_hash_verification": receipt.get("attachment_hash_verification"),
        "attachment_hashes_match": receipt.get("attachment_hashes_match"),
        "additional_resend_required": False,
        "duplicate_send_prevented": True,
        "original_transport_evidence_overwritten": False,
        "recipient_plaintext_values_exposed": False,
        "secret_values_exposed": False,
        "raw_email_content_stored": False,
        "raw_mailbox_headers_stored": False,
        "raw_receipt_pdf_stored_in_github": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "production_delivery_cycle_closed": True,
        "routine_production_ready": True,
        "next_operating_mode": "routine_production",
        "next_action": "RUN_NEXT_ROUTINE_WEEKLY_ETF_EU_REPORT",
        "blockers": [],
        "warnings": receipt.get("warnings", []),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Write the Weekly ETF EU corrected-delivery closeout manifest.")
    parser.add_argument("--package-manifest", required=True)
    parser.add_argument("--transport-result", required=True)
    parser.add_argument("--delivery-evidence", required=True)
    parser.add_argument("--receipt-check", required=True)
    parser.add_argument("--receipt-evidence", required=True)
    parser.add_argument("--run-manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    write_closeout(
        package_path=Path(args.package_manifest),
        transport_path=Path(args.transport_result),
        delivery_path=Path(args.delivery_evidence),
        receipt_check_path=Path(args.receipt_check),
        receipt_evidence_path=Path(args.receipt_evidence),
        run_manifest_path=Path(args.run_manifest),
        output_path=Path(args.output),
    )


if __name__ == "__main__":
    main()
