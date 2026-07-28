from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import smtplib
from datetime import datetime, timezone
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from pathlib import Path
from typing import Any


DATA_URI_RE = re.compile(r"data:image/png;base64,([A-Za-z0-9+/=]+)")
SHADOW_SUBJECT_PREFIX = "SHADOW DELIVERY TEST — NO PORTFOLIO CHANGE | Weekly ETF EU"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def hash_value(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.strip().lower().encode("utf-8")).hexdigest()


def find_one(source_dir: Path, pattern: str) -> Path:
    matches = sorted(path for path in source_dir.rglob(pattern) if path.is_file())
    require(len(matches) == 1, f"Expected exactly one {pattern}; found {len(matches)}")
    return matches[0]


def source_files(source_dir: Path) -> dict[str, Path]:
    return {
        "nl_html": find_one(source_dir, "weekly_etf_eu_sister_shadow_nl_*.html"),
        "en_html": find_one(source_dir, "weekly_etf_eu_sister_shadow_en_*.html"),
        "nl_pdf": find_one(source_dir, "weekly_etf_eu_sister_shadow_nl_*.pdf"),
        "en_pdf": find_one(source_dir, "weekly_etf_eu_sister_shadow_en_*.pdf"),
    }


def report_date_from_name(path: Path) -> str:
    match = re.search(r"_(\d{8})\.(?:html|pdf)$", path.name)
    require(bool(match), f"Could not derive report date from {path.name}")
    raw = match.group(1)
    return f"{raw[:4]}-{raw[4:6]}-{raw[6:]}"


def recipients() -> tuple[str, list[str]]:
    mail_from = str(os.environ.get("MRKT_RPRTS_MAIL_FROM") or "").strip()
    raw = str(os.environ.get("MRKT_RPRTS_MAIL_TO_NL") or os.environ.get("MRKT_RPRTS_MAIL_TO") or "").strip()
    require(bool(mail_from), "Shadow sender is missing")
    require(bool(raw), "Shadow recipient is missing")
    values = [part.strip() for part in raw.replace(";", ",").split(",") if part.strip()]
    require(len(values) == 1, "Shadow CID test requires exactly one recipient")
    require(values[0].casefold() == mail_from.casefold(), "Shadow CID test is restricted to self-delivery")
    return mail_from, values


def attach_file(root: MIMEMultipart, path: Path, subtype: str) -> dict[str, Any]:
    payload = path.read_bytes()
    part = MIMEApplication(payload, _subtype=subtype)
    part.add_header("Content-Disposition", "attachment", filename=path.name)
    root.attach(part)
    return {
        "filename": path.name,
        "size_bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "content_type": f"application/{subtype}",
    }


def build_message(paths: dict[str, Path], run_id: str) -> tuple[MIMEMultipart, dict[str, Any]]:
    mail_from, to_values = recipients()
    report_date = report_date_from_name(paths["nl_html"])
    require(report_date == report_date_from_name(paths["en_html"]), "Bilingual report dates differ")

    html_source = paths["nl_html"].read_text(encoding="utf-8")
    matches = list(DATA_URI_RE.finditer(html_source))
    require(len(matches) == 1, f"Expected exactly one embedded PNG data URI; found {len(matches)}")
    image_bytes = base64.b64decode(matches[0].group(1), validate=True)
    require(image_bytes.startswith(b"\x89PNG\r\n\x1a\n"), "Embedded chart is not a PNG")

    cid_value = f"weekly-etf-eu-chart-{run_id}@weekly-etf-eu.local"
    html_body = DATA_URI_RE.sub(f"cid:{cid_value}", html_source, count=1)
    require("data:image/" not in html_body, "Data URI remained in the outgoing HTML body")
    require(html_body.count(f"cid:{cid_value}") == 1, "Outgoing HTML must contain exactly one CID reference")
    require("/mnt/data/" not in html_body and "file://" not in html_body, "Outgoing HTML contains a local path")

    root = MIMEMultipart("mixed")
    subject = f"{SHADOW_SUBJECT_PREFIX} | {report_date} | {run_id}"
    root["Subject"] = subject
    root["From"] = mail_from
    root["To"] = to_values[0]
    root["Date"] = formatdate(localtime=False)
    message_id = make_msgid(domain="weekly-etf-eu.local")
    root["Message-ID"] = message_id
    root["X-ETF-EU-Shadow-Test"] = "true"
    root["X-ETF-EU-Shadow-Run-ID"] = run_id
    root["X-ETF-EU-Portfolio-Mutation"] = "false"

    related = MIMEMultipart("related")
    alternative = MIMEMultipart("alternative")
    plain = (
        "SHADOW DELIVERY TEST — NO PORTFOLIO CHANGE\n\n"
        "This message validates multipart MIME, inline CID chart rendering and report attachments. "
        "It does not change the model portfolio, trade ledger, production report or delivery state."
    )
    test_banner = (
        '<div style="border:2px solid #a05a00;background:#fff4df;padding:12px;margin:0 0 16px 0;">'
        '<strong>SHADOW DELIVERY TEST — NO PORTFOLIO CHANGE</strong><br>'
        'MIME/CID rendering test only. No model-portfolio, ledger or production-delivery change.'</n        '</div>'
    )
    alternative.attach(MIMEText(plain, "plain", "utf-8"))
    alternative.attach(MIMEText(test_banner + html_body, "html", "utf-8"))
    related.attach(alternative)

    image = MIMEImage(image_bytes, _subtype="png")
    image.add_header("Content-ID", f"<{cid_value}>")
    image.add_header("Content-Disposition", "inline", filename="weekly_etf_eu_portfolio_curve.png")
    image.add_header("Content-Location", "weekly_etf_eu_portfolio_curve.png")
    related.attach(image)
    root.attach(related)

    attachments = [
        attach_file(root, paths["nl_pdf"], "pdf"),
        attach_file(root, paths["en_pdf"], "pdf"),
        attach_file(root, paths["nl_html"], "html"),
        attach_file(root, paths["en_html"], "html"),
    ]
    raw = root.as_bytes()
    evidence = {
        "schema_version": "etf_eu_shadow_cid_transport_evidence_v1",
        "artifact_type": "etf_eu_shadow_cid_transport_evidence",
        "generated_at_utc": utc_now(),
        "run_id": run_id,
        "report_date": report_date,
        "subject": subject,
        "message_id": message_id,
        "sender_hash": hash_value(mail_from),
        "recipient_hashes": [hash_value(value) for value in to_values],
        "self_delivery_only": True,
        "mime_structure": {
            "root": "multipart/mixed",
            "inline_container": "multipart/related",
            "body_container": "multipart/alternative",
            "body_parts": ["text/plain", "text/html"],
            "inline_image_content_type": "image/png",
            "inline_image_content_id": cid_value,
            "inline_image_filename": "weekly_etf_eu_portfolio_curve.png",
            "attachment_count": len(attachments),
        },
        "html_checks": {
            "embedded_png_data_uri_count_before": len(matches),
            "embedded_data_uri_count_after": 0,
            "cid_reference_count": html_body.count(f"cid:{cid_value}"),
            "local_path_reference_count": html_body.count("/mnt/data/") + html_body.count("file://"),
        },
        "inline_image": {
            "size_bytes": len(image_bytes),
            "sha256": hashlib.sha256(image_bytes).hexdigest(),
        },
        "attachments": attachments,
        "raw_message_size_bytes": len(raw),
        "source_files": {
            key: {"filename": path.name, "size_bytes": path.stat().st_size, "sha256": file_sha256(path)}
            for key, path in paths.items()
        },
        "smtp_transport_success": False,
        "receipt_confirmed": False,
        "portfolio_mutation": False,
        "ledger_write": False,
        "funding_authority": False,
        "execution_authority": False,
        "activation_authority": False,
        "production_delivery_authority": False,
    }
    return root, evidence


def send(message: MIMEMultipart, recipients_list: list[str]) -> None:
    host = str(os.environ.get("MRKT_RPRTS_SMTP_HOST") or "").strip()
    port = int(os.environ.get("MRKT_RPRTS_SMTP_PORT") or "587")
    user = str(os.environ.get("MRKT_RPRTS_SMTP_USER") or "").strip()
    password = str(os.environ.get("MRKT_RPRTS_SMTP_PASS") or "")
    mail_from = str(os.environ.get("MRKT_RPRTS_MAIL_FROM") or "").strip()
    require(bool(host), "SMTP host is missing")
    require(bool(user), "SMTP user is missing")
    require(bool(password), "SMTP password is missing")
    require(bool(mail_from), "SMTP sender is missing")
    with smtplib.SMTP(host, port, timeout=60) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(mail_from, recipients_list, message.as_string())


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a self-addressed ETF EU shadow CID delivery test")
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=("dry_run", "send"), required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    paths = source_files(args.source_dir)
    message, evidence = build_message(paths, args.run_id)
    if args.mode == "send":
        _mail_from, to_values = recipients()
        send(message, to_values)
        evidence["smtp_transport_success"] = True
    evidence["mode"] = args.mode
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
