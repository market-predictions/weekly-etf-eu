from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
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


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _language_codes(languages: list[dict[str, object]]) -> set[str]:
    return {str(item.get("language")) for item in languages if isinstance(item, dict)}


def _validate_language_evidence(languages: list[dict[str, object]], *, pdf_generation: bool) -> None:
    _require(_language_codes(languages) == {"nl", "en"}, "ETF EU delivery evidence requires exactly nl and en languages")
    for item in languages:
        language = str(item.get("language"))
        _require(language in {"nl", "en"}, f"unsupported language: {language}")
        _require(item.get("recipient_redacted") is True, f"{language}: recipient must be redacted")
        recipient_hash = str(item.get("recipient_hash") or "")
        _require(bool(recipient_hash), f"{language}: recipient_hash missing")
        _require("@" not in recipient_hash, f"{language}: recipient_hash must not contain plaintext recipient")
        _require(bool(item.get("report_path")), f"{language}: report_path missing")
        _require(bool(item.get("source_manifest_path")), f"{language}: source_manifest_path missing")
        _require(bool(item.get("source_manifest_type")), f"{language}: source_manifest_type missing")
        _require(bool(item.get("timestamp_utc")), f"{language}: timestamp_utc missing")
        _require(bool(item.get("mode")), f"{language}: mode missing")
        _require(bool(item.get("report")), f"{language}: report missing")
        _require("html_body" in item, f"{language}: html_body missing")
        attachments = item.get("attachments") or []
        pdf_attachments = item.get("pdf_attachments") or []
        _require(isinstance(attachments, list), f"{language}: attachments must be a list")
        _require(isinstance(pdf_attachments, list), f"{language}: pdf_attachments must be a list")
        _require(item.get("attachment_count") == len(attachments), f"{language}: attachment_count mismatch")
        if pdf_generation:
            _require(item.get("pdf_attached") == "yes", f"{language}: pdf attachment evidence required")
            _require(bool(pdf_attachments), f"{language}: pdf_attachments required")
        else:
            _require(item.get("pdf_attached") in {"no", "yes"}, f"{language}: pdf_attached must be yes/no")


def build_etf_eu_delivery_evidence(
    *,
    run_id: str,
    report_date: str,
    report_suffix: str,
    sender_entrypoint_path: Path,
    dutch_primary_report_path: Path,
    english_companion_report_path: Path,
    controlled_send_preflight_manifest: Path,
    base_delivery_manifest: Path,
    delivery_status: str,
    delivery_status_meaning: str,
    languages: list[dict[str, object]],
    source: dict[str, object],
    generated_at_utc: str | None = None,
) -> dict[str, object]:
    _require(delivery_status in ALLOWED_DELIVERY_STATUSES, f"unsupported delivery_status={delivery_status}")
    _require(bool(delivery_status_meaning), "delivery_status_meaning required")
    if delivery_status in {"smtp_sendmail_returned_no_exception", "transport_succeeded_unconfirmed"}:
        _require(SUCCESS_CAVEAT in delivery_status_meaning, "transport-layer evidence must include inbox-receipt caveat")
    _validate_language_evidence(languages, pdf_generation=False)
    delivery_success = delivery_status == "smtp_sendmail_returned_no_exception"
    email_delivery = delivery_success
    production_delivery = delivery_success
    delivery_receipt = delivery_status == "receipt_confirmed"
    if delivery_status in {"not_attempted", "attempt_pending", "transport_failed", "receipt_not_found_after_delay", "transport_succeeded_unconfirmed"}:
        delivery_success = False
        email_delivery = False
        production_delivery = False
        delivery_receipt = False
    return {
        "schema_version": "etf_eu_delivery_evidence_v1",
        "artifact_type": "etf_eu_controlled_send_delivery_evidence",
        "generated_at_utc": generated_at_utc or _utc_now(),
        "run_id": run_id,
        "report_date": report_date,
        "report_suffix": report_suffix,
        "delivery_status": delivery_status,
        "delivery_status_meaning": delivery_status_meaning,
        "recipient_data_policy": "redacted_hash_only",
        "sender_entrypoint_path": str(sender_entrypoint_path),
        "dutch_primary_report_path": str(dutch_primary_report_path),
        "english_companion_report_path": str(english_companion_report_path),
        "controlled_send_preflight_manifest": str(controlled_send_preflight_manifest),
        "base_delivery_manifest": str(base_delivery_manifest),
        "language_count": len(languages),
        "languages": languages,
        "source": source,
        "secret_values_exposed": False,
        "recipient_plaintext_values_exposed": False,
        "production_delivery": production_delivery,
        "email_delivery": email_delivery,
        "pdf_generation": False,
        "delivery_receipt": delivery_receipt,
        "delivery_success": delivery_success,
        "delivery_error": None if delivery_status in {"not_attempted", "attempt_pending", "transport_succeeded_unconfirmed"} else source.get("delivery_error"),
        "receipt_status": "receipt_confirmed" if delivery_receipt else delivery_status,
    }


def write_etf_eu_delivery_evidence(
    output_dir: Path,
    *,
    run_id: str,
    report_date: str,
    report_suffix: str,
    sender_entrypoint_path: Path,
    dutch_primary_report_path: Path,
    english_companion_report_path: Path,
    controlled_send_preflight_manifest: Path,
    base_delivery_manifest: Path,
    delivery_status: str,
    delivery_status_meaning: str,
    languages: list[dict[str, object]],
    source: dict[str, object],
    generated_at_utc: str | None = None,
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence = build_etf_eu_delivery_evidence(
        run_id=run_id,
        report_date=report_date,
        report_suffix=report_suffix,
        sender_entrypoint_path=sender_entrypoint_path,
        dutch_primary_report_path=dutch_primary_report_path,
        english_companion_report_path=english_companion_report_path,
        controlled_send_preflight_manifest=controlled_send_preflight_manifest,
        base_delivery_manifest=base_delivery_manifest,
        delivery_status=delivery_status,
        delivery_status_meaning=delivery_status_meaning,
        languages=languages,
        source=source,
        generated_at_utc=generated_at_utc,
    )
    path = output_dir / f"etf_eu_delivery_evidence_{run_id}.json"
    path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _controlled_languages(
    *,
    nl_md: Path,
    en_md: Path,
    delivery_package_manifest: Path,
    mode: str,
    recipient_hashes: dict[str, str] | None = None,
) -> list[dict[str, object]]:
    timestamp = _utc_now()
    hashes = recipient_hashes or {"nl": "unavailable_pre_transport", "en": "unavailable_pre_transport"}
    reports = {"nl": nl_md, "en": en_md}
    labels = {"nl": "Dutch primary client report", "en": "English companion report"}
    return [
        {
            "language": language,
            "report_path": str(reports[language]),
            "source_manifest_path": str(delivery_package_manifest),
            "source_manifest_type": "etf_eu_delivery_package_manifest_v1",
            "timestamp_utc": timestamp,
            "mode": mode,
            "report": labels[language],
            "recipient_hash": hashes[language],
            "recipient_redacted": True,
            "html_body": False,
            "pdf_attached": "no",
            "attachments": [],
            "attachment_count": 0,
            "pdf_attachments": [],
        }
        for language in ("nl", "en")
    ]


def _validate_transport_result_binding(
    result: dict[str, Any],
    *,
    run_id: str,
    report_date: str,
    report_suffix: str,
    nl_md: Path,
    en_md: Path,
) -> dict[str, str]:
    _require(result.get("schema_version") == "etf_eu_controlled_transport_result_v1", "unexpected controlled transport result schema")
    _require(result.get("artifact_type") == "etf_eu_controlled_transport_result", "unexpected controlled transport artifact type")
    _require(str(result.get("run_id")) == run_id, "transport result run_id does not match controlled evidence run")
    _require(str(result.get("report_date")) == report_date, "transport result report_date does not match controlled evidence run")
    _require(str(result.get("report_suffix")) == report_suffix, "transport result report_suffix does not match controlled evidence run")
    rows = {str(row.get("language")): row for row in result.get("languages", []) if isinstance(row, dict)}
    _require(set(rows) == {"nl", "en"}, "controlled transport result must contain exactly nl and en")
    expected_paths = {"nl": str(nl_md), "en": str(en_md)}
    hashes: dict[str, str] = {}
    for language in ("nl", "en"):
        row = rows[language]
        _require(str(row.get("report_path")) == expected_paths[language], f"{language}: transport result report_path does not match assured path")
        _require(row.get("recipient_redacted") is True, f"{language}: transport result recipient must be redacted")
        recipient_hash = str(row.get("recipient_hash") or "")
        _require(bool(recipient_hash) and "@" not in recipient_hash, f"{language}: invalid redacted recipient hash")
        hashes[language] = recipient_hash
    return hashes


def _write_controlled(args: argparse.Namespace) -> Path:
    nl_md = Path(args.nl_md)
    en_md = Path(args.en_md)
    delivery_package_manifest = Path(args.delivery_package_manifest)
    for path, label in ((nl_md, "NL report"), (en_md, "EN report"), (delivery_package_manifest, "delivery package manifest")):
        _require(path.is_file(), f"{label} missing: {path}")

    if args.stage == "pre":
        status = "attempt_pending"
        meaning = "Controlled pre-transport evidence; exact assured artifacts bound and sender not yet executed"
        languages = _controlled_languages(
            nl_md=nl_md,
            en_md=en_md,
            delivery_package_manifest=delivery_package_manifest,
            mode="controlled_pre",
        )
        source: dict[str, object] = {
            "writer": "runtime/write_etf_eu_delivery_evidence.py",
            "basis": "controlled_pre",
            "transport_executed": False,
        }
    else:
        _require(bool(args.transport_result_path), "--transport-result-path required for controlled post evidence")
        result_path = Path(args.transport_result_path)
        _require(result_path.is_file(), f"transport result missing: {result_path}")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        status = str(result.get("transport_status"))
        _require(status in {"transport_succeeded_unconfirmed", "transport_failed"}, f"unsupported controlled transport status: {status}")
        recipient_hashes = _validate_transport_result_binding(
            result,
            run_id=args.run_id,
            report_date=args.report_date,
            report_suffix=args.report_suffix,
            nl_md=nl_md,
            en_md=en_md,
        )
        meaning = (
            f"Controlled transport returned without exception; {SUCCESS_CAVEAT}"
            if status == "transport_succeeded_unconfirmed"
            else "Controlled transport failed before receipt confirmation"
        )
        languages = _controlled_languages(
            nl_md=nl_md,
            en_md=en_md,
            delivery_package_manifest=delivery_package_manifest,
            mode="controlled_post",
            recipient_hashes=recipient_hashes,
        )
        source = {
            "writer": "runtime/write_etf_eu_delivery_evidence.py",
            "basis": "controlled_post",
            "transport_result_path": str(result_path),
            "transport_executed": True,
            "delivery_error": result.get("delivery_error"),
        }

    return write_etf_eu_delivery_evidence(
        Path(args.output_dir),
        run_id=args.run_id,
        report_date=args.report_date,
        report_suffix=args.report_suffix,
        sender_entrypoint_path=Path("runtime/send_etf_eu_controlled_report.py"),
        dutch_primary_report_path=nl_md,
        english_companion_report_path=en_md,
        controlled_send_preflight_manifest=delivery_package_manifest,
        base_delivery_manifest=delivery_package_manifest,
        delivery_status=status,
        delivery_status_meaning=meaning,
        languages=languages,
        source=source,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--controlled", action="store_true")
    parser.add_argument("--stage", choices=["pre", "post"], default="pre")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--nl-md", required=True)
    parser.add_argument("--en-md", required=True)
    parser.add_argument("--delivery-package-manifest", required=True)
    parser.add_argument("--transport-result-path", default=None)
    parser.add_argument("--output-dir", default="output/delivery")
    args = parser.parse_args()
    if not args.controlled:
        raise SystemExit("Use --controlled for the canonical ETF EU delivery-evidence path.")
    path = _write_controlled(args)
    print(f"ETF_EU_CONTROLLED_DELIVERY_EVIDENCE_OK | stage={args.stage} | evidence={path}")


if __name__ == "__main__":
    main()
