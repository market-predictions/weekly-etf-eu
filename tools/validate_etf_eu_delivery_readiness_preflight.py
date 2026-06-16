from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_delivery_readiness_preflight_v1"
ALLOWED_STATUS = {"blocked_not_ready_for_wp13", "ready_for_wp13_preflight_only"}
ALLOWED_PREREQUISITE_STATUS = {"missing", "present"}

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "run_id",
    "created_at_utc",
    "report_date",
    "status",
    "ready_for_wp13",
    "recipient_allowlist_status",
    "recipient_allowlist_path_or_null",
    "smtp_secrets_policy_status",
    "smtp_secrets_policy_path_or_null",
    "delivery_receipt_validator_status",
    "delivery_receipt_validator_path_or_null",
    "send_attempted",
    "email_delivery",
    "delivery_receipt",
    "production_delivery",
    "pdf_generation",
    "funding_authority",
    "portfolio_mutation",
    "candidate_promotion",
    "valuation_grade_promotion",
    "authority",
    "blockers",
}

REQUIRED_NON_EMPTY_STRINGS = {
    "run_id",
    "created_at_utc",
    "report_date",
}

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

PREREQUISITE_STATUS_TO_PATH = {
    "recipient_allowlist_status": "recipient_allowlist_path_or_null",
    "smtp_secrets_policy_status": "smtp_secrets_policy_path_or_null",
    "delivery_receipt_validator_status": "delivery_receipt_validator_path_or_null",
}

MISSING_STATUS_TO_BLOCKER = {
    "recipient_allowlist_status": "recipient allowlist not present",
    "smtp_secrets_policy_status": "SMTP/secrets policy not present",
    "delivery_receipt_validator_status": "delivery receipt validator not present",
}

REQUIRED_BLOCKED_BLOCKERS = {
    "recipient allowlist not present",
    "SMTP/secrets policy not present",
    "delivery receipt validator not present",
    "real delivery not authorized",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _missing(required: set[str], payload: dict[str, Any]) -> list[str]:
    return sorted(required - set(payload))


def _require_false(payload: dict[str, Any], key: str, *, prefix: str = "delivery readiness preflight") -> None:
    if payload.get(key) is not False:
        raise RuntimeError(f"{prefix} failed: {key} must remain false")


def _require_optional_path_consistency(payload: dict[str, Any], status_key: str, path_key: str) -> None:
    status = payload[status_key]
    path_value = payload[path_key]

    if status not in ALLOWED_PREREQUISITE_STATUS:
        raise RuntimeError(f"delivery readiness preflight failed: unsupported {status_key}={status}")

    if status == "missing" and path_value is not None:
        raise RuntimeError(f"delivery readiness preflight failed: {status_key}=missing requires {path_key}=null")

    if status == "present":
        if not isinstance(path_value, str) or not path_value.strip():
            raise RuntimeError(f"delivery readiness preflight failed: {status_key}=present requires non-empty {path_key}")


def validate_delivery_readiness_preflight(path: Path) -> None:
    payload = _load(path)

    missing_top = _missing(REQUIRED_TOP_LEVEL, payload)
    if missing_top:
        raise RuntimeError(
            "delivery readiness preflight failed: missing top-level key(s): "
            + ", ".join(missing_top)
        )

    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(
            f"delivery readiness preflight failed: unsupported schema_version={payload['schema_version']}"
        )

    if payload["status"] not in ALLOWED_STATUS:
        raise RuntimeError(f"delivery readiness preflight failed: unsupported status={payload['status']}")

    if not isinstance(payload["ready_for_wp13"], bool):
        raise RuntimeError("delivery readiness preflight failed: ready_for_wp13 must be boolean")

    for key in REQUIRED_NON_EMPTY_STRINGS:
        value = payload[key]
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(f"delivery readiness preflight failed: {key} must be a non-empty string")

    for status_key, path_key in PREREQUISITE_STATUS_TO_PATH.items():
        _require_optional_path_consistency(payload, status_key, path_key)

    prerequisite_statuses = [payload[status_key] for status_key in PREREQUISITE_STATUS_TO_PATH]
    all_prerequisites_present = all(status == "present" for status in prerequisite_statuses)
    any_prerequisite_missing = any(status == "missing" for status in prerequisite_statuses)

    if payload["ready_for_wp13"] is True and any_prerequisite_missing:
        raise RuntimeError(
            "delivery readiness preflight failed: ready_for_wp13=true requires all prerequisites present"
        )

    if payload["ready_for_wp13"] is True and payload["status"] != "ready_for_wp13_preflight_only":
        raise RuntimeError(
            "delivery readiness preflight failed: ready_for_wp13=true requires status=ready_for_wp13_preflight_only"
        )

    if payload["status"] == "ready_for_wp13_preflight_only":
        if payload["ready_for_wp13"] is not True:
            raise RuntimeError(
                "delivery readiness preflight failed: ready_for_wp13_preflight_only requires ready_for_wp13=true"
            )
        if not all_prerequisites_present:
            raise RuntimeError(
                "delivery readiness preflight failed: ready_for_wp13_preflight_only requires all prerequisites present"
            )

    if payload["status"] == "blocked_not_ready_for_wp13" and payload["ready_for_wp13"] is not False:
        raise RuntimeError(
            "delivery readiness preflight failed: blocked_not_ready_for_wp13 requires ready_for_wp13=false"
        )

    for key in AUTHORITY_FALSE_FIELDS:
        _require_false(payload, key)

    authority = payload["authority"]
    if not isinstance(authority, dict):
        raise RuntimeError("delivery readiness preflight failed: authority must be an object")

    missing_authority = _missing(AUTHORITY_FALSE_FIELDS, authority)
    if missing_authority:
        raise RuntimeError(
            "delivery readiness preflight failed: authority missing required key(s): "
            + ", ".join(missing_authority)
        )

    for key in AUTHORITY_FALSE_FIELDS:
        if authority[key] is not False:
            raise RuntimeError(f"delivery readiness preflight failed: authority.{key} must remain false")

    blockers = payload["blockers"]
    if not isinstance(blockers, list) or not blockers:
        raise RuntimeError("delivery readiness preflight failed: blockers must be a non-empty list")

    if "real delivery not authorized" not in blockers:
        raise RuntimeError("delivery readiness preflight failed: blockers must include real delivery not authorized")

    if payload["status"] == "blocked_not_ready_for_wp13":
        if all(status == "missing" for status in prerequisite_statuses):
            missing_blockers = sorted(REQUIRED_BLOCKED_BLOCKERS - set(blockers))
            if missing_blockers:
                raise RuntimeError(
                    "delivery readiness preflight failed: blocked artifact missing blocker(s): "
                    + ", ".join(missing_blockers)
                )

        for status_key, blocker in MISSING_STATUS_TO_BLOCKER.items():
            if payload[status_key] == "missing" and blocker not in blockers:
                raise RuntimeError(
                    f"delivery readiness preflight failed: missing prerequisite blocker not present: {blocker}"
                )

    print(
        "ETF_EU_DELIVERY_READINESS_PREFLIGHT_OK | "
        f"artifact={path} | status={payload['status']} | ready_for_wp13={payload['ready_for_wp13']} | "
        "send_attempted=false | email_delivery=false | production_delivery=false"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_delivery_readiness_preflight(Path(args.artifact))


if __name__ == "__main__":
    main()
