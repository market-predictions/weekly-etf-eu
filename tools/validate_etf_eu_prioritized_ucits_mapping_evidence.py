from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


EXPECTED_ORDER = [
    "non_us_developed_equities",
    "grid_power",
    "biotech_innovation",
    "healthcare_quality",
    "uranium_nuclear",
    "power_utilities_capex",
    "defense_resilience",
    "agri_food_security",
]
EXPECTED_CANONICAL_MAPPINGS = {
    "non_us_developed_equities": "developed_ex_us_ishares_msci_world_ex_usa",
    "biotech_innovation": "biotech_ishares_nasdaq_us_biotechnology",
    "healthcare_quality": "healthcare_ishares_msci_world_advanced",
    "uranium_nuclear": "uranium_nuclear_vaneck_nukl",
    "defense_resilience": "defense_vaneck_dfen",
    "agri_food_security": "agriculture_ishares_agribusiness",
}


def load(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Prioritized mapping evidence must be a YAML object")
    return payload


def num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def validate(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_eu_prioritized_ucits_mapping_evidence_v1":
        blockers.append("unexpected schema_version")
    if payload.get("artifact_type") != "etf_eu_prioritized_ucits_mapping_evidence":
        blockers.append("unexpected artifact_type")
    if payload.get("status") != "shadow_only":
        blockers.append("mapping evidence must remain shadow_only")
    if payload.get("strategy_source") != "weekly_etf_shared_contract_v1_0_0":
        blockers.append("strategy source release mismatch")
    for key in (
        "production_registry_overwrite",
        "mapping_authority",
        "allocation_authority",
        "portfolio_mutation",
        "funding_authority",
        "execution_authority",
        "production_delivery_authority",
    ):
        if payload.get(key) is not False:
            blockers.append(f"{key} must be false")

    rows = [row for row in (payload.get("rows") or []) if isinstance(row, dict)]
    if [row.get("exposure_id") for row in rows] != EXPECTED_ORDER:
        blockers.append("mapping review order mismatch")
    if [row.get("priority") for row in rows] != list(range(1, len(EXPECTED_ORDER) + 1)):
        blockers.append("mapping priorities must be contiguous")
    index = {str(row.get("exposure_id")): row for row in rows if row.get("exposure_id")}

    for exposure_id, registry_id in EXPECTED_CANONICAL_MAPPINGS.items():
        row = index.get(exposure_id, {})
        if row.get("canonical_mapping_status") != "mapped":
            blockers.append(f"{exposure_id} must be canonically mapped")
        if row.get("candidate_registry_id") != registry_id:
            blockers.append(f"{exposure_id} registry mapping mismatch")
        if row.get("official_identity_status") != "pass":
            blockers.append(f"{exposure_id} official identity must pass")
        if row.get("exact_trading_line_status") != "pass":
            blockers.append(f"{exposure_id} exact line must pass")

    ixua = index.get("non_us_developed_equities", {})
    correction = ixua.get("correction") if isinstance(ixua.get("correction"), dict) else {}
    if correction.get("previous_status") != "kid_missing":
        blockers.append("IXUA previous KID status is not recorded")
    if correction.get("current_status") != "issuer_kid_available_exact_artifact_not_captured":
        blockers.append("IXUA KID status correction mismatch")
    if ixua.get("exact_kid_artifact_status") != "incomplete":
        blockers.append("IXUA exact KID artifact must remain incomplete")
    if ixua.get("cutover_status") != "blocked":
        blockers.append("IXUA cutover status must remain blocked")

    grid = index.get("grid_power", {})
    if grid.get("canonical_mapping_status") != "unmapped":
        blockers.append("grid_power must remain unmapped")
    if grid.get("official_product_existence_status") != "pass":
        blockers.append("grid official product existence is not recorded")
    if grid.get("official_identity_status") != "incomplete" or grid.get("exact_trading_line_status") != "incomplete":
        blockers.append("grid identity and line evidence must remain incomplete")
    if grid.get("candidate_registry_id") not in (None, ""):
        blockers.append("grid must not claim a registry candidate")

    utilities = index.get("power_utilities_capex", {})
    if utilities.get("canonical_mapping_status") != "research_candidate_not_mapped":
        blockers.append("utilities must remain a research candidate rather than canonical mapping")
    if utilities.get("exposure_fit") != "adjacent_broad_utilities_proxy":
        blockers.append("utilities exposure-purity boundary mismatch")
    if "exposure_purity_review_required" not in (utilities.get("blocker_codes") or []):
        blockers.append("utilities exposure-purity blocker missing")

    nuclear = index.get("uranium_nuclear", {})
    defense = index.get("defense_resilience", {})
    if nuclear.get("exact_kid_artifact_status") != "pass":
        blockers.append("NUKL exact KID artifact must pass")
    if defense.get("exact_kid_artifact_status") != "pass":
        blockers.append("DFEN exact KID artifact must pass")
    if defense.get("boundary") != "must_not_be_reused_as_exact_europe_only_defense_mapping":
        blockers.append("DFEN Europe-only boundary missing")

    for row in rows:
        if row.get("cutover_status") not in {"blocked", "watch_only_no_donor_target"}:
            blockers.append(f"{row.get('exposure_id')} has invalid cutover status")
        if row.get("cutover_status") == "blocked" and not row.get("blocker_codes"):
            blockers.append(f"{row.get('exposure_id')} blocked without blocker codes")

    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    expected_summary = {
        "reviewed_exposure_count": 8,
        "canonical_mapped_count": 6,
        "research_candidate_not_mapped_count": 1,
        "unmapped_count": 1,
        "exact_kid_artifact_pass_count": 2,
        "cutover_ready_count": 0,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            blockers.append(f"summary {key} mismatch")
    if abs(num(summary.get("donor_target_weight_newly_mapped_pct")) - 11.82) > 0.001:
        blockers.append("newly mapped donor target weight mismatch")
    if abs(num(summary.get("donor_target_weight_still_unmapped_pct")) - 5.59) > 0.001:
        blockers.append("still-unmapped donor target weight mismatch")
    largest = summary.get("largest_remaining_unmapped_target") if isinstance(summary.get("largest_remaining_unmapped_target"), dict) else {}
    if largest.get("exposure_id") != "grid_power" or abs(num(largest.get("donor_target_weight_pct")) - 5.06) > 0.001:
        blockers.append("largest remaining unmapped target mismatch")

    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate prioritized UCITS mapping evidence")
    parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=Path("config/etf_eu_prioritized_ucits_mapping_evidence_20260728.yml"),
    )
    args = parser.parse_args()
    payload = load(args.path)
    blockers = validate(payload)
    print(json.dumps({
        "artifact_type": "etf_eu_prioritized_ucits_mapping_evidence_validation",
        "valid": not blockers,
        "blockers": blockers,
        "summary": payload.get("summary"),
    }, indent=2, ensure_ascii=False))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
