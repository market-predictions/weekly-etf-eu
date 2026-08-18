from __future__ import annotations

import json
from pathlib import Path
from typing import Any

AUTHORIZED_EXACT_STATUSES = {"fresh_exact_verified", "fresh_exact_unverified"}


def _text(value: Any) -> str:
    return str(value or "").strip()


def apply_primary_verification_to_legacy(
    *,
    qualification_path: Path,
    legacy_path: Path,
) -> dict[str, Any]:
    qualification = json.loads(qualification_path.read_text(encoding="utf-8"))
    legacy = json.loads(legacy_path.read_text(encoding="utf-8"))
    lines = {
        _text(line.get("basket_id")): line
        for line in qualification.get("lines") or []
        if isinstance(line, dict) and _text(line.get("basket_id"))
    }

    for row in legacy.get("rows") or []:
        if not isinstance(row, dict):
            continue
        line = lines.get(_text(row.get("basket_id")))
        if line is None:
            continue
        status = _text(line.get("qualification_status"))
        authorized = status in AUTHORIZED_EXACT_STATUSES and line.get("static_identity_binding") is True
        primary_provider = _text(line.get("primary_provider")) or None
        verification_providers = [
            _text(item) for item in line.get("verification_providers") or [] if _text(item)
        ]
        row["pricing_status"] = "priced_non_authoritative" if authorized else "blocked"
        row["close_date"] = line.get("selected_close_date") if authorized else None
        row["close_price"] = line.get("selected_close_price") if authorized else None
        row["source_id"] = primary_provider or "none"
        row["source_name"] = (
            f"{primary_provider} exact completed close"
            if authorized and primary_provider
            else "No authorized exact completed close"
        )
        row["source_quality_status"] = status
        row["source_agreement_status"] = status
        row["requested_report_date"] = qualification.get("report_date")
        row["completed_close_on_or_before_report_date"] = authorized
        row["completed_close_on_requested_report_date"] = authorized
        row["valuation_grade"] = authorized
        row["primary_provider"] = primary_provider
        row["verification_status"] = line.get("verification_status")
        row["verification_providers"] = verification_providers
        row["static_identity_binding"] = line.get("static_identity_binding") is True
        row["static_identity_binding_status"] = line.get("static_identity_binding_status")
        row["static_identity_registry_id"] = line.get("static_identity_registry_id")
        row["static_identity_blockers"] = list(line.get("static_identity_blockers") or [])
        row["agreeing_providers"] = list(line.get("agreeing_providers") or [])
        row["agreement_spread_pct"] = line.get("agreement_spread_pct")
        row["same_date_provider_count"] = int(line.get("same_date_provider_count") or 0)
        row["identity_assurance_status"] = line.get("identity_assurance_status")
        row["identity_anchor_provider_count"] = int(line.get("identity_anchor_provider_count") or 0)

    rows = [row for row in legacy.get("rows") or [] if isinstance(row, dict)]
    priced = [row for row in rows if row.get("pricing_status") == "priced_non_authoritative"]
    legacy["priced_line_count"] = len(priced)
    legacy["failed_line_count"] = len(rows) - len(priced)
    legacy["report_pricing_gate_passed"] = qualification.get("report_pricing_gate_passed") is True
    legacy["valuation_grade"] = qualification.get("report_pricing_gate_passed") is True
    legacy["funded_pricing_authorized_count"] = int(qualification.get("funded_pricing_authorized_count") or 0)
    legacy["funded_verified_count"] = int(qualification.get("funded_verified_count") or 0)
    legacy["funded_unverified_count"] = int(qualification.get("funded_unverified_count") or 0)
    legacy["funded_consensus_count"] = int(qualification.get("funded_consensus_count") or 0)
    legacy["funded_static_identity_bound_count"] = int(qualification.get("funded_static_identity_bound_count") or 0)
    legacy["pricing_authority_policy"] = qualification.get("pricing_authority_policy")
    legacy["identity_policy"] = qualification.get("identity_policy")
    legacy["static_identity_binding_artifact"] = qualification.get("static_identity_binding_artifact")
    legacy["legacy_projection_semantics"] = "primary_exact_close_with_optional_verification_v1"
    legacy_path.write_text(json.dumps(legacy, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return legacy
