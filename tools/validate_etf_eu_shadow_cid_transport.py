from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_ATTACHMENT_SUFFIXES = {
    "_nl_20260724.pdf",
    "_en_20260724.pdf",
    "_nl_20260724.html",
    "_en_20260724.html",
}


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Shadow CID evidence must be a JSON object")
    return payload


def validate(payload: dict[str, Any], *, require_send: bool) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_eu_shadow_cid_transport_evidence_v1":
        blockers.append("unexpected schema_version")
    if payload.get("artifact_type") != "etf_eu_shadow_cid_transport_evidence":
        blockers.append("unexpected artifact_type")
    if not str(payload.get("subject") or "").startswith("SHADOW DELIVERY TEST — NO PORTFOLIO CHANGE | Weekly ETF EU"):
        blockers.append("shadow subject boundary missing")
    if payload.get("self_delivery_only") is not True:
        blockers.append("self-delivery boundary missing")
    if len(payload.get("recipient_hashes") or []) != 1:
        blockers.append("exactly one redacted recipient is required")
    if payload.get("receipt_confirmed") is not False:
        blockers.append("transport evidence must not claim receipt confirmation")
    for key in (
        "portfolio_mutation",
        "ledger_write",
        "funding_authority",
        "execution_authority",
        "activation_authority",
        "production_delivery_authority",
    ):
        if payload.get(key) is not False:
            blockers.append(f"{key} must be false")

    mime = payload.get("mime_structure") if isinstance(payload.get("mime_structure"), dict) else {}
    expected_mime = {
        "root": "multipart/mixed",
        "inline_container": "multipart/related",
        "body_container": "multipart/alternative",
        "inline_image_content_type": "image/png",
        "inline_image_filename": "weekly_etf_eu_portfolio_curve.png",
        "attachment_count": 4,
    }
    for key, expected in expected_mime.items():
        if mime.get(key) != expected:
            blockers.append(f"MIME field {key} mismatch")
    if mime.get("body_parts") != ["text/plain", "text/html"]:
        blockers.append("multipart alternative body parts mismatch")
    cid = str(mime.get("inline_image_content_id") or "")
    if not cid.startswith("weekly-etf-eu-chart-") or not cid.endswith("@weekly-etf-eu.local"):
        blockers.append("inline CID format mismatch")

    html = payload.get("html_checks") if isinstance(payload.get("html_checks"), dict) else {}
    if html.get("embedded_png_data_uri_count_before") != 1:
        blockers.append("source HTML must contain exactly one embedded PNG")
    if html.get("embedded_data_uri_count_after") != 0:
        blockers.append("outgoing HTML still contains a data URI")
    if html.get("cid_reference_count") != 1:
        blockers.append("outgoing HTML must reference the CID exactly once")
    if html.get("local_path_reference_count") != 0:
        blockers.append("outgoing HTML contains a local path")

    image = payload.get("inline_image") if isinstance(payload.get("inline_image"), dict) else {}
    if int(image.get("size_bytes") or 0) < 1000:
        blockers.append("inline PNG is unexpectedly small")
    if len(str(image.get("sha256") or "")) != 64:
        blockers.append("inline PNG hash missing")

    attachments = [row for row in (payload.get("attachments") or []) if isinstance(row, dict)]
    if len(attachments) != 4:
        blockers.append("attachment count mismatch")
    filenames = [str(row.get("filename") or "") for row in attachments]
    for suffix in EXPECTED_ATTACHMENT_SUFFIXES:
        if not any(name.endswith(suffix) for name in filenames):
            blockers.append(f"attachment with suffix {suffix} missing")
    if sum(1 for row in attachments if row.get("content_type") == "application/pdf") != 2:
        blockers.append("two PDF attachments are required")
    if sum(1 for row in attachments if row.get("content_type") == "text/html") != 2:
        blockers.append("two HTML attachments are required")
    for row in attachments:
        if int(row.get("size_bytes") or 0) <= 0 or len(str(row.get("sha256") or "")) != 64:
            blockers.append(f"invalid attachment evidence: {row.get('filename')}")

    source_files = payload.get("source_files") if isinstance(payload.get("source_files"), dict) else {}
    if set(source_files) != {"nl_html", "en_html", "nl_pdf", "en_pdf"}:
        blockers.append("source file inventory mismatch")
    if int(payload.get("raw_message_size_bytes") or 0) <= sum(int(row.get("size_bytes") or 0) for row in attachments):
        blockers.append("raw MIME message size is implausible")

    if require_send:
        if payload.get("mode") != "send":
            blockers.append("send-mode evidence required")
        if payload.get("smtp_transport_success") is not True:
            blockers.append("SMTP transport did not succeed")
    else:
        if payload.get("mode") not in {"dry_run", "send"}:
            blockers.append("unsupported mode")

    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ETF EU shadow CID transport evidence")
    parser.add_argument("path", type=Path)
    parser.add_argument("--require-send", action="store_true")
    args = parser.parse_args()
    payload = load(args.path)
    blockers = validate(payload, require_send=args.require_send)
    print(json.dumps({
        "artifact_type": "etf_eu_shadow_cid_transport_validation",
        "valid": not blockers,
        "blockers": blockers,
        "subject": payload.get("subject"),
        "message_id": payload.get("message_id"),
        "mime_structure": payload.get("mime_structure"),
        "smtp_transport_success": payload.get("smtp_transport_success"),
        "receipt_confirmed": payload.get("receipt_confirmed"),
    }, indent=2, ensure_ascii=False))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
