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
        raise SystemExit(f"missing input: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--routine-manifest", required=True)
    parser.add_argument("--transport-result", required=True)
    parser.add_argument("--delivery-evidence", required=True)
    args = parser.parse_args()

    routine_path = Path(args.routine_manifest)
    result_path = Path(args.transport_result)
    evidence_path = Path(args.delivery_evidence)
    routine = _load(routine_path)
    result = _load(result_path)
    evidence = _load(evidence_path)

    if result.get("run_id") != evidence.get("run_id"):
        raise SystemExit("transport/evidence runtime id mismatch")
    if result.get("report_date") != routine.get("report_date"):
        raise SystemExit("transport/routine report date mismatch")
    if result.get("report_suffix") != routine.get("report_suffix"):
        raise SystemExit("transport/routine report suffix mismatch")
    if result.get("transport_attempted") is not True:
        raise SystemExit("transport was not attempted")
    if result.get("transport_success") is not True:
        raise SystemExit(f"transport failed: {result.get('transport_error')}")
    if result.get("delivery_status") != "smtp_sendmail_returned_no_exception":
        raise SystemExit("unexpected delivery status")
    for payload in (result, evidence):
        if payload.get("recipient_plaintext_values_exposed") is not False:
            raise SystemExit("recipient plaintext exposure flag is not false")
        if payload.get("secret_values_exposed") is not False:
            raise SystemExit("secret exposure flag is not false")
        if payload.get("receipt_confirmed") is not False:
            raise SystemExit("transport evidence cannot confirm receipt")

    routine.update({
        "generated_at_utc": _utc_now(),
        "routine_stage": "routine_guarded_transport_completed_awaiting_receipt",
        "workflow_status": "routine_guarded_transport_completed_awaiting_receipt",
        "workflow_conclusion": "success",
        "runtime_run_id": result["run_id"],
        "transport_result_artifact": str(result_path),
        "delivery_evidence_artifact": str(evidence_path),
        "delivery_status": result["delivery_status"],
        "delivery_status_meaning": "SMTP success is not an end-recipient inbox receipt.",
        "transport_attempted": True,
        "transport_success": True,
        "send_executed": True,
        "receipt_confirmed": False,
        "receipt_confirmed_from_new_run": False,
        "recipient_plaintext_values_exposed": False,
        "secret_values_exposed": False,
        "raw_email_content_stored": False,
        "raw_receipt_pdf_stored_in_github": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "next_package": None,
        "next_action": "VERIFY_ROUTINE_RECEIPT_AFTER_DELAY",
    })
    routine_path.write_text(json.dumps(routine, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ETF_EU_ROUTINE_TRANSPORT_MANIFEST_UPDATED | manifest={routine_path} | runtime_run_id={result['run_id']}")


if __name__ == "__main__":
    main()
