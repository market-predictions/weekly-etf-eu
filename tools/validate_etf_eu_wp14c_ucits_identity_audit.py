from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_wp14c_ucits_identity_audit_v1"
REQUIRED_FILES = {
    "control/UCITS_SYMBOL_REGISTRY_CONTRACT.md",
    "control/UCITS_ETF_REVIEW_CONTRACT_V1.md",
    "control/UCITS_INVESTABILITY_RULES.md",
    "control/UCITS_MIGRATION_PLAN.md",
    "config/ucits_symbol_registry.yml",
}
DIMENSIONS = {
    "isin_first_identity",
    "exchange_line_identity",
    "currency_identity",
    "fund_name_identity",
    "proxy_vs_candidate_separation",
    "investability_rule_alignment",
    "registry_schema_completeness",
    "validator_coverage",
    "fixture_coverage",
    "report_surface_dependency_risk",
}
FINDING_FIELDS = {
    "id",
    "dimension",
    "status",
    "severity",
    "finding",
    "evidence_files",
    "recommended_next_action",
    "implementation_allowed_in_wp14c",
}
VALID_STATUS = {"ok", "gap", "risk", "needs_followup"}
VALID_SEVERITY = {"low", "medium", "high"}
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
    "registry was " + "mutated",
    "report renderer was " + "changed",
    "production delivery is active",
    "delivery " + "succeeded",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("WP14C failed: JSON root must be object")
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


def _non_empty_list(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise RuntimeError(f"WP14C failed: {key} must be non-empty list")


def _false(payload: dict[str, Any], key: str) -> None:
    if payload.get(key) is not False:
        raise RuntimeError(f"WP14C failed: {key} must remain false")


def _validate_input(state: Any) -> None:
    if not isinstance(state, dict):
        raise RuntimeError("WP14C failed: input_state must be object")
    if state.get("selected_implementation_lane") != "ucits_instrument_identity_lane":
        raise RuntimeError("WP14C failed: wrong selected lane")
    if state.get("plan_only") is not True:
        raise RuntimeError("WP14C failed: plan_only must be true")
    for key in ("production_delivery", "wp13_authority", "operational_prerequisites_complete"):
        if state.get(key) is not False:
            raise RuntimeError(f"WP14C failed: input_state.{key} must remain false")


def _validate_files(files: Any) -> None:
    if not isinstance(files, list) or not files:
        raise RuntimeError("WP14C failed: audited_files must be non-empty list")
    missing = sorted(REQUIRED_FILES - set(files))
    if missing:
        raise RuntimeError("WP14C failed: audited_files missing " + ", ".join(missing))


def _validate_dimensions(dimensions: Any) -> None:
    if not isinstance(dimensions, dict):
        raise RuntimeError("WP14C failed: audit_dimensions must be object")
    missing = sorted(DIMENSIONS - set(dimensions))
    if missing:
        raise RuntimeError("WP14C failed: audit_dimensions missing " + ", ".join(missing))
    for key in DIMENSIONS:
        if dimensions.get(key) != "reviewed":
            raise RuntimeError(f"WP14C failed: dimension {key} must be reviewed")


def _validate_findings(findings: Any) -> tuple[int, int, int, int]:
    if not isinstance(findings, list) or not findings:
        raise RuntimeError("WP14C failed: findings must be non-empty list")
    high = medium = low = 0
    for item in findings:
        if not isinstance(item, dict):
            raise RuntimeError("WP14C failed: finding must be object")
        missing = _missing(FINDING_FIELDS, item)
        if missing:
            raise RuntimeError("WP14C failed: finding missing " + ", ".join(missing))
        if item["dimension"] not in DIMENSIONS:
            raise RuntimeError("WP14C failed: invalid finding dimension")
        if item["status"] not in VALID_STATUS:
            raise RuntimeError("WP14C failed: invalid finding status")
        if item["severity"] not in VALID_SEVERITY:
            raise RuntimeError("WP14C failed: invalid finding severity")
        if item["implementation_allowed_in_wp14c"] is not False:
            raise RuntimeError("WP14C failed: finding implementation flag must remain false")
        _non_empty_list(item, "evidence_files")
        if item["severity"] == "high":
            high += 1
        elif item["severity"] == "medium":
            medium += 1
        else:
            low += 1
    return len(findings), high, medium, low


def _validate_summary(summary: Any, counts: tuple[int, int, int, int]) -> None:
    if not isinstance(summary, dict):
        raise RuntimeError("WP14C failed: summary must be object")
    total, high, medium, low = counts
    expected = {
        "total_findings": total,
        "high_severity_findings": high,
        "medium_severity_findings": medium,
        "low_severity_findings": low,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise RuntimeError(f"WP14C failed: summary count mismatch for {key}")
    if summary.get("safe_to_continue_to_wp14d") is not True:
        raise RuntimeError("WP14C failed: safe_to_continue_to_wp14d must be true")


def _validate_authority(authority: Any) -> None:
    if not isinstance(authority, dict):
        raise RuntimeError("WP14C failed: authority must be object")
    missing = _missing(AUTHORITY, authority)
    if missing:
        raise RuntimeError("WP14C failed: authority missing " + ", ".join(missing))
    if authority["ready_for_wp13_preflight_only"] is not True:
        raise RuntimeError("WP14C failed: ready_for_wp13_preflight_only must be true")
    for key in AUTHORITY_FALSE:
        if authority[key] is not False:
            raise RuntimeError(f"WP14C failed: authority.{key} must remain false")


def validate_wp14c_ucits_identity_audit(path: Path) -> dict[str, Any]:
    payload = _load(path)
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise RuntimeError("WP14C failed: unsupported schema_version")
    if payload.get("status") != "ucits_identity_audit_completed":
        raise RuntimeError("WP14C failed: bad status")
    if payload.get("review_scope") != "ucits_identity_audit_review_only":
        raise RuntimeError("WP14C failed: bad review_scope")
    _non_empty_list(payload, "basis")
    _validate_input(payload.get("input_state"))
    _validate_files(payload.get("audited_files"))
    _validate_dimensions(payload.get("audit_dimensions"))
    counts = _validate_findings(payload.get("findings"))
    _validate_summary(payload.get("summary"), counts)
    for key in (
        "implementation_allowed_in_this_package",
        "registry_mutation_allowed_in_this_package",
        "report_renderer_mutation_allowed_in_this_package",
        "activation_allowed_in_this_package",
        "authority_created",
    ):
        _false(payload, key)
    if payload.get("selected_next_package") != "WP14D":
        raise RuntimeError("WP14C failed: selected_next_package must be WP14D")
    _non_empty_list(payload, "explicitly_out_of_scope")
    _validate_authority(payload.get("authority"))
    flattened = _text(payload).lower()
    for phrase in BAD_TEXT:
        if phrase in flattened:
            raise RuntimeError(f"WP14C failed: forbidden wording: {phrase}")
    total, high, medium, low = counts
    result = {
        "schema_version": "etf_eu_wp14c_ucits_identity_audit_validation_v1",
        "status": "valid_review_only_ucits_identity_audit",
        "review_path": str(path),
        "total_findings": total,
        "high_severity_findings": high,
        "medium_severity_findings": medium,
        "low_severity_findings": low,
        "selected_next_package": payload["selected_next_package"],
    }
    print(
        "ETF_EU_WP14C_UCITS_IDENTITY_AUDIT_OK | "
        f"artifact={path} | findings={total} | high={high} | medium={medium} | low={low} | "
        f"selected_next_package={payload['selected_next_package']} | production_delivery=false | wp14_authority=false"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_wp14c_ucits_identity_audit(Path(args.artifact))


if __name__ == "__main__":
    main()
