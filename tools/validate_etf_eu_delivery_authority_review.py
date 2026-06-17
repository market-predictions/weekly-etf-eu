from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_delivery_authority_review_v1"
ALLOWED_STATUS = {
    "delivery_authority_not_granted",
    "delivery_authority_preparation_allowed",
}
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "review_id",
    "created_at_utc",
    "status",
    "decision",
    "preflight_reference",
    "preflight_status",
    "preflight_ready_for_wp13",
    "authority_scope",
    "rationale",
    "required_before_real_delivery",
    "send_attempted",
    "email_delivery",
    "delivery_receipt",
    "production_delivery",
    "pdf_generation",
    "recipient_activation",
    "real_recipients",
    "mail_setup_active",
    "mail_transport_enabled",
    "external_mail_api_enabled",
    "funding_authority",
    "portfolio_mutation",
    "candidate_promotion",
    "valuation_grade_promotion",
}
AUTHORITY_FALSE_FIELDS = {
    "send_attempted",
    "email_delivery",
    "delivery_receipt",
    "production_delivery",
    "pdf_generation",
    "recipient_activation",
    "real_recipients",
    "mail_setup_active",
    "mail_transport_enabled",
    "external_mail_api_enabled",
    "funding_authority",
    "portfolio_mutation",
    "candidate_promotion",
    "valuation_grade_promotion",
}
FORBIDDEN_CLAIM_PHRASES = {
    "delivery succeeded",
    "delivery successful",
    "delivery completed",
    "report delivered",
    "email sent",
    "sent successfully",
    "production delivery enabled",
    "production delivery authorized",
    "real receipt created",
    "receipt proof created",
    "provider confirmation received",
    "transport message id",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("delivery authority review failed: JSON root must be an object")
    return payload


def _missing(required: set[str], payload: dict[str, Any]) -> list[str]:
    return sorted(required - set(payload))


def _flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(_flatten_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(_flatten_text(v) for v in value)
    if isinstance(value, str):
        return value
    return ""


def _require_false(payload: dict[str, Any], key: str) -> None:
    if payload.get(key) is not False:
        raise RuntimeError(f"delivery authority review failed: {key} must remain false")


def _require_non_empty_string(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"delivery authority review failed: {key} must be a non-empty string")


def _require_non_empty_list(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise RuntimeError(f"delivery authority review failed: {key} must be a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise RuntimeError(f"delivery authority review failed: {key} must contain non-empty strings")


def validate_delivery_authority_review(path: Path) -> dict[str, Any]:
    payload = _load(path)

    missing_top = _missing(REQUIRED_TOP_LEVEL, payload)
    if missing_top:
        raise RuntimeError(
            "delivery authority review failed: missing top-level key(s): "
            + ", ".join(missing_top)
        )

    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(
            f"delivery authority review failed: unsupported schema_version={payload['schema_version']}"
        )

    if payload["status"] not in ALLOWED_STATUS:
        raise RuntimeError(f"delivery authority review failed: unsupported status={payload['status']}")

    for key in {"review_id", "created_at_utc", "decision", "preflight_reference"}:
        _require_non_empty_string(payload, key)

    if payload["preflight_status"] != "ready_for_wp13_preflight_only":
        raise RuntimeError(
            "delivery authority review failed: preflight_status must be ready_for_wp13_preflight_only"
        )

    if payload["preflight_ready_for_wp13"] is not True:
        raise RuntimeError("delivery authority review failed: preflight_ready_for_wp13 must be true")

    if payload["authority_scope"] != "decision_review_only":
        raise RuntimeError("delivery authority review failed: authority_scope must be decision_review_only")

    _require_non_empty_list(payload, "rationale")
    _require_non_empty_list(payload, "required_before_real_delivery")

    for key in AUTHORITY_FALSE_FIELDS:
        _require_false(payload, key)

    if payload["status"] == "delivery_authority_not_granted":
        if payload["decision"] != "do_not_prepare_delivery_authority_yet":
            raise RuntimeError(
                "delivery authority review failed: not-granted status requires decision=do_not_prepare_delivery_authority_yet"
            )

    flattened = _flatten_text(payload).lower()
    for phrase in FORBIDDEN_CLAIM_PHRASES:
        if phrase in flattened:
            raise RuntimeError(
                f"delivery authority review failed: artifact contains forbidden delivery-success-like wording: {phrase}"
            )

    result = {
        "schema_version": "etf_eu_delivery_authority_review_validation_v1",
        "status": "valid_decision_review_only",
        "review_path": str(path),
        "decision_status": payload["status"],
        "send_attempted": False,
        "email_delivery": False,
        "delivery_receipt": False,
        "production_delivery": False,
        "pdf_generation": False,
        "recipient_activation": False,
        "real_recipients": False,
        "mail_setup_active": False,
        "mail_transport_enabled": False,
        "external_mail_api_enabled": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "candidate_promotion": False,
        "valuation_grade_promotion": False,
    }

    print(
        "ETF_EU_DELIVERY_AUTHORITY_REVIEW_OK | "
        f"artifact={path} | status={payload['status']} | "
        "send_attempted=false | production_delivery=false | delivery_authority=false"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_delivery_authority_review(Path(args.artifact))


if __name__ == "__main__":
    main()
