from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_delivery_readiness_preflight_v1"
DEFAULT_OUTPUT_DIR = Path("output/delivery")

AUTHORITY_FALSE_FIELDS = {
    "send_attempted",
    "email_delivery",
    "delivery_receipt",
    "production_delivery",
    "pdf_generation",
    "funding_authority",
    "portfolio_mutation",
    "candidate_promotion",
    "valuation_grade_promotion",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clean_optional_path(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _status_for_path(value: str | None) -> str:
    return "present" if _clean_optional_path(value) else "missing"


def build_delivery_readiness_preflight(
    *,
    run_id: str,
    report_date: str,
    recipient_allowlist_path: str | None = None,
    smtp_secrets_policy_path: str | None = None,
    delivery_receipt_validator_path: str | None = None,
    created_at_utc: str | None = None,
) -> dict[str, Any]:
    clean_recipient_allowlist_path = _clean_optional_path(recipient_allowlist_path)
    clean_smtp_secrets_policy_path = _clean_optional_path(smtp_secrets_policy_path)
    clean_delivery_receipt_validator_path = _clean_optional_path(delivery_receipt_validator_path)

    recipient_allowlist_status = _status_for_path(clean_recipient_allowlist_path)
    smtp_secrets_policy_status = _status_for_path(clean_smtp_secrets_policy_path)
    delivery_receipt_validator_status = _status_for_path(clean_delivery_receipt_validator_path)

    prerequisite_statuses = {
        "recipient_allowlist_status": recipient_allowlist_status,
        "smtp_secrets_policy_status": smtp_secrets_policy_status,
        "delivery_receipt_validator_status": delivery_receipt_validator_status,
    }
    all_prerequisites_present = all(status == "present" for status in prerequisite_statuses.values())

    status = "ready_for_wp13_preflight_only" if all_prerequisites_present else "blocked_not_ready_for_wp13"
    ready_for_wp13 = all_prerequisites_present

    blockers: list[str] = []
    if recipient_allowlist_status == "missing":
        blockers.append("recipient allowlist not present")
    if smtp_secrets_policy_status == "missing":
        blockers.append("SMTP/secrets policy not present")
    if delivery_receipt_validator_status == "missing":
        blockers.append("delivery receipt validator not present")
    blockers.append("real delivery not authorized")

    authority = {field: False for field in sorted(AUTHORITY_FALSE_FIELDS)}

    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at_utc": created_at_utc or _utc_now(),
        "report_date": report_date,
        "status": status,
        "ready_for_wp13": ready_for_wp13,
        "recipient_allowlist_status": recipient_allowlist_status,
        "recipient_allowlist_path_or_null": clean_recipient_allowlist_path,
        "smtp_secrets_policy_status": smtp_secrets_policy_status,
        "smtp_secrets_policy_path_or_null": clean_smtp_secrets_policy_path,
        "delivery_receipt_validator_status": delivery_receipt_validator_status,
        "delivery_receipt_validator_path_or_null": clean_delivery_receipt_validator_path,
        "send_attempted": False,
        "email_delivery": False,
        "delivery_receipt": False,
        "production_delivery": False,
        "pdf_generation": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "candidate_promotion": False,
        "valuation_grade_promotion": False,
        "authority": authority,
        "blockers": blockers,
    }


def write_delivery_readiness_preflight(
    output_dir: Path,
    *,
    run_id: str,
    report_date: str,
    recipient_allowlist_path: str | None = None,
    smtp_secrets_policy_path: str | None = None,
    delivery_receipt_validator_path: str | None = None,
    created_at_utc: str | None = None,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_delivery_readiness_preflight(
        run_id=run_id,
        report_date=report_date,
        recipient_allowlist_path=recipient_allowlist_path,
        smtp_secrets_policy_path=smtp_secrets_policy_path,
        delivery_receipt_validator_path=delivery_receipt_validator_path,
        created_at_utc=created_at_utc,
    )
    path = output_dir / f"etf_eu_delivery_readiness_preflight_{run_id}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--recipient-allowlist-path")
    parser.add_argument("--smtp-secrets-policy-path")
    parser.add_argument("--delivery-receipt-validator-path")
    args = parser.parse_args()

    path = write_delivery_readiness_preflight(
        Path(args.output_dir),
        run_id=args.run_id,
        report_date=args.report_date,
        recipient_allowlist_path=args.recipient_allowlist_path,
        smtp_secrets_policy_path=args.smtp_secrets_policy_path,
        delivery_receipt_validator_path=args.delivery_receipt_validator_path,
    )
    print(
        "ETF_EU_DELIVERY_READINESS_PREFLIGHT_CREATED | "
        f"artifact={path} | ready_for_wp13=false-or-preflight-only | "
        "send_attempted=false | email_delivery=false | production_delivery=false"
    )


if __name__ == "__main__":
    main()
