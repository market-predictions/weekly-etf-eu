from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import yaml

from runtime.current.pricing import find_exact_price_row, load_pricing_artifact, verification_status

SCHEMA_VERSION = "etf_eu_current_normalized_state_v1"
_HISTORICAL_TARGET_FIELDS = ("strategic_target_weight_pct", "phase_target_weight_pct", "target_weight_pct", "weight_inherited_pct")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict): raise RuntimeError(f"Expected JSON object in {path}")
    return payload


def _load_registry(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict): raise RuntimeError(f"Expected registry mapping in {path}")
    return payload


def _registry_line(registry: dict[str, Any], position: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    isin = str(position.get("isin") or "").strip().upper()
    ticker = str(position.get("exchange_ticker") or position.get("ticker") or "").strip().upper()
    currency = str(position.get("trading_currency") or "").strip().upper()
    exchange = str(position.get("primary_exchange") or "").strip().lower()
    matches: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for fund in registry.get("funds") or []:
        if not isinstance(fund, dict) or str(fund.get("isin") or "").strip().upper() != isin: continue
        for line in fund.get("trading_lines") or []:
            if not isinstance(line, dict): continue
            if str(line.get("exchange_ticker") or "").strip().upper() != ticker: continue
            if str(line.get("trading_currency") or "").strip().upper() != currency: continue
            if exchange and str(line.get("exchange") or "").strip().lower() != exchange: continue
            matches.append((fund, line))
    if len(matches) != 1: raise RuntimeError(f"Exact identity binding failed for funded position {isin}/{ticker}/{currency}; matches={len(matches)}")
    return matches[0]


def build_normalized_state(*, portfolio_state_path: Path, pricing_artifact_path: Path, registry_path: Path, report_date: str, run_id: str) -> dict[str, Any]:
    protected, pricing, registry = _load_json(portfolio_state_path), load_pricing_artifact(pricing_artifact_path), _load_registry(registry_path)
    if str(pricing.get("report_date") or "") != report_date: raise RuntimeError(f"Pricing artifact report date mismatch: {pricing.get('report_date')} != {report_date}")
    if str(protected.get("base_currency") or "EUR").upper() != "EUR": raise RuntimeError("Thin current kernel currently requires EUR portfolio base currency")
    cash = float(protected.get("cash_eur") or 0)
    if cash < 0: raise RuntimeError("Protected cash cannot be negative")
    normalized_positions: list[dict[str, Any]] = []
    invested = 0.0
    for source_row in protected.get("positions") or []:
        if not isinstance(source_row, dict) or source_row.get("investability_status") != "funded_model_position": continue
        row = copy.deepcopy(source_row)
        trading_currency = str(row.get("trading_currency") or "EUR").upper()
        if trading_currency != "EUR":
            raise RuntimeError(f"FX valuation evidence is required before funding a non-EUR trading line: {_ticker_for_error(row)}/{trading_currency}")
        fund, line = _registry_line(registry, row)
        price_row = find_exact_price_row(pricing, isin=str(row.get("isin") or ""), ticker=str(row.get("exchange_ticker") or row.get("ticker") or ""), venue_code=str(line.get("venue_code") or ""), currency=trading_currency, report_date=report_date)
        shares = int(row.get("shares") or 0)
        if shares <= 0: raise RuntimeError(f"Funded position must use positive whole shares: {row.get('ticker')}")
        close = float(price_row["close_price"])
        market_value = round(shares * close, 2)
        invested += market_value
        avg_entry = float(row.get("avg_entry_local") or 0)
        cost_basis = shares * avg_entry if avg_entry > 0 else None
        pnl = round(market_value - cost_basis, 2) if cost_basis is not None else None
        pnl_pct = ((close / avg_entry) - 1.0) * 100.0 if avg_entry > 0 else None
        historical = {key: row.pop(key) for key in _HISTORICAL_TARGET_FIELDS if key in row and row.get(key) is not None}
        if historical:
            row["historical_allocation_metadata"] = historical
            row["historical_allocation_metadata_authority"] = "non_current_history_only"
        row.update({
            "registry_id": fund.get("registry_id"), "identity_binding": "isin_plus_exact_trading_line", "identity_binding_valid": True,
            "venue_code": line.get("venue_code"), "current_price_local": close, "market_value_local": market_value, "market_value_eur": market_value,
            "price_date": report_date, "pricing_completed_close": True, "pricing_status": "valuation_grade_exact_close",
            "verification_status": verification_status(price_row), "pricing_source": price_row.get("source_name") or price_row.get("source_id"),
            "pricing_source_quality": price_row.get("source_quality_status"), "pricing_agreeing_providers": list(price_row.get("agreeing_providers") or []),
            "portfolio_contribution_eur": pnl, "unrealized_pnl_eur": pnl, "unrealized_pnl_pct": round(pnl_pct, 6) if pnl_pct is not None else None,
            "valuation_source": "thin_current_kernel_exact_line_pricing", "source_run_id": run_id,
        })
        normalized_positions.append(row)
    invested = round(invested, 2); nav = round(cash + invested, 2)
    if nav <= 0: raise RuntimeError("Normalized portfolio NAV must be positive")
    for row in normalized_positions:
        row["current_weight_pct"] = round(100.0 * float(row["market_value_eur"]) / nav, 6)
        pnl = row.get("portfolio_contribution_eur")
        row["portfolio_contribution_pct_nav"] = round(100.0 * float(pnl) / nav, 6) if pnl is not None else None
    return {
        "schema_version": SCHEMA_VERSION, "artifact_type": "weekly_etf_eu_current_normalized_state", "run_id": run_id, "report_date": report_date,
        "state_valid": True, "blockers": [],
        "authority": {"portfolio_mutation": False, "trade_ledger_write": False, "real_broker_execution": False, "funding_authority": False, "delivery_authority": False},
        "sources": {"protected_portfolio_state": str(portfolio_state_path), "pricing_artifact": str(pricing_artifact_path), "identity_registry": str(registry_path)},
        "portfolio": {"base_currency": "EUR", "inception_date": protected.get("inception_date"), "cash_eur": cash, "invested_market_value_eur": invested, "nav_eur": nav, "position_count": len(normalized_positions), "positions": normalized_positions},
        "pricing_contract": {"pricing_authority_mode": "primary_exact_close_plus_optional_independent_verification", "exact_date_required": True, "identity_binding_required": True, "verifier_missing_does_not_invalidate_valid_primary": True, "same_date_disagreement_fails_closed": True, "source_artifact_gate_passed": True},
    }


def _ticker_for_error(row: dict[str, Any]) -> str:
    return str(row.get("exchange_ticker") or row.get("ticker") or "UNKNOWN").strip().upper()
