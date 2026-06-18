from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_delivery_authorization_decision_v1"
DECISION = "remain_blocked"
FALSE_FIELDS = [
    "delivery_authorized",
    "production_delivery",
    "recipient_activation",
    "send_attempted",
    "mail_transport_enabled",
    "smtp_configured",
    "secrets_present",
    "real_recipients",
    "real_receipt",
    "proof_claimed",
    "portfolio_mutation",
    "candidate_promotion",
    "funding_authority",
    "valuation_grade",
    "send_design_allowed",
]
REQUIRED_FIELDS = {
    "schema_version",
    "run_id",
    "status",
    "created_at_utc",
    "decision_layer",
    "input_authorization_gate_artifact_path",
    "recipient_policy_path",
    "secrets_policy_path",
    "delivery_authorization_gate_path",
    "html_pdf_render_dry_run_artifact_path",
    "delivery_authorization_decision",
    "decision_reason",
    "send_design_allowed_reason",
    "validators_run",
    "tests_expected",
    "selected_next_package",
    "selected_next_package_title",
    *FALSE_FIELDS,
}


class EtfEuDeliveryAuthorizationDecisionError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise EtfEuDeliveryAuthorizationDecisionError("artifact root must be object")
    return payload


def _path(payload: dict[str, Any], key: str) -> Path:
    raw = str(payload.get(key) or "").strip()
    if not raw:
        raise EtfEuDeliveryAuthorizationDecisionError(f"{key} missing")
    path = Path(raw)
    if not path.exists():
        raise EtfEuDeliveryAuthorizationDecisionError(f"{key} does not exist: {raw}")
    return path


def validate_delivery_authorization_decision(path: Path) -> dict[str, str]:
    payload = _load(path)
    missing = sorted(REQUIRED_FIELDS - set(payload))
    if missing:
        raise EtfEuDeliveryAuthorizationDecisionError("missing fields: " + ", ".join(missing))
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise EtfEuDeliveryAuthorizationDecisionError("bad schema_version")
    if payload.get("status") != "completed":
        raise EtfEuDeliveryAuthorizationDecisionError("status must be completed")
    if payload.get("decision_layer") != "delivery_authorization_review":
        raise EtfEuDeliveryAuthorizationDecisionError("decision_layer must be delivery_authorization_review")
    if payload.get("delivery_authorization_decision") != DECISION:
        raise EtfEuDeliveryAuthorizationDecisionError("delivery_authorization_decision must be remain_blocked")
    for field in FALSE_FIELDS:
        if payload.get(field) is not False:
            raise EtfEuDeliveryAuthorizationDecisionError(f"{field} must be false")
    for key in (
        "input_authorization_gate_artifact_path",
        "recipient_policy_path",
        "secrets_policy_path",
        "delivery_authorization_gate_path",
        "html_pdf_render_dry_run_artifact_path",
    ):
        _path(payload, key)
    if not str(payload.get("selected_next_package") or "").strip():
        raise EtfEuDeliveryAuthorizationDecisionError("selected_next_package missing")
    print(f"ETF_EU_DELIVERY_AUTHORIZATION_DECISION_OK | artifact={path} | decision={payload['delivery_authorization_decision']} | selected_next_package={payload['selected_next_package']}")
    return {
        "status": "valid",
        "artifact": str(path),
        "decision": str(payload["delivery_authorization_decision"]),
        "selected_next_package": str(payload["selected_next_package"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_delivery_authorization_decision(Path(args.artifact))


if __name__ == "__main__":
    main()
