from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


ALLOWED = {
    "PARITY",
    "EU_ADAPTED_PARITY",
    "INTENTIONAL_EU_DIVERGENCE",
    "GAP_BLOCKING",
    "GAP_NONBLOCKING",
}

REQUIRED_BUCKETS = {
    "ai_digital_infrastructure",
    "defense_resilience",
    "grid_power_electrification",
    "uranium_nuclear",
    "agriculture_food_security",
    "water",
    "china",
    "india_regional_industrialization",
    "biotech_healthcare_innovation",
    "fintech_financial_infrastructure",
    "robotics_automation",
    "critical_minerals_materials",
}


def text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def yaml_obj(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def result(capability: str, layer: str, status: str, evidence: list[str], note: str) -> dict[str, Any]:
    if status not in ALLOWED:
        raise ValueError(status)
    return {
        "capability": capability,
        "layer": layer,
        "status": status,
        "evidence": evidence,
        "note": note,
    }


def audit(root: Path, donor_root: Path | None = None) -> dict[str, Any]:
    discovery = yaml_obj(root / "config/etf_eu_discovery_universe.yml")
    transition = yaml_obj(root / "config/etf_eu_transition_policy_v1.yml")
    investability = text(root / "control/UCITS_INVESTABILITY_RULES.md")
    authority = text(root / "control/ETF_EU_ALLOCATION_AUTHORITY_CONVERGENCE_V1.md")
    reunderwriting = text(root / "control/CAPITAL_REUNDERWRITING_RULES.md")
    lane_contract = text(root / "control/LANE_DISCOVERY_CONTRACT.md")
    system_index = text(root / "control/SYSTEM_INDEX.md")
    runbook = text(root / "control/ETF_EU_ROUTINE_WEEKLY_PRODUCTION_RUNBOOK_V2.md")
    state_v3 = text(root / "runtime/build_etf_eu_production_convergence_state_v3.py")
    client_surface = text(root / "runtime/synchronize_etf_eu_current_state_surface_v2.py")
    score_builder = text(root / "runtime/build_etf_eu_current_reunderwriting_scorecard.py")
    score_validator = text(root / "tools/validate_etf_eu_current_reunderwriting_scorecard.py")
    macro = text(root / "runtime/adapt_weekly_etf_macro_for_eu.py")
    routine = text(root / ".github/workflows/run-weekly-etf-eu-routine.yml")
    assurance = text(root / "tools/validate_etf_eu_release_assurance.py")

    items: list[dict[str, Any]] = []

    required = set(discovery.get("required_breadth_buckets") or [])
    lanes = [row for row in discovery.get("lanes") or [] if isinstance(row, dict)]
    lane_buckets = {str(row.get("bucket") or "") for row in lanes}
    rules = discovery.get("rules") if isinstance(discovery.get("rules"), dict) else {}
    discovery_ok = (
        REQUIRED_BUCKETS <= required
        and REQUIRED_BUCKETS <= lane_buckets
        and rules.get("historical_stage1_allowlist_is_discovery_gate") is False
        and rules.get("missing_ucits_mapping_blocks_funding_not_research") is True
        and int(rules.get("target_candidate_lanes_min") or 0) >= 10
        and int(rules.get("minimum_challengers") or 0) >= 4
    )
    items.append(result(
        "broad_discovery",
        "decision_framework",
        "EU_ADAPTED_PARITY" if discovery_ok else "GAP_BLOCKING",
        ["config/etf_eu_discovery_universe.yml", "control/LANE_DISCOVERY_CONTRACT.md"],
        "Donor-comparable breadth is preserved while missing exact UCITS mappings block funding rather than research." if discovery_ok else "Required donor breadth or Stage-1 de-freezing is incomplete.",
    ))

    mapping_ok = all(
        row.get("proxy_authority") in {None, "research_only"}
        and row.get("mapping_status")
        for row in lanes
    ) and "U.S.-listed ETFs remain research references only" in investability
    items.append(result(
        "proxy_to_ucits_mapping",
        "input_state_contract",
        "INTENTIONAL_EU_DIVERGENCE" if mapping_ok else "GAP_BLOCKING",
        ["control/UCITS_INVESTABILITY_RULES.md", "config/etf_eu_discovery_universe.yml"],
        "EU requires exact UCITS identity/KID/trading-line evidence; U.S. vehicles remain research proxies." if mapping_ok else "Proxy/fundable boundary is not explicit enough.",
    ))

    transition_ok = (
        transition.get("status") == "historical_shadow_only"
        and transition.get("current_allocation_authority") is False
        and transition.get("client_control_authority") is False
        and ((transition.get("stage_1") or {}).get("current_candidate_gate_authority") is False)
        and "shadow_policy_used_for_current_allocation" in state_v3
        and "historical_stage1_candidate_gate_applied" in state_v3
    )
    items.append(result(
        "allocation_authority",
        "decision_framework",
        "EU_ADAPTED_PARITY" if transition_ok else "GAP_BLOCKING",
        ["control/ETF_EU_ALLOCATION_AUTHORITY_CONVERGENCE_V1.md", "config/etf_eu_transition_policy_v1.yml", "runtime/build_etf_eu_production_convergence_state_v3.py"],
        "Current authority is separated from historical Stage-1/shadow scenarios without inventing replacement caps." if transition_ok else "Historical transition policy can still affect current allocation authority.",
    ))

    retired_tokens = ["35% minimum cash", "15% maximum new ETF", "50% cash-first"]
    authority_ok = all(token in authority for token in retired_tokens) and "current_allocation_authority=false" in authority
    client_ok = (
        "transition_allocator_removed_from_client_authority" in client_surface
        and "measured_lower_bound_not_target_or_control" in client_surface
        and "broker_neutral_model_execution_permission_separate" in client_surface
    )
    items.append(result(
        "client_control_authority_hygiene",
        "output_contract",
        "EU_ADAPTED_PARITY" if authority_ok and client_ok else "GAP_BLOCKING",
        ["runtime/synchronize_etf_eu_current_state_surface_v2.py", "control/ETF_EU_ALLOCATION_AUTHORITY_CONVERGENCE_V1.md"],
        "Retired/shadow percentages are removed from current client authority and embedded exposure is typed as a lower bound." if authority_ok and client_ok else "Current client authority can still expose historical controls or ambiguous lower-bound semantics.",
    ))

    broker_ok = (
        "broker_specific_permission_required_for_model=false" in investability
        and "broker_permission_required_for_real_execution=true" in investability
        and "broker_specific_permission_required_for_model=false" in runbook
        and "broker_permission_required_for_real_execution=true" in runbook
    )
    items.append(result(
        "broker_neutral_model_boundary",
        "input_state_contract",
        "INTENTIONAL_EU_DIVERGENCE" if broker_ok else "GAP_BLOCKING",
        ["control/UCITS_INVESTABILITY_RULES.md", "control/ETF_EU_ROUTINE_WEEKLY_PRODUCTION_RUNBOOK_V2.md"],
        "Model investability is broker-neutral; account permission is reserved for real execution." if broker_ok else "Broker-neutrality contracts remain contradictory.",
    ))

    reunderwriting_ok = all(token in reunderwriting for token in [
        "Would initiate today?",
        "Exact-UCITS alternative duel",
        "Action clock / inertia",
        "Cash policy",
    ]) and "funded positions" in score_validator and "fresh_cash_test" in score_builder
    items.append(result(
        "capital_reunderwriting",
        "decision_framework",
        "EU_ADAPTED_PARITY" if reunderwriting_ok else "GAP_BLOCKING",
        ["control/CAPITAL_REUNDERWRITING_RULES.md", "runtime/build_etf_eu_current_reunderwriting_scorecard.py", "tools/validate_etf_eu_current_reunderwriting_scorecard.py"],
        "Donor fresh-cash, alternative-duel, action-clock and cash-discipline behaviors are adapted to exact UCITS candidates." if reunderwriting_ok else "Current-run re-underwriting memory is incomplete.",
    ))

    normalized_ok = all(token in state_v3 for token in [
        "current_allocation_authority",
        "historical_transition_scenario",
        "historical_target_used_for_current_trade",
        "promoted_exposures",
    ])
    items.append(result(
        "normalized_state_authority",
        "input_state_contract",
        "EU_ADAPTED_PARITY" if normalized_ok else "GAP_BLOCKING",
        ["runtime/build_etf_eu_production_convergence_state_v3.py"],
        "Actual state/current review authority is explicitly separated from historical transition evidence." if normalized_ok else "Normalized state still conflates current and historical authority.",
    ))

    macro_ok = all(token in macro for token in [
        "source_sha256",
        "source_report_date",
        "age_days_at_eu_report_date",
        "age_days > 3",
    ]) and "runtime.adapt_weekly_etf_macro_for_eu" in routine
    items.append(result(
        "macro_provenance_and_freshness",
        "input_state_contract",
        "EU_ADAPTED_PARITY" if macro_ok else "GAP_BLOCKING",
        ["runtime/adapt_weekly_etf_macro_for_eu.py", ".github/workflows/run-weekly-etf-eu-routine.yml"],
        "Donor macro content is hash/date bound and current routine adapts it with a fail-closed freshness limit." if macro_ok else "Current routine is not provably tied to donor macro evidence date/content identity.",
    ))

    routine_ok = (
        "ETF_EU_REPORT_DATE" in routine
        and "request_path" in routine
        and "Build and validate independent governance release assurance" in routine
        and "Execute guarded current-run delivery" in routine
        and "run-weekly-etf-eu-routine.yml" in system_index
        and "RUNBOOK_V2" in system_index
    )
    items.append(result(
        "canonical_dynamic_routine",
        "operational_runbook",
        "EU_ADAPTED_PARITY" if routine_ok else "GAP_BLOCKING",
        [".github/workflows/run-weekly-etf-eu-routine.yml", "control/ETF_EU_ROUTINE_WEEKLY_PRODUCTION_RUNBOOK_V2.md", "control/SYSTEM_INDEX.md"],
        "The routine is request/run-scoped and separate from historical hardcoded repair workflows." if routine_ok else "Routine-production authority or dynamic date/run identity remains ambiguous.",
    ))

    assurance_ok = bool(assurance) and "governance" in system_index.casefold() and "receipt" in runbook.casefold()
    items.append(result(
        "independent_release_and_delivery_assurance",
        "governance_release_assurance",
        "PARITY" if assurance_ok else "GAP_BLOCKING",
        ["tools/validate_etf_eu_release_assurance.py", "control/ETF_EU_TWO_ROLE_GOVERNANCE_MODEL_V1.md", "control/ETF_EU_ROUTINE_WEEKLY_PRODUCTION_RUNBOOK_V2.md"],
        "Independent candidate assurance and separate receipt-confirmed delivery closeout are preserved." if assurance_ok else "Release/delivery assurance evidence is incomplete.",
    ))

    intentional = [
        ("isin_first_identity", "input_state_contract", "ISIN + exact share class/trading line is stronger EU-specific authority."),
        ("ucits_priips_kid_gate", "input_state_contract", "UCITS/PRIIPs/KID is an EU-specific fundability boundary."),
        ("dutch_primary_output", "output_contract", "Dutch-primary plus English companion is an intentional product divergence."),
        ("us_etfs_research_only", "decision_framework", "U.S. ETFs are research proxies, never funded EU holdings."),
        ("no_report_workflow_broker_execution", "operational_runbook", "Report workflow cannot execute real broker orders."),
    ]
    for capability, layer, note in intentional:
        items.append(result(capability, layer, "INTENTIONAL_EU_DIVERGENCE", ["control/SYSTEM_INDEX.md"], note))

    donor_evidence: dict[str, Any] = {"checked": False}
    if donor_root is not None:
        donor_files = [
            donor_root / "control/LANE_DISCOVERY_CONTRACT.md",
            donor_root / "control/CAPITAL_REUNDERWRITING_RULES.md",
            donor_root / "control/ETF_RUNTIME_STATE_CONTRACT.md",
        ]
        donor_evidence = {
            "checked": True,
            "required_files": [str(path) for path in donor_files],
            "all_required_files_present": all(path.exists() for path in donor_files),
        }
        if not donor_evidence["all_required_files_present"]:
            items.append(result(
                "donor_reference_material",
                "governance_release_assurance",
                "GAP_BLOCKING",
                [str(path) for path in donor_files],
                "Required donor reference contracts are not available to the parity audit.",
            ))
        else:
            items.append(result(
                "donor_reference_material",
                "governance_release_assurance",
                "PARITY",
                [str(path) for path in donor_files],
                "Mature donor discovery/re-underwriting/runtime reference contracts are present for comparison.",
            ))

    blockers = [item for item in items if item["status"] == "GAP_BLOCKING"]
    nonblocking = [item for item in items if item["status"] == "GAP_NONBLOCKING"]
    payload = {
        "schema_version": "etf_eu_donor_parity_audit_v1",
        "repository": "market-predictions/weekly-etf-eu",
        "donor_repository": "market-predictions/weekly-etf",
        "items": items,
        "summary": {
            "item_count": len(items),
            "blocking_gap_count": len(blockers),
            "nonblocking_gap_count": len(nonblocking),
            "release_blocked": bool(blockers),
            "statuses": {
                status: sum(1 for item in items if item["status"] == status)
                for status in sorted(ALLOWED)
            },
        },
        "donor_evidence": donor_evidence,
        "valid": not blockers,
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit Weekly ETF EU behavioral parity against the mature Weekly ETF donor contracts")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--donor-root", type=Path)
    parser.add_argument("--output", type=Path, default=Path("output/quality/etf_eu_donor_parity_audit.json"))
    args = parser.parse_args()
    payload = audit(args.root, args.donor_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    if not payload["valid"]:
        raise SystemExit("ETF_EU_DONOR_PARITY_BLOCKING_GAPS")


if __name__ == "__main__":
    main()
