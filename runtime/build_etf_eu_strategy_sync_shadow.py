from __future__ import annotations

import argparse
import json
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
    lines = []
    for line in fund.get("trading_lines") or []:
        if not isinstance(line, dict):
            continue
        if str(line.get("line_verification_status") or "").startswith("verified_ucits_trading_line"):
            lines.append(line)
    return lines


def _fund_identity_status(fund: dict[str, Any] | None, fallback: str) -> tuple[str, list[str]]:
    if not fund:
        return "unmapped", [fallback if fallback in ALLOWED_REASON_CODES else "ucits_identity_unverified"]
    instrument_type = str(fund.get("instrument_type") or "")
    if instrument_type != "UCITS ETF":
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
    ticker = str(position.get("ticker") or position.get("exchange_ticker") or "").upper()
    line_tickers = {
        str(line.get("exchange_ticker") or "").upper()
        for line in fund.get("trading_lines") or []
        if isinstance(line, dict)
    }
    return bool(ticker and ticker in line_tickers)


def _candidate_summary(fund: dict[str, Any] | None) -> dict[str, Any] | None:
    if not fund:
        return None
    lines = []
    for line in fund.get("trading_lines") or []:
        if isinstance(line, dict):
            lines.append(
                {
                    "exchange": line.get("exchange"),
                    "venue_code": line.get("venue_code"),
                    "exchange_ticker": line.get("exchange_ticker"),
                    "trading_currency": line.get("trading_currency"),
                    "verification_status": line.get("line_verification_status"),
                }
            )
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


def _action_candidate(shared_direction: str, promoted: bool, current_weight: float, status: str) -> str:
    if current_weight > 0:
        if promoted:
            return "hold_and_reunderwrite"
        return "review_existing_position_opportunity_cost"
    if not promoted:
        return "watch_only"
    if status == "verified_product_line":
        return "prepare_separate_pricing_and_allocation_review"
    return "reserve_capacity_and_resolve_implementation"


def build_sync_shadow(
    shared_state: dict[str, Any],
    portfolio: dict[str, Any],
    registry: dict[str, Any],
    mapping_config: dict[str, Any],
) -> dict[str, Any]:
    if shared_state.get("schema_version") != "etf_shared_strategy_state_v1":
        raise RuntimeError("Unsupported shared strategy state schema")
    shared_authority = shared_state.get("authority") if isinstance(shared_state.get("authority"), dict) else {}
    if shared_authority.get("portfolio_mutation") is not False or shared_authority.get("execution_authority") is not False:
        raise RuntimeError("Shared strategy state violates the non-execution boundary")

    registry_by_id = _registry_index(registry)
    exposure_mappings = mapping_config.get("exposures") if isinstance(mapping_config.get("exposures"), dict) else {}
    legacy_map = mapping_config.get("legacy_position_exposures") if isinstance(mapping_config.get("legacy_position_exposures"), dict) else {}
    positions = [item for item in (portfolio.get("positions") or []) if isinstance(item, dict)]

    rows: list[dict[str, Any]] = []
    promoted_rows: list[dict[str, Any]] = []
    matched_position_tickers: set[str] = set()

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
        current_tickers = []
        for position in matched_positions:
            ticker = str(position.get("ticker") or position.get("exchange_ticker") or "").upper()
            if ticker:
                current_tickers.append(ticker)
                matched_position_tickers.add(ticker)

        if matched_positions:
            implementation_status = "funded_current_position"
            reasons = []
        elif identity_status == "verified_product_line":
            implementation_status = "mapped_pending_pricing_and_allocation"
            reasons = ["pricing_missing_or_stale"]
        else:
            implementation_status = identity_status

        promoted = lane.get("promoted") is True
        action = _action_candidate(str(lane.get("desired_direction") or "watch"), promoted, current_weight, identity_status)
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
            "action_candidate": action,
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

    legacy_positions = []
    for position in positions:
        ticker = str(position.get("ticker") or position.get("exchange_ticker") or "").upper()
        if not ticker or ticker in matched_position_tickers:
            continue
        legacy_positions.append(
            {
                "ticker": ticker,
                "isin": position.get("isin"),
                "fund_name": position.get("fund_name"),
                "current_weight_pct": _num(position.get("current_weight_pct")),
                "market_value_eur": _num(position.get("market_value_eur")),
                "legacy_exposure_id": legacy_map.get(ticker),
                "status": "existing_position_transition",
                "reason_codes": ["existing_position_transition"],
                "required_action": "reunderwrite_against_shared_promoted_exposures",
            }
        )

    unexplained = [
        row["exposure_id"]
        for row in promoted_rows
        if row["divergence_from_promoted_exposure"] and not row["divergence_reason_codes"]
    ]
    invalid_reasons = sorted(
        {
            reason
            for row in rows
            for reason in row["divergence_reason_codes"]
            if reason not in ALLOWED_REASON_CODES
        }
    )

    return {
        "schema_version": "etf_eu_strategy_sync_shadow_v1",
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
        "eu_portfolio": {
            "portfolio_mode": portfolio.get("portfolio_mode"),
            "base_currency": portfolio.get("base_currency"),
            "starting_capital_eur": portfolio.get("starting_capital_eur"),
            "cash_eur": portfolio.get("cash_eur"),
            "invested_market_value_eur": portfolio.get("invested_market_value_eur"),
            "nav_eur": portfolio.get("nav_eur"),
            "position_count": len(positions),
            "last_valuation_report_date": portfolio.get("last_valuation_report_date"),
        },
        "exposure_rows": rows,
        "promoted_exposure_comparison": promoted_rows,
        "legacy_current_positions": legacy_positions,
        "allowed_divergence_reason_codes": sorted(ALLOWED_REASON_CODES),
        "validation": {
            "shared_promoted_count": len(promoted_rows),
            "promoted_divergence_count": sum(1 for row in promoted_rows if row["divergence_from_promoted_exposure"]),
            "promoted_with_explained_divergence": sum(
                1 for row in promoted_rows if row["divergence_from_promoted_exposure"] and row["divergence_reason_codes"]
            ),
            "unexplained_promoted_divergences": unexplained,
            "invalid_reason_codes": invalid_reasons,
            "legacy_position_count": len(legacy_positions),
            "portfolio_mutation": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build EU synchronization shadow state from donor strategy state")
    parser.add_argument("--shared-strategy-state", type=Path, required=True)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--registry", type=Path, default=Path("config/ucits_symbol_registry.yml"))
    parser.add_argument("--mapping", type=Path, default=Path("config/shared_exposure_ucits_map.yml"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    state = build_sync_shadow(
        shared_state=_load_json(args.shared_strategy_state),
        portfolio=_load_json(args.portfolio_state),
        registry=_load_yaml(args.registry),
        mapping_config=_load_yaml(args.mapping),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
