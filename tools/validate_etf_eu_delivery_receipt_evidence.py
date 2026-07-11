from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


RECEIPT_SCHEMA = "etf_eu_current_package_receipt_evidence_v1"
TRANSPORT_SCHEMA = "etf_eu_current_package_transport_result_v1"
DELIVERY_SCHEMA = "etf_eu_current_package_delivery_evidence_v1"


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AssertionError(f"missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate(receipt_path: Path, transport_path: Path, delivery_path: Path) -> dict[str, Any]:
    receipt = _load(receipt_path)
    transport = _load(transport_path)
    delivery = _load(delivery_path)

    _require(receipt.get("schema_version") == RECEIPT_SCHEMA, "receipt schema mismatch")
    _require(transport.get("schema_version") == TRANSPORT_SCHEMA, "transport schema mismatch")
    _require(delivery.get("schema_version") == DELIVERY_SCHEMA, "delivery schema mismatch")
    _require(receipt.get("runtime_run_id") == "20260711_175327", "runtime run mismatch")
    _require(transport.get("transport_success") is True, "transport success missing")
    _require(delivery.get("transport_success") is True, "delivery transport success missing")
    _require(receipt.get("transport_success") is True, "receipt transport success missing")
    _require(isinstance(receipt.get("receipt_confirmed"), bool), "receipt_confirmed must be boolean")

    if receipt.get("receipt_confirmed") is True:
        _require(receipt.get("receipt_source") in {"gmail_api", "mailbox_api"}, "independent source missing")
        _require(receipt.get("inbox_label_seen") is True, "inbox match missing")
        _require(receipt.get("matched_report_date") == "2026-07-10", "report date mismatch")
        _require(receipt.get("matched_report_suffix") == "260710", "report suffix mismatch")
        for key in [
            "dutch_primary_pdf_seen",
            "english_companion_pdf_seen",
            "dutch_primary_html_seen",
            "english_companion_html_seen",
        ]:
            _require(receipt.get(key) is True, f"missing attachment match: {key}")

    for key in [
        "recipient_plaintext_values_exposed",
        "secret_values_exposed",
        "raw_email_content_stored",
        "raw_receipt_pdf_stored_in_github",
        "valuation_grade",
        "funding_authority",
        "portfolio_mutation",
        "production_delivery_authority",
    ]:
        _require(receipt.get(key) is False, f"{key} must be false")

    for key in ["message_reference_hash", "subject_hash", "recipient_hash", "sender_hash"]:
        value = str(receipt.get(key) or "")
        _require(value.startswith("sha256:"), f"invalid hash field: {key}")
        _require("@" not in value, f"plaintext leak in {key}")

    return {
        "status": "valid",
        "receipt": str(receipt_path),
        "runtime_run_id": receipt.get("runtime_run_id"),
        "receipt_confirmed": receipt.get("receipt_confirmed"),
        "transport_success": receipt.get("transport_success"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--transport-result", required=True)
    parser.add_argument("--delivery-evidence", required=True)
    args = parser.parse_args()
    result = validate(Path(args.receipt), Path(args.transport_result), Path(args.delivery_evidence))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
