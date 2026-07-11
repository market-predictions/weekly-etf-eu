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
RESULT_SCHEMA = "etf_eu_current_package_transport_result_v1"
EVIDENCE_SCHEMA = "etf_eu_current_package_delivery_evidence_v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _load_json(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    _require(path.exists(), f"missing input: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _read_queue(path: Path) -> dict[str, str]:
    _require(path.exists(), f"missing queue: {path}")
    data: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    _require(data.get("schema_version") == "etf_eu_current_package_delivery_queue_v1", "queue schema mismatch")
    return data


def _hash_value(value: str) -> str:
    raw = value.strip().lower()
    _require(bool(raw), "empty redaction value")
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _recipients(*, dry_run: bool) -> list[str]:
    if dry_run:
        return ["dry-run@example.invalid"]
    raw = os.environ.get("MRKT_RPRTS_MAIL_TO_NL") or os.environ.get("MRKT_RPRTS_MAIL_TO")
    _require(bool(raw), "runtime recipient target missing")
    return [part.strip() for part in str(raw).replace(";", ",").split(",") if part.strip()]


def _package_paths(manifest: dict[str, Any]) -> dict[str, Path]:
    return {
        "dutch_primary_markdown": Path(str(manifest["dutch_primary_markdown"])),
        "english_companion_markdown": Path(str(manifest["english_companion_markdown"])),
        "dutch_primary_html": Path(str(manifest["dutch_primary_html"])),
        "english_companion_html": Path(str(manifest["english_companion_html"])),
        "dutch_primary_pdf": Path(str(manifest["dutch_primary_pdf"])),
        "english_companion_pdf": Path(str(manifest["english_companion_pdf"])),
    }


def _validate_current_package(queue: dict[str, str]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Path]]:
    manifest = _load_json(queue["package_manifest"])
    authorization = _load_json(queue["authorization_artifact"])

    _require(manifest.get("schema_version") == "etf_eu_fresh_generation_package_v1", "fresh package manifest schema mismatch")
    _require(manifest.get("ready_for_controlled_delivery") is True, "fresh package is not ready")
    _require(manifest.get("dutch_primary") is True, "Dutch primary flag missing")
    _require(manifest.get("english_companion") is True, "English companion flag missing")
    _require(manifest.get("html_output_available") is True, "HTML output unavailable")
    _require(manifest.get("pdf_output_available") is True, "PDF output unavailable")
    _require(manifest.get("valuation_grade") is False, "valuation grade must stay false")
    _require(manifest.get("funding_authority") is False, "funding authority must stay false")
    _require(manifest.get("portfolio_mutation") is False, "portfolio mutation must stay false")
    _require(manifest.get("production_delivery_authority") is False, "production delivery authority must stay false")
    _require(str(manifest.get("report_suffix")) == str(queue.get("report_suffix")), "report suffix mismatch")

    _require(authorization.get("delivery_authorized") is True, "delivery_authorized must be true")
    _require(authorization.get("send_command_allowed") is True, "send_command_allowed must be true")
    _require(authorization.get("recipient_plaintext_values_exposed") is False, "recipient plaintext exposure flag must be false")
    _require(authorization.get("secret_values_exposed") is False, "secret exposure flag must be false")

    paths = _package_paths(manifest)
    for label, path in paths.items():
        _require(path.exists(), f"{label} missing: {path}")
    return manifest, authorization, paths


def _attach_file(message: MIMEMultipart, path: Path, subtype: str) -> str:
    payload = path.read_bytes()
    part = MIMEApplication(payload, _subtype=subtype)
    part.add_header("Content-Disposition", "attachment", filename=path.name)
    message.attach(part)
    return str(path)


def _build_message(report_date: str, recipients: list[str], paths: dict[str, Path]) -> tuple[MIMEMultipart, str, list[str]]:
    mail_from = os.environ.get("MRKT_RPRTS_MAIL_FROM")
    _require(bool(mail_from), "runtime sender missing")
    subject_prefix = os.environ.get("MRKT_RPRTS_SUBJECT_PREFIX_NL") or "Weekly ETF EU Review | Nederlands"
    root = MIMEMultipart("mixed")
    root["Subject"] = f"{subject_prefix} {report_date}"
    root["From"] = str(mail_from)
    root["To"] = ", ".join(recipients)
    root["Date"] = formatdate(localtime=False)
    message_id = make_msgid(domain="weekly-etf-eu.local")
    root["Message-ID"] = message_id
    body = MIMEMultipart("alternative")
    html = paths["dutch_primary_html"].read_text(encoding="utf-8")
    body.attach(MIMEText("Weekly ETF EU Review. Dutch primary PDF and English companion PDF attached.", "plain", "utf-8"))
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


def _language_rows(*, recipients: list[str], paths: dict[str, Path], queue: dict[str, str], timestamp: str) -> list[dict[str, Any]]:
    redacted = ",".join(_hash_value(item) for item in recipients)
    return [
        {
            "language": "nl",
            "report_path": str(paths["dutch_primary_markdown"]),
            "source_manifest_path": str(queue["package_manifest"]),
            "source_manifest_type": "etf_eu_fresh_generation_package_v1",
            "timestamp_utc": timestamp,
            "mode": "current_package_transport",
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
            "report_path": str(paths["english_companion_markdown"]),
            "source_manifest_path": str(queue["package_manifest"]),
            "source_manifest_type": "etf_eu_fresh_generation_package_v1",
            "timestamp_utc": timestamp,
            "mode": "current_package_transport_companion",
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


def execute(*, queue_path: Path, mode: str, run_id: str | None, output_dir: Path) -> dict[str, Any]:
    _require(mode in {"dry_run", "send"}, f"unsupported mode: {mode}")
    queue = _read_queue(queue_path)
    _manifest, _authorization, paths = _validate_current_package(queue)
    timestamp = _utc_now()
    effective_run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dry_run = mode == "dry_run"
    recipients = _recipients(dry_run=dry_run)
    message_id = None
    transport_attempted = False
    transport_success = False
    transport_error = None
    status = "dry_run_no_transport"
    status_meaning = "Dry-run evidence only; no outbound transport was attempted."
    provider = "dry_run_no_transport"
    attachments = [str(paths["dutch_primary_pdf"]), str(paths["english_companion_pdf"]), str(paths["dutch_primary_html"]), str(paths["english_companion_html"])]

    if not dry_run:
        transport_attempted = True
        provider = "smtp"
        try:
            message, message_id, attachments = _build_message(str(queue["report_date"]), recipients, paths)
            _send(message, recipients)
            transport_success = True
            status = "smtp_sendmail_returned_no_exception"
            status_meaning = SUCCESS_CAVEAT
        except Exception as exc:  # noqa: BLE001
            transport_error = f"{type(exc).__name__}: {exc}"
            status = "smtp_sendmail_failed"
            status_meaning = "Transport attempt failed before receipt confirmation."

    output_dir.mkdir(parents=True, exist_ok=True)
    languages = _language_rows(recipients=recipients, paths=paths, queue=queue, timestamp=timestamp)
    evidence = {
        "schema_version": EVIDENCE_SCHEMA,
        "artifact_type": "etf_eu_current_package_delivery_evidence",
        "generated_at_utc": timestamp,
        "run_id": effective_run_id,
        "report_date": queue["report_date"],
        "report_suffix": queue["report_suffix"],
        "delivery_mode": mode,
        "delivery_status": status,
        "delivery_status_meaning": status_meaning,
        "recipient_data_policy": "redacted_hash_only",
        "recipient_plaintext_values_exposed": False,
        "secret_values_exposed": False,
        "raw_receipt_pdf_stored_in_github": False,
        "transport_attempted": transport_attempted,
        "transport_success": transport_success,
        "transport_error": transport_error,
        "smtp_or_transport_provider": provider,
        "message_id_or_receipt_reference": f"smtp_message_id:{message_id}" if message_id else None,
        "receipt_confirmed": False,
        "delivery_success_claimed": False,
        "queue_artifact": str(queue_path),
        "package_manifest": queue["package_manifest"],
        "authorization_artifact": queue["authorization_artifact"],
        "languages": languages,
        "language_count": len(languages),
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
    }
    evidence_path = output_dir / f"etf_eu_current_package_delivery_evidence_{effective_run_id}.json"
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = {
        "schema_version": RESULT_SCHEMA,
        "artifact_type": "etf_eu_current_package_transport_result",
        "generated_at_utc": timestamp,
        "run_id": effective_run_id,
        "report_date": queue["report_date"],
        "report_suffix": queue["report_suffix"],
        "delivery_mode": mode,
        "delivery_status": status,
        "transport_attempted": transport_attempted,
        "transport_success": transport_success,
        "transport_error": transport_error,
        "message_id_or_receipt_reference": f"smtp_message_id:{message_id}" if message_id else None,
        "delivery_evidence_path": str(evidence_path),
        "attachment_paths": attachments,
        "recipient_target_redacted": True,
        "recipient_hashes": [_hash_value(item) for item in recipients],
        "receipt_confirmed": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "recipient_plaintext_values_exposed": False,
        "secret_values_exposed": False,
        "raw_receipt_pdf_stored_in_github": False,
    }
    result_path = output_dir / f"etf_eu_current_package_transport_result_{effective_run_id}.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result["transport_result_path"] = str(result_path)
    print(
        "ETF_EU_CURRENT_PACKAGE_TRANSPORT_RESULT | "
        f"mode={mode} | attempted={transport_attempted} | success={transport_success} | evidence={evidence_path}"
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
