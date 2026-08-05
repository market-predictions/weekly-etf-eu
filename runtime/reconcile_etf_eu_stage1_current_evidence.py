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


def allocation_rows(variant: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("exposure_id")): row
        for row in variant.get("allocation_rows") or []
        if isinstance(row, dict) and row.get("exposure_id")
    }


def num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


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


def validate_allocator_state(rows: dict[str, dict[str, Any]]) -> None:
    ai = rows.get("ai_compute_infrastructure") or {}
    cyber = rows.get("cyber_security") or {}
    if ai.get("eligible") is not True or ai.get("selected") is not True:
        raise RuntimeError("VVSM must remain the selected eligible Stage-1 analytical candidate")
    if cyber.get("eligible") is not True:
        raise RuntimeError("Funded cybersecurity exposure must remain strategy-eligible")
    if cyber.get("selected") is True:
        raise RuntimeError("Funded cybersecurity exposure must not be selected as a new Stage-1 trade")
    cyber_order = cyber.get("order") if isinstance(cyber.get("order"), dict) else {}
    if num(cyber_order.get("share_delta")) != 0 or num(cyber_order.get("target_shares")) > 0:
        raise RuntimeError("Funded cybersecurity exposure received a duplicate order")


def apply(state_path: Path, allocator_path: Path) -> None:
    state = load_object(state_path)
    allocator = load_object(allocator_path)
    variant = preferred_variant(allocator)
    rows = allocation_rows(variant)
    validate_allocator_state(rows)

    portfolio = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    funded_positions = {
        normalize_ticker(row.get("ticker") or row.get("exchange_ticker")): row
        for row in positions
        if normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
    }
    if set(funded_positions) != {"VWCE", "EUNA", "SXR8", "L0CK"}:
        raise RuntimeError(f"Expected activated four-position model state; found {sorted(funded_positions)}")

    quote_path, quotes = latest_quote_evidence()
    activation = portfolio.get("last_model_capital_activation") or state.get("model_capital_activation") or {}
    if not activation.get("activation_id"):
        raise RuntimeError("L0CK activation provenance missing from convergence state")

    remaining_blockers: list[str] = []
    proposals: list[dict[str, Any]] = []
    activated_tickers: list[str] = []
    monitored_tickers: list[str] = []
    selected_exposures: list[str] = []
    eligible_exposures: list[str] = []

    for candidate in state.get("stage_1_review_candidates") or []:
        if not isinstance(candidate, dict):
            continue
        exposure_id = str(candidate.get("exposure_id") or "")
        allocation = rows.get(exposure_id)
        if allocation is None:
            raise RuntimeError(f"Stage-1 allocator row missing: {exposure_id}")
        if allocation.get("eligible") is True:
            eligible_exposures.append(exposure_id)
        if allocation.get("selected") is True:
            selected_exposures.append(exposure_id)

        candidate_evidence = allocation.get("candidate") if isinstance(allocation.get("candidate"), dict) else {}
        ticker = normalize_ticker(candidate_evidence.get("ticker") or candidate.get("exchange_symbol"))
        order = allocation.get("order") if isinstance(allocation.get("order"), dict) else {}
        quote = quotes.get(ticker, {})
        funded = ticker in funded_positions
        quote_pass = quote.get("status") == "qualified_timestamped_exact_line_quote"

        if funded:
            if ticker != "L0CK":
                raise RuntimeError(f"Unexpected funded Stage-1 candidate: {ticker}")
            if allocation.get("selected") is True or num(order.get("share_delta")) != 0:
                raise RuntimeError("Funded L0CK must be an incumbent hold with zero share delta")
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

        if ticker != "VVSM":
            raise RuntimeError(f"Unexpected unfunded Stage-1 candidate: {ticker}")
        if allocation.get("selected") is not True or allocation.get("eligible") is not True:
            raise RuntimeError("VVSM monitoring case must remain selected and eligible analytically")

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

    if set(activated_tickers) != {"L0CK"} or set(monitored_tickers) != {"VVSM"}:
        raise RuntimeError(
            f"Stage-1 reconciliation scope mismatch: activated={activated_tickers}, monitored={monitored_tickers}"
        )

    stage = state.setdefault("stage_1_decision", {})
    stage.update(
        {
            "value": "partially_activated",
            "status": "model_position_activated_remaining_candidate_monitored",
            "expanded_status": "l0ck_funded_vvsm_monitored",
            "blockers": sorted(set(remaining_blockers)),
            "blocker_count": len(set(remaining_blockers)),
            "stage_1_activation_authorized": True,
            "official_state_applied": True,
            "executable_trade_intents": [],
            "activated_tickers": ["L0CK"],
            "remaining_monitored_tickers": ["VVSM"],
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
        "selected_exposures": sorted(selected_exposures),
        "eligible_exposures": sorted(eligible_exposures),
        "activated_tickers": ["L0CK"],
        "remaining_monitored_tickers": ["VVSM"],
        "fresh_close_liquidity_and_quote_evidence_reconciled": True,
        "portfolio_mutation": False,
        "real_broker_execution": False,
    }
    state.setdefault("validation", {}).update(
        {
            "stage_1_blocked": False,
            "stage_1_partial_activation": True,
            "activated_stage_1_tickers": ["L0CK"],
            "remaining_monitored_stage_1_tickers": ["VVSM"],
        }
    )
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "ETF_EU_STAGE1_CURRENT_EVIDENCE_RECONCILED"
        " | activated=L0CK | monitored=VVSM | official_state_applied=true"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path)
    parser.add_argument("--allocator", type=Path, required=True)
    args = parser.parse_args()
    apply(args.state, args.allocator)


if __name__ == "__main__":
    main()
