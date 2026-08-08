from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

CORE_FUNDED = {"VWCE", "EUNA", "SXR8"}
ALLOWED_ACTIVATED = {"L0CK"}
EXPECTED_STAGE_1 = {
    "IE00BMC38736": {"symbol": "VVSM", "currently_promoted": False},
    "IE00BG0J4C88": {"symbol": "L0CK", "currently_promoted": True},
}


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("State must be a JSON object")
    return payload


def ticker(row: dict[str, Any]) -> str:
    value = str(row.get("ticker") or row.get("exchange_ticker") or "").strip().upper()
    return "L0CK" if value == "LOCK" else value


def validate(state: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if state.get("schema_version") != "etf_eu_production_convergence_state_v1":
        blockers.append("unexpected state schema")
    if not state.get("run_id") or not state.get("report_date"):
        blockers.append("run identity is incomplete")

    portfolio = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    funded = {ticker(row) for row in positions if ticker(row)}
    if not CORE_FUNDED.issubset(funded):
        blockers.append(f"core funded tickers are incomplete: {sorted(funded)}")
    extras = funded - CORE_FUNDED
    if not extras.issubset(ALLOWED_ACTIVATED):
        blockers.append(f"unexpected activated funded tickers: {sorted(extras)}")
    if portfolio.get("position_count") != len(positions):
        blockers.append("official funded position count does not match positions")
    if len(positions) not in {3, 4}:
        blockers.append("official funded position count must be three or four")
    if not portfolio.get("portfolio_state_sha256") or not portfolio.get("trade_ledger_sha256"):
        blockers.append("protected-state hashes are missing")
    activated_state = funded == CORE_FUNDED | {"L0CK"}
    if activated_state:
        if portfolio.get("model_portfolio_only") is not True:
            blockers.append("activated portfolio must remain model-only")
        if portfolio.get("real_broker_execution") is not False:
            blockers.append("activated portfolio must not imply broker execution")
        activation = portfolio.get("last_model_capital_activation") or state.get("model_capital_activation") or {}
        if not activation.get("activation_id"):
            blockers.append("activated portfolio provenance is missing")

    strategy = state.get("strategy") if isinstance(state.get("strategy"), dict) else {}
    if strategy.get("promoted_exposure_count") != 6:
        blockers.append("promoted exposure count must be six")
    if strategy.get("mapped_promoted_exposure_count") != 6:
        blockers.append("all six promoted exposures must be mapped")
    if strategy.get("unmapped_promoted_exposure_count") != 0:
        blockers.append("unmapped promoted exposure count must be zero")

    promoted_rows = [row for row in state.get("promoted_exposures") or [] if isinstance(row, dict)]
    if len(promoted_rows) != 6:
        blockers.append("promoted exposure rows must contain six items")
    exposure_ids = [str(row.get("exposure_id") or "") for row in promoted_rows]
    if len(set(exposure_ids)) != len(exposure_ids):
        blockers.append("promoted exposure IDs must be unique")
    if any(not row.get("isin") for row in promoted_rows):
        blockers.append("every promoted exposure must contain a mapped ISIN")
    if "ai_compute_infrastructure" in exposure_ids:
        blockers.append("VVSM must not be represented as currently promoted in the donor set")
    if "cyber_security" not in exposure_ids:
        blockers.append("cybersecurity must remain in the current promoted set")

    stage_rows = [row for row in state.get("stage_1_review_candidates") or [] if isinstance(row, dict)]
    if len(stage_rows) != 2:
        blockers.append("Stage-1 review must contain exactly two candidates")
    by_isin = {str(row.get("isin") or "").upper(): row for row in stage_rows}
    for isin, expected in EXPECTED_STAGE_1.items():
        row = by_isin.get(isin)
        if not row:
            blockers.append(f"Stage-1 review candidate missing: {isin}")
            continue
        symbol = expected["symbol"]
        if str(row.get("exchange_symbol") or "").upper() != symbol:
            blockers.append(f"Stage-1 exchange symbol mismatch for {isin}")
        if row.get("currently_promoted") is not expected["currently_promoted"]:
            blockers.append(f"Stage-1 current-promotion status mismatch for {isin}")
        if row.get("exact_identity_pass") is not True:
            blockers.append(f"Stage-1 exact identity must pass for {isin}")
        if row.get("exact_current_issuer_kid_pass") is not True:
            blockers.append(f"Stage-1 current issuer KID must pass for {isin}")
        if symbol in funded:
            if symbol != "L0CK":
                blockers.append(f"unexpected funded Stage-1 candidate: {symbol}")
            if row.get("client_action") != "hold_current_position":
                blockers.append("funded L0CK client action must be hold_current_position")
            if float(row.get("actionable_target_weight_pct") or 0) <= 0:
                blockers.append("funded L0CK actionable weight must be positive")
            if row.get("blockers"):
                blockers.append("funded L0CK must not retain activation blockers")
            if row.get("official_state_applied") is not True:
                blockers.append("funded L0CK must show official state applied")
        else:
            if float(row.get("actionable_target_weight_pct") or 0) != 0.0:
                blockers.append(f"unfunded Stage-1 actionable target must be zero for {isin}")
            if row.get("client_action") != "blocked_monitor":
                blockers.append(f"unfunded Stage-1 client action must be blocked_monitor for {isin}")
            if not row.get("blockers"):
                blockers.append(f"unfunded Stage-1 blockers missing for {isin}")

    decision = state.get("stage_1_decision") if isinstance(state.get("stage_1_decision"), dict) else {}
    if activated_state:
        if decision.get("value") != "partially_activated":
            blockers.append("activated Stage-1 decision must be partially_activated")
        if decision.get("status") != "model_position_activated_remaining_candidate_monitored":
            blockers.append("activated Stage-1 status mismatch")
        if decision.get("stage_1_activation_authorized") is not True:
            blockers.append("historical Stage-1 activation authority must be recorded")
        if decision.get("official_state_applied") is not True:
            blockers.append("activated Stage-1 official state must be applied")
        if set(decision.get("activated_tickers") or []) != {"L0CK"}:
            blockers.append("activated Stage-1 ticker set must contain L0CK only")
        if set(decision.get("remaining_monitored_tickers") or []) != {"VVSM"}:
            blockers.append("remaining monitored Stage-1 ticker must be VVSM")
    else:
        if decision.get("value") != "blocked" or decision.get("status") != "blocked_not_activation_ready":
            blockers.append("pre-activation Stage-1 decision must remain blocked")
        if decision.get("stage_1_activation_authorized") is not False:
            blockers.append("pre-activation Stage-1 authority must be false")
        if decision.get("official_state_applied") is not False:
            blockers.append("pre-activation official state must not be applied")
    if decision.get("executable_trade_intents") != []:
        blockers.append("executable trade intents must be empty")

    client = state.get("client_contract") if isinstance(state.get("client_contract"), dict) else {}
    required_client_flags = {
        "dutch_primary": True,
        "english_companion": True,
        "premium_surface_required": True,
        "shadow_language_allowed": False,
        "raw_internal_tokens_allowed": False,
    }
    for key, expected in required_client_flags.items():
        if client.get(key) is not expected:
            blockers.append(f"client contract {key} must be {expected}")
    if client.get("actionable_new_positions") != []:
        blockers.append("client contract actionable new positions must be empty")

    authority = state.get("authority") if isinstance(state.get("authority"), dict) else {}
    for key in (
        "portfolio_mutation",
        "ledger_write",
        "funding_authority",
        "execution_authority",
        "activation_authority",
        "production_delivery_authority",
    ):
        if authority.get(key) is not False:
            blockers.append(f"current report authority {key} must be false")

    validation = state.get("validation") if isinstance(state.get("validation"), dict) else {}
    if validation.get("protected_state_unchanged") is not True:
        blockers.append("protected-state unchanged proof is missing")
    if activated_state:
        if validation.get("stage_1_partial_activation") is not True:
            blockers.append("state validation must confirm partial Stage-1 activation")
        if set(validation.get("activated_stage_1_tickers") or []) != {"L0CK"}:
            blockers.append("validation activated ticker set mismatch")
    elif validation.get("stage_1_blocked") is not True:
        blockers.append("pre-activation validation must confirm Stage 1 is blocked")
    if validation.get("stage_1_review_candidate_count") != 2:
        blockers.append("state validation Stage-1 review count must be two")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    state = load(args.path)
    blockers = validate(state)
    positions = state.get("official_portfolio", {}).get("positions") or []
    result = {
        "artifact_type": "etf_eu_production_convergence_state_validation",
        "valid": not blockers,
        "blockers": blockers,
        "funded_tickers": sorted({ticker(row) for row in positions if isinstance(row, dict)}),
        "funded_position_count": len(positions),
        "promoted_exposure_count": len(state.get("promoted_exposures") or []),
        "stage_1_review_candidate_count": len(state.get("stage_1_review_candidates") or []),
        "stage_1_current_promotion": {
            str(row.get("exchange_symbol") or ""): row.get("currently_promoted")
            for row in state.get("stage_1_review_candidates") or []
            if isinstance(row, dict)
        },
        "stage_1_decision": state.get("stage_1_decision", {}).get("value"),
        "model_portfolio_only": state.get("official_portfolio", {}).get("model_portfolio_only"),
        "real_broker_execution": state.get("official_portfolio", {}).get("real_broker_execution"),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
