from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMA_VERSION = "etf_eu_cockpit_poc_package_v1"
READY = "ready_for_client_surface_review"
TRUE_FIELDS = ["package_created", "proof_of_concept_package_created", "client_surface_package_index_created", "readiness_gate_preserved", "pricing_integration_preserved", "pricing_line_evidence_preserved", "authority_boundary_preserved", "proxy_separation_preserved", "debug_surface_hygiene_preserved"]
FALSE_FIELDS = ["production_delivery", "portfolio_mutation", "candidate_promotion", "funding_authority", "valuation_grade"]
PATH_FIELDS = ["source_client_surface_readiness_artifact_path", "source_client_surface_readiness_notes_path", "source_pricing_integration_manifest_path", "source_pricing_line_expansion_manifest_path", "authorization_decision_artifact_path", "recommended_first_review_file"]
LIST_FIELDS = ["client_facing_review_files", "supporting_manifest_files", "supporting_notes_files", "validator_files", "test_files"]
INDEX_TERMS = ["ETF EU Cockpit Proof-of-Concept Package", "ready for coordinator/client-surface review", "CSPX.L", "SXR8.DE", "IE00B5BMR087", "IE00BMC38736", "SMH", "Gold/ETC", "Infrastructure", "SPY", "GLD", "PAVE", "review-only", "usable_for_review_only", "pricing_symbol_ambiguous", "policy_blocked", "identity_incomplete", "delivery_authorization_decision=remain_blocked", "production_delivery=false", "portfolio_mutation=false", "candidate_promotion=false", "funding_authority=false", "valuation_grade=false"]
FORBIDDEN_PAIRS = [("production delivery", "authorized"), ("delivery receipt", "exists"), ("portfolio mutation", "authorized"), ("candidate promotion", "authorized"), ("funding", "authorized"), ("valuation-grade authority", "created"), ("smh", "safe as ucits pricing evidence"), ("spy", "as eu holding"), ("smh", "as eu holding"), ("gld", "as eu holding"), ("pave", "as eu holding"), ("gld", "as eu pricing line"), ("pave", "as eu pricing line")]


class EtfEuCockpitPocPackageError(RuntimeError):
    pass


def _load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise EtfEuCockpitPocPackageError("manifest root must be object")
    return data


def _must_exist(raw: str, label: str) -> None:
    if not raw or not Path(raw).exists():
        raise EtfEuCockpitPocPackageError(f"missing {label}: {raw}")


def validate_cockpit_poc_package(path: Path) -> dict[str, str]:
    if not path.exists():
        raise EtfEuCockpitPocPackageError(f"missing package manifest: {path}")
    payload = _load(path)
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise EtfEuCockpitPocPackageError("bad schema_version")
    if payload.get("status") != "completed":
        raise EtfEuCockpitPocPackageError("status must be completed")
    if payload.get("overall_readiness_status") != READY:
        raise EtfEuCockpitPocPackageError("overall_readiness_status mismatch")
    if payload.get("delivery_authorization_decision") != "remain_blocked":
        raise EtfEuCockpitPocPackageError("delivery decision changed")
    if payload.get("visible_candidate_count") != 4:
        raise EtfEuCockpitPocPackageError("visible_candidate_count must be 4")
    for field in TRUE_FIELDS:
        if payload.get(field) is not True:
            raise EtfEuCockpitPocPackageError(f"{field} must be true")
    for field in FALSE_FIELDS:
        if payload.get(field) is not False:
            raise EtfEuCockpitPocPackageError(f"{field} must be false")
    for field in PATH_FIELDS:
        _must_exist(str(payload.get(field) or ""), field)
    for field in LIST_FIELDS:
        values = payload.get(field)
        if not isinstance(values, list) or not values:
            raise EtfEuCockpitPocPackageError(f"{field} must be non-empty list")
        for item in values:
            _must_exist(str(item), f"{field} item")
    index_path = Path(str(payload["recommended_first_review_file"]))
    index = index_path.read_text(encoding="utf-8")
    lower_index = index.lower()
    for term in INDEX_TERMS:
        if term.lower() not in lower_index:
            raise EtfEuCockpitPocPackageError(f"index missing term: {term}")
    combined = (json.dumps(payload, sort_keys=True) + "\n" + index).lower()
    for left, right in FORBIDDEN_PAIRS:
        if left in combined and right in combined:
            raise EtfEuCockpitPocPackageError(f"forbidden authority wording: {left} + {right}")
    if not str(payload.get("selected_next_package") or "").strip():
        raise EtfEuCockpitPocPackageError("selected_next_package missing")
    print(f"ETF_EU_COCKPIT_POC_PACKAGE_OK | artifact={path} | recommended_first_review_file={payload['recommended_first_review_file']} | selected_next_package={payload['selected_next_package']}")
    return {"status": "valid", "artifact": str(path), "selected_next_package": str(payload["selected_next_package"])}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_cockpit_poc_package(Path(args.artifact))


if __name__ == "__main__":
    main()
