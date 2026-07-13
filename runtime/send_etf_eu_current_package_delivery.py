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

SUCCESS_CAVEAT = "SMTP success is not an end-recipient inbox receipt."
CURRENT_QUEUE_SCHEMA = "etf_eu_current_package_delivery_queue_v1"
CORRECTED_QUEUE_SCHEMA = "etf_eu_corrected_resend_queue_v1"
CURRENT_RESULT_SCHEMA = "etf_eu_current_package_transport_result_v1"
CURRENT_EVIDENCE_SCHEMA = "etf_eu_current_package_delivery_evidence_v1"
CORRECTED_RESULT_SCHEMA = "etf_eu_corrected_transport_result_v1"
CORRECTED_EVIDENCE_SCHEMA = "etf_eu_corrected_delivery_evidence_v1"
CORRECTION_NOTICE_NL = (
    "Dit is de gecorrigeerde versie van het Weekly ETF EU-rapport van 12 juli 2026. "
    "De eerdere PDF-bijlage was technisch onvolledig. De analyse, aanbeveling en "
    "portefeuillebeslissing zijn niet gewijzigd."
)
CORRECTION_NOTICE_EN = (
    "This is the corrected version of the Weekly ETF EU report dated 12 July 2026. "
    "The earlier PDF attachment was technically incomplete. The analysis, recommendation "
    "and portfolio decision are unchanged."
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _load_json(path: str | Path) -> dict[str, Any]:
    resolved = Path(path)
    _require(resolved.exists(), f"missing input: {resolved}")
    return json.loads(resolved.read_text(encoding="utf-8"))


def _read_queue(path: Path) -> dict[str, str]:
    _require(path.exists(), f"missing queue: {path}")
    data: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    _require(
        data.get("schema_version") in {CURRENT_QUEUE_SCHEMA, CORRECTED_QUEUE_SCHEMA},
        "queue schema mismatch",
    )
    return data


def _hash_value(value: str) -> str:
    raw = value.strip().lower()
    _require(bool(raw), "empty redaction value")
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _recipients(*, dry_run: bool) -> list[str]:
    if dry_run:
        return ["dry-run@example.invalid"]
    raw = os.environ.get("MRKT_RPRTS_MAIL_TO_NL") or os.environ.get("MRKT_RPRTS_MAIL_TO")
    _require(bool(raw), "runtime recipient target missing")
    recipients = [part.strip() for part in str(raw).replace(";", ",").split(",") if part.strip()]
    _require(bool(recipients), "runtime recipient target empty")
    return recipients


def _current_package_paths(manifest: dict[str, Any]) -> dict[str, Path]:
    return {
        "dutch_primary_markdown": Path(str(manifest["dutch_primary_markdown"])),
        "english_companion_markdown": Path(str(manifest["english_companion_markdown"])),
        "dutch_primary_html": Path(str(manifest["dutch_primary_html"])),
        "english_companion_html": Path(str(manifest["english_companion_html"])),
        "dutch_primary_pdf": Path(str(manifest["dutch_primary_pdf"])),
        "english_companion_pdf": Path(str(manifest["english_companion_pdf"])),
    }


def _corrected_package_paths(manifest: dict[str, Any]) -> dict[str, Path]:
    delivery = manifest.get("corrected_delivery_files") or {}
    required = {
        "dutch_primary_html",
        "dutch_primary_pdf",
        "english_companion_html",
        "english_companion_pdf",
    }
    _require(set(delivery) == required, "corrected delivery file set mismatch")
    return {key: Path(str(value)) for key, value in delivery.items()}


def _validate_current_package(
    queue: dict[str, str],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Path], dict[str, Any]]:
    manifest = _load_json(queue["package_manifest"])
    authorization = _load_json(queue["authorization_artifact"])

    _require(manifest.get("schema_version") == "etf_eu_fresh_generation_package_v1", "fresh package manifest schema mismatch")
    _require(manifest.get("ready_for_controlled_delivery") is True, "fresh package is not ready")
    _require(manifest.get("dutch_primary") is True, "Dutch primary flag missing")
    _require(manifest.get("english_companion") is True, "English companion flag missing")
    _require(manifest.get("html_output_available") is True, "HTML output unavailable")
    _require(manifest.get("pdf_output_available") is True, "PDF output unavailable")
    for key in ("valuation_grade", "funding_authority", "portfolio_mutation", "production_delivery_authority"):
        _require(manifest.get(key) is False, f"{key} must stay false")
    _require(str(manifest.get("report_suffix")) == str(queue.get("report_suffix")), "report suffix mismatch")

    _require(authorization.get("delivery_authorized") is True, "delivery_authorized must be true")
    _require(authorization.get("send_command_allowed") is True, "send_command_allowed must be true")
    _require(authorization.get("recipient_plaintext_values_exposed") is False, "recipient plaintext exposure flag must be false")
    _require(authorization.get("secret_values_exposed") is False, "secret exposure flag must be false")

    paths = _current_package_paths(manifest)
    for label, path in paths.items():
        _require(path.exists(), f"{label} missing: {path}")

    context = {
        "correction_transport": False,
        "package_manifest": queue["package_manifest"],
        "authorization_artifact": queue["authorization_artifact"],
        "correction_control_id": None,
        "source_run_id": None,
        "repair_run_id": None,
        "source_manifest_type": "etf_eu_fresh_generation_package_v1",
    }
    return manifest, authorization, paths, context


def _validate_corrected_package(
    queue: dict[str, str],
    *,
    mode: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Path], dict[str, Any]]:
    manifest_path = Path(queue["corrected_package_manifest"])
    manifest = _load_json(manifest_path)
    combined = _load_json(queue["combined_machine_gate_artifact"])
    visual = _load_json(queue["visual_review_artifact"])
    original_result = _load_json(queue["original_transport_result"])
    original_evidence = _load_json(queue["original_delivery_evidence"])

    _require(manifest.get("schema_version") == "etf_eu_corrected_resend_package_v1", "corrected package schema mismatch")
    _require(manifest.get("correction_control_id") == queue.get("correction_control_id"), "correction control id mismatch")
    _require(manifest.get("source_run_id") == queue.get("source_run_id"), "source run mismatch")
    _require(manifest.get("repair_run_id") == queue.get("repair_run_id"), "repair run mismatch")
    _require(manifest.get("report_date") == queue.get("report_date"), "report date mismatch")
    _require(str(manifest.get("report_suffix")) == str(queue.get("report_suffix")), "report suffix mismatch")
    _require(manifest.get("corrected_resend_prepared") is True, "corrected resend package is not prepared")
    _require(manifest.get("corrected_resend_executed") is False, "corrected resend package already marked executed")
    _require(manifest.get("corrected_client_output_valid") is True, "corrected client output invalid")
    _require(manifest.get("byte_identity_passed") is True, "corrected package byte identity failed")
    _require(manifest.get("original_client_output_valid") is False, "original output validity changed")
    _require(not manifest.get("blockers"), "corrected package has blockers")
    for key in (
        "recipient_plaintext_values_exposed",
        "secret_values_exposed",
        "raw_receipt_pdf_stored_in_github",
        "valuation_grade",
        "funding_authority",
        "portfolio_mutation",
        "production_delivery_authority",
    ):
        _require(manifest.get(key) is False, f"{key} must stay false")

    _require(combined.get("pdf_client_grade_passed") is True, "combined corrected PDF machine gate failed")
    _require(not combined.get("blockers"), "combined corrected PDF machine gate has blockers")
    _require(visual.get("visual_review_passed") is True, "corrected PDF visual review failed")
    _require(not visual.get("blockers"), "corrected PDF visual review has blockers")
    _require(original_result.get("transport_success") is True, "original transport result not successful")
    _require(original_result.get("receipt_confirmed") is False, "original transport receipt state changed")
    _require(original_evidence.get("transport_success") is True, "original delivery evidence not successful")
    _require(original_evidence.get("receipt_confirmed") is False, "original delivery receipt state changed")

    paths = _corrected_package_paths(manifest)
    expected_hashes = manifest.get("delivery_sha256") or {}
    for label, path in paths.items():
        _require(path.exists(), f"corrected delivery file missing: {label}={path}")
        _require(
            str(path).startswith(f"output/corrected_delivery_package/{queue['correction_control_id']}/"),
            f"corrected delivery file outside package: {path}",
        )
        _require(_file_sha256(path) == str(expected_hashes.get(label)), f"corrected delivery hash mismatch: {label}")

    authorization: dict[str, Any] = {
        "corrected_resend_authorized": mode != "send",
        "send_command_allowed": mode != "send",
        "recipient_plaintext_values_exposed": False,
        "secret_values_exposed": False,
    }
    authorization_path = os.environ.get("ETF_EU_CORRECTED_AUTHORIZATION_ARTIFACT")
    if mode == "send":
        _require(bool(authorization_path), "corrected resend authorization artifact missing")
        authorization = _load_json(str(authorization_path))
        _require(authorization.get("corrected_resend_authorized") is True, "corrected resend not authorized")
        _require(authorization.get("send_command_allowed") is True, "corrected send command not allowed")
        _require(authorization.get("send_confirmation_received") is True, "corrected send confirmation missing")
        _require(authorization.get("recipient_plaintext_values_exposed") is False, "recipient exposure flag must be false")
        _require(authorization.get("secret_values_exposed") is False, "secret exposure flag must be false")

    context = {
        "correction_transport": True,
        "package_manifest": str(manifest_path),
        "authorization_artifact": str(authorization_path) if authorization_path else None,
        "correction_control_id": queue["correction_control_id"],
        "source_run_id": queue["source_run_id"],
        "repair_run_id": queue["repair_run_id"],
        "source_manifest_type": "etf_eu_corrected_resend_package_v1",
    }
    return manifest, authorization, paths, context


def _attach_file(message: MIMEMultipart, path: Path, subtype: str) -> str:
    payload = path.read_bytes()
    part = MIMEApplication(payload, _subtype=subtype)
    part.add_header("Content-Disposition", "attachment", filename=path.name)
    message.attach(part)
    return str(path)


def _build_message(
    report_date: str,
    recipients: list[str],
    paths: dict[str, Path],
    *,
    correction_transport: bool,
) -> tuple[MIMEMultipart, str, list[str]]:
    mail_from = os.environ.get("MRKT_RPRTS_MAIL_FROM")
    _require(bool(mail_from), "runtime sender missing")
    subject_prefix = os.environ.get("MRKT_RPRTS_SUBJECT_PREFIX_NL") or "Weekly ETF EU Review | Nederlands"
    if correction_transport:
        subject_prefix = f"{subject_prefix} | Gecorrigeerde versie"

    root = MIMEMultipart("mixed")
    root["Subject"] = f"{subject_prefix} {report_date}"
    root["From"] = str(mail_from)
    root["To"] = ", ".join(recipients)
    root["Date"] = formatdate(localtime=False)
    message_id = make_msgid(domain="weekly-etf-eu.local")
    root["Message-ID"] = message_id

    body = MIMEMultipart("alternative")
    html = paths["dutch_primary_html"].read_text(encoding="utf-8")
    if correction_transport:
        plain = f"{CORRECTION_NOTICE_NL}\n\n{CORRECTION_NOTICE_EN}"
        notice_html = (
            '<div style="border:1px solid #c7ced6;padding:12px;margin:0 0 16px 0;">'
            f"<p><strong>Gecorrigeerde versie</strong></p><p>{CORRECTION_NOTICE_NL}</p>"
            f"<p>{CORRECTION_NOTICE_EN}</p></div>"
        )
        html = notice_html + html
    else:
        plain = "Weekly ETF EU Review. Dutch primary PDF and English companion PDF attached."
    body.attach(MIMEText(plain, "plain", "utf-8"))
    body.attach(MIMEText(html, "html", "utf-8"))
    root.attach(body)

    attachments = [
        _attach_file(root, paths["dutch_primary_pdf"], "pdf"),
        _attach_file(root, paths["english_companion_pdf"], "pdf"),
        _attach_file(root, paths["dutch_primary_html"], "html"),
        _attach_file(root, paths["english_companion_html"], "html"),
    ]
    return root, message_id, attachments


def _send(message: MIMEMultipart, recipients: list[str]) -> None:
    host = os.environ.get("MRKT_RPRTS_SMTP_HOST")
    port = int(os.environ.get("MRKT_RPRTS_SMTP_PORT") or "587")
    user = os.environ.get("MRKT_RPRTS_SMTP_USER")
    password = os.environ.get("MRKT_RPRTS_SMTP_PASS")
    mail_from = os.environ.get("MRKT_RPRTS_MAIL_FROM")
    _require(bool(host), "runtime transport host missing")
    _require(bool(user), "runtime transport user missing")
    _require(bool(password), "runtime transport credential missing")
    _require(bool(mail_from), "runtime sender missing")
    with smtplib.SMTP(str(host), port) as server:
        server.starttls()
        server.login(str(user), str(password))
        server.sendmail(str(mail_from), recipients, message.as_string())


def _language_rows(
    *,
    recipients: list[str],
    paths: dict[str, Path],
    context: dict[str, Any],
    timestamp: str,
) -> list[dict[str, Any]]:
    redacted = ",".join(_hash_value(item) for item in recipients)
    correction = bool(context["correction_transport"])
    mode_prefix = "corrected_resend_transport" if correction else "current_package_transport"
    return [
        {
            "language": "nl",
            "report_path": str(paths["dutch_primary_pdf"]),
            "source_manifest_path": context["package_manifest"],
            "source_manifest_type": context["source_manifest_type"],
            "timestamp_utc": timestamp,
            "mode": mode_prefix,
            "report": "Dutch primary corrected client report" if correction else "Dutch primary client report",
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
            "report_path": str(paths["english_companion_pdf"]),
            "source_manifest_path": context["package_manifest"],
            "source_manifest_type": context["source_manifest_type"],
            "timestamp_utc": timestamp,
            "mode": f"{mode_prefix}_companion",
            "report": "English corrected companion report" if correction else "English companion report",
            "recipient_hash": redacted,
            "recipient_redacted": True,
            "html_body": False,
            "pdf_attached": "yes",
            "attachments": [str(paths["english_companion_pdf"]), str(paths["english_companion_html"])],
            "attachment_count": 2,
            "pdf_attachments": [str(paths["english_companion_pdf"])],
        },
    ]


def execute(*, queue_path: Path, mode: str, run_id: str | None, output_dir: Path) -> dict[str, Any]:
    _require(mode in {"dry_run", "send"}, f"unsupported mode: {mode}")
    queue = _read_queue(queue_path)
    correction_transport = queue["schema_version"] == CORRECTED_QUEUE_SCHEMA
    if correction_transport:
        _manifest, _authorization, paths, context = _validate_corrected_package(queue, mode=mode)
    else:
        _manifest, _authorization, paths, context = _validate_current_package(queue)

    timestamp = _utc_now()
    effective_run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dry_run = mode == "dry_run"
    recipients = _recipients(dry_run=dry_run)
    message_id: str | None = None
    transport_attempted = False
    transport_success = False
    transport_error: str | None = None
    status = "dry_run_no_transport"
    status_meaning = "Dry-run evidence only; no outbound transport was attempted."
    provider = "dry_run_no_transport"
    attachments = [
        str(paths["dutch_primary_pdf"]),
        str(paths["english_companion_pdf"]),
        str(paths["dutch_primary_html"]),
        str(paths["english_companion_html"]),
    ]

    if not dry_run:
        transport_attempted = True
        provider = "smtp"
        try:
            message, message_id, attachments = _build_message(
                str(queue["report_date"]),
                recipients,
                paths,
                correction_transport=correction_transport,
            )
            _send(message, recipients)
            transport_success = True
            status = "smtp_sendmail_returned_no_exception"
            status_meaning = SUCCESS_CAVEAT
        except Exception as exc:  # noqa: BLE001
            transport_error = f"{type(exc).__name__}: {exc}"
            status = "smtp_sendmail_failed"
            status_meaning = "Transport attempt failed before receipt confirmation."

    output_dir.mkdir(parents=True, exist_ok=True)
    languages = _language_rows(recipients=recipients, paths=paths, context=context, timestamp=timestamp)
    attachment_sha256 = {
        label: _file_sha256(path)
        for label, path in paths.items()
        if label in {
            "dutch_primary_html",
            "dutch_primary_pdf",
            "english_companion_html",
            "english_companion_pdf",
        }
    }
    message_reference_hash = _hash_value(message_id) if message_id else None
    evidence_schema = CORRECTED_EVIDENCE_SCHEMA if correction_transport else CURRENT_EVIDENCE_SCHEMA
    result_schema = CORRECTED_RESULT_SCHEMA if correction_transport else CURRENT_RESULT_SCHEMA
    evidence_type = (
        "etf_eu_corrected_delivery_evidence"
        if correction_transport
        else "etf_eu_current_package_delivery_evidence"
    )
    result_type = (
        "etf_eu_corrected_transport_result"
        if correction_transport
        else "etf_eu_current_package_transport_result"
    )
    evidence_prefix = (
        "etf_eu_corrected_delivery_evidence"
        if correction_transport
        else "etf_eu_current_package_delivery_evidence"
    )
    result_prefix = (
        "etf_eu_corrected_transport_result"
        if correction_transport
        else "etf_eu_current_package_transport_result"
    )

    evidence = {
        "schema_version": evidence_schema,
        "artifact_type": evidence_type,
        "generated_at_utc": timestamp,
        "run_id": effective_run_id,
        "correction_transport": correction_transport,
        "correction_control_id": context["correction_control_id"],
        "source_run_id": context["source_run_id"],
        "repair_run_id": context["repair_run_id"],
        "report_date": queue["report_date"],
        "report_suffix": queue["report_suffix"],
        "delivery_mode": mode,
        "delivery_status": status,
        "delivery_status_meaning": status_meaning,
        "recipient_data_policy": "redacted_hash_only",
        "recipient_plaintext_values_exposed": False,
        "secret_values_exposed": False,
        "raw_receipt_pdf_stored_in_github": False,
        "raw_email_content_stored": False,
        "transport_attempted": transport_attempted,
        "transport_success": transport_success,
        "send_executed": transport_success,
        "transport_error": transport_error,
        "smtp_or_transport_provider": provider,
        "message_reference_hash": message_reference_hash,
        "receipt_confirmed": False,
        "delivery_success_claimed": False,
        "queue_artifact": str(queue_path),
        "package_manifest": context["package_manifest"],
        "authorization_artifact": context["authorization_artifact"],
        "languages": languages,
        "language_count": len(languages),
        "attachment_count": len(attachments),
        "attachment_paths": attachments,
        "attachment_sha256": attachment_sha256,
        "original_transport_evidence_overwritten": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
    }
    evidence_path = output_dir / f"{evidence_prefix}_{effective_run_id}.json"
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = {
        "schema_version": result_schema,
        "artifact_type": result_type,
        "generated_at_utc": timestamp,
        "run_id": effective_run_id,
        "correction_transport": correction_transport,
        "correction_control_id": context["correction_control_id"],
        "source_run_id": context["source_run_id"],
        "repair_run_id": context["repair_run_id"],
        "report_date": queue["report_date"],
        "report_suffix": queue["report_suffix"],
        "delivery_mode": mode,
        "delivery_status": status,
        "delivery_status_meaning": status_meaning,
        "transport_attempted": transport_attempted,
        "transport_success": transport_success,
        "send_executed": transport_success,
        "transport_error": transport_error,
        "message_reference_hash": message_reference_hash,
        "delivery_evidence_path": str(evidence_path),
        "attachment_count": len(attachments),
        "attachment_paths": attachments,
        "attachment_sha256": attachment_sha256,
        "recipient_target_redacted": True,
        "recipient_hashes": [_hash_value(item) for item in recipients],
        "receipt_confirmed": False,
        "original_transport_evidence_overwritten": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "recipient_plaintext_values_exposed": False,
        "secret_values_exposed": False,
        "raw_email_content_stored": False,
        "raw_receipt_pdf_stored_in_github": False,
    }
    result_path = output_dir / f"{result_prefix}_{effective_run_id}.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result["transport_result_path"] = str(result_path)
    print(
        "ETF_EU_TRANSPORT_RESULT | "
        f"correction={correction_transport} | mode={mode} | attempted={transport_attempted} | "
        f"success={transport_success} | evidence={evidence_path}"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", required=True)
    parser.add_argument("--mode", choices=["dry_run", "send"], required=True)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-dir", default="output/delivery")
    args = parser.parse_args()
    execute(queue_path=Path(args.queue), mode=args.mode, run_id=args.run_id, output_dir=Path(args.output_dir))


if __name__ == "__main__":
    main()
