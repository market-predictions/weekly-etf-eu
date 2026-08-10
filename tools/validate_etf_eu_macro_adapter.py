from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


SUPPORTED_SCHEMAS = {"etf_eu_macro_policy_pack_v1", "etf_eu_macro_policy_pack_v2"}


def fail(code: str, **details: Any) -> None:
    payload = {"ok": False, "code": code, **details}
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(1)


def validate(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail("ETF_EU_MACRO_ARTIFACT_MISSING", path=str(path))
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail("ETF_EU_MACRO_ARTIFACT_INVALID_JSON", error=type(exc).__name__)

    if payload.get("schema_version") not in SUPPORTED_SCHEMAS:
        fail("ETF_EU_MACRO_CONTRACT_MISMATCH", field="schema_version", expected=sorted(SUPPORTED_SCHEMAS), actual=payload.get("schema_version"))
    for key, expected in {
        "artifact_type": "etf_eu_macro_policy_pack",
        "source_of_truth_repo": "market-predictions/weekly-etf-eu",
        "reference_architecture_repo": "market-predictions/weekly-etf",
    }.items():
        if payload.get(key) != expected:
            fail("ETF_EU_MACRO_CONTRACT_MISMATCH", field=key, expected=expected, actual=payload.get(key))

    for key in ("report_date", "run_id", "generated_at_utc", "donor_provenance", "authority", "eu_adaptation"):
        if not payload.get(key):
            fail("ETF_EU_MACRO_REQUIRED_FIELD_MISSING", field=key)

    authority = payload.get("authority") or {}
    eu = payload.get("eu_adaptation") or {}
    if authority.get("decision_authority") != "descriptive_only":
        fail("ETF_EU_MACRO_DECISION_AUTHORITY_ESCALATED")
    for field in ("valuation_grade", "funding_authority", "portfolio_mutation", "production_delivery_authority"):
        if eu.get(field) is not False:
            fail("ETF_EU_MACRO_AUTHORITY_ESCALATED", field=field, actual=eu.get(field))

    donor = payload.get("donor_provenance") or {}
    age_days = donor.get("age_days_at_eu_report_date")
    if not isinstance(age_days, int) or age_days < 0 or age_days > 3:
        fail("ETF_EU_MACRO_DONOR_STALE", age_days=age_days)
    if not donor.get("source_sha256") or len(str(donor.get("source_sha256"))) != 64:
        fail("ETF_EU_MACRO_SOURCE_DIGEST_INVALID")

    if payload.get("schema_version") == "etf_eu_macro_policy_pack_v2":
        if donor.get("freshness_passed") is not True:
            fail("ETF_EU_MACRO_FRESHNESS_NOT_PASSED")
        if donor.get("wrapper_generation_refreshes_underlying_evidence_date") is not False:
            fail("ETF_EU_MACRO_WRAPPER_REFRESHED_EVIDENCE_DATE")
        if not donor.get("source_report_date") or not donor.get("source_date_field"):
            fail("ETF_EU_MACRO_UNDERLYING_EVIDENCE_DATE_MISSING")
        if authority.get("broker_specific_permission_required_for_model") is not False:
            fail("ETF_EU_MACRO_BROKER_MODEL_BOUNDARY_INVALID")
        if authority.get("broker_permission_required_for_real_execution") is not True:
            fail("ETF_EU_MACRO_BROKER_EXECUTION_BOUNDARY_INVALID")
        if eu.get("broker_specific_permission_required_for_model") is not False:
            fail("ETF_EU_MACRO_EU_MODEL_BROKER_BOUNDARY_INVALID")
        if eu.get("broker_permission_required_for_real_execution") is not True:
            fail("ETF_EU_MACRO_EU_EXECUTION_BROKER_BOUNDARY_INVALID")

    return {
        "ok": True,
        "path": str(path),
        "schema_version": payload["schema_version"],
        "report_date": payload["report_date"],
        "run_id": payload["run_id"],
        "source_report_date": donor.get("source_report_date"),
        "source_date_field": donor.get("source_date_field"),
        "age_days": age_days,
        "decision_authority": authority.get("decision_authority"),
        "broker_specific_permission_required_for_model": authority.get("broker_specific_permission_required_for_model"),
    }


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: validate_etf_eu_macro_adapter.py <artifact.json>")
    print(json.dumps(validate(Path(sys.argv[1])), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
