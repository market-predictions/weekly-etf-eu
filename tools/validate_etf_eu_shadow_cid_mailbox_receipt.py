from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED_ATTACHMENTS = {
    "weekly_etf_eu_sister_shadow_nl_20260724.pdf": ("application/pdf", 142103, "16e62d7cec7a352d3bdae65589e4014f80517f08d3d574ee70a6e8913f3e4d10"),
    "weekly_etf_eu_sister_shadow_en_20260724.pdf": ("application/pdf", 138959, "9ef6b3d0e66628e0c6d6089153ad4eeb39b9f8215d94c1228a89a81516a7d85f"),
    "weekly_etf_eu_sister_shadow_nl_20260724.html": ("text/html", 115823, "4415340d643e0a8a9fc149b0e714ccbe5784db77bdcd26930c52363e42dc5b33"),
    "weekly_etf_eu_sister_shadow_en_20260724.html": ("text/html", 112733, "899f87f7317ddc5ac22f0e510e14f14588081a0acfba8173b0ffcb80309f7ca6"),
}


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Receipt must be a JSON object")
    return payload


def validate(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_eu_shadow_cid_mailbox_receipt_v1":
        blockers.append("unexpected schema_version")
    if payload.get("artifact_type") != "etf_eu_shadow_cid_mailbox_receipt":
        blockers.append("unexpected artifact_type")
    if payload.get("shadow_run_id") != "wp_sync_08_cid_20260729_002500":
        blockers.append("shadow run mismatch")
    if payload.get("source_delivery_workflow_run_id") != 30410951339:
        blockers.append("delivery run mismatch")
    if payload.get("source_report_workflow_run_id") != 30410361517:
        blockers.append("report run mismatch")
    if payload.get("source_report_head_sha") != "d33169fa513e22ac9197efe4fab9857ebaa6f85f":
        blockers.append("report source SHA mismatch")
    for key in ("sent_match_observed", "inbox_match_observed", "same_message_observed_in_sent_and_inbox", "mailbox_html_rendering_observed"):
        if payload.get(key) is not True:
            blockers.append(f"{key} must be true")
    if payload.get("attachment_count") != 4:
        blockers.append("attachment count mismatch")
    rows = {str(row.get("filename")): row for row in payload.get("attachments") or [] if isinstance(row, dict)}
    if set(rows) != set(EXPECTED_ATTACHMENTS):
        blockers.append("attachment filename set mismatch")
    for filename, (mime_type, size, digest) in EXPECTED_ATTACHMENTS.items():
        row = rows.get(filename) or {}
        if row.get("mime_type") != mime_type or row.get("size_bytes") != size or row.get("sha256") != digest:
            blockers.append(f"attachment evidence mismatch: {filename}")
    image = payload.get("inline_image") if isinstance(payload.get("inline_image"), dict) else {}
    if payload.get("inline_image_count") != 1:
        blockers.append("inline image count mismatch")
    if image.get("filename") != "weekly_etf_eu_portfolio_curve.png":
        blockers.append("inline image filename mismatch")
    if image.get("mime_type") != "image/png" or image.get("size_bytes") != 57780:
        blockers.append("inline image type or size mismatch")
    if image.get("sha256") != "aa4ae5bef0db3bc133f28ab16d6f5b98caa944263b986245476554966c861963":
        blockers.append("inline image digest mismatch")
    if image.get("content_id") != "weekly-etf-eu-chart-wp_sync_08_cid_20260729_002500@weekly-etf-eu.local":
        blockers.append("inline image Content-ID mismatch")
    if payload.get("cid_reference_count_expected") != 1:
        blockers.append("CID reference count mismatch")
    if payload.get("recipient_plaintext_stored") is not False or payload.get("raw_mime_stored") is not False:
        blockers.append("privacy boundary violated")
    for key in ("portfolio_mutation", "ledger_write", "funding_authority", "execution_authority", "activation_authority", "production_delivery_authority"):
        if payload.get(key) is not False:
            blockers.append(f"authority {key} must be false")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    payload = load(args.receipt)
    blockers = validate(payload)
    print(json.dumps({"valid": not blockers, "blockers": blockers, "shadow_run_id": payload.get("shadow_run_id")}, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
