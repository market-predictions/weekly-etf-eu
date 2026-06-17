from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_delivery_authority_prerequisite_reconciliation_v1"
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "review_id",
    "created_at_utc",
    "status",
    "review_scope",
    "basis",
    "prerequisite_domains",
    "reconciliation_result",
    "implementation_allowed_in_this_package",
    "activation_allowed_in_this_package",
    "authority_created",
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
DOMAIN_REQUIRED = {
    "review_artifact",
    "review_status",
    "activation_status",
    "production_ready",
    "authority_created",
}
RECONCILIATION_REQUIRED = {
    "review_chain_complete",
    "operational_prerequisites_complete",
    "delivery_authority_can_be_granted",
    "delivery_authority_review_can_be_considered_later",
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
    "delivery_proof",
    "send_attempted",
    "delivery_authority",
    "ready_for_wp13_preflight_only",
    "wp13_authority",
}
AUTHORITY_MUST_BE_FALSE = AUTHORITY_REQUIRED - {"ready_for_wp13_preflight_only"}
FORBIDDEN_POSITIVE_PHRASES = {
    "delivery authority granted",
    "production delivery enabled",
    "production delivery authorized",
    "recipient activation occurred",
    "transport activation occurred",
    "delivery proof exists",
    "delivery succeeded",
    "operational delivery enabled",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("delivery authority prerequisite reconciliation failed: JSON root must be an object")
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
        raise RuntimeError(
            f"delivery authority prerequisite reconciliation failed: {key} must be a non-empty string"
        )


def _require_non_empty_list(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise RuntimeError(
            f"delivery authority prerequisite reconciliation failed: {key} must be a non-empty list"
        )
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise RuntimeError(
            f"delivery authority prerequisite reconciliation failed: {key} must contain non-empty strings"
        )


def _require_false(payload: dict[str, Any], key: str) -> None:
    if payload.get(key) is not False:
        raise RuntimeError(f"delivery authority prerequisite reconciliation failed: {key} must remain false")


def _validate_domain(name: str, domain: Any) -> None:
    if not isinstance(domain, dict):
        raise RuntimeError(f"delivery authority prerequisite reconciliation failed: {name} must be an object")
    missing_domain = _missing(DOMAIN_REQUIRED, domain)
    if missing_domain:
        raise RuntimeError(
            f"delivery authority prerequisite reconciliation failed: {name} missing key(s): "
            + ", ".join(missing_domain)
        )
    if domain["review_status"] != "completed":
        raise RuntimeError(
            f"delivery authority prerequisite reconciliation failed: {name}.review_status must be completed"
        )
    if domain["activation_status"] != "not_activated":
        raise RuntimeError(
            f"delivery authority prerequisite reconciliation failed: {name}.activation_status must be not_activated"
        )
    if domain["production_ready"] is not False:
        raise RuntimeError(
            f"delivery authority prerequisite reconciliation failed: {name}.production_ready must remain false"
        )
    if domain["authority_created"] is not False:
        raise RuntimeError(
            f"delivery authority prerequisite reconciliation failed: {name}.authority_created must remain false"
        )
    _require_non_empty_string(domain, "review_artifact")


def _validate_domains(domains: Any) -> None:
    if not isinstance(domains, dict):
        raise RuntimeError("delivery authority prerequisite reconciliation failed: prerequisite_domains must be an object")
    missing_domains = _missing(REQUIRED_DOMAINS, domains)
    if missing_domains:
        raise RuntimeError(
            "delivery authority prerequisite reconciliation failed: prerequisite_domains missing required domain(s): "
            + ", ".join(missing_domains)
        )
    for domain_name in REQUIRED_DOMAINS:
        _validate_domain(domain_name, domains[domain_name])


def _validate_reconciliation_result(result: Any) -> None:
    if not isinstance(result, dict):
        raise RuntimeError("delivery authority prerequisite reconciliation failed: reconciliation_result must be an object")
    missing_result = _missing(RECONCILIATION_REQUIRED, result)
    if missing_result:
        raise RuntimeError(
            "delivery authority prerequisite reconciliation failed: reconciliation_result missing key(s): "
            + ", ".join(missing_result)
        )
    if result["review_chain_complete"] is not True:
        raise RuntimeError(
            "delivery authority prerequisite reconciliation failed: review_chain_complete must be true"
        )
    if result["operational_prerequisites_complete"] is not False:
        raise RuntimeError(
            "delivery authority prerequisite reconciliation failed: operational_prerequisites_complete must remain false"
        )
    if result["delivery_authority_can_be_granted"] is not False:
        raise RuntimeError(
            "delivery authority prerequisite reconciliation failed: delivery_authority_can_be_granted must remain false"
        )
    if result["delivery_authority_review_can_be_considered_later"] is not True:
        raise RuntimeError(
            "delivery authority prerequisite reconciliation failed: delivery_authority_review_can_be_considered_later must be true"
        )
    _require_non_empty_string(result, "reason")


def _validate_authority(authority: Any) -> None:
    if not isinstance(authority, dict):
        raise RuntimeError("delivery authority prerequisite reconciliation failed: authority must be an object")
    missing_authority = _missing(AUTHORITY_REQUIRED, authority)
    if missing_authority:
        raise RuntimeError(
            "delivery authority prerequisite reconciliation failed: authority missing required key(s): "
            + ", ".join(missing_authority)
        )
    if authority["ready_for_wp13_preflight_only"] is not True:
        raise RuntimeError(
            "delivery authority prerequisite reconciliation failed: authority.ready_for_wp13_preflight_only must be true"
        )
    for key in AUTHORITY_MUST_BE_FALSE:
        if authority[key] is not False:
            raise RuntimeError(
                f"delivery authority prerequisite reconciliation failed: authority.{key} must remain false"
            )


def validate_delivery_authority_prerequisite_reconciliation(path: Path) -> dict[str, Any]:
    payload = _load(path)

    missing_top = _missing(REQUIRED_TOP_LEVEL, payload)
    if missing_top:
        raise RuntimeError(
            "delivery authority prerequisite reconciliation failed: missing top-level key(s): "
            + ", ".join(missing_top)
        )

    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(
            f"delivery authority prerequisite reconciliation failed: unsupported schema_version={payload['schema_version']}"
        )
    if payload["status"] != "delivery_authority_prerequisite_reconciliation_completed":
        raise RuntimeError(
            "delivery authority prerequisite reconciliation failed: status must be delivery_authority_prerequisite_reconciliation_completed"
        )
    if payload["review_scope"] != "delivery_authority_prerequisite_reconciliation_only":
        raise RuntimeError(
            "delivery authority prerequisite reconciliation failed: review_scope must be delivery_authority_prerequisite_reconciliation_only"
        )

    for key in {"review_id", "created_at_utc", "selected_next_package", "selected_next_package_title"}:
        _require_non_empty_string(payload, key)

    _require_non_empty_list(payload, "basis")
    _validate_domains(payload["prerequisite_domains"])
    _validate_reconciliation_result(payload["reconciliation_result"])
    _require_non_empty_list(payload, "explicitly_out_of_scope")

    for key in (
        "implementation_allowed_in_this_package",
        "activation_allowed_in_this_package",
        "authority_created",
    ):
        _require_false(payload, key)

    if payload["selected_next_package"] != "WP13H":
        raise RuntimeError(
            "delivery authority prerequisite reconciliation failed: selected_next_package must be WP13H"
        )

    _validate_authority(payload["authority"])

    flattened = _flatten_text(payload).lower()
    for phrase in FORBIDDEN_POSITIVE_PHRASES:
        if phrase in flattened:
            raise RuntimeError(
                "delivery authority prerequisite reconciliation failed: "
                f"artifact contains operational-authority-like wording: {phrase}"
            )

    result = {
        "schema_version": "etf_eu_delivery_authority_prerequisite_reconciliation_validation_v1",
        "status": "valid_review_only_delivery_authority_prerequisite_reconciliation",
        "review_path": str(path),
        "selected_next_package": payload["selected_next_package"],
        "review_chain_complete": True,
        "operational_prerequisites_complete": False,
        "delivery_authority_can_be_granted": False,
        "delivery_authority": False,
        "production_delivery": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "candidate_promotion": False,
        "wp13_authority": False,
    }

    print(
        "ETF_EU_DELIVERY_AUTHORITY_PREREQUISITE_RECONCILIATION_OK | "
        f"artifact={path} | selected_next_package={payload['selected_next_package']} | "
        "review_chain_complete=true | operational_prerequisites_complete=false | "
        "delivery_authority=false | production_delivery=false | wp13_authority=false"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_delivery_authority_prerequisite_reconciliation(Path(args.artifact))


if __name__ == "__main__":
    main()
