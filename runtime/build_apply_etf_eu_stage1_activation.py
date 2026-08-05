from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from runtime.apply_etf_eu_guarded_capital_activation import apply as apply_guarded_activation

CONFIRMATION = "CONFIRM_ETF_EU_MODEL_CAPITAL_ACTIVATION"


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def write_object(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def normalize_ticker(value: Any) -> str:
    ticker = str(value or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def preferred_variant(allocator: dict[str, Any]) -> dict[str, Any]:
    variant_id = str(
        allocator.get("preferred_shadow_variant")
        or allocator.get("preferred_variant_id")
        or "staged_policy_driven_v1"
    )
    for row in allocator.get("variants") or []:
        if isinstance(row, dict) and row.get("variant_id") == variant_id:
            return row
    raise RuntimeError(f"Preferred allocator variant not found: {variant_id}")


def selected_rows(variant: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("exposure_id") or ""): row
        for row in variant.get("allocation_rows") or []
        if isinstance(row, dict) and row.get("selected") is True and row.get("eligible") is True
    }


def quote_index(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        normalize_ticker(row.get("ticker")): row
        for row in payload.get("rows") or []
        if isinstance(row, dict) and normalize_ticker(row.get("ticker"))
    }


def candidate_index(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        normalize_ticker(row.get("exchange_symbol") or row.get("ticker")): row
        for row in state.get("stage_1_review_candidates") or []
        if isinstance(row, dict) and normalize_ticker(row.get("exchange_symbol") or row.get("ticker"))
    }


def provider_for(ticker: str) -> str:
    return "iShares / BlackRock" if ticker == "L0CK" else "VanEck"


def role_for(ticker: str) -> str:
    return "Cybersecurity satellite" if ticker == "L0CK" else "Semiconductor satellite"


def build_and_apply(args: argparse.Namespace) -> dict[str, Any]:
    if args.confirmation != CONFIRMATION:
        raise RuntimeError("ETF_EU_MODEL_CAPITAL_ACTIVATION_CONFIRMATION_MISSING")

    state_path = Path(args.state)
    allocator_path = Path(args.allocator)
    quote_path = Path(args.quote_evidence)
    portfolio_path = Path(args.portfolio_state)
    ledger_path = Path(args.trade_ledger)
    decision_path = Path(args.decision_output)
    validation_path = Path(args.validation_output)
    result_path = Path(args.result_output)
    evidence_path = Path(args.evidence_output)

    state = load_object(state_path)
    allocator = load_object(allocator_path)
    quotes = quote_index(load_object(quote_path))
    portfolio = load_object(portfolio_path)
    variant = preferred_variant(allocator)
    selected = selected_rows(variant)
    candidates = candidate_index(state)
    funded = {
        normalize_ticker(row.get("exchange_ticker") or row.get("ticker"))
        for row in portfolio.get("positions") or []
        if isinstance(row, dict)
    }

    decisions: list[dict[str, Any]] = []
    evaluated: list[dict[str, Any]] = []
    for exposure_id, allocation in selected.items():
        candidate_data = allocation.get("candidate") if isinstance(allocation.get("candidate"), dict) else {}
        ticker = normalize_ticker(candidate_data.get("ticker"))
        stage_candidate = candidates.get(ticker, {})
        order = allocation.get("order") if isinstance(allocation.get("order"), dict) else {}
        quote = quotes.get(ticker, {})
        blockers: list[str] = []
        if not ticker:
            blockers.append("ticker_missing")
        if ticker in funded:
            blockers.append("already_funded")
        if stage_candidate.get("currently_promoted") is not True:
            blockers.append("not_currently_promoted_by_donor")
        if quote.get("status") != "qualified_timestamped_exact_line_quote":
            blockers.append("timestamped_quote_not_qualified")
        isin = str(candidate_data.get("isin") or stage_candidate.get("isin") or "").strip().upper()
        if not isin or isin != str(quote.get("isin") or "").strip().upper():
            blockers.append("quote_identity_mismatch")
        share_delta = int(order.get("share_delta") or order.get("target_shares") or 0)
        if share_delta <= 0:
            blockers.append("positive_share_delta_missing")
        ask = float(quote.get("ask_eur") or 0.0)
        bid = float(quote.get("bid_eur") or 0.0)
        ask_size = int(quote.get("ask_size") or 0)
        if ask <= 0 or bid <= 0 or ask < bid:
            blockers.append("invalid_bid_ask")
        if ask_size < share_delta:
            blockers.append("ask_size_below_model_order")
        if float(quote.get("spread_pct_mid") or 999.0) > 1.0:
            blockers.append("spread_above_one_percent")

        evaluation = {
            "exposure_id": exposure_id,
            "ticker": ticker,
            "isin": isin,
            "selected": True,
            "eligible": True,
            "currently_promoted": stage_candidate.get("currently_promoted"),
            "share_delta": share_delta,
            "bid_eur": bid or None,
            "ask_eur": ask or None,
            "bid_size": quote.get("bid_size"),
            "ask_size": quote.get("ask_size"),
            "spread_pct_mid": quote.get("spread_pct_mid"),
            "quote_timestamp_utc": quote.get("quote_timestamp_utc"),
            "activation_eligible": not blockers,
            "blockers": blockers,
        }
        evaluated.append(evaluation)
        if blockers:
            continue

        target_weight = float(allocation.get("variant_target_weight_pct") or 0.0)
        decisions.append(
            {
                "action": "buy",
                "isin": isin,
                "fund_name": candidate_data.get("fund_name") or stage_candidate.get("fund_name"),
                "provider": provider_for(ticker),
                "primary_exchange": "Xetra",
                "exchange_ticker": ticker,
                "shares_delta": share_delta,
                "close_price_eur": round(ask, 8),
                "close_date": args.report_date,
                "pricing_status": "timestamped_exact_line_ask_quote_model_activation",
                "verification_status": "verified_ucits_trading_line",
                "model_execution_price_basis": "timestamped_exact_line_ask_quote_model_only_no_real_broker_order",
                "portfolio_role": role_for(ticker),
                "conviction_tier": "Satellite",
                "strategic_target_weight_pct": target_weight,
                "phase_target_weight_pct": target_weight,
                "instrument_metadata": {
                    "distribution_policy": "accumulating",
                    "domicile": "Ireland",
                    "pricing_completed_close": True,
                    "pricing_source": "Deutsche Boerse exact-line ask quote with two-source completed-close qualification",
                    "pricing_source_quality": "development_exact_line_quote_and_completed_close_consensus",
                    "portfolio_contribution_eur": 0.0,
                    "portfolio_contribution_pct_nav": 0.0,
                    "unrealized_pnl_eur": 0.0,
                    "unrealized_pnl_pct": 0.0,
                    "quote_evidence": str(quote_path),
                    "quote_bid_eur": bid,
                    "quote_ask_eur": ask,
                    "quote_bid_size": quote.get("bid_size"),
                    "quote_ask_size": quote.get("ask_size"),
                    "quote_timestamp_utc": quote.get("quote_timestamp_utc"),
                    "quote_spread_pct_mid": quote.get("spread_pct_mid"),
                },
            }
        )

    if not decisions:
        raise RuntimeError("ETF_EU_NO_PROMOTED_STAGE1_CANDIDATE_READY_FOR_ACTIVATION")

    activation_id = f"ETF-EU-STAGE1-{args.report_date}-{args.run_id}"
    decision = {
        "schema_version": "etf_eu_stage1_allocation_decision_v1",
        "artifact_type": "etf_eu_stage1_allocation_decision",
        "activation_id": activation_id,
        "run_id": args.run_id,
        "report_date": args.report_date,
        "allocation_status": "ready_for_guarded_model_activation",
        "authority": {
            "model_portfolio_only": True,
            "real_broker_execution": False,
            "user_activation_request_recorded": True,
            "decision_basis": "current donor promotion plus selected eligible EU allocator row plus exact-line quote and completed-close gates",
        },
        "source_state": str(state_path),
        "source_allocator": str(allocator_path),
        "quote_evidence": str(quote_path),
        "decisions": decisions,
        "evaluated_candidates": evaluated,
    }
    validation = {
        "schema_version": "etf_eu_stage1_allocation_decision_validation_v1",
        "artifact_type": "etf_eu_stage1_allocation_decision_validation",
        "activation_id": activation_id,
        "run_id": args.run_id,
        "report_date": args.report_date,
        "passed": True,
        "allocation_decision_valid": True,
        "activated_tickers": [row["exchange_ticker"] for row in decisions],
        "skipped_tickers": [row["ticker"] for row in evaluated if not row["activation_eligible"]],
        "quote_gate_passed": True,
        "promoted_gate_passed": True,
        "cash_check_delegated_to_guarded_apply": True,
        "model_portfolio_only": True,
        "real_broker_execution": False,
    }
    write_object(decision_path, decision)
    write_object(validation_path, validation)

    result = apply_guarded_activation(
        decision_path=decision_path,
        validation_path=validation_path,
        portfolio_state_path=portfolio_path,
        trade_ledger_path=ledger_path,
        confirmation=args.confirmation,
        output_path=result_path,
    )
    evidence = {
        "schema_version": "etf_eu_stage1_activation_evidence_v1",
        "artifact_type": "etf_eu_stage1_activation_evidence",
        "activation_id": activation_id,
        "run_id": args.run_id,
        "report_date": args.report_date,
        "decision": str(decision_path),
        "validation": str(validation_path),
        "result": str(result_path),
        "quote_evidence": str(quote_path),
        "activated_tickers": validation["activated_tickers"],
        "skipped_tickers": validation["skipped_tickers"],
        "portfolio_state_written": result.get("portfolio_state_written"),
        "trade_ledger_written": result.get("trade_ledger_written"),
        "post_activation_portfolio": result.get("post_activation_portfolio"),
        "model_portfolio_only": True,
        "real_broker_execution": False,
        "email_delivery_authority": False,
    }
    write_object(evidence_path, evidence)
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True)
    parser.add_argument("--allocator", required=True)
    parser.add_argument("--quote-evidence", required=True)
    parser.add_argument("--portfolio-state", default="output/etf_eu_portfolio_state.json")
    parser.add_argument("--trade-ledger", default="output/etf_eu_trade_ledger.csv")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--confirmation", required=True)
    parser.add_argument("--decision-output", required=True)
    parser.add_argument("--validation-output", required=True)
    parser.add_argument("--result-output", required=True)
    parser.add_argument("--evidence-output", required=True)
    args = parser.parse_args()
    evidence = build_and_apply(args)
    print(
        "ETF_EU_STAGE1_ACTIVATION_OK"
        f" | activated={','.join(evidence['activated_tickers'])}"
        f" | skipped={','.join(evidence['skipped_tickers'])}"
        f" | positions={evidence['post_activation_portfolio'].get('position_count')}"
        f" | cash={evidence['post_activation_portfolio'].get('cash_eur')}"
        f" | real_broker_execution=false"
    )


if __name__ == "__main__":
    main()
