from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_next_review_step_decision_v1"
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "decision_id",
    "created_at_utc",
    "status",
    "selected_next_package",
    "selected_next_package_title",
    "basis",
    "next_package_scope",
    "explicitly_out_of_scope",
    "authority",
}
AUTHORITY_REQUIRED = {
    "valuation_grade",
    "funding_authority",
    "portfolio_mutation",
    "production_delivery",
    "candidate_promotion",
    "ready_for_wp13_preflight_only",
    "wp13_authority",
}
AUTHORITY_MUST_BE_FALSE = AUTHORITY_REQUIRED - {"ready_for_wp13_preflight_only"}
FORBIDDEN_POSITIVE_PHRASES = {
    "operational delivery enabled",
    "delivery enabled",
    "delivery authorized",
    "production delivery enabled",
    "production delivery authorized",
    "recipient activation enabled",
    "transport activation enabled",
    "production pdf generation enabled",
    "real receipt created",
    "report dispatch enabled",
    "portfolio mutation enabled",
    "candidate promotion enabled",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("next review step decision failed: JSON root must be an object")
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
        raise RuntimeError(f"next review step decision failed: {key} must be a non-empty string")


def _require_non_empty_list(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise RuntimeError(f"next review step decision failed: {key} must be a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise RuntimeError(f"next review step decision failed: {key} must contain non-empty strings")


def validate_next_review_step_decision(path: Path) -> dict[str, Any]:
    payload = _load(path)

    missing_top = _missing(REQUIRED_TOP_LEVEL, payload)
    if missing_top:
        raise RuntimeError(
            "next review step decision failed: missing top-level key(s): " + ", ".join(missing_top)
        )

    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(
            f"next review step decision failed: unsupported schema_version={payload['schema_version']}"
        )

    if payload["status"] != "next_review_step_selected":
        raise RuntimeError("next review step decision failed: status must be next_review_step_selected")

    _require_non_empty_string(payload, "selected_next_package")
    if payload["selected_next_package"] != "WP13C":
        raise RuntimeError("next review step decision failed: selected_next_package must be WP13C")

    _require_non_empty_string(payload, "selected_next_package_title")
    _require_non_empty_list(payload, "basis")
    _require_non_empty_list(payload, "next_package_scope")
    _require_non_empty_list(payload, "explicitly_out_of_scope")

    authority = payload["authority"]
    if not isinstance(authority, dict):
        raise RuntimeError("next review step decision failed: authority must be an object")

    missing_authority = _missing(AUTHORITY_REQUIRED, authority)
    if missing_authority:
        raise RuntimeError(
            "next review step decision failed: authority missing required key(s): "
            + ", ".join(missing_authority)
        )

    if authority["ready_for_wp13_preflight_only"] is not True:
        raise RuntimeError(
            "next review step decision failed: authority.ready_for_wp13_preflight_only must be true"
        )

    for key in AUTHORITY_MUST_BE_FALSE:
        if authority[key] is not False:
            raise RuntimeError(f"next review step decision failed: authority.{key} must remain false")

    flattened = _flatten_text(payload).lower()
    for phrase in FORBIDDEN_POSITIVE_PHRASES:
        if phrase in flattened:
            raise RuntimeError(
                f"next review step decision failed: artifact contains operational-delivery-like wording: {phrase}"
            )

    result = {
        "schema_version": "etf_eu_next_review_step_decision_validation_v1",
        "status": "valid_review_only_next_step",
        "decision_path": str(path),
        "selected_next_package": payload["selected_next_package"],
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "candidate_promotion": False,
        "wp13_authority": False,
    }

    print(
        "ETF_EU_NEXT_REVIEW_STEP_DECISION_OK | "
        f"artifact={path} | selected_next_package={payload['selected_next_package']} | "
        "wp13_authority=false | production_delivery=false"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_next_review_step_decision(Path(args.artifact))


if __name__ == "__main__":
    main()
