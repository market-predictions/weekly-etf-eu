from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_delivery_closeout_manifest_v1"
ARTIFACT_TYPE = "etf_eu_delivery_closeout_manifest"
EXPECTED_STATUS = "completed_guarded_resend_with_receipt_confirmed"
ALLOWED_NEXT_PACKAGES = {
    "ETF-EU-MVP21_POST_DELIVERY_HARDENING",
    "ETF-EU-MVP22_ROUTINE_WEEKLY_EU_REPORT_OPERATING_LOOP",
}
REQUIRED_ATTACHMENTS = {
    "weekly_etf_eu_review_nl_260709.pdf",
    "weekly_etf_eu_review_260709.pdf",
    "weekly_etf_eu_review_nl_260709.html",
    "weekly_etf_eu_review_260709.html",
}


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AssertionError(f"missing manifest: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _require_path(value: object, label: str) -> Path:
    raw = str(value or "").strip()
    _require(bool(raw), f"{label} missing")
    path = Path(raw)
    _require(path.exists(), f"{label} missing path: {path}")
    return path


def validate(manifest_path: Path) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    data = _load(manifest_path)

    _require(data.get("schema_version") == SCHEMA_VERSION, "schema_version mismatch")
    _require(data.get("artifact_type") == ARTIFACT_TYPE, "artifact_type mismatch")
    _require(data.get("work_package_id") == "ETF-EU-MVP21_POST_DELIVERY_HARDENING", "work_package_id mismatch")
    _require(data.get("status") == EXPECTED_STATUS, f"status mismatch: {data.get('status')}")
    _require(data.get("workflow_run_id") == "29105468659", "workflow_run_id mismatch")
    _require(data.get("workflow_job_id") == "86404756891", "workflow_job_id mismatch")

    for key in [
        "transport_attempted",
        "transport_success",
        "resend_performed",
        "send_executed",
        "delivery_success_closed",
        "receipt_confirmed",
        "completion_claimed",
    ]:
        _require(data.get(key) is True, f"{key} must be true")

    for key in [
        "raw_receipt_pdf_stored_in_github",
        "recipient_plaintext_values_exposed",
        "secret_values_exposed",
        "valuation_grade",
        "funding_authority",
        "portfolio_mutation",
        "production_delivery_authority",
    ]:
        _require(data.get(key) is False, f"{key} must be false")

    _require(data.get("attachment_count") == 4, "attachment_count must be 4")
    attachments = set(data.get("attachments_observed") or [])
    _require(attachments == REQUIRED_ATTACHMENTS, f"attachment set mismatch: {sorted(attachments)}")
    _require(data.get("next_package") in ALLOWED_NEXT_PACKAGES, f"unexpected next_package={data.get('next_package')}")
    _require(bool(data.get("upstream_pattern_adapted")), "upstream_pattern_adapted missing")

    delivery_package = _require_path(data.get("delivery_package_manifest"), "delivery_package_manifest")
    ready_artifact = _require_path(data.get("ready_artifact"), "ready_artifact")
    manual_receipt = _require_path(data.get("manual_receipt_confirmation_artifact"), "manual_receipt_confirmation_artifact")

    package = _load(delivery_package)
    ready = _load(ready_artifact)
    receipt = _load(manual_receipt)
    _require(package.get("client_grade_package_ready") is True, "delivery package not client-grade ready")
    _require(package.get("dutch_primary") is True, "delivery package missing Dutch primary")
    _require(package.get("english_companion") is True, "delivery package missing English companion")
    _require(ready.get("transport_guard", {}).get("ready_for_controlled_resend") is True, "ready artifact not ready for controlled resend")
    _require(receipt.get("receipt_confirmed") is True, "manual receipt is not confirmed")
    _require(receipt.get("raw_receipt_pdf_stored_in_github") is False, "manual receipt claims raw PDF stored")
    _require(receipt.get("recipient_plaintext_values_exposed_in_artifact") is False, "manual receipt exposes plaintext recipient")
    _require(receipt.get("secret_values_exposed") is False, "manual receipt exposes secrets")

    latest = manifest_path.parent / "latest_etf_eu_delivery_closeout_manifest_path.txt"
    _require(latest.exists(), "latest closeout manifest pointer missing")
    pointed = latest.read_text(encoding="utf-8").strip()
    _require(pointed == str(manifest_path), f"latest pointer mismatch: {pointed}")

    return {
        "status": "valid",
        "manifest": str(manifest_path),
        "work_package_id": data.get("work_package_id"),
        "delivery_status": data.get("status"),
        "receipt_confirmed": data.get("receipt_confirmed"),
        "next_package": data.get("next_package"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ETF EU delivery closeout manifest.")
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    print(json.dumps(validate(Path(args.manifest)), indent=2))


if __name__ == "__main__":
    main()
