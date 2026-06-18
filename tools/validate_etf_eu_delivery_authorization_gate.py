from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_delivery_authorization_gate_v1"
FALSE_FIELDS = [
    "delivery_authorized",
    "production_delivery",
    "recipient_activation",
    "send_attempted",
    "real_receipt",
    "proof_claimed",
    "real_recipients",
    "secrets_present",
    "mail_transport_enabled",
    "smtp_configured",
    "portfolio_mutation",
    "candidate_promotion",
    "funding_authority",
    "valuation_grade",
]
REQUIRED_FIELDS = {
    "schema_version",
    "run_id",
    "status",
    "created_at_utc",
    "recipient_policy_path",
    "secrets_policy_path",
    "delivery_authorization_gate_path",
    "html_pdf_render_dry_run_artifact_path",
    "english_html_output_path",
    "dutch_html_output_path",
    "delivery_authorization_reason",
    "recipient_policy_exists",
    "secrets_policy_exists",
    "recipient_source",
    "secrets_required_for_this_package",
    "validators_run",
    "tests_expected",
    "selected_next_package",
    "selected_next_package_title",
    *FALSE_FIELDS,
}


class EtfEuDeliveryAuthorizationGateError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise EtfEuDeliveryAuthorizationGateError("artifact root must be object")
    return payload


def _path(payload: dict[str, Any], key: str) -> Path:
    raw = str(payload.get(key) or "").strip()
    if not raw:
        raise EtfEuDeliveryAuthorizationGateError(f"{key} missing")
    path = Path(raw)
    if not path.exists():
        raise EtfEuDeliveryAuthorizationGateError(f"{key} does not exist: {raw}")
    return path


def _require_policy_text(path: Path, snippets: list[str], label: str) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [snippet for snippet in snippets if snippet not in text]
    if missing:
        raise EtfEuDeliveryAuthorizationGateError(f"{label} policy missing: " + ", ".join(missing))


def validate_delivery_authorization_gate(path: Path) -> dict[str, str]:
    payload = _load(path)
    missing = sorted(REQUIRED_FIELDS - set(payload))
    if missing:
        raise EtfEuDeliveryAuthorizationGateError("missing fields: " + ", ".join(missing))
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise EtfEuDeliveryAuthorizationGateError("bad schema_version")
    if payload.get("status") != "completed":
        raise EtfEuDeliveryAuthorizationGateError("status must be completed")
    for field in FALSE_FIELDS:
        if payload.get(field) is not False:
            raise EtfEuDeliveryAuthorizationGateError(f"{field} must be false")
    if payload.get("recipient_policy_exists") is not True:
        raise EtfEuDeliveryAuthorizationGateError("recipient_policy_exists must be true")
    if payload.get("secrets_policy_exists") is not True:
        raise EtfEuDeliveryAuthorizationGateError("secrets_policy_exists must be true")
    if payload.get("secrets_required_for_this_package") is not False:
        raise EtfEuDeliveryAuthorizationGateError("secrets_required_for_this_package must be false")
    if payload.get("recipient_source") != "none":
        raise EtfEuDeliveryAuthorizationGateError("recipient_source must be none")
    recipient_policy = _path(payload, "recipient_policy_path")
    secrets_policy = _path(payload, "secrets_policy_path")
    gate_policy = _path(payload, "delivery_authorization_gate_path")
    _path(payload, "html_pdf_render_dry_run_artifact_path")
    _path(payload, "english_html_output_path")
    _path(payload, "dutch_html_output_path")
    _require_policy_text(recipient_policy, ["real_recipients=false", "recipient_activation=false", "recipient_source=none"], "recipient")
    _require_policy_text(secrets_policy, ["secrets_present=false", "mail_transport_enabled=false", "smtp_configured=false"], "secrets")
    _require_policy_text(gate_policy, ["delivery_authorized=false", "production_delivery=false", "real_receipt=false"], "delivery gate")
    if not str(payload.get("selected_next_package") or "").strip():
        raise EtfEuDeliveryAuthorizationGateError("selected_next_package missing")
    print(f"ETF_EU_DELIVERY_AUTHORIZATION_GATE_OK | artifact={path} | selected_next_package={payload['selected_next_package']}")
    return {"status": "valid", "artifact": str(path), "selected_next_package": str(payload["selected_next_package"])}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_delivery_authorization_gate(Path(args.artifact))


if __name__ == "__main__":
    main()
