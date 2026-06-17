from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_production_prerequisite_gap_review_v1"
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "review_id",
    "created_at_utc",
    "status",
    "review_scope",
    "basis",
    "gap_domains",
    "recommended_gap_closure_sequence",
    "selected_next_package",
    "selected_next_package_title",
    "explicitly_out_of_scope",
    "authority",
}
REQUIRED_DOMAINS = {
    "recipient_policy",
    "secure_transport_setup",
    "receipt_proof_path",
}
REQUIRED_DOMAIN_FIELDS = {
    "domain",
    "current_state",
    "gap_status",
    "required_future_review",
    "implementation_allowed_in_this_package",
    "activation_allowed_in_this_package",
    "authority_created",
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
    "gap closed",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("production prerequisite gap review failed: JSON root must be an object")
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
        raise RuntimeError(f"production prerequisite gap review failed: {key} must be a non-empty string")


def _require_non_empty_list(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise RuntimeError(f"production prerequisite gap review failed: {key} must be a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise RuntimeError(f"production prerequisite gap review failed: {key} must contain non-empty strings")


def _validate_authority(authority: Any) -> None:
    if not isinstance(authority, dict):
        raise RuntimeError("production prerequisite gap review failed: authority must be an object")
    missing_authority = _missing(AUTHORITY_REQUIRED, authority)
    if missing_authority:
        raise RuntimeError(
            "production prerequisite gap review failed: authority missing required key(s): "
            + ", ".join(missing_authority)
        )
    if authority["ready_for_wp13_preflight_only"] is not True:
        raise RuntimeError(
            "production prerequisite gap review failed: authority.ready_for_wp13_preflight_only must be true"
        )
    for key in AUTHORITY_MUST_BE_FALSE:
        if authority[key] is not False:
            raise RuntimeError(f"production prerequisite gap review failed: authority.{key} must remain false")


def _validate_gap_domains(gap_domains: Any) -> None:
    if not isinstance(gap_domains, list) or not gap_domains:
        raise RuntimeError("production prerequisite gap review failed: gap_domains must be a non-empty list")

    seen_domains: set[str] = set()
    for index, domain_payload in enumerate(gap_domains):
        if not isinstance(domain_payload, dict):
            raise RuntimeError(
                f"production prerequisite gap review failed: gap_domains[{index}] must be an object"
            )
        missing_domain_keys = _missing(REQUIRED_DOMAIN_FIELDS, domain_payload)
        if missing_domain_keys:
            raise RuntimeError(
                f"production prerequisite gap review failed: gap_domains[{index}] missing key(s): "
                + ", ".join(missing_domain_keys)
            )
        domain = domain_payload["domain"]
        if not isinstance(domain, str) or not domain.strip():
            raise RuntimeError(
                f"production prerequisite gap review failed: gap_domains[{index}].domain must be non-empty"
            )
        seen_domains.add(domain)
        if domain_payload["gap_status"] != "gap_open":
            raise RuntimeError(
                f"production prerequisite gap review failed: {domain}.gap_status must be gap_open"
            )
        for key in (
            "implementation_allowed_in_this_package",
            "activation_allowed_in_this_package",
            "authority_created",
        ):
            if domain_payload[key] is not False:
                raise RuntimeError(
                    f"production prerequisite gap review failed: {domain}.{key} must remain false"
                )

    missing_required_domains = sorted(REQUIRED_DOMAINS - seen_domains)
    if missing_required_domains:
        raise RuntimeError(
            "production prerequisite gap review failed: missing required gap domain(s): "
            + ", ".join(missing_required_domains)
        )


def validate_production_prerequisite_gap_review(path: Path) -> dict[str, Any]:
    payload = _load(path)

    missing_top = _missing(REQUIRED_TOP_LEVEL, payload)
    if missing_top:
        raise RuntimeError(
            "production prerequisite gap review failed: missing top-level key(s): "
            + ", ".join(missing_top)
        )

    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(
            f"production prerequisite gap review failed: unsupported schema_version={payload['schema_version']}"
        )
    if payload["status"] != "gap_review_completed":
        raise RuntimeError("production prerequisite gap review failed: status must be gap_review_completed")
    if payload["review_scope"] != "production_prerequisites_review_only":
        raise RuntimeError(
            "production prerequisite gap review failed: review_scope must be production_prerequisites_review_only"
        )

    for key in {"review_id", "created_at_utc", "selected_next_package", "selected_next_package_title"}:
        _require_non_empty_string(payload, key)

    _require_non_empty_list(payload, "basis")
    _require_non_empty_list(payload, "recommended_gap_closure_sequence")
    _require_non_empty_list(payload, "explicitly_out_of_scope")
    _validate_gap_domains(payload["gap_domains"])

    if payload["selected_next_package"] != "WP13D":
        raise RuntimeError("production prerequisite gap review failed: selected_next_package must be WP13D")

    _validate_authority(payload["authority"])

    flattened = _flatten_text(payload).lower()
    for phrase in FORBIDDEN_POSITIVE_PHRASES:
        if phrase in flattened:
            raise RuntimeError(
                f"production prerequisite gap review failed: artifact contains operational-delivery-like wording: {phrase}"
            )

    result = {
        "schema_version": "etf_eu_production_prerequisite_gap_review_validation_v1",
        "status": "valid_review_only_gap_review",
        "review_path": str(path),
        "selected_next_package": payload["selected_next_package"],
        "reviewed_domains": sorted(REQUIRED_DOMAINS),
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "candidate_promotion": False,
        "wp13_authority": False,
    }

    print(
        "ETF_EU_PRODUCTION_PREREQUISITE_GAP_REVIEW_OK | "
        f"artifact={path} | selected_next_package={payload['selected_next_package']} | "
        "gap_status=gap_open | wp13_authority=false | production_delivery=false"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_production_prerequisite_gap_review(Path(args.artifact))


if __name__ == "__main__":
    main()
