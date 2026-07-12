from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

FORBIDDEN_CLOSEOUT_FIELDS = {
    "raw_subject",
    "raw_sender",
    "raw_recipient",
    "mailbox_message_id",
    "smtp_message_id",
    "raw_email_body",
    "raw_headers",
    "gmail_message_subject_observed",
    "gmail_received_local_display",
    "receipt_confirmation_file_title",
}


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AssertionError(f"missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate(
    closeout_path: Path,
    transport_path: Path,
    delivery_path: Path,
    receipt_path: Path,
    routine_path: Path,
) -> dict[str, Any]:
    closeout = _load(closeout_path)
    transport = _load(transport_path)
    delivery = _load(delivery_path)
    receipt = _load(receipt_path)
    routine = _load(routine_path)

    runtime_id = str(closeout.get("runtime_run_id") or "")
    _require(runtime_id == "20260711_175327", "unexpected runtime_run_id")
    for label, payload in {
        "transport": transport,
        "delivery": delivery,
        "receipt": receipt,
        "routine": routine,
    }.items():
        _require(str(payload.get("run_id") or payload.get("runtime_run_id") or "") == runtime_id, f"{label}: runtime id mismatch")

    _require(closeout.get("transport_attempted") is True, "transport_attempted must be true")
    _require(closeout.get("transport_success") is True, "transport_success must be true")
    _require(closeout.get("send_executed") is True, "send_executed must be true")
    _require(closeout.get("delivery_status") == "smtp_sendmail_returned_no_exception", "delivery status mismatch")
    _require(closeout.get("receipt_check_status") == "receipt_confirmed", "receipt check status mismatch")
    _require(closeout.get("receipt_confirmed") is True, "receipt must be confirmed")
    _require(receipt.get("receipt_confirmed") is True, "independent receipt evidence missing")
    _require(receipt.get("independent_evidence_basis") == "inbox_message_match", "independent evidence basis missing")

    _require(closeout.get("attachment_count_seen") == 4, "attachment_count_seen must be 4")
    for field in [
        "dutch_primary_pdf_seen",
        "english_companion_pdf_seen",
        "dutch_primary_html_seen",
        "english_companion_html_seen",
    ]:
        _require(closeout.get(field) is True, f"{field} must be true")

    for field in [
        "recipient_plaintext_values_exposed",
        "secret_values_exposed",
        "raw_email_content_stored",
        "raw_receipt_pdf_stored_in_github",
        "valuation_grade",
        "funding_authority",
        "portfolio_mutation",
        "production_delivery_authority",
    ]:
        _require(closeout.get(field) is False, f"{field} must remain false")

    _require(not (FORBIDDEN_CLOSEOUT_FIELDS & set(closeout)), "raw mailbox field present in closeout")
    _require(closeout.get("production_delivery_cycle_closed") is True, "cycle not closed")
    _require(closeout.get("routine_production_ready") is True, "routine production not ready")
    _require(closeout.get("next_operating_mode") == "routine_production", "operating mode mismatch")
    _require(closeout.get("blockers") == [], "closeout blockers must be empty")
    _require(Path(str(closeout.get("routine_runbook") or "")).exists(), "routine runbook missing")

    return {
        "status": "valid",
        "runtime_run_id": runtime_id,
        "transport_success": True,
        "receipt_confirmed": True,
        "routine_production_ready": True,
        "closeout": str(closeout_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--closeout", required=True)
    parser.add_argument("--transport-result", required=True)
    parser.add_argument("--delivery-evidence", required=True)
    parser.add_argument("--receipt-evidence", required=True)
    parser.add_argument("--routine-manifest", required=True)
    args = parser.parse_args()
    result = validate(
        Path(args.closeout),
        Path(args.transport_result),
        Path(args.delivery_evidence),
        Path(args.receipt_evidence),
        Path(args.routine_manifest),
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
