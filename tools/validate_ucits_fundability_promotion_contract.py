from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("PyYAML is required for UCITS fundability validation") from exc

PLACEHOLDER_VALUES = {"", "TBD", "pending_verification", "primary_line_pending_verification"}
REQUIRED_GATES = {
    "instrument_identity",
    "eu_investability",
    "trading_line",
    "pricing_quality",
    "tradability_liquidity",
    "portfolio_role",
    "decision",
}
ALLOWED_GATE_ROW_STATUSES = {"not_fundable_blocked", "gate_passed_no_promotion"}


def _as_str(value: Any) -> str:
    return str(value if value is not None else "").strip()


def _is_placeholder(value: Any) -> bool:
    return _as_str(value) in PLACEHOLDER_VALUES


def _funds(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return list(payload.get("funds") or [])


def _has_verified_trading_line(fund: dict[str, Any]) -> bool:
    for line in fund.get("trading_lines") or []:
        if not _is_placeholder(line.get("exchange")) and not _is_placeholder(line.get("exchange_ticker")) and not _is_placeholder(line.get("trading_currency")) and not _is_placeholder(line.get("pricing_symbol_yahoo")):
            return True
    return False


def validate_registry(path: Path) -> None:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    errors: list[str] = []
    fundable_count = 0

    for fund in _funds(payload):
        registry_id = _as_str(fund.get("registry_id")) or "unknown"
        fundable_status = _as_str(fund.get("fundable_status"))
        investability_status = _as_str(fund.get("investability_status"))
        instrument_type = _as_str(fund.get("instrument_type"))
        ucits_status = _as_str(fund.get("ucits_status"))
        kid_status = _as_str(fund.get("priips_kid_status"))
        us_proxy = _as_str(fund.get("us_research_proxy"))

        if fundable_status == "fundable":
            fundable_count += 1
            if investability_status != "fundable":
                errors.append(f"{registry_id}:fundable_status_requires_investability_status_fundable")
            if instrument_type != "ETF":
                errors.append(f"{registry_id}:fundable_status_requires_etf_under_current_ucits_policy")
            if "confirmed" not in ucits_status:
                errors.append(f"{registry_id}:fundable_status_requires_confirmed_ucits_status")
            if kid_status != "available":
                errors.append(f"{registry_id}:fundable_status_requires_kid_available")
            if not _has_verified_trading_line(fund):
                errors.append(f"{registry_id}:fundable_status_requires_verified_trading_line")
            if us_proxy and us_proxy != "TBD":
                pass

        if instrument_type == "ETC" and "fundable" in fundable_status and "not_fundable" not in fundable_status:
            errors.append(f"{registry_id}:etc_must_not_be_fundable_under_current_ucits_only_policy")
        if investability_status == "verified_candidate_not_funded" and fundable_status == "fundable":
            errors.append(f"{registry_id}:verified_candidate_not_funded_must_not_be_auto_promoted")

    if fundable_count:
        errors.append("current_bootstrap_registry_must_not_have_fundable_candidates_without_separate_decision")
    if errors:
        raise RuntimeError("UCITS fundability promotion validation failed: " + "; ".join(errors))
    print(f"UCITS_FUNDABILITY_PROMOTION_CONTRACT_OK | registry={path} | fundable_candidates=0")


def validate_gate_artifact(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []

    if payload.get("schema_version") != "ucits_fundability_gate_v1":
        errors.append("schema_version_must_be_ucits_fundability_gate_v1")
    for field in ["funding_authority", "portfolio_mutation", "production_delivery", "candidate_promotion"]:
        if payload.get(field) is not False:
            errors.append(f"top_level_{field}_must_be_false")
    if set(payload.get("required_gates") or []) != REQUIRED_GATES:
        errors.append("required_gates_must_match_contract")

    rows = payload.get("rows") or []
    if not isinstance(rows, list) or not rows:
        errors.append("at_least_one_fundability_gate_row_required")
        rows = []

    gate_passed_count = 0
    not_fundable_count = 0
    for idx, row in enumerate(rows):
        registry_id = _as_str(row.get("registry_id")) or f"row_{idx}"
        label = f"row:{idx}:{registry_id}"
        status = row.get("fundability_gate_status")
        if status not in ALLOWED_GATE_ROW_STATUSES:
            errors.append(f"{label}:unexpected_fundability_gate_status:{status}")
        if status == "gate_passed_no_promotion":
            gate_passed_count += 1
        if status == "not_fundable_blocked":
            not_fundable_count += 1
        for field in ["funding_authority", "portfolio_mutation", "production_delivery", "candidate_promotion"]:
            if row.get(field) is not False:
                errors.append(f"{label}:{field}_must_be_false")
        gates = row.get("gates") or {}
        if set(gates) != REQUIRED_GATES:
            errors.append(f"{label}:gates_must_match_required_contract")
        for gate_name, gate in gates.items():
            gate_status = gate.get("status")
            blockers = gate.get("blockers")
            if gate_status not in {"passed", "blocked"}:
                errors.append(f"{label}:{gate_name}:unexpected_gate_status:{gate_status}")
            if not isinstance(blockers, list):
                errors.append(f"{label}:{gate_name}:blockers_must_be_list")
            elif gate_status == "blocked" and not blockers:
                errors.append(f"{label}:{gate_name}:blocked_gate_requires_blockers")
            elif gate_status == "passed" and blockers:
                errors.append(f"{label}:{gate_name}:passed_gate_must_not_have_blockers")
        gate_blockers = row.get("gate_blockers") or []
        if status == "not_fundable_blocked" and not gate_blockers:
            errors.append(f"{label}:not_fundable_blocked_requires_gate_blockers")
        if status == "gate_passed_no_promotion" and gate_blockers:
            errors.append(f"{label}:gate_passed_no_promotion_must_not_have_gate_blockers")

    if payload.get("candidate_count") != len(rows):
        errors.append(f"candidate_count_mismatch:declared={payload.get('candidate_count')}:actual={len(rows)}")
    if payload.get("gate_passed_no_promotion_count") != gate_passed_count:
        errors.append("gate_passed_no_promotion_count_mismatch")
    if payload.get("not_fundable_count") != not_fundable_count:
        errors.append("not_fundable_count_mismatch")
    if errors:
        raise RuntimeError("UCITS fundability gate artifact validation failed: " + "; ".join(errors))
    print("UCITS_FUNDABILITY_GATE_ARTIFACT_OK" f" | artifact={path}" f" | candidates={len(rows)}" f" | not_fundable={not_fundable_count}" " | candidate_promotion=false" " | portfolio_mutation=false" " | delivery=false")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="config/ucits_symbol_registry.yml")
    parser.add_argument("--artifact", default=None)
    args = parser.parse_args()
    validate_registry(Path(args.registry))
    if args.artifact:
        validate_gate_artifact(Path(args.artifact))


if __name__ == "__main__":
    main()
