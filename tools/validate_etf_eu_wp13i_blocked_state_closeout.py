from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_wp13i_blocked_state_closeout_v1"
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "review_id",
    "created_at_utc",
    "status",
    "review_scope",
    "decision",
    "blocked_state_result",
    "closed_review_chain",
    "roadmap_decision",
    "implementation_allowed_in_this_package",
    "activation_allowed_in_this_package",
    "authority_created",
    "selected_next_package",
    "selected_next_package_title",
    "explicitly_out_of_scope",
    "authority",
}
REQUIRED_CHAIN = {
    "WP13A",
    "WP13B",
    "WP13C",
    "WP13D",
    "WP13E",
    "WP13F",
    "WP13G",
    "WP13H",
}
BLOCKED_RESULT_REQUIRED = {
    "wp13_review_chain_complete",
    "delivery_authority_not_granted",
    "operational_prerequisites_complete",
    "production_delivery",
    "wp13_authority",
    "roadmap_loop_closed",
}
ROADMAP_REQUIRED = {
    "next_phase",
    "recommended_next_lane",
    "operational_delivery_allowed",
    "authority_review_reopen_allowed_only_after_new_inputs",
    "reason",
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
    "delivery_authority",
    "ready_for_wp13_preflight_only",
    "wp13_authority",
}
AUTHORITY_MUST_BE_FALSE = AUTHORITY_REQUIRED - {"ready_for_wp13_preflight_only"}
FORBIDDEN_POSITIVE_PHRASES = {
    "authority was granted",
    "authority granted",
    "production delivery can start",
    "production delivery enabled",
    "recipient activation occurred",
    "transport activation occurred",
    "delivery proof exists",
    "delivery succeeded",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("wp13i blocked-state closeout failed: JSON root must be an object")
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
        raise RuntimeError(f"wp13i blocked-state closeout failed: {key} must be a non-empty string")


def _require_non_empty_list(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise RuntimeError(f"wp13i blocked-state closeout failed: {key} must be a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise RuntimeError(f"wp13i blocked-state closeout failed: {key} must contain non-empty strings")


def _require_false(payload: dict[str, Any], key: str) -> None:
    if payload.get(key) is not False:
        raise RuntimeError(f"wp13i blocked-state closeout failed: {key} must remain false")


def _validate_blocked_state(result: Any) -> None:
    if not isinstance(result, dict):
        raise RuntimeError("wp13i blocked-state closeout failed: blocked_state_result must be an object")
    missing_result = _missing(BLOCKED_RESULT_REQUIRED, result)
    if missing_result:
        raise RuntimeError(
            "wp13i blocked-state closeout failed: blocked_state_result missing key(s): "
            + ", ".join(missing_result)
        )
    if result["wp13_review_chain_complete"] is not True:
        raise RuntimeError("wp13i blocked-state closeout failed: wp13_review_chain_complete must be true")
    if result["delivery_authority_not_granted"] is not True:
        raise RuntimeError("wp13i blocked-state closeout failed: delivery_authority_not_granted must be true")
    for key in ("operational_prerequisites_complete", "production_delivery", "wp13_authority"):
        if result[key] is not False:
            raise RuntimeError(f"wp13i blocked-state closeout failed: {key} must remain false")
    if result["roadmap_loop_closed"] is not True:
        raise RuntimeError("wp13i blocked-state closeout failed: roadmap_loop_closed must be true")


def _validate_chain(chain: Any) -> None:
    if not isinstance(chain, list):
        raise RuntimeError("wp13i blocked-state closeout failed: closed_review_chain must be a list")
    chain_set = set(chain)
    missing_chain = sorted(REQUIRED_CHAIN - chain_set)
    if missing_chain:
        raise RuntimeError(
            "wp13i blocked-state closeout failed: closed_review_chain missing required package(s): "
            + ", ".join(missing_chain)
        )


def _validate_roadmap_decision(roadmap: Any) -> None:
    if not isinstance(roadmap, dict):
        raise RuntimeError("wp13i blocked-state closeout failed: roadmap_decision must be an object")
    missing_roadmap = _missing(ROADMAP_REQUIRED, roadmap)
    if missing_roadmap:
        raise RuntimeError(
            "wp13i blocked-state closeout failed: roadmap_decision missing key(s): "
            + ", ".join(missing_roadmap)
        )
    _require_non_empty_string(roadmap, "next_phase")
    _require_non_empty_string(roadmap, "recommended_next_lane")
    _require_non_empty_string(roadmap, "reason")
    if roadmap["operational_delivery_allowed"] is not False:
        raise RuntimeError("wp13i blocked-state closeout failed: operational_delivery_allowed must remain false")
    if roadmap["authority_review_reopen_allowed_only_after_new_inputs"] is not True:
        raise RuntimeError(
            "wp13i blocked-state closeout failed: authority_review_reopen_allowed_only_after_new_inputs must be true"
        )


def _validate_authority(authority: Any) -> None:
    if not isinstance(authority, dict):
        raise RuntimeError("wp13i blocked-state closeout failed: authority must be an object")
    missing_authority = _missing(AUTHORITY_REQUIRED, authority)
    if missing_authority:
        raise RuntimeError(
            "wp13i blocked-state closeout failed: authority missing required key(s): "
            + ", ".join(missing_authority)
        )
    if authority["ready_for_wp13_preflight_only"] is not True:
        raise RuntimeError("wp13i blocked-state closeout failed: authority.ready_for_wp13_preflight_only must be true")
    for key in AUTHORITY_MUST_BE_FALSE:
        if authority[key] is not False:
            raise RuntimeError(f"wp13i blocked-state closeout failed: authority.{key} must remain false")


def validate_wp13i_blocked_state_closeout(path: Path) -> dict[str, Any]:
    payload = _load(path)

    missing_top = _missing(REQUIRED_TOP_LEVEL, payload)
    if missing_top:
        raise RuntimeError("wp13i blocked-state closeout failed: missing top-level key(s): " + ", ".join(missing_top))

    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(f"wp13i blocked-state closeout failed: unsupported schema_version={payload['schema_version']}")
    if payload["status"] != "blocked_state_closeout_completed":
        raise RuntimeError("wp13i blocked-state closeout failed: status must be blocked_state_closeout_completed")
    if payload["review_scope"] != "blocked_state_closeout_review_only":
        raise RuntimeError("wp13i blocked-state closeout failed: review_scope must be blocked_state_closeout_review_only")
    if payload["decision"] != "blocked_state_closed":
        raise RuntimeError("wp13i blocked-state closeout failed: decision must be blocked_state_closed")

    for key in {"review_id", "created_at_utc", "selected_next_package", "selected_next_package_title"}:
        _require_non_empty_string(payload, key)

    _validate_blocked_state(payload["blocked_state_result"])
    _validate_chain(payload["closed_review_chain"])
    _validate_roadmap_decision(payload["roadmap_decision"])
    _require_non_empty_list(payload, "explicitly_out_of_scope")

    for key in (
        "implementation_allowed_in_this_package",
        "activation_allowed_in_this_package",
        "authority_created",
    ):
        _require_false(payload, key)

    if payload["selected_next_package"] != "WP14A":
        raise RuntimeError("wp13i blocked-state closeout failed: selected_next_package must be WP14A")

    _validate_authority(payload["authority"])

    flattened = _flatten_text(payload).lower()
    for phrase in FORBIDDEN_POSITIVE_PHRASES:
        if phrase in flattened:
            raise RuntimeError(
                f"wp13i blocked-state closeout failed: artifact contains operational-authority-like wording: {phrase}"
            )

    result = {
        "schema_version": "etf_eu_wp13i_blocked_state_closeout_validation_v1",
        "status": "valid_review_only_blocked_state_closeout",
        "review_path": str(path),
        "selected_next_package": payload["selected_next_package"],
        "decision": payload["decision"],
        "roadmap_loop_closed": True,
        "production_delivery": False,
        "wp13_authority": False,
    }

    print(
        "ETF_EU_WP13I_BLOCKED_STATE_CLOSEOUT_OK | "
        f"artifact={path} | selected_next_package={payload['selected_next_package']} | "
        "decision=blocked_state_closed | roadmap_loop_closed=true | "
        "production_delivery=false | wp13_authority=false"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_wp13i_blocked_state_closeout(Path(args.artifact))


if __name__ == "__main__":
    main()
