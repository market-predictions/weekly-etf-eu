from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_wp14b_roadmap_lane_implementation_plan_v1"
TOP = {
    "schema_version",
    "review_id",
    "created_at_utc",
    "status",
    "review_scope",
    "basis",
    "input_state",
    "lane_decision",
    "implementation_plan",
    "implementation_allowed_in_this_package",
    "activation_allowed_in_this_package",
    "authority_created",
    "selected_next_package",
    "selected_next_package_title",
    "explicitly_out_of_scope",
    "authority",
}
INPUT_TRUE = {"wp13_review_chain_complete", "authority_not_granted", "roadmap_loop_closed", "lane_selection_deferred_to_wp14b"}
INPUT_FALSE = {"operational_prerequisites_complete", "production_delivery", "wp13_authority"}
LANE_FLAGS_FALSE = {"delivery_inputs_lane_selected", "product_quality_lane_selected", "report_surface_quality_lane_selected"}
AUTHORITY = {
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
AUTHORITY_FALSE = AUTHORITY - {"ready_for_wp13_preflight_only"}
BAD_TEXT = {
    "authority " + "granted",
    "lane was " + "implemented",
    "registry mutation " + "occurred",
    "delivery " + "succeeded",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("WP14B failed: JSON root must be object")
    return payload


def _missing(required: set[str], payload: dict[str, Any]) -> list[str]:
    return sorted(required - set(payload))


def _text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(_text(v) for v in value)
    if isinstance(value, str):
        return value
    return ""


def _non_empty_str(payload: dict[str, Any], key: str) -> None:
    if not isinstance(payload.get(key), str) or not payload[key].strip():
        raise RuntimeError(f"WP14B failed: {key} must be non-empty string")


def _non_empty_list(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise RuntimeError(f"WP14B failed: {key} must be non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise RuntimeError(f"WP14B failed: {key} items must be non-empty strings")


def _false(payload: dict[str, Any], key: str) -> None:
    if payload.get(key) is not False:
        raise RuntimeError(f"WP14B failed: {key} must remain false")


def _validate_input(state: Any) -> None:
    if not isinstance(state, dict):
        raise RuntimeError("WP14B failed: input_state must be object")
    missing = _missing(INPUT_TRUE | INPUT_FALSE, state)
    if missing:
        raise RuntimeError("WP14B failed: input_state missing " + ", ".join(missing))
    for key in INPUT_TRUE:
        if state[key] is not True:
            raise RuntimeError(f"WP14B failed: input_state.{key} must be true")
    for key in INPUT_FALSE:
        if state[key] is not False:
            raise RuntimeError(f"WP14B failed: input_state.{key} must remain false")


def _validate_lane(decision: Any) -> None:
    if not isinstance(decision, dict):
        raise RuntimeError("WP14B failed: lane_decision must be object")
    required = {"selected_implementation_lane", "ucits_instrument_identity_lane_selected", "reason"} | LANE_FLAGS_FALSE
    missing = _missing(required, decision)
    if missing:
        raise RuntimeError("WP14B failed: lane_decision missing " + ", ".join(missing))
    if decision["selected_implementation_lane"] != "ucits_instrument_identity_lane":
        raise RuntimeError("WP14B failed: selected_implementation_lane must be ucits_instrument_identity_lane")
    if decision["ucits_instrument_identity_lane_selected"] is not True:
        raise RuntimeError("WP14B failed: ucits lane selected must be true")
    for key in LANE_FLAGS_FALSE:
        if decision[key] is not False:
            raise RuntimeError(f"WP14B failed: {key} must remain false")
    _non_empty_str(decision, "reason")


def _validate_plan(plan: Any) -> None:
    if not isinstance(plan, dict):
        raise RuntimeError("WP14B failed: implementation_plan must be object")
    required = {
        "plan_only",
        "implementation_allowed_in_wp14b",
        "recommended_next_package",
        "recommended_next_package_title",
        "required_future_files_to_review",
        "future_work_items",
    }
    missing = _missing(required, plan)
    if missing:
        raise RuntimeError("WP14B failed: implementation_plan missing " + ", ".join(missing))
    if plan["plan_only"] is not True:
        raise RuntimeError("WP14B failed: plan_only must be true")
    if plan["implementation_allowed_in_wp14b"] is not False:
        raise RuntimeError("WP14B failed: implementation_allowed_in_wp14b must remain false")
    if plan["recommended_next_package"] != "WP14C":
        raise RuntimeError("WP14B failed: recommended_next_package must be WP14C")
    _non_empty_str(plan, "recommended_next_package_title")
    _non_empty_list(plan, "required_future_files_to_review")
    _non_empty_list(plan, "future_work_items")


def _validate_authority(authority: Any) -> None:
    if not isinstance(authority, dict):
        raise RuntimeError("WP14B failed: authority must be object")
    missing = _missing(AUTHORITY, authority)
    if missing:
        raise RuntimeError("WP14B failed: authority missing " + ", ".join(missing))
    if authority["ready_for_wp13_preflight_only"] is not True:
        raise RuntimeError("WP14B failed: ready_for_wp13_preflight_only must be true")
    for key in AUTHORITY_FALSE:
        if authority[key] is not False:
            raise RuntimeError(f"WP14B failed: authority.{key} must remain false")


def validate_wp14b_roadmap_lane_implementation_plan(path: Path) -> dict[str, Any]:
    payload = _load(path)
    missing = _missing(TOP, payload)
    if missing:
        raise RuntimeError("WP14B failed: missing top-level " + ", ".join(missing))
    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError("WP14B failed: unsupported schema_version")
    if payload["status"] != "roadmap_lane_implementation_plan_completed":
        raise RuntimeError("WP14B failed: bad status")
    if payload["review_scope"] != "post_wp13_implementation_plan_review_only":
        raise RuntimeError("WP14B failed: bad review_scope")
    for key in {"review_id", "created_at_utc", "selected_next_package", "selected_next_package_title"}:
        _non_empty_str(payload, key)
    if payload["selected_next_package"] != "WP14C":
        raise RuntimeError("WP14B failed: selected_next_package must be WP14C")
    _non_empty_list(payload, "basis")
    _validate_input(payload["input_state"])
    _validate_lane(payload["lane_decision"])
    _validate_plan(payload["implementation_plan"])
    _non_empty_list(payload, "explicitly_out_of_scope")
    for key in ("implementation_allowed_in_this_package", "activation_allowed_in_this_package", "authority_created"):
        _false(payload, key)
    _validate_authority(payload["authority"])
    flattened = _text(payload).lower()
    for phrase in BAD_TEXT:
        if phrase in flattened:
            raise RuntimeError(f"WP14B failed: forbidden positive wording: {phrase}")
    result = {
        "schema_version": "etf_eu_wp14b_roadmap_lane_implementation_plan_validation_v1",
        "status": "valid_review_only_roadmap_implementation_plan",
        "review_path": str(path),
        "selected_implementation_lane": payload["lane_decision"]["selected_implementation_lane"],
        "selected_next_package": payload["selected_next_package"],
        "plan_only": True,
        "production_delivery": False,
        "wp14_authority": False,
    }
    print(
        "ETF_EU_WP14B_ROADMAP_LANE_IMPLEMENTATION_PLAN_OK | "
        f"artifact={path} | selected_implementation_lane={payload['lane_decision']['selected_implementation_lane']} | "
        f"selected_next_package={payload['selected_next_package']} | plan_only=true | production_delivery=false | wp14_authority=false"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_wp14b_roadmap_lane_implementation_plan(Path(args.artifact))


if __name__ == "__main__":
    main()
