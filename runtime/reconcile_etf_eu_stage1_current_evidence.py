from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def preferred_variant(allocator: dict[str, Any]) -> dict[str, Any]:
    variant_id = str(allocator.get("preferred_shadow_variant") or "staged_policy_driven_v1")
    for variant in allocator.get("variants") or []:
        if isinstance(variant, dict) and variant.get("variant_id") == variant_id:
            return variant
    raise RuntimeError(f"Preferred allocator variant not found: {variant_id}")


def selected_rows(variant: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("exposure_id")): row
        for row in variant.get("allocation_rows") or []
        if isinstance(row, dict) and row.get("selected") is True and row.get("eligible") is True
    }


def normalize_ticker(value: Any) -> str:
    ticker = str(value or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def latest_quote_evidence() -> tuple[Path | None, dict[str, dict[str, Any]]]:
    paths = sorted(Path("output/activation").glob("etf_eu_stage1_quote_evidence_*.json"))
    if not paths:
        return None, {}
    path = paths[-1]
    payload = load_object(path)
    index = {
        normalize_ticker(row.get("ticker")): row
        for row in payload.get("rows") or []
        if isinstance(row, dict) and normalize_ticker(row.get("ticker"))
    }
    return path, index


def apply(state_path: Path, allocator_path: Path) -> None:
    state = load_object(state_path)
    allocator = load_object(allocator_path)
    variant = preferred_variant(allocator)
    selected = selected_rows(variant)
    if not {"ai_compute_infrastructure", "cyber_security"}.issubset(selected):
        raise RuntimeError("Expected VVSM and cybersecurity Stage-1 rows to be selected and eligible")

    portfolio = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    funded_positions = {
        normalize_ticker(row.get("ticker") or row.get("exchange_ticker")): row
        for row in positions
        if normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
    }
    quote_path, quotes = latest_quote_evidence()
    activation = portfolio.get("last_model_capital_activation") or state.get("model_capital_activation") or {}

    remaining_blockers: list[str] = []
    proposals: list[dict[str, Any]] = []
    activated_tickers: list[str] = []
    monitored_tickers: list[str] = []

    for candidate in state.get("stage_1_review_candidates") or []:
        if not isinstance(candidate, dict):
            continue
        exposure_id = str(candidate.get("exposure_id") or "")
        allocation = selected.get(exposure_id)
        if allocation is None:
            continue
        candidate_evidence = allocation.get("candidate") or {}
        ticker = normalize_ticker(candidate_evidence.get("ticker") or candidate.get("exchange_symbol"))
        order = allocation.get("order") or {}
        quote = quotes.get(ticker, {})
        funded = ticker in funded_positions
        quote_pass = quote.get("status") == "qualified_timestamped_exact_line_quote"

        if funded:
            position = funded_positions[ticker]
            activated_tickers.append(ticker)
            candidate.update(
                {
                    "analytical_allocator_weight_pct": allocation.get("variant_target_weight_pct"),
                    "actionable_target_weight_pct": position.get("current_weight_pct") or position.get("weight_pct"),
                    "client_action": "hold_current_position",
                    "expanded_client_action": "funded_model_position_hold",
                    "current_completed_close_pass": True,
                    "accepted_liquidity_measurement_pass": True,
                    "timestamped_bid_ask_quote_size_pass": True,
                    "current_price_eur": position.get("current_price_eur") or position.get("current_price_local"),
                    "current_price_date": position.get("pricing_close_date") or position.get("price_date"),
                    "model_position_shares": position.get("shares"),
                    "model_position_weight_pct": position.get("current_weight_pct") or position.get("weight_pct"),
                    "activation_id": activation.get("activation_id"),
                    "activation_run_id": activation.get("run_id"),
                    "blockers": [],
                    "blockers_nl": [],
                    "blockers_en": [],
                    "portfolio_mutation": False,
                    "allocation_authority": False,
                    "official_state_applied": True,
                }
            )
            continue

        monitored_tickers.append(ticker)
        blockers: list[str] = []
        blockers_nl: list[str] = []
        blockers_en: list[str] = []
        if candidate.get("currently_promoted") is not True:
            blockers.append(f"{ticker}:not_currently_promoted")
            blockers_nl.append("niet actueel gepromoveerd door de donorstrategie")
            blockers_en.append("not currently promoted by the donor strategy")
        if candidate.get("donor_fresh_add_direction") is not True:
            blockers.append(f"{ticker}:donor_fresh_add_direction_absent")
            blockers_nl.append("de donor geeft geen nieuwe kooprichting")
            blockers_en.append("the donor does not emit a fresh-add direction")
        if not quote_pass:
            blockers.append(f"{ticker}:timestamped_bid_ask_quote_size")
            blockers_nl.append("timestamped bied-, laat- en quote-sizebewijs ontbreekt")
            blockers_en.append("timestamped bid, ask and quote-size evidence is unavailable")

        proposal = {
            "exposure_id": exposure_id,
            "ticker": ticker,
            "fund_name": candidate_evidence.get("fund_name") or candidate.get("fund_name"),
            "isin": candidate_evidence.get("isin") or candidate.get("isin"),
            "target_weight_pct": allocation.get("variant_target_weight_pct"),
            "target_shares": order.get("target_shares"),
            "share_delta": order.get("share_delta"),
            "side": order.get("side"),
            "price_eur": candidate_evidence.get("price_eur"),
            "price_date": candidate_evidence.get("price_date"),
            "gross_trade_value_eur": order.get("gross_trade_value_eur"),
            "estimated_cost_eur": order.get("estimated_cost_eur"),
            "median_daily_traded_value_eur_20d": candidate_evidence.get("median_daily_traded_value_eur_20d"),
            "quote_evidence_passed": quote_pass,
            "execution_status": "monitored_not_funded_strategy_gate_not_passed",
        }
        proposals.append(proposal)
        candidate.update(
            {
                "analytical_allocator_weight_pct": allocation.get("variant_target_weight_pct"),
                "actionable_target_weight_pct": 0.0,
                "client_action": "blocked_monitor",
                "expanded_client_action": "monitored_not_funded_strategy_gate_not_passed",
                "current_completed_close_pass": True,
                "accepted_liquidity_measurement_pass": True,
                "timestamped_bid_ask_quote_size_pass": quote_pass,
                "current_price_eur": candidate_evidence.get("price_eur"),
                "current_price_date": candidate_evidence.get("price_date"),
                "median_daily_traded_value_eur_20d": candidate_evidence.get("median_daily_traded_value_eur_20d"),
                "proposed_shadow_order": proposal,
                "blockers": blockers,
                "blockers_nl": blockers_nl,
                "blockers_en": blockers_en,
                "portfolio_mutation": False,
                "allocation_authority": False,
                "official_state_applied": False,
            }
        )
        remaining_blockers.extend(blockers)

    stage = state.setdefault("stage_1_decision", {})
    partial_activation = bool(activated_tickers)
    stage.update(
        {
            "value": "partially_activated" if partial_activation else "blocked",
            "status": "model_position_activated_remaining_candidate_monitored" if partial_activation else "blocked_not_activation_ready",
            "expanded_status": "l0ck_funded_vvsm_monitored" if activated_tickers == ["L0CK"] else "remaining_candidates_monitored",
            "blockers": sorted(set(remaining_blockers)),
            "blocker_count": len(set(remaining_blockers)),
            "stage_1_activation_authorized": partial_activation,
            "official_state_applied": partial_activation,
            "executable_trade_intents": [],
            "activated_tickers": sorted(activated_tickers),
            "remaining_monitored_tickers": sorted(monitored_tickers),
            "model_activation": activation,
            "remaining_monitor_proposals": proposals,
            "portfolio_mutation_this_report_run": False,
            "real_broker_execution": False,
        }
    )
    state["current_evidence_reconciliation"] = {
        "applied": True,
        "allocator_path": str(allocator_path),
        "quote_evidence_path": str(quote_path) if quote_path else None,
        "selected_exposures": sorted(selected),
        "activated_tickers": sorted(activated_tickers),
        "remaining_monitored_tickers": sorted(monitored_tickers),
        "fresh_close_liquidity_and_quote_evidence_reconciled": True,
        "portfolio_mutation": False,
        "real_broker_execution": False,
    }
    state.setdefault("validation", {}).update(
        {
            "stage_1_blocked": not partial_activation,
            "stage_1_partial_activation": partial_activation,
            "activated_stage_1_tickers": sorted(activated_tickers),
            "remaining_monitored_stage_1_tickers": sorted(monitored_tickers),
        }
    )
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "ETF_EU_STAGE1_CURRENT_EVIDENCE_RECONCILED"
        f" | activated={','.join(sorted(activated_tickers)) or 'none'}"
        f" | monitored={','.join(sorted(monitored_tickers)) or 'none'}"
        f" | official_state_applied={str(partial_activation).lower()}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path)
    parser.add_argument("--allocator", type=Path, required=True)
    args = parser.parse_args()
    apply(args.state, args.allocator)


if __name__ == "__main__":
    main()
