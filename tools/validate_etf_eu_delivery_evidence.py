from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ALLOWED_DELIVERY_STATUSES = {
    "not_attempted",
    "smtp_sendmail_returned_no_exception",
    "smtp_sendmail_failed",
    "evidence_invalid",
}
SUCCESS_CAVEAT = "not an end-recipient inbox receipt"
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

    if delivery_status == "smtp_sendmail_returned_no_exception":
        _require(SUCCESS_CAVEAT in str(data.get("delivery_status_meaning") or ""), "missing status caveat")
        _require(data.get("email_delivery") is True, "email_delivery should be true for successful transport evidence")
    if delivery_status == "not_attempted":
        for key in ["production_delivery", "email_delivery", "delivery_receipt", "delivery_success"]:
            _require(data.get(key) is False, f"expected false for not_attempted: {key}")

    if data.get("delivery_success") is True:
        _require(delivery_status == "smtp_sendmail_returned_no_exception", "success requires successful transport status")
        _require(SUCCESS_CAVEAT in str(data.get("delivery_status_meaning") or ""), "success requires caveat")

    for label in [
        "controlled_send_preflight_manifest",
        "base_delivery_manifest",
        "sender_entrypoint_path",
        "dutch_primary_report_path",
        "english_companion_report_path",
    ]:
        _path_exists(data.get(label), label)

    return {
        "status": "valid",
        "evidence": str(evidence_path),
        "delivery_status": delivery_status,
        "delivery_success": data.get("delivery_success"),
        "recipient_data_policy": data.get("recipient_data_policy"),
        "language_count": data.get("language_count"),
        "languages": sorted(codes),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True)
    args = parser.parse_args()
    print(json.dumps(validate(Path(args.evidence)), indent=2))


if __name__ == "__main__":
    main()
