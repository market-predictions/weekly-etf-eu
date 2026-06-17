from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_wp13h_explicit_authority_review_v1"
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "review_id",
    "created_at_utc",
    "status",
    "review_scope",
    "decision",
    "decision_reason",
    "input_state",
    "decision_result",
    "implementation_allowed_in_this_package",
    "activation_allowed_in_this_package",
    "authority_created",
    "selected_next_package",
    "selected_next_package_title",
    "authority",
}
INPUT_REQUIRED = {
    "review_chain_complete",
    "operational_prerequisites_complete",
    "authority_can_be_granted",
    "recipient_policy_reviewed",
    "secure_transport_setup_reviewed",
    "receipt_proof_path_reviewed",
    "recipient_activation",
    "real_recipients",
    "mail_transport_enabled",
    "external_mail_api_enabled",
    "real_receipt",
    "proof_claimed",
    "send_attempted",
}
INPUT_MUST_BE_FALSE = {
    "operational_prerequisites_complete",
    "authority_can_be_granted",
    "recipient_activation",
    "real_recipients",
    "mail_transport_enabled",
    "external_mail_api_enabled",
    "real_receipt",
    "proof_claimed",
    "send_attempted",
}
INPUT_MUST_BE_TRUE = {
    "review_chain_complete",
    "recipient_policy_reviewed",
    "secure_transport_setup_reviewed",
    "receipt_proof_path_reviewed",
}
DECISION_RESULT_REQUIRED = {
    "authority_granted",
    "wp13_authority",
    "production_delivery",
    "operational_package_allowed",
    "activation_allowed",
    "future_review_allowed_after_new_authority",
}
DECISION_RESULT_MUST_BE_FALSE = {
    "authority_granted",
    "wp13_authority",
    "production_delivery",
    "operational_package_allowed",
    "activation_allowed",
}
AUTHORITY_REQUIRED = {
    "valuation_grade",
    "funding_authority",
    "portfolio_mutation",
    "production_delivery",
    "candidate_promotion",
    "recipient_activation",
    "real_recipients",
    "smtp_configured",
    "secrets_present",
    "mail_transport_enabled",
    "external_mail_api_enabled",
    "real_receipt",
    "proof_claimed",
    "send_attempted",
    "authority_granted",
    "ready_for_wp13_preflight_only",
    "wp13_authority",
}
AUTHORITY_MUST_BE_FALSE = AUTHORITY_REQUIRED - {"ready_for_wp13_preflight_only"}
FORBIDDEN_POSITIVE_PHRASES = {
    "authority granted",
    "production delivery enabled",
    "recipient activation occurred",
    "transport activation occurred",
    "proof exists",
    "delivery succeeded",
    "operational package allowed",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("wp13h explicit authority review failed: JSON root must be an object")
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
        raise RuntimeError(f"wp13h explicit authority review failed: {key} must be a non-empty string")


def _require_non_empty_list(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise RuntimeError(f"wp13h explicit authority review failed: {key} must be a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise RuntimeError(f"wp13h explicit authority review failed: {key} must contain non-empty strings")


def _require_false(payload: dict[str, Any], key: str) -> None:
    if payload.get(key) is not False:
        raise RuntimeError(f"wp13h explicit authority review failed: {key} must remain false")


def _validate_input_state(state: Any) -> None:
    if not isinstance(state, dict):
        raise RuntimeError("wp13h explicit authority review failed: input_state must be an object")
    missing_state = _missing(INPUT_REQUIRED, state)
    if missing_state:
        raise RuntimeError("wp13h explicit authority review failed: input_state missing key(s): " + ", ".join(missing_state))
    for key in INPUT_MUST_BE_TRUE:
        if state[key] is not True:
            raise RuntimeError(f"wp13h explicit authority review failed: input_state.{key} must be true")
    for key in INPUT_MUST_BE_FALSE:
        if state[key] is not False:
            raise RuntimeError(f"wp13h explicit authority review failed: input_state.{key} must remain false")


def _validate_decision_result(result: Any) -> None:
    if not isinstance(result, dict):
        raise RuntimeError("wp13h explicit authority review failed: decision_result must be an object")
    missing_result = _missing(DECISION_RESULT_REQUIRED, result)
    if missing_result:
        raise RuntimeError("wp13h explicit authority review failed: decision_result missing key(s): " + ", ".join(missing_result))
    for key in DECISION_RESULT_MUST_BE_FALSE:
        if result[key] is not False:
            raise RuntimeError(f"wp13h explicit authority review failed: decision_result.{key} must remain false")
    if result["future_review_allowed_after_new_authority"] is not True:
        raise RuntimeError("wp13h explicit authority review failed: future_review_allowed_after_new_authority must be true")


def _validate_authority(authority: Any) -> None:
    if not isinstance(authority, dict):
        raise RuntimeError("wp13h explicit authority review failed: authority must be an object")
    missing_authority = _missing(AUTHORITY_REQUIRED, authority)
    if missing_authority:
        raise RuntimeError("wp13h explicit authority review failed: authority missing required key(s): " + ", ".join(missing_authority))
    if authority["ready_for_wp13_preflight_only"] is not True:
        raise RuntimeError("wp13h explicit authority review failed: authority.ready_for_wp13_preflight_only must be true")
    for key in AUTHORITY_MUST_BE_FALSE:
        if authority[key] is not False:
            raise RuntimeError(f"wp13h explicit authority review failed: authority.{key} must remain false")


def validate_wp13h_explicit_authority_review(path: Path) -> dict[str, Any]:
    payload = _load(path)

    missing_top = _missing(REQUIRED_TOP_LEVEL, payload)
    if missing_top:
        raise RuntimeError("wp13h explicit authority review failed: missing top-level key(s): " + ", ".join(missing_top))

    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(f"wp13h explicit authority review failed: unsupported schema_version={payload['schema_version']}")
    if payload["status"] != "explicit_authority_review_completed":
        raise RuntimeError("wp13h explicit authority review failed: status must be explicit_authority_review_completed")
    if payload["review_scope"] != "authority_decision_review_only":
        raise RuntimeError("wp13h explicit authority review failed: review_scope must be authority_decision_review_only")
    if payload["decision"] != "not_granted":
        raise RuntimeError("wp13h explicit authority review failed: decision must be not_granted")

    for key in {"review_id", "created_at_utc", "selected_next_package", "selected_next_package_title"}:
        _require_non_empty_string(payload, key)

    _require_non_empty_list(payload, "decision_reason")
    _validate_input_state(payload["input_state"])
    _validate_decision_result(payload["decision_result"])

    for key in (
        "implementation_allowed_in_this_package",
        "activation_allowed_in_this_package",
        "authority_created",
    ):
        _require_false(payload, key)

    if payload["selected_next_package"] != "WP13I":
        raise RuntimeError("wp13h explicit authority review failed: selected_next_package must be WP13I")

    _validate_authority(payload["authority"])

    flattened = _flatten_text(payload).lower()
    for phrase in FORBIDDEN_POSITIVE_PHRASES:
        if phrase in flattened:
            raise RuntimeError(
                f"wp13h explicit authority review failed: artifact contains operational-authority-like wording: {phrase}"
            )

    result = {
        "schema_version": "etf_eu_wp13h_explicit_authority_review_validation_v1",
        "status": "valid_review_only_explicit_authority_review",
        "review_path": str(path),
        "selected_next_package": payload["selected_next_package"],
        "decision": payload["decision"],
        "authority_granted": False,
        "production_delivery": False,
        "wp13_authority": False,
    }

    print(
        "ETF_EU_WP13H_EXPLICIT_AUTHORITY_REVIEW_OK | "
        f"artifact={path} | selected_next_package={payload['selected_next_package']} | "
        "decision=not_granted | authority_granted=false | production_delivery=false | wp13_authority=false"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_wp13h_explicit_authority_review(Path(args.artifact))


if __name__ == "__main__":
    main()
