from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_recipient_policy_contract_review_v1"
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "review_id",
    "created_at_utc",
    "status",
    "review_scope",
    "basis",
    "current_recipient_policy_state",
    "required_future_production_controls",
    "future_policy_required_fields",
    "implementation_allowed_in_this_package",
    "activation_allowed_in_this_package",
    "authority_created",
    "selected_next_package",
    "selected_next_package_title",
    "explicitly_out_of_scope",
    "authority",
}
CURRENT_STATE_REQUIRED = {
    "source_path",
    "status",
    "recipient_activation",
    "real_recipients",
    "production_policy_exists",
}
AUTHORITY_REQUIRED = {
    "valuation_grade",
    "funding_authority",
    "portfolio_mutation",
    "production_delivery",
    "candidate_promotion",
    "recipient_activation",
    "real_recipients",
    "ready_for_wp13_preflight_only",
    "wp13_authority",
}
AUTHORITY_MUST_BE_FALSE = AUTHORITY_REQUIRED - {"ready_for_wp13_preflight_only"}
FORBIDDEN_POSITIVE_PHRASES = {
    "operational delivery enabled",
    "delivery enabled",
    "delivery authorized",
    "recipient activation enabled",
    "recipient activation completed",
    "real recipients added",
    "real recipient added",
    "production recipient policy created",
    "recipient policy implemented",
    "production delivery enabled",
    "production delivery authorized",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("recipient policy contract review failed: JSON root must be an object")
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


def _require_non_empty_string(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"recipient policy contract review failed: {key} must be a non-empty string")


def _require_non_empty_list(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise RuntimeError(f"recipient policy contract review failed: {key} must be a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise RuntimeError(f"recipient policy contract review failed: {key} must contain non-empty strings")


def _require_false(payload: dict[str, Any], key: str) -> None:
    if payload.get(key) is not False:
        raise RuntimeError(f"recipient policy contract review failed: {key} must remain false")


def _validate_current_state(state: Any) -> None:
    if not isinstance(state, dict):
        raise RuntimeError("recipient policy contract review failed: current_recipient_policy_state must be an object")
    missing_state = _missing(CURRENT_STATE_REQUIRED, state)
    if missing_state:
        raise RuntimeError(
            "recipient policy contract review failed: current_recipient_policy_state missing key(s): "
            + ", ".join(missing_state)
        )
    if state["status"] != "sample_only_inactive":
        raise RuntimeError(
            "recipient policy contract review failed: current_recipient_policy_state.status must be sample_only_inactive"
        )
    for key in ("recipient_activation", "real_recipients", "production_policy_exists"):
        if state[key] is not False:
            raise RuntimeError(
                f"recipient policy contract review failed: current_recipient_policy_state.{key} must remain false"
            )


def _validate_authority(authority: Any) -> None:
    if not isinstance(authority, dict):
        raise RuntimeError("recipient policy contract review failed: authority must be an object")
    missing_authority = _missing(AUTHORITY_REQUIRED, authority)
    if missing_authority:
        raise RuntimeError(
            "recipient policy contract review failed: authority missing required key(s): "
            + ", ".join(missing_authority)
        )
    if authority["ready_for_wp13_preflight_only"] is not True:
        raise RuntimeError(
            "recipient policy contract review failed: authority.ready_for_wp13_preflight_only must be true"
        )
    for key in AUTHORITY_MUST_BE_FALSE:
        if authority[key] is not False:
            raise RuntimeError(f"recipient policy contract review failed: authority.{key} must remain false")


def validate_recipient_policy_contract_review(path: Path) -> dict[str, Any]:
    payload = _load(path)

    missing_top = _missing(REQUIRED_TOP_LEVEL, payload)
    if missing_top:
        raise RuntimeError(
            "recipient policy contract review failed: missing top-level key(s): "
            + ", ".join(missing_top)
        )

    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(
            f"recipient policy contract review failed: unsupported schema_version={payload['schema_version']}"
        )
    if payload["status"] != "recipient_policy_contract_review_completed":
        raise RuntimeError(
            "recipient policy contract review failed: status must be recipient_policy_contract_review_completed"
        )
    if payload["review_scope"] != "recipient_policy_review_only":
        raise RuntimeError(
            "recipient policy contract review failed: review_scope must be recipient_policy_review_only"
        )

    for key in {"review_id", "created_at_utc", "selected_next_package", "selected_next_package_title"}:
        _require_non_empty_string(payload, key)

    _require_non_empty_list(payload, "basis")
    _validate_current_state(payload["current_recipient_policy_state"])
    _require_non_empty_list(payload, "required_future_production_controls")
    _require_non_empty_list(payload, "future_policy_required_fields")
    _require_non_empty_list(payload, "explicitly_out_of_scope")

    for key in (
        "implementation_allowed_in_this_package",
        "activation_allowed_in_this_package",
        "authority_created",
    ):
        _require_false(payload, key)

    if payload["selected_next_package"] != "WP13E":
        raise RuntimeError("recipient policy contract review failed: selected_next_package must be WP13E")

    _validate_authority(payload["authority"])

    flattened = _flatten_text(payload).lower()
    for phrase in FORBIDDEN_POSITIVE_PHRASES:
        if phrase in flattened:
            raise RuntimeError(
                f"recipient policy contract review failed: artifact contains operational-recipient-like wording: {phrase}"
            )

    result = {
        "schema_version": "etf_eu_recipient_policy_contract_review_validation_v1",
        "status": "valid_review_only_recipient_policy_review",
        "review_path": str(path),
        "selected_next_package": payload["selected_next_package"],
        "recipient_policy_state": payload["current_recipient_policy_state"]["status"],
        "recipient_activation": False,
        "real_recipients": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "candidate_promotion": False,
        "wp13_authority": False,
    }

    print(
        "ETF_EU_RECIPIENT_POLICY_CONTRACT_REVIEW_OK | "
        f"artifact={path} | selected_next_package={payload['selected_next_package']} | "
        "recipient_activation=false | real_recipients=false | wp13_authority=false"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_recipient_policy_contract_review(Path(args.artifact))


if __name__ == "__main__":
    main()
