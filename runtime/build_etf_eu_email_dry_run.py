from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT_DIR = Path("output/delivery")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _clean_list(values: list[str] | None) -> list[str]:
    return [value.strip() for value in values or [] if value and value.strip()]


def build_email_dry_run(
    *,
    run_id: str,
    report_date: str,
    recipient_allowlist_status: str = "not_configured",
    subject_preview: str | None = None,
    body_preview: str | None = None,
    attachment_paths: list[str] | None = None,
    delivery_manifest_path: str | None = None,
    pdf_paths: list[str] | None = None,
    created_at_utc: str | None = None,
) -> dict[str, Any]:
    clean_delivery_manifest_path = _clean_optional(delivery_manifest_path)
    clean_pdf_paths = _clean_list(pdf_paths)
    clean_attachment_paths = _clean_list(attachment_paths)

    delivery_manifest_status = "available" if clean_delivery_manifest_path else "not_available"
    pdf_status = "shadow_paths_available" if clean_pdf_paths else "not_available"

    blockers = [
        "email delivery dry-run only",
        "send_attempted=false",
        "recipient activation not enabled",
        "mail sending out of scope",
        "delivery receipt not created",
        "production delivery disabled",
    ]
    if delivery_manifest_status == "not_available":
        blockers.append("delivery_manifest_status=not_available")
    if pdf_status == "not_available":
        blockers.append("pdf_status=not_available")

    return {
        "schema_version": "etf_eu_email_dry_run_v1",
        "run_id": run_id,
        "created_at_utc": created_at_utc or _utc_now(),
        "report_date": report_date,
        "status": "design_only_blocked",
        "recipient_allowlist_status": recipient_allowlist_status,
        "subject_preview": subject_preview or f"DRY RUN ONLY - Weekly ETF EU Review - {report_date}",
        "body_preview": body_preview
        or (
            "Dry-run metadata only. No email send was attempted. "
            "Production delivery, email delivery and delivery receipt remain false."
        ),
        "attachment_paths": clean_attachment_paths,
        "delivery_manifest_path": clean_delivery_manifest_path,
        "delivery_manifest_status": delivery_manifest_status,
        "pdf_paths_or_null": clean_pdf_paths if clean_pdf_paths else None,
        "pdf_status": pdf_status,
        "send_attempted": False,
        "email_delivery": False,
        "delivery_receipt": False,
        "production_delivery": False,
        "authority": {
            "mail_transport_configured": False,
            "external_mail_api_enabled": False,
            "send_function_present": False,
            "recipient_activation": False,
            "pdf_generation": False,
            "email_delivery": False,
            "delivery_receipt": False,
            "production_delivery": False,
        },
        "blockers": blockers,
    }


def write_email_dry_run(
    output_dir: Path,
    *,
    run_id: str,
    report_date: str,
    recipient_allowlist_status: str = "not_configured",
    subject_preview: str | None = None,
    body_preview: str | None = None,
    attachment_paths: list[str] | None = None,
    delivery_manifest_path: str | None = None,
    pdf_paths: list[str] | None = None,
    created_at_utc: str | None = None,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    dry_run = build_email_dry_run(
        run_id=run_id,
        report_date=report_date,
        recipient_allowlist_status=recipient_allowlist_status,
        subject_preview=subject_preview,
        body_preview=body_preview,
        attachment_paths=attachment_paths,
        delivery_manifest_path=delivery_manifest_path,
        pdf_paths=pdf_paths,
        created_at_utc=created_at_utc,
    )
    path = output_dir / f"email_dry_run_{run_id}.json"
    path.write_text(json.dumps(dry_run, indent=2, sort_keys=True), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--recipient-allowlist-status", default="not_configured")
    parser.add_argument("--subject-preview")
    parser.add_argument("--body-preview")
    parser.add_argument("--attachment-path", action="append", default=[])
    parser.add_argument("--delivery-manifest-path")
    parser.add_argument("--pdf-path", action="append", default=[])
    args = parser.parse_args()

    path = write_email_dry_run(
        Path(args.output_dir),
        run_id=args.run_id,
        report_date=args.report_date,
        recipient_allowlist_status=args.recipient_allowlist_status,
        subject_preview=args.subject_preview,
        body_preview=args.body_preview,
        attachment_paths=list(args.attachment_path),
        delivery_manifest_path=args.delivery_manifest_path,
        pdf_paths=list(args.pdf_path),
    )
    print(
        "ETF_EU_EMAIL_DRY_RUN_DESIGN_ONLY_OK | "
        f"artifact={path} | send_attempted=false | email_delivery=false | production_delivery=false"
    )


if __name__ == "__main__":
    main()
