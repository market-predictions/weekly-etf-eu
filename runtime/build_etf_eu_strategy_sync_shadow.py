from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


ALLOWED_REASON_CODES = {
    "no_ucits_equivalent",
    "ucits_identity_unverified",
    "kid_missing",
    "trading_line_unverified",
    "pricing_missing_or_stale",
    "liquidity_below_threshold",
    "currency_policy_blocked",
    "product_type_blocked",
    "whole_share_rounding",
    "position_limit",
    "factor_overlap_limit",
    "turnover_guard",
    "cash_reserve",
    "existing_position_transition",
}


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"Required JSON input is missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"Required YAML input is missing: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _ticker(position: dict[str, Any]) -> str:
    return str(position.get("ticker") or position.get("exchange_ticker") or "").upper()


def _registry_index(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for fund in registry.get("funds") or []:
        if not isinstance(fund, dict):
            continue
        registry_id = str(fund.get("registry_id") or "").strip()
        if registry_id:
            result[registry_id] = fund
    return result


def _verified_lines(fund: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        line
        for line in (fund.get("trading_lines") or [])
        if isinstance(line, dict)
        and str(line.get("line_verification_status") or "").startswith("verified_ucits_trading_line")
    ]


def _fund_identity_status(fund: dict[str, Any] | None, fallback: str) -> tuple[str, list[str]]:
    if not fund:
        return "unmapped", [fallback if fallback in ALLOWED_REASON_CODES else "ucits_identity_unverified"]
    if str(fund.get("instrument_type") or "") != "UCITS ETF":
        return "policy_blocked", ["product_type_blocked"]
    isin = str(fund.get("isin") or "").strip().upper()
    if not isin or isin == "TBD":
        return "identity_unverified", ["ucits_identity_unverified"]
    if str(fund.get("ucits_status") or "") not in {"confirmed", "confirmed_by_fund_name"}:
        return "identity_unverified", ["ucits_identity_unverified"]
    if str(fund.get("priips_kid_status") or "") != "available":
        return "kid_missing", ["kid_missing"]
    if not _verified_lines(fund):
        return "trading_line_unverified", ["trading_line_unverified"]
    return "verified_product_line", []


def _position_matches_fund(position: dict[str, Any], fund: dict[str, Any]) -> bool:
    position_isin = str(position.get("isin") or "").upper()
    fund_isin = str(fund.get("isin") or "").upper()
    if position_isin and fund_isin and position_isin == fund_isin:
        return True
    line_tickers = {
        str(line.get("exchange_ticker") or "").upper()
        for line in fund.get("trading_lines") or []
        if isinstance(line, dict)
    }
    return bool(_ticker(position) and _ticker(position) in line_tickers)


def _candidate_summary(fund: dict[str, Any] | None) -> dict[str, Any] | None:
    if not fund:
        return None
    lines = [
        {
            "exchange": line.get("exchange"),
            "venue_code": line.get("venue_code"),
            "exchange_ticker": line.get("exchange_ticker"),
            "trading_currency": line.get("trading_currency"),
            "verification_status": line.get("line_verification_status"),
        }
        for line in (fund.get("trading_lines") or [])
        if isinstance(line, dict)
    ]
    return {
        "registry_id": fund.get("registry_id"),
        "fund_name": fund.get("fund_name"),
        "isin": fund.get("isin"),
        "instrument_type": fund.get("instrument_type"),
        "ucits_status": fund.get("ucits_status"),
        "priips_kid_status": fund.get("priips_kid_status"),
        "ter_pct": fund.get("ter_pct"),
        "trading_lines": lines,
    }


def _select_candidate(mapping: dict[str, Any], registry_by_id: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [item for item in (mapping.get("candidates") or []) if isinstance(item, dict)]
    candidates.sort(key=lambda item: item.get("preferred") is not True)
    for candidate in candidates:
        fund = registry_by_id.get(str(candidate.get("registry_id") or ""))
        if fund:
            return fund
    return None


def _action_candidate(promoted: bool, current_weight: float, status: str) -> str:
    if current_weight > 0:
        return "hold_and_reunderwrite" if promoted else "review_existing_position_opportunity_cost"
    if not promoted:
        return "watch_only"
    if status == "verified_product_line":
        return "prepare_separate_pricing_and_allocation_review"
    return "reserve_capacity_and_resolve_implementation"


def _alignment_action(current_weight: float, target_weight: float, identity_status: str) -> str:
    gap = target_weight - current_weight
    if abs(gap) <= 1.0:
        return "hold_near_target"
    if current_weight > 0 and gap > 0:
        return "increase_after_separate_authorization"
    if current_weight > 0 and gap < 0:
        return "reduce_after_separate_authorization"
    if target_weight > 0 and identity_status == "verified_product_line":
        return "prepare_new_position_review"
    if target_weight > 0:
        return "resolve_ucits_implementation_then_review"
    return "review_legacy_exposure_exit_or_retention"


def build_sync_shadow(
    shared_state: dict[str, Any],
    shared_portfolio_target: dict[str, Any],
    portfolio: dict[str, Any],
    registry: dict[str, Any],
    mapping_config: dict[str, Any],
) -> dict[str, Any]:
    if shared_state.get("schema_version") != "etf_shared_strategy_state_v1":
        raise RuntimeError("Unsupported shared strategy state schema")
    if shared_portfolio_target.get("schema_version") != "etf_shared_portfolio_target_v1":
        raise RuntimeError("Unsupported shared portfolio target schema")
    if str(shared_state.get("source_run_id")) != str(shared_portfolio_target.get("source_run_id")):
        raise RuntimeError("Shared strategy and portfolio target run IDs differ")
    for artifact in (shared_state, shared_portfolio_target):
        authority = artifact.get("authority") if isinstance(artifact.get("authority"), dict) else {}
        if authority.get("portfolio_mutation") is not False or authority.get("execution_authority") is not False:
            raise RuntimeError("Donor artifact violates the non-execution boundary")

    registry_by_id = _registry_index(registry)
    exposure_mappings = mapping_config.get("exposures") if isinstance(mapping_config.get("exposures"), dict) else {}
    legacy_map = mapping_config.get("legacy_position_exposures") if isinstance(mapping_config.get("legacy_position_exposures"), dict) else {}
    positions = [item for item in (portfolio.get("positions") or []) if isinstance(item, dict)]

    rows: list[dict[str, Any]] = []
    promoted_rows: list[dict[str, Any]] = []
    matched_position_tickers: set[str] = set()
    ticker_to_shared_exposure: dict[str, str] = {}

    for lane in shared_state.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        exposure_id = str(lane.get("exposure_id") or "")
        mapping = exposure_mappings.get(exposure_id) if isinstance(exposure_mappings.get(exposure_id), dict) else {}
        fallback_reason = str(mapping.get("unresolved_reason_code") or "ucits_identity_unverified")
        fund = _select_candidate(mapping, registry_by_id)
        identity_status, reasons = _fund_identity_status(fund, fallback_reason)
        matched_positions = [position for position in positions if fund and _position_matches_fund(position, fund)]
        current_weight = round(sum(_num(position.get("current_weight_pct")) for position in matched_positions), 6)
        current_value = round(sum(_num(position.get("market_value_eur")) for position in matched_positions), 2)
        current_tickers: list[str] = []
        for position in matched_positions:
            ticker = _ticker(position)
            if ticker:
                current_tickers.append(ticker)
                matched_position_tickers.add(ticker)
                ticker_to_shared_exposure[ticker] = exposure_id

        if matched_positions:
            implementation_status = "funded_current_position"
            reasons = []
        elif identity_status == "verified_product_line":
            implementation_status = "mapped_pending_pricing_and_allocation"
            reasons = ["pricing_missing_or_stale"]
        else:
            implementation_status = identity_status

        promoted = lane.get("promoted") is True
        divergence = promoted and current_weight <= 0
        if divergence and not reasons:
            reasons = ["existing_position_transition"]
        reasons = [reason for reason in reasons if reason in ALLOWED_REASON_CODES]
        row = {
            "shared_rank": lane.get("rank"),
            "exposure_id": exposure_id,
            "lane_name": lane.get("lane_name"),
            "promoted": promoted,
            "shared_desired_direction": lane.get("desired_direction"),
            "shared_score": (lane.get("scores") or {}).get("donor_final_rank_score"),
            "shared_evidence_summary": lane.get("evidence_summary"),
            "shared_why_now": lane.get("why_now"),
            "portfolio_role": mapping.get("portfolio_role"),
            "preferred_ucits_candidate": _candidate_summary(fund),
            "implementation_status": implementation_status,
            "current_eu_tickers": sorted(set(current_tickers)),
            "current_eu_weight_pct": current_weight,
            "current_eu_market_value_eur": current_value,
            "action_candidate": _action_candidate(promoted, current_weight, identity_status),
            "divergence_from_promoted_exposure": divergence,
            "divergence_reason_codes": reasons,
            "mapping_note": mapping.get("mapping_note"),
            "research_required": mapping.get("research_required"),
            "portfolio_mutation": False,
            "allocation_authority": False,
        }
        rows.append(row)
        if promoted:
            promoted_rows.append(row)

    legacy_positions: list[dict[str, Any]] = []
    for position in positions:
        ticker = _ticker(position)
        if not ticker or ticker in matched_position_tickers:
            continue
        legacy_positions.append({
            "ticker": ticker,
            "isin": position.get("isin"),
            "fund_name": position.get("fund_name"),
            "current_weight_pct": _num(position.get("current_weight_pct")),
            "market_value_eur": _num(position.get("market_value_eur")),
            "legacy_exposure_id": legacy_map.get(ticker),
            "status": "existing_position_transition",
            "reason_codes": ["existing_position_transition"],
            "required_action": "reunderwrite_against_shared_portfolio_target",
        })

    actual_exposures: dict[str, dict[str, Any]] = defaultdict(lambda: {"weight_pct": 0.0, "market_value_eur": 0.0, "tickers": []})
    for position in positions:
        ticker = _ticker(position)
        exposure_id = ticker_to_shared_exposure.get(ticker) or legacy_map.get(ticker) or f"unmapped_current_{ticker.lower()}"
        actual_exposures[exposure_id]["weight_pct"] += _num(position.get("current_weight_pct"))
        actual_exposures[exposure_id]["market_value_eur"] += _num(position.get("market_value_eur"))
        actual_exposures[exposure_id]["tickers"].append(ticker)

    alignment_rows: list[dict[str, Any]] = []
    donor_target_ids: set[str] = set()
    represented_target_weight = 0.0
    donor_invested_target_weight = 0.0
    for target in shared_portfolio_target.get("exposure_targets") or []:
        if not isinstance(target, dict):
            continue
        exposure_id = str(target.get("exposure_id") or "")
        donor_target_ids.add(exposure_id)
        target_weight = _num(target.get("target_weight_pct"))
        donor_invested_target_weight += target_weight
        actual = actual_exposures.get(exposure_id, {"weight_pct": 0.0, "market_value_eur": 0.0, "tickers": []})
        current_weight = _num(actual.get("weight_pct"))
        represented_target_weight += min(max(current_weight, 0.0), max(target_weight, 0.0))
        gap = round(current_weight - target_weight, 6)
        mapping = exposure_mappings.get(exposure_id) if isinstance(exposure_mappings.get(exposure_id), dict) else {}
        fallback_reason = str(mapping.get("unresolved_reason_code") or "ucits_identity_unverified")
        fund = _select_candidate(mapping, registry_by_id)
        identity_status, reasons = _fund_identity_status(fund, fallback_reason)
        if abs(gap) <= 1.0:
            status = "aligned_within_one_percentage_point"
            reasons = []
        elif current_weight > 0:
            status = "partially_aligned_weight_gap"
            reasons = ["existing_position_transition"]
        else:
            status = "missing_donor_target_exposure"
            if not reasons:
                reasons = ["pricing_missing_or_stale" if identity_status == "verified_product_line" else "existing_position_transition"]
        alignment_rows.append({
            "exposure_id": exposure_id,
            "lane_name": target.get("lane_name"),
            "donor_source_tickers": list(target.get("source_tickers") or []),
            "donor_actions": list(target.get("actions") or []),
            "donor_current_weight_pct": _num(target.get("current_weight_pct")),
            "donor_target_weight_pct": target_weight,
            "eu_current_tickers": sorted(set(actual.get("tickers") or [])),
            "eu_current_weight_pct": round(current_weight, 6),
            "weight_gap_eu_minus_donor_pct": gap,
            "preferred_ucits_candidate": _candidate_summary(fund),
            "implementation_status": identity_status,
            "alignment_status": status,
            "alignment_action": _alignment_action(current_weight, target_weight, identity_status),
            "divergence_reason_codes": [reason for reason in reasons if reason in ALLOWED_REASON_CODES],
            "portfolio_mutation": False,
            "allocation_authority": False,
        })

    for exposure_id, actual in actual_exposures.items():
        if exposure_id in donor_target_ids:
            continue
        alignment_rows.append({
            "exposure_id": exposure_id,
            "lane_name": None,
            "donor_source_tickers": [],
            "donor_actions": [],
            "donor_current_weight_pct": 0.0,
            "donor_target_weight_pct": 0.0,
            "eu_current_tickers": sorted(set(actual.get("tickers") or [])),
            "eu_current_weight_pct": round(_num(actual.get("weight_pct")), 6),
            "weight_gap_eu_minus_donor_pct": round(_num(actual.get("weight_pct")), 6),
            "preferred_ucits_candidate": None,
            "implementation_status": "eu_legacy_exposure_not_in_donor_target",
            "alignment_status": "eu_only_legacy_exposure",
            "alignment_action": "review_legacy_exposure_exit_or_retention",
            "divergence_reason_codes": ["existing_position_transition"],
            "portfolio_mutation": False,
            "allocation_authority": False,
        })

    donor_cash_weight = _num((shared_portfolio_target.get("portfolio_summary") or {}).get("cash_weight_pct"))
    eu_nav = _num(portfolio.get("nav_eur"))
    eu_cash_weight = (_num(portfolio.get("cash_eur")) / eu_nav * 100.0) if eu_nav else 0.0
    alignment_rows.append({
        "exposure_id": "cash",
        "lane_name": "Cash",
        "donor_source_tickers": ["CASH"],
        "donor_actions": ["retain_cash"],
        "donor_current_weight_pct": donor_cash_weight,
        "donor_target_weight_pct": donor_cash_weight,
        "eu_current_tickers": ["CASH"],
        "eu_current_weight_pct": round(eu_cash_weight, 6),
        "weight_gap_eu_minus_donor_pct": round(eu_cash_weight - donor_cash_weight, 6),
        "preferred_ucits_candidate": None,
        "implementation_status": "cash",
        "alignment_status": "aligned_within_one_percentage_point" if abs(eu_cash_weight - donor_cash_weight) <= 1.0 else "cash_weight_divergence",
        "alignment_action": "hold_near_target" if abs(eu_cash_weight - donor_cash_weight) <= 1.0 else "allocate_only_after_separate_transition_authorization",
        "divergence_reason_codes": [] if abs(eu_cash_weight - donor_cash_weight) <= 1.0 else ["cash_reserve", "existing_position_transition"],
        "portfolio_mutation": False,
        "allocation_authority": False,
    })
    alignment_rows.sort(key=lambda row: (-_num(row.get("donor_target_weight_pct")), str(row.get("exposure_id"))))

    unexplained_promoted = [row["exposure_id"] for row in promoted_rows if row["divergence_from_promoted_exposure"] and not row["divergence_reason_codes"]]
    invalid_reasons = sorted({reason for row in rows + alignment_rows for reason in row.get("divergence_reason_codes", []) if reason not in ALLOWED_REASON_CODES})
    portfolio_unexplained = [row["exposure_id"] for row in alignment_rows if row["alignment_status"] != "aligned_within_one_percentage_point" and not row["divergence_reason_codes"]]
    coverage_pct = round(represented_target_weight / donor_invested_target_weight * 100.0, 4) if donor_invested_target_weight else 0.0

    return {
        "schema_version": "etf_eu_strategy_sync_shadow_v2",
        "artifact_type": "etf_eu_strategy_synchronization_shadow",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "authority": {
            "shadow_only": True,
            "portfolio_mutation": False,
            "funding_authority": False,
            "execution_authority": False,
            "production_delivery_authority": False,
        },
        "shared_strategy": {
            "source_repository": shared_state.get("source_repository"),
            "source_run_id": shared_state.get("source_run_id"),
            "report_date": shared_state.get("report_date"),
            "requested_close_date": shared_state.get("requested_close_date"),
            "regime": shared_state.get("regime"),
            "lane_count": len(shared_state.get("lanes") or []),
            "promoted_count": len(shared_state.get("promoted_exposures") or []),
        },
        "shared_portfolio_target": {
            "source_repository": shared_portfolio_target.get("source_repository"),
            "source_run_id": shared_portfolio_target.get("source_run_id"),
            "report_date": shared_portfolio_target.get("report_date"),
            "portfolio_summary": shared_portfolio_target.get("portfolio_summary"),
            "constraints": shared_portfolio_target.get("constraints"),
            "exposure_target_count": len(shared_portfolio_target.get("exposure_targets") or []),
        },
        "eu_portfolio": {
            "portfolio_mode": portfolio.get("portfolio_mode"),
            "base_currency": portfolio.get("base_currency"),
            "starting_capital_eur": portfolio.get("starting_capital_eur"),
            "cash_eur": portfolio.get("cash_eur"),
            "cash_weight_pct": round(eu_cash_weight, 6),
            "invested_market_value_eur": portfolio.get("invested_market_value_eur"),
            "nav_eur": portfolio.get("nav_eur"),
            "position_count": len(positions),
            "last_valuation_report_date": portfolio.get("last_valuation_report_date"),
        },
        "exposure_rows": rows,
        "promoted_exposure_comparison": promoted_rows,
        "portfolio_alignment_rows": alignment_rows,
        "portfolio_alignment_summary": {
            "donor_invested_target_weight_pct": round(donor_invested_target_weight, 6),
            "donor_target_weight_represented_in_eu_pct": round(represented_target_weight, 6),
            "exact_exposure_coverage_pct_of_donor_invested_target": coverage_pct,
            "aligned_row_count": sum(1 for row in alignment_rows if row["alignment_status"] == "aligned_within_one_percentage_point"),
            "divergent_row_count": sum(1 for row in alignment_rows if row["alignment_status"] != "aligned_within_one_percentage_point"),
        },
        "legacy_current_positions": legacy_positions,
        "allowed_divergence_reason_codes": sorted(ALLOWED_REASON_CODES),
        "validation": {
            "shared_promoted_count": len(promoted_rows),
            "promoted_divergence_count": sum(1 for row in promoted_rows if row["divergence_from_promoted_exposure"]),
            "promoted_with_explained_divergence": sum(1 for row in promoted_rows if row["divergence_from_promoted_exposure"] and row["divergence_reason_codes"]),
            "unexplained_promoted_divergences": unexplained_promoted,
            "portfolio_target_exposure_count": len(shared_portfolio_target.get("exposure_targets") or []),
            "portfolio_alignment_row_count": len(alignment_rows),
            "unexplained_portfolio_divergences": portfolio_unexplained,
            "invalid_reason_codes": invalid_reasons,
            "legacy_position_count": len(legacy_positions),
            "portfolio_mutation": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build EU synchronization shadow from donor strategy and portfolio target")
    parser.add_argument("--shared-strategy-state", type=Path, required=True)
    parser.add_argument("--shared-portfolio-target", type=Path, required=True)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--registry", type=Path, default=Path("config/ucits_symbol_registry.yml"))
    parser.add_argument("--mapping", type=Path, default=Path("config/shared_exposure_ucits_map.yml"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    state = build_sync_shadow(
        shared_state=_load_json(args.shared_strategy_state),
        shared_portfolio_target=_load_json(args.shared_portfolio_target),
        portfolio=_load_json(args.portfolio_state),
        registry=_load_yaml(args.registry),
        mapping_config=_load_yaml(args.mapping),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
