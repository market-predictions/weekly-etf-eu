from __future__ import annotations

import argparse
import hashlib
import json
import os
import smtplib
from datetime import datetime, timezone
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from pathlib import Path
from typing import Any

from runtime.write_etf_eu_delivery_evidence import SUCCESS_CAVEAT, write_etf_eu_delivery_evidence

SCHEMA_VERSION = "etf_eu_real_transport_result_v1"
EVIDENCE_CONTRACT_VERSION = "etf_eu_real_transport_evidence_contract_v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _load_json(path: Path) -> dict[str, Any]:
    _require(path.exists(), f"required input is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _redact_recipient(value: str) -> str:
    raw = (value or "").strip().lower()
    _require(bool(raw), "recipient target is required")
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _redacted_targets(recipients: list[str]) -> list[str]:
    return [_redact_recipient(item) for item in recipients if item.strip()]


def _recipient_env() -> list[str]:
    value = os.environ.get("MRKT_RPRTS_MAIL_TO_NL") or os.environ.get("MRKT_RPRTS_MAIL_TO")
    _require(bool(value), "MRKT_RPRTS_MAIL_TO_NL or MRKT_RPRTS_MAIL_TO is required for real EU transport")
    recipients = [item.strip() for item in str(value).replace(";", ",").split(",") if item.strip()]
    _require(bool(recipients), "at least one recipient is required for real EU transport")
    return recipients


def _read_text(path: Path) -> str:
    _require(path.exists(), f"required file missing: {path}")
    return path.read_text(encoding="utf-8")


def _attach_file(message: MIMEMultipart, path: Path, subtype: str | None = None) -> str:
    _require(path.exists(), f"attachment missing: {path}")
    payload = path.read_bytes()
    guessed = subtype or path.suffix.lstrip(".") or "octet-stream"
    part = MIMEApplication(payload, _subtype=guessed)
    part.add_header("Content-Disposition", "attachment", filename=path.name)
    message.attach(part)
    return str(path)


def _package_paths(manifest: dict[str, Any]) -> dict[str, Path]:
    return {
        "dutch_primary_pdf": Path(str(manifest["dutch_primary_pdf"])),
        "english_companion_pdf": Path(str(manifest["english_companion_pdf"])),
        "dutch_primary_html": Path(str(manifest["dutch_primary_html"])),
        "english_companion_html": Path(str(manifest["english_companion_html"])),
    }


def _validate_inputs(
    *,
    delivery_package_manifest: Path,
    ready_artifact: Path,
    report_suffix: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Path]]:
    manifest = _load_json(delivery_package_manifest)
    ready = _load_json(ready_artifact)

    _require(manifest.get("schema_version") == "etf_eu_delivery_package_manifest_v1", "delivery package manifest schema mismatch")
    _require(manifest.get("client_grade_package_ready") is True, "delivery package is not client-grade ready")
    _require(manifest.get("dutch_primary") is True, "Dutch primary package flag missing")
    _require(manifest.get("english_companion") is True, "English companion package flag missing")
    _require(manifest.get("pdf_output_available") is True, "PDF output is not available")
    _require(manifest.get("html_output_available") is True, "HTML output is not available")
    _require(manifest.get("valuation_grade") is False, "package must not claim valuation grade")
    _require(manifest.get("funding_authority") is False, "package must not claim funding authority")
    _require(manifest.get("portfolio_mutation") is False, "package must not claim portfolio mutation")
    _require(str(manifest.get("report_suffix")) == report_suffix, "report suffix mismatch against delivery package manifest")

    _require(ready.get("schema_version") == "etf_eu_mvp19_fix2_ready_for_controlled_resend_v1", "ready artifact schema mismatch")
    _require(ready.get("work_package_id") == "ETF-EU-MVP19-FIX2", "unexpected ready work package")
    _require(ready.get("transport_guard", {}).get("ready_for_controlled_resend") is True, "ready artifact is not ready for controlled resend")
    _require(ready.get("transport_guard", {}).get("resend_performed") is False, "ready artifact already marks resend performed")
    _require(ready.get("transport_guard", {}).get("receipt_confirmed") is False, "ready artifact already marks receipt confirmed")
    _require(ready.get("transport_guard", {}).get("production_delivery_authority") is False, "ready artifact must not create production delivery authority")

    paths = _package_paths(manifest)
    for label, path in paths.items():
        _require(path.exists(), f"{label} missing: {path}")

    return manifest, ready, paths


def _language_rows(
    *,
    recipients: list[str],
    paths: dict[str, Path],
    report_suffix: str,
    delivery_package_manifest: Path,
    timestamp: str,
) -> list[dict[str, Any]]:
    redacted = ",".join(_redacted_targets(recipients))
    return [
        {
            "language": "nl",
            "report_path": f"output/weekly_etf_eu_review_nl_{report_suffix}.md",
            "source_manifest_path": str(delivery_package_manifest),
            "source_manifest_type": "etf_eu_delivery_package_manifest_v1",
            "timestamp_utc": timestamp,
            "mode": "mvp20a_real_transport",
            "report": "Dutch primary client report",
            "recipient_hash": redacted,
            "recipient_redacted": True,
            "html_body": True,
            "pdf_attached": "yes",
            "attachments": [str(paths["dutch_primary_pdf"]), str(paths["dutch_primary_html"])],
            "attachment_count": 2,
            "pdf_attachments": [str(paths["dutch_primary_pdf"])],
        },
        {
            "language": "en",
            "report_path": f"output/weekly_etf_eu_review_{report_suffix}.md",
            "source_manifest_path": str(delivery_package_manifest),
            "source_manifest_type": "etf_eu_delivery_package_manifest_v1",
            "timestamp_utc": timestamp,
            "mode": "mvp20a_real_transport_companion",
            "report": "English companion report",
            "recipient_hash": redacted,
            "recipient_redacted": True,
            "html_body": False,
            "pdf_attached": "yes",
            "attachments": [str(paths["english_companion_pdf"]), str(paths["english_companion_html"])],
            "attachment_count": 2,
            "pdf_attachments": [str(paths["english_companion_pdf"])],
        },
    ]


def _build_message(
    *,
    report_date: str,
    recipients: list[str],
    mail_from: str,
    paths: dict[str, Path],
) -> tuple[MIMEMultipart, str, list[str]]:
    subject_prefix = os.environ.get("MRKT_RPRTS_SUBJECT_PREFIX_NL") or "Weekly ETF EU Review | Dutch primary"
    subject = f"{subject_prefix} {report_date}"

    root = MIMEMultipart("mixed")
    root["Subject"] = subject
    root["From"] = mail_from
    root["To"] = ", ".join(recipients)
    root["Date"] = formatdate(localtime=False)
    message_id = make_msgid(domain="weekly-etf-eu.local")
    root["Message-ID"] = message_id

    alternative = MIMEMultipart("alternative")
    nl_html = _read_text(paths["dutch_primary_html"])
    plain = (
        "Weekly ETF EU Review - Dutch primary package.\n\n"
        "The Dutch primary PDF is attached. The English companion PDF is attached as companion material.\n"
        "This message is generated by the guarded ETF EU transport path."
    )
    alternative.attach(MIMEText(plain, "plain", "utf-8"))
    alternative.attach(MIMEText(nl_html, "html", "utf-8"))
    root.attach(alternative)

    attachments = [
        _attach_file(root, paths["dutch_primary_pdf"], "pdf"),
        _attach_file(root, paths["english_companion_pdf"], "pdf"),
        _attach_file(root, paths["dutch_primary_html"], "html"),
        _attach_file(root, paths["english_companion_html"], "html"),
    ]
    return root, message_id, attachments


def _send_message(message: MIMEMultipart, *, recipients: list[str], mail_from: str) -> None:
    smtp_host = os.environ.get("MRKT_RPRTS_SMTP_HOST")
    smtp_port = int(os.environ.get("MRKT_RPRTS_SMTP_PORT") or "587")
    smtp_user = os.environ.get("MRKT_RPRTS_SMTP_USER")
    smtp_pass = os.environ.get("MRKT_RPRTS_SMTP_PASS")
    _require(bool(smtp_host), "MRKT_RPRTS_SMTP_HOST is required")
    _require(bool(smtp_user), "MRKT_RPRTS_SMTP_USER is required")
    _require(bool(smtp_pass), "MRKT_RPRTS_SMTP_PASS is required")
    with smtplib.SMTP(str(smtp_host), smtp_port) as server:
        server.starttls()
        server.login(str(smtp_user), str(smtp_pass))
        server.sendmail(mail_from, recipients, message.as_string())


def _write_transport_result(output_dir: Path, payload: dict[str, Any], run_id: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"etf_eu_transport_result_{run_id}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _write_evidence_with_transport_contract(
    *,
    output_dir: Path,
    run_id: str,
    report_date: str,
    report_suffix: str,
    delivery_status: str,
    delivery_status_meaning: str,
    languages: list[dict[str, Any]],
    source: dict[str, Any],
    delivery_package_manifest: Path,
    ready_artifact: Path,
    paths: dict[str, Path],
    delivery_mode: str,
    transport_attempted: bool,
    transport_success: bool,
    transport_error: str | None,
    recipient_target_redacted: bool,
    smtp_or_transport_provider: str,
    message_id_or_receipt_reference: str | None,
) -> Path:
    evidence_path = write_etf_eu_delivery_evidence(
        output_dir,
        run_id=run_id,
        report_date=report_date,
        report_suffix=report_suffix,
        sender_entrypoint_path=Path("runtime/send_etf_eu_delivery_package.py"),
        dutch_primary_report_path=Path(f"output/weekly_etf_eu_review_nl_{report_suffix}.md"),
        english_companion_report_path=Path(f"output/weekly_etf_eu_review_{report_suffix}.md"),
        controlled_send_preflight_manifest=delivery_package_manifest,
        base_delivery_manifest=delivery_package_manifest,
        delivery_status=delivery_status,
        delivery_status_meaning=delivery_status_meaning,
        languages=languages,
        source=source,
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    evidence.update({
        "transport_contract_version": EVIDENCE_CONTRACT_VERSION,
        "delivery_mode": delivery_mode,
        "transport_attempted": transport_attempted,
        "transport_success": transport_success,
        "transport_error": transport_error,
        "recipient_target_redacted": recipient_target_redacted,
        "dutch_primary_pdf": str(paths["dutch_primary_pdf"]),
        "english_companion_pdf": str(paths["english_companion_pdf"]),
        "dutch_primary_html": str(paths["dutch_primary_html"]),
        "english_companion_html": str(paths["english_companion_html"]),
        "delivery_package_manifest": str(delivery_package_manifest),
        "ready_artifact": str(ready_artifact),
        "smtp_or_transport_provider": smtp_or_transport_provider,
        "message_id_or_receipt_reference": message_id_or_receipt_reference,
        "receipt_confirmed": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
    })
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return evidence_path


def execute_transport(
    *,
    run_id: str,
    report_date: str,
    report_suffix: str,
    delivery_package_manifest: Path,
    ready_artifact: Path,
    output_dir: Path,
    dry_run: bool,
) -> dict[str, Any]:
    _manifest, _ready, paths = _validate_inputs(
        delivery_package_manifest=delivery_package_manifest,
        ready_artifact=ready_artifact,
        report_suffix=report_suffix,
    )
    timestamp = _utc_now()
    recipients = ["dry-run@example.invalid"] if dry_run else _recipient_env()
    redacted_targets = _redacted_targets(recipients)
    mail_from = os.environ.get("MRKT_RPRTS_MAIL_FROM", "dry-run@example.invalid") if dry_run else os.environ.get("MRKT_RPRTS_MAIL_FROM")
    _require(bool(mail_from), "MRKT_RPRTS_MAIL_FROM is required")

    message_id = None
    attachments = [str(paths["dutch_primary_pdf"]), str(paths["english_companion_pdf"]), str(paths["dutch_primary_html"]), str(paths["english_companion_html"])]
    transport_attempted = False
    transport_success = False
    transport_error: str | None = None
    delivery_status = "not_attempted"
    meaning = "MVP20A dry-run evidence; no outbound delivery executed"
    provider = "dry_run_no_smtp"

    if not dry_run:
        transport_attempted = True
        provider = "smtp"
        try:
            message, message_id, attachments = _build_message(
                report_date=report_date,
                recipients=recipients,
                mail_from=str(mail_from),
                paths=paths,
            )
            _send_message(message, recipients=recipients, mail_from=str(mail_from))
            transport_success = True
            delivery_status = "smtp_sendmail_returned_no_exception"
            meaning = f"MVP20A SMTP sendmail returned without exception; {SUCCESS_CAVEAT}"
        except Exception as exc:  # noqa: BLE001 - evidence must capture exact transport failure
            transport_error = f"{type(exc).__name__}: {exc}"
            delivery_status = "smtp_sendmail_failed"
            meaning = "MVP20A SMTP transport failed before receipt confirmation"

    languages = _language_rows(
        recipients=recipients,
        paths=paths,
        report_suffix=report_suffix,
        delivery_package_manifest=delivery_package_manifest,
        timestamp=timestamp,
    )
    source = {
        "writer": "runtime/send_etf_eu_delivery_package.py",
        "basis": "mvp20a_real_transport",
        "transport_executed": transport_attempted,
        "transport_success": transport_success,
        "transport_error": transport_error,
        "delivery_error": transport_error,
        "delivery_package_manifest": str(delivery_package_manifest),
        "ready_artifact": str(ready_artifact),
    }
    evidence_path = _write_evidence_with_transport_contract(
        output_dir=output_dir,
        run_id=run_id,
        report_date=report_date,
        report_suffix=report_suffix,
        delivery_status=delivery_status,
        delivery_status_meaning=meaning,
        languages=languages,
        source=source,
        delivery_package_manifest=delivery_package_manifest,
        ready_artifact=ready_artifact,
        paths=paths,
        delivery_mode="dry_run" if dry_run else "send",
        transport_attempted=transport_attempted,
        transport_success=transport_success,
        transport_error=transport_error,
        recipient_target_redacted=True,
        smtp_or_transport_provider=provider,
        message_id_or_receipt_reference=(f"smtp_message_id:{message_id}" if message_id else None),
    )
    result = {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": timestamp,
        "run_id": run_id,
        "report_date": report_date,
        "report_suffix": report_suffix,
        "delivery_mode": "dry_run" if dry_run else "send",
        "transport_status": "transport_succeeded_unconfirmed" if transport_success else ("not_attempted" if dry_run else "transport_failed"),
        "transport_attempted": transport_attempted,
        "transport_success": transport_success,
        "transport_error": transport_error,
        "recipient_target_redacted": True,
        "recipient_hashes": redacted_targets,
        "attachment_paths": attachments,
        "delivery_evidence_path": str(evidence_path),
        "message_id_or_receipt_reference": f"smtp_message_id:{message_id}" if message_id else None,
        "receipt_confirmed": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
    }
    result_path = _write_transport_result(output_dir, result, run_id)
    result["transport_result_path"] = str(result_path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--delivery-package-manifest", required=True)
    parser.add_argument("--ready-artifact", required=True)
    parser.add_argument("--output-dir", default="output/delivery")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    result = execute_transport(
        run_id=args.run_id,
        report_date=args.report_date,
        report_suffix=args.report_suffix,
        delivery_package_manifest=Path(args.delivery_package_manifest),
        ready_artifact=Path(args.ready_artifact),
        output_dir=Path(args.output_dir),
        dry_run=args.dry_run,
    )
    print(
        "ETF_EU_MVP20A_TRANSPORT_RESULT | "
        f"mode={result['delivery_mode']} | attempted={result['transport_attempted']} | "
        f"success={result['transport_success']} | evidence={result['delivery_evidence_path']}"
    )
    if result["transport_attempted"] and not result["transport_success"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
