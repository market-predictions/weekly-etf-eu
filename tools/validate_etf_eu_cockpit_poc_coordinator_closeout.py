from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMA_VERSION = "etf_eu_cockpit_poc_coordinator_closeout_v1"
READY = "ready_for_client_surface_review"
COORDINATOR_READY = "ready_for_coordinator_review"
TRUE_FIELDS = ["coordinator_closeout_created", "review_acceptance_checklist_created", "proof_of_concept_package_preserved", "readiness_gate_preserved", "pricing_integration_preserved", "pricing_line_evidence_preserved", "authority_boundary_preserved", "proxy_separation_preserved", "debug_surface_hygiene_preserved"]
FALSE_FIELDS = ["production_delivery", "portfolio_mutation", "candidate_promotion", "funding_authority", "valuation_grade"]
PATH_FIELDS = ["source_poc_package_manifest_path", "source_poc_package_index_path", "source_client_surface_readiness_artifact_path", "source_pricing_integration_manifest_path", "source_pricing_line_expansion_manifest_path", "authorization_decision_artifact_path", "recommended_first_review_file"]
LIST_FIELDS = ["review_files", "supporting_manifest_files"]
CHECKLIST_PATH = Path("output/client_surface/etf_eu_cockpit_poc_coordinator_closeout_checklist_20260618_000000.md")
CHECKLIST_TERMS = ["ETF EU Cockpit POC Coordinator Closeout", "ready for coordinator/client-surface review", "CSPX.L", "SXR8.DE", "IE00B5BMR087", "IE00BMC38736", "SMH", "Gold/ETC", "Infrastructure", "SPY", "GLD", "PAVE", "review-only", "usable_for_review_only", "pricing_symbol_ambiguous", "policy_blocked", "identity_incomplete", "delivery_authorization_decision=remain_blocked", "production_delivery=false", "portfolio_mutation=false", "candidate_promotion=false", "funding_authority=false", "valuation_grade=false"]
FORBIDDEN_PAIRS = [("production delivery", "authorized"), ("delivery receipt", "exists"), ("portfolio mutation", "authorized"), ("candidate promotion", "authorized"), ("funding", "authorized"), ("valuation-grade authority", "created"), ("smh", "safe as ucits pricing evidence"), ("spy", "as eu holding"), ("smh", "as eu holding"), ("gld", "as eu holding"), ("pave", "as eu holding"), ("gld", "as eu pricing line"), ("pave", "as eu pricing line")]


class EtfEuCockpitPocCoordinatorCloseoutError(RuntimeError):
    pass


def _load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise EtfEuCockpitPocCoordinatorCloseoutError("closeout root must be object")
    return data


def _must_exist(raw: str, label: str) -> None:
    if not raw or not Path(raw).exists():
        raise EtfEuCockpitPocCoordinatorCloseoutError(f"missing {label}: {raw}")


def validate_coordinator_closeout(path: Path) -> dict[str, str]:
    if not path.exists():
        raise EtfEuCockpitPocCoordinatorCloseoutError(f"missing closeout artifact: {path}")
    if not CHECKLIST_PATH.exists():
        raise EtfEuCockpitPocCoordinatorCloseoutError(f"missing closeout checklist: {CHECKLIST_PATH}")
    payload = _load(path)
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise EtfEuCockpitPocCoordinatorCloseoutError("bad schema_version")
    if payload.get("status") != "completed":
        raise EtfEuCockpitPocCoordinatorCloseoutError("status must be completed")
    if payload.get("overall_readiness_status") != READY:
        raise EtfEuCockpitPocCoordinatorCloseoutError("overall_readiness_status mismatch")
    if payload.get("coordinator_review_status") != COORDINATOR_READY:
        raise EtfEuCockpitPocCoordinatorCloseoutError("coordinator_review_status mismatch")
    if payload.get("delivery_authorization_decision") != "remain_blocked":
        raise EtfEuCockpitPocCoordinatorCloseoutError("delivery decision changed")
    if payload.get("visible_candidate_count") != 4:
        raise EtfEuCockpitPocCoordinatorCloseoutError("visible_candidate_count must be 4")
    for field in TRUE_FIELDS:
        if payload.get(field) is not True:
            raise EtfEuCockpitPocCoordinatorCloseoutError(f"{field} must be true")
    for field in FALSE_FIELDS:
        if payload.get(field) is not False:
            raise EtfEuCockpitPocCoordinatorCloseoutError(f"{field} must be false")
    for field in PATH_FIELDS:
        _must_exist(str(payload.get(field) or ""), field)
    for field in LIST_FIELDS:
        values = payload.get(field)
        if not isinstance(values, list) or not values:
            raise EtfEuCockpitPocCoordinatorCloseoutError(f"{field} must be non-empty list")
        for item in values:
            _must_exist(str(item), f"{field} item")
    checklist = CHECKLIST_PATH.read_text(encoding="utf-8")
    checklist_lower = checklist.lower()
    for term in CHECKLIST_TERMS:
        if term.lower() not in checklist_lower:
            raise EtfEuCockpitPocCoordinatorCloseoutError(f"checklist missing term: {term}")
    combined = (json.dumps(payload, sort_keys=True) + "\n" + checklist).lower()
    for left, right in FORBIDDEN_PAIRS:
        if left in combined and right in combined:
            raise EtfEuCockpitPocCoordinatorCloseoutError(f"forbidden authority wording: {left} + {right}")
    checklist_map = payload.get("acceptance_checklist")
    if not isinstance(checklist_map, dict) or not checklist_map:
        raise EtfEuCockpitPocCoordinatorCloseoutError("acceptance_checklist missing")
    for key, value in checklist_map.items():
        if value is not True:
            raise EtfEuCockpitPocCoordinatorCloseoutError(f"acceptance checklist item not true: {key}")
    if not str(payload.get("selected_next_package") or "").strip():
        raise EtfEuCockpitPocCoordinatorCloseoutError("selected_next_package missing")
    print(f"ETF_EU_COCKPIT_POC_COORDINATOR_CLOSEOUT_OK | artifact={path} | coordinator_review_status={payload['coordinator_review_status']} | selected_next_package={payload['selected_next_package']}")
    return {"status": "valid", "artifact": str(path), "selected_next_package": str(payload["selected_next_package"])}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_coordinator_closeout(Path(args.artifact))


if __name__ == "__main__":
    main()
