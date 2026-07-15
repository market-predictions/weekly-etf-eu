from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


EXPECTED = {
    "source_run_id": "20260712_125000",
    "source_runtime_run_id": "20260712_182002",
    "correction_control_id": "20260713_180000",
    "repair_run_id": "20260713_180000",
    "transport_runtime_run_id": "20260715_152543",
    "github_workflow_run_id": 29428021408,
    "report_date": "2026-07-12",
    "report_suffix": "260712",
}
FORBIDDEN_KEYS = {
    "sender",
    "recipient",
    "to",
    "from",
    "subject",
    "body",
    "email_body",
    "message_id",
    "smtp_message_id",
    "headers",
    "display_url",
}
EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Closeout validation failed: missing referenced artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _walk_keys(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_KEYS:
                found.append(key)
            found.extend(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_walk_keys(child))
    return found


def validate(closeout_path: Path) -> dict[str, Any]:
    closeout = _load(closeout_path)
    errors: list[str] = []

    for key, expected in EXPECTED.items():
        if closeout.get(key) != expected:
            errors.append(f"{key}={closeout.get(key)!r}, expected {expected!r}")

    required_true = [
        "client_surface_clean",
        "corrected_client_output_valid",
        "pdf_machine_gate_passed",
        "pdf_visual_gate_passed",
        "authority_separation_gate_passed",
        "transport_attempted",
        "transport_success",
        "send_executed",
        "receipt_confirmed",
        "expected_attachment_set_seen",
        "dutch_primary_pdf_seen",
        "dutch_primary_html_seen",
        "english_companion_pdf_seen",
        "english_companion_html_seen",
        "duplicate_send_prevented",
        "production_delivery_cycle_closed",
        "routine_production_ready",
    ]
    for key in required_true:
        if closeout.get(key) is not True:
            errors.append(f"{key} must be true")

    required_false = [
        "additional_resend_required",
        "original_transport_evidence_overwritten",
        "recipient_plaintext_values_exposed",
        "secret_values_exposed",
        "raw_email_content_stored",
        "raw_mailbox_headers_stored",
        "raw_receipt_pdf_stored_in_github",
        "valuation_grade",
        "funding_authority",
        "portfolio_mutation",
        "production_delivery_authority",
    ]
    for key in required_false:
        if closeout.get(key) is not False:
            errors.append(f"{key} must be false")

    if closeout.get("attachment_count_seen") != 4:
        errors.append("attachment_count_seen must equal 4")
    if closeout.get("delivery_status") != "smtp_sendmail_returned_no_exception":
        errors.append("delivery_status is not the guarded SMTP success status")
    if closeout.get("receipt_check_status") != "receipt_confirmed":
        errors.append("receipt_check_status is not receipt_confirmed")
    if closeout.get("next_operating_mode") != "routine_production":
        errors.append("next_operating_mode must be routine_production")
    if closeout.get("next_action") != "RUN_NEXT_ROUTINE_WEEKLY_ETF_EU_REPORT":
        errors.append("next_action must select the next fresh routine report")
    if closeout.get("blockers") not in ([], None):
        errors.append("closeout blockers must be empty")

    path_fields = [
        "package_manifest",
        "transport_result",
        "delivery_evidence",
        "receipt_check",
        "receipt_evidence",
        "corrected_run_manifest",
    ]
    artifacts: dict[str, dict[str, Any]] = {}
    for key in path_fields:
        raw = str(closeout.get(key) or "")
        if not raw:
            errors.append(f"missing {key}")
            continue
        if "20260713_000000" in raw:
            errors.append(f"{key} references the superseded package")
            continue
        try:
            artifacts[key] = _load(Path(raw))
        except RuntimeError as exc:
            errors.append(str(exc))

    package = artifacts.get("package_manifest", {})
    transport = artifacts.get("transport_result", {})
    delivery = artifacts.get("delivery_evidence", {})
    receipt = artifacts.get("receipt_check", {})
    receipt_evidence = artifacts.get("receipt_evidence", {})
    run_manifest = artifacts.get("corrected_run_manifest", {})

    if package.get("correction_control_id") != EXPECTED["correction_control_id"]:
        errors.append("package correction identity mismatch")
    if package.get("combined_machine_gate_passed") is not True:
        errors.append("package machine gate did not pass")
    if package.get("visual_review_passed") is not True:
        errors.append("package visual gate did not pass")
    if package.get("authority_separation_gate_passed") is not True:
        errors.append("package authority-separation gate did not pass")

    if transport.get("run_id") != EXPECTED["transport_runtime_run_id"]:
        errors.append("transport runtime mismatch")
    if transport.get("delivery_mode") != "send":
        errors.append("dry-run evidence cannot satisfy closeout")
    for key in ("transport_attempted", "transport_success", "send_executed"):
        if transport.get(key) is not True:
            errors.append(f"transport.{key} must be true")

    if delivery.get("attachment_count") != 4:
        errors.append("delivery evidence must contain four attachments")
    if delivery.get("original_transport_evidence_overwritten") is not False:
        errors.append("original transport evidence was overwritten")

    if receipt.get("mailbox_search_performed") is not True:
        errors.append("independent mailbox search is missing")
    if receipt.get("matching_message_found") is not True:
        errors.append("matching mailbox message was not found")
    if receipt.get("receipt_confirmed") is not True:
        errors.append("receipt check is not confirmed")
    if receipt.get("attachment_count_seen") != 4:
        errors.append("receipt check did not observe four attachments")
    if receipt.get("expected_attachment_set_seen") is not True:
        errors.append("receipt check did not observe the expected attachment set")

    if receipt_evidence.get("receipt_confirmed") is not True:
        errors.append("receipt evidence is not confirmed")
    if receipt_evidence.get("additional_resend_required") is not False:
        errors.append("receipt evidence requests another resend")

    if run_manifest.get("runtime_run_id") != EXPECTED["transport_runtime_run_id"]:
        errors.append("corrected run manifest runtime mismatch")
    if run_manifest.get("transport_result") != closeout.get("transport_result"):
        errors.append("run manifest does not preserve the live transport result")
    if run_manifest.get("delivery_evidence") != closeout.get("delivery_evidence"):
        errors.append("run manifest does not preserve the live delivery evidence")

    combined_artifacts: list[Any] = [closeout, *artifacts.values()]
    forbidden = sorted(set(_walk_keys(combined_artifacts)))
    if forbidden:
        errors.append("forbidden raw mailbox keys present: " + ", ".join(forbidden))
    serialized = json.dumps(combined_artifacts, sort_keys=True)
    if EMAIL_RE.search(serialized):
        errors.append("raw email address detected in closeout evidence")

    if errors:
        raise RuntimeError("ETF EU corrected-delivery closeout failed: " + "; ".join(sorted(set(errors))))

    result = {
        "closeout_valid": True,
        "correction_control_id": EXPECTED["correction_control_id"],
        "transport_runtime_run_id": EXPECTED["transport_runtime_run_id"],
        "receipt_confirmed": True,
        "attachment_count_seen": 4,
        "additional_resend_required": False,
        "routine_production_ready": True,
        "next_action": "RUN_NEXT_ROUTINE_WEEKLY_ETF_EU_REPORT",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the Weekly ETF EU corrected-delivery closeout.")
    parser.add_argument("--closeout", required=True)
    args = parser.parse_args()
    validate(Path(args.closeout))


if __name__ == "__main__":
    main()
