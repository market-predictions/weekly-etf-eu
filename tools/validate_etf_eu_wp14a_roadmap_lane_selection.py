from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_wp14a_roadmap_lane_selection_v1"
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "review_id",
    "created_at_utc",
    "status",
    "review_scope",
    "basis",
    "input_state",
    "candidate_lanes",
    "selected_lane",
    "selected_lane_result",
    "implementation_allowed_in_this_package",
    "activation_allowed_in_this_package",
    "authority_created",
    "selected_next_package",
    "selected_next_package_title",
    "explicitly_out_of_scope",
    "authority",
}
INPUT_REQUIRED = {
    "wp13_review_chain_complete",
    "authority_not_granted",
    "operational_prerequisites_complete",
    "production_delivery",
    "wp13_authority",
    "roadmap_loop_closed",
}
REQUIRED_LANES = {
    "delivery_inputs_lane",
    "product_quality_lane",
    "ucits_instrument_identity_lane",
    "report_surface_quality_lane",
}
SAFE_LANES = REQUIRED_LANES - {"delivery_inputs_lane"}
SELECTED_RESULT_REQUIRED = {
    "delivery_inputs_lane_selected",
    "product_quality_lane_selected",
    "ucits_instrument_identity_lane_selected",
    "report_surface_quality_lane_selected",
    "lane_selection_deferred_to_wp14b",
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
    "authority_granted",
    "ready_for_wp13_preflight_only",
    "wp14_authority",
}
AUTHORITY_MUST_BE_FALSE = AUTHORITY_REQUIRED - {"ready_for_wp13_preflight_only"}
CONCRETE_SELECTION_FLAGS = {
    "delivery_inputs_lane_selected",
    "product_quality_lane_selected",
    "ucits_instrument_identity_lane_selected",
    "report_surface_quality_lane_selected",
}
FORBIDDEN_POSITIVE_PHRASES = {
    "authority granted",
    "delivery can start",
    "lane was implemented",
    "production delivery is active",
    "delivery succeeded",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("wp14a roadmap lane selection failed: JSON root must be an object")
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
        raise RuntimeError(f"wp14a roadmap lane selection failed: {key} must be a non-empty string")


def _require_non_empty_list(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise RuntimeError(f"wp14a roadmap lane selection failed: {key} must be a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise RuntimeError(f"wp14a roadmap lane selection failed: {key} must contain non-empty strings")


def _require_false(payload: dict[str, Any], key: str) -> None:
    if payload.get(key) is not False:
        raise RuntimeError(f"wp14a roadmap lane selection failed: {key} must remain false")


def _validate_input_state(state: Any) -> None:
    if not isinstance(state, dict):
        raise RuntimeError("wp14a roadmap lane selection failed: input_state must be an object")
    missing_state = _missing(INPUT_REQUIRED, state)
    if missing_state:
        raise RuntimeError("wp14a roadmap lane selection failed: input_state missing key(s): " + ", ".join(missing_state))
    if state["wp13_review_chain_complete"] is not True:
        raise RuntimeError("wp14a roadmap lane selection failed: wp13_review_chain_complete must be true")
    if state["authority_not_granted"] is not True:
        raise RuntimeError("wp14a roadmap lane selection failed: authority_not_granted must be true")
    if state["roadmap_loop_closed"] is not True:
        raise RuntimeError("wp14a roadmap lane selection failed: roadmap_loop_closed must be true")
    for key in ("operational_prerequisites_complete", "production_delivery", "wp13_authority"):
        if state[key] is not False:
            raise RuntimeError(f"wp14a roadmap lane selection failed: input_state.{key} must remain false")


def _validate_candidate_lanes(lanes: Any) -> None:
    if not isinstance(lanes, dict):
        raise RuntimeError("wp14a roadmap lane selection failed: candidate_lanes must be an object")
    missing_lanes = _missing(REQUIRED_LANES, lanes)
    if missing_lanes:
        raise RuntimeError("wp14a roadmap lane selection failed: candidate_lanes missing lane(s): " + ", ".join(missing_lanes))
    for lane_name in REQUIRED_LANES:
        lane = lanes[lane_name]
        if not isinstance(lane, dict):
            raise RuntimeError(f"wp14a roadmap lane selection failed: {lane_name} must be an object")
        _require_non_empty_string(lane, "reason")
        if lane_name == "delivery_inputs_lane":
            if lane.get("allowed_now") is not False:
                raise RuntimeError("wp14a roadmap lane selection failed: delivery_inputs_lane.allowed_now must remain false")
        elif lane.get("allowed_now") is not True:
            raise RuntimeError(f"wp14a roadmap lane selection failed: {lane_name}.allowed_now must be true")


def _validate_selected_lane_result(result: Any) -> None:
    if not isinstance(result, dict):
        raise RuntimeError("wp14a roadmap lane selection failed: selected_lane_result must be an object")
    missing_result = _missing(SELECTED_RESULT_REQUIRED, result)
    if missing_result:
        raise RuntimeError("wp14a roadmap lane selection failed: selected_lane_result missing key(s): " + ", ".join(missing_result))
    if result["lane_selection_deferred_to_wp14b"] is not True:
        raise RuntimeError("wp14a roadmap lane selection failed: lane_selection_deferred_to_wp14b must be true")
    for key in CONCRETE_SELECTION_FLAGS:
        if result[key] is not False:
            raise RuntimeError(f"wp14a roadmap lane selection failed: {key} must remain false in WP14A")
    _require_non_empty_string(result, "reason")


def _validate_authority(authority: Any) -> None:
    if not isinstance(authority, dict):
        raise RuntimeError("wp14a roadmap lane selection failed: authority must be an object")
    missing_authority = _missing(AUTHORITY_REQUIRED, authority)
    if missing_authority:
        raise RuntimeError("wp14a roadmap lane selection failed: authority missing key(s): " + ", ".join(missing_authority))
    if authority["ready_for_wp13_preflight_only"] is not True:
        raise RuntimeError("wp14a roadmap lane selection failed: ready_for_wp13_preflight_only must be true")
    for key in AUTHORITY_MUST_BE_FALSE:
        if authority[key] is not False:
            raise RuntimeError(f"wp14a roadmap lane selection failed: authority.{key} must remain false")


def validate_wp14a_roadmap_lane_selection(path: Path) -> dict[str, Any]:
    payload = _load(path)
    missing_top = _missing(REQUIRED_TOP_LEVEL, payload)
    if missing_top:
        raise RuntimeError("wp14a roadmap lane selection failed: missing top-level key(s): " + ", ".join(missing_top))

    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(f"wp14a roadmap lane selection failed: unsupported schema_version={payload['schema_version']}")
    if payload["status"] != "roadmap_lane_selection_completed":
        raise RuntimeError("wp14a roadmap lane selection failed: status must be roadmap_lane_selection_completed")
    if payload["review_scope"] != "post_wp13_roadmap_lane_selection_only":
        raise RuntimeError("wp14a roadmap lane selection failed: review_scope must be post_wp13_roadmap_lane_selection_only")

    for key in {"review_id", "created_at_utc", "selected_lane", "selected_next_package", "selected_next_package_title"}:
        _require_non_empty_string(payload, key)
    if payload["selected_lane"] != "post_wp13_roadmap_lane_selection":
        raise RuntimeError("wp14a roadmap lane selection failed: selected_lane must be post_wp13_roadmap_lane_selection")
    if payload["selected_next_package"] != "WP14B":
        raise RuntimeError("wp14a roadmap lane selection failed: selected_next_package must be WP14B")

    _require_non_empty_list(payload, "basis")
    _validate_input_state(payload["input_state"])
    _validate_candidate_lanes(payload["candidate_lanes"])
    _validate_selected_lane_result(payload["selected_lane_result"])
    _require_non_empty_list(payload, "explicitly_out_of_scope")

    for key in ("implementation_allowed_in_this_package", "activation_allowed_in_this_package", "authority_created"):
        _require_false(payload, key)

    _validate_authority(payload["authority"])

    flattened = _flatten_text(payload).lower()
    for phrase in FORBIDDEN_POSITIVE_PHRASES:
        if phrase in flattened:
            raise RuntimeError(
                f"wp14a roadmap lane selection failed: artifact contains operational-roadmap-like wording: {phrase}"
            )

    result = {
        "schema_version": "etf_eu_wp14a_roadmap_lane_selection_validation_v1",
        "status": "valid_review_only_roadmap_lane_selection",
        "review_path": str(path),
        "selected_next_package": payload["selected_next_package"],
        "lane_selection_deferred_to_wp14b": True,
        "production_delivery": False,
        "wp14_authority": False,
    }

    print(
        "ETF_EU_WP14A_ROADMAP_LANE_SELECTION_OK | "
        f"artifact={path} | selected_next_package={payload['selected_next_package']} | "
        "lane_selection_deferred_to_wp14b=true | production_delivery=false | wp14_authority=false"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_wp14a_roadmap_lane_selection(Path(args.artifact))


if __name__ == "__main__":
    main()
