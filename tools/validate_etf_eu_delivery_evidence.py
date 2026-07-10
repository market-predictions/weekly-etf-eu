from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ALLOWED_DELIVERY_STATUSES = {
    "not_attempted",
    "attempt_pending",
    "transport_succeeded_unconfirmed",
    "transport_failed",
    "receipt_confirmed",
    "receipt_not_found_after_delay",
    "smtp_sendmail_returned_no_exception",
    "smtp_sendmail_failed",
    "evidence_invalid",
}
SUCCESS_CAVEAT = "not an end-recipient inbox receipt"
TRANSPORT_CONTRACT_VERSION = "etf_eu_real_transport_evidence_contract_v1"
NL_REPORT_RE = re.compile(r"weekly_etf_eu_review_nl_(\d{6})\.md$")
EN_REPORT_RE = re.compile(r"weekly_etf_eu_review_(\d{6})\.md$")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _path_exists(path_value: object, label: str) -> None:
    path = Path(str(path_value or ""))
    _require(str(path), f"{label} missing")
    _require(path.exists(), f"{label} missing path: {path}")


def _validate_transport_contract(data: dict[str, Any], delivery_status: str) -> None:
    if "transport_contract_version" not in data:
        return

    _require(data.get("transport_contract_version") == TRANSPORT_CONTRACT_VERSION, "transport contract version mismatch")
    for key in [
        "delivery_mode",
        "transport_attempted",
        "transport_success",
        "transport_error",
        "recipient_target_redacted",
        "dutch_primary_pdf",
        "english_companion_pdf",
        "dutch_primary_html",
        "english_companion_html",
        "delivery_package_manifest",
        "ready_artifact",
        "smtp_or_transport_provider",
        "message_id_or_receipt_reference",
        "receipt_confirmed",
        "valuation_grade",
        "funding_authority",
        "portfolio_mutation",
        "production_delivery_authority",
    ]:
        _require(key in data, f"transport contract field missing: {key}")

    delivery_mode = str(data.get("delivery_mode"))
    _require(delivery_mode in {"dry_run", "send"}, f"unsupported delivery_mode={delivery_mode}")
    _require(data.get("recipient_target_redacted") is True, "recipient target must be redacted")
    _require(data.get("receipt_confirmed") is False or delivery_status == "receipt_confirmed", "receipt cannot be confirmed without receipt status")
    _require(data.get("valuation_grade") is False, "transport evidence must not create valuation grade")
    _require(data.get("funding_authority") is False, "transport evidence must not create funding authority")
    _require(data.get("portfolio_mutation") is False, "transport evidence must not mutate portfolio")
    _require(data.get("production_delivery_authority") is False, "transport evidence must not create production delivery authority")

    for label in [
        "dutch_primary_pdf",
        "english_companion_pdf",
        "dutch_primary_html",
        "english_companion_html",
        "delivery_package_manifest",
        "ready_artifact",
    ]:
        _path_exists(data.get(label), label)

    attempted = data.get("transport_attempted")
    success = data.get("transport_success")
    _require(isinstance(attempted, bool), "transport_attempted must be boolean")
    _require(isinstance(success, bool), "transport_success must be boolean")
    if delivery_mode == "dry_run":
        _require(attempted is False, "dry_run must not attempt transport")
        _require(success is False, "dry_run must not claim transport success")
    if success:
        _require(attempted is True, "transport_success requires transport_attempted")
        _require(delivery_status == "smtp_sendmail_returned_no_exception", "transport_success requires SMTP success status")
        _require(not data.get("transport_error"), "transport_success requires empty transport_error")
        _require(bool(data.get("message_id_or_receipt_reference")), "transport_success requires message id or receipt reference")
        _require(SUCCESS_CAVEAT in str(data.get("delivery_status_meaning") or ""), "transport_success requires inbox receipt caveat")
    if attempted and not success:
        _require(bool(data.get("transport_error")), "failed attempted transport requires transport_error")


def validate(evidence_path: Path) -> dict[str, Any]:
    evidence_path = Path(evidence_path)
    _require(evidence_path.exists(), f"missing evidence: {evidence_path}")
    data = _load(evidence_path)

    _require(data.get("schema_version") == "etf_eu_delivery_evidence_v1", "schema mismatch")
    _require(data.get("artifact_type") == "etf_eu_controlled_send_delivery_evidence", "artifact type mismatch")
    delivery_status = str(data.get("delivery_status"))
    _require(delivery_status in ALLOWED_DELIVERY_STATUSES, f"invalid delivery_status={delivery_status}")
    _require(data.get("recipient_data_policy") == "redacted_hash_only", "recipient policy mismatch")
    _require(data.get("secret_values_exposed") is False, "secret values exposed")
    _require(data.get("recipient_plaintext_values_exposed") is False, "recipient plaintext exposed")

    report_suffix = str(data.get("report_suffix") or "")
    nl_path = str(data.get("dutch_primary_report_path") or "")
    en_path = str(data.get("english_companion_report_path") or "")
    _require(NL_REPORT_RE.search(nl_path), "Dutch primary report path is not canonical")
    _require(EN_REPORT_RE.search(en_path), "English companion report path is not canonical")
    _require(nl_path.endswith(f"weekly_etf_eu_review_nl_{report_suffix}.md"), "Dutch suffix mismatch")
    _require(en_path.endswith(f"weekly_etf_eu_review_{report_suffix}.md"), "English suffix mismatch")

    languages = data.get("languages") or []
    _require(isinstance(languages, list), "languages must be a list")
    _require(data.get("language_count") == len(languages), "language_count mismatch")
    codes = {str(item.get("language")) for item in languages if isinstance(item, dict)}
    _require(codes == {"nl", "en"}, f"language set mismatch: {sorted(codes)}")
    expected_paths = {"nl": nl_path, "en": en_path}
    for item in languages:
        _require(isinstance(item, dict), "language item must be object")
        language = str(item.get("language"))
        _require(str(item.get("report_path")) == expected_paths[language], f"{language}: report path mismatch")
        _require(item.get("recipient_redacted") is True, f"{language}: recipient not redacted")
        recipient_hash = str(item.get("recipient_hash") or "")
        _require(bool(recipient_hash), f"{language}: recipient_hash missing")
        _require("@" not in recipient_hash, f"{language}: recipient_hash contains plaintext recipient")
        _require(bool(item.get("source_manifest_path")), f"{language}: source_manifest_path missing")
        _require(bool(item.get("source_manifest_type")), f"{language}: source_manifest_type missing")
        _require(bool(item.get("timestamp_utc")), f"{language}: timestamp missing")
        _require(bool(item.get("mode")), f"{language}: mode missing")
        _require(bool(item.get("report")), f"{language}: report missing")
        _require("html_body" in item, f"{language}: html_body missing")
        attachments = item.get("attachments") or []
        pdf_attachments = item.get("pdf_attachments") or []
        _require(isinstance(attachments, list), f"{language}: attachments not list")
        _require(isinstance(pdf_attachments, list), f"{language}: pdf_attachments not list")
        _require(item.get("attachment_count") == len(attachments), f"{language}: attachment_count mismatch")
        if data.get("pdf_generation") is True:
            _require(item.get("pdf_attached") == "yes", f"{language}: pdf_attached must be yes")
            _require(bool(pdf_attachments), f"{language}: pdf_attachments missing")
        else:
            _require(item.get("pdf_attached") in {"no", "yes"}, f"{language}: pdf_attached invalid")

    if delivery_status in {"smtp_sendmail_returned_no_exception", "transport_succeeded_unconfirmed"}:
        _require(SUCCESS_CAVEAT in str(data.get("delivery_status_meaning") or ""), "missing status caveat")
    if delivery_status in {"not_attempted", "attempt_pending", "transport_succeeded_unconfirmed", "transport_failed", "receipt_not_found_after_delay", "smtp_sendmail_failed"}:
        for key in ["production_delivery", "email_delivery", "delivery_success"]:
            _require(data.get(key) is False, f"expected false for {delivery_status}: {key}")

    if data.get("delivery_success") is True:
        _require(delivery_status == "smtp_sendmail_returned_no_exception", "success requires successful transport status")
        _require(SUCCESS_CAVEAT in str(data.get("delivery_status_meaning") or ""), "success requires caveat")
        _require(data.get("delivery_receipt") is False, "transport success is not inbox receipt confirmation")

    for label in [
        "controlled_send_preflight_manifest",
        "base_delivery_manifest",
        "sender_entrypoint_path",
        "dutch_primary_report_path",
        "english_companion_report_path",
    ]:
        _path_exists(data.get(label), label)

    _validate_transport_contract(data, delivery_status)

    return {
        "status": "valid",
        "evidence": str(evidence_path),
        "delivery_status": delivery_status,
        "delivery_success": data.get("delivery_success"),
        "recipient_data_policy": data.get("recipient_data_policy"),
        "language_count": data.get("language_count"),
        "languages": sorted(codes),
        "transport_contract_version": data.get("transport_contract_version"),
        "transport_attempted": data.get("transport_attempted"),
        "transport_success": data.get("transport_success"),
        "receipt_confirmed": data.get("receipt_confirmed", data.get("delivery_receipt")),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True)
    args = parser.parse_args()
    print(json.dumps(validate(Path(args.evidence)), indent=2))


if __name__ == "__main__":
    main()
