from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_FUNDED = {"VWCE", "EUNA", "SXR8"}
EXPECTED_STAGE_1 = {
    "IE00BMC38736": "VVSM",
    "IE00BG0J4C88": "L0CK",
}


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("State must be a JSON object")
    return payload


def ticker(row: dict[str, Any]) -> str:
    return str(row.get("ticker") or row.get("exchange_ticker") or "").strip().upper()


def validate(state: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if state.get("schema_version") != "etf_eu_production_convergence_state_v1":
        blockers.append("unexpected state schema")
    if not state.get("run_id") or not state.get("report_date"):
        blockers.append("run identity is incomplete")

    portfolio = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    funded = {ticker(row) for row in positions if ticker(row)}
    if funded != EXPECTED_FUNDED:
        blockers.append(f"official funded tickers differ: {sorted(funded)}")
    if portfolio.get("position_count") != 3 or len(positions) != 3:
        blockers.append("official funded position count must be three")
    if not portfolio.get("portfolio_state_sha256") or not portfolio.get("trade_ledger_sha256"):
        blockers.append("protected-state hashes are missing")

    strategy = state.get("strategy") if isinstance(state.get("strategy"), dict) else {}
    if strategy.get("promoted_exposure_count") != 6:
        blockers.append("promoted exposure count must be six")
    if strategy.get("mapped_promoted_exposure_count") != 6:
        blockers.append("all six promoted exposures must be mapped")
    if strategy.get("unmapped_promoted_exposure_count") != 0:
        blockers.append("unmapped promoted exposure count must be zero")

    rows = [row for row in state.get("promoted_exposures") or [] if isinstance(row, dict)]
    if len(rows) != 6:
        blockers.append("promoted exposure rows must contain six items")
    exposure_ids = [str(row.get("exposure_id") or "") for row in rows]
    if len(set(exposure_ids)) != len(exposure_ids):
        blockers.append("promoted exposure IDs must be unique")
    if any(not row.get("isin") for row in rows):
        blockers.append("every promoted exposure must contain a mapped ISIN")

    by_isin = {str(row.get("isin") or "").upper(): row for row in rows}
    for isin, symbol in EXPECTED_STAGE_1.items():
        row = by_isin.get(isin)
        if not row:
            blockers.append(f"Stage-1 mapped exposure missing: {isin}")
            continue
        if str(row.get("exchange_symbol") or "").upper() != symbol:
            blockers.append(f"Stage-1 exchange symbol mismatch for {isin}")
        if row.get("exact_identity_pass") is not True:
            blockers.append(f"Stage-1 exact identity must pass for {isin}")
        if row.get("exact_current_issuer_kid_pass") is not True:
            blockers.append(f"Stage-1 current issuer KID must pass for {isin}")
        if float(row.get("actionable_target_weight_pct") or 0) != 0.0:
            blockers.append(f"Stage-1 actionable target must be zero for {isin}")
        if row.get("client_action") != "blocked_monitor":
            blockers.append(f"Stage-1 client action must be blocked_monitor for {isin}")
        if not row.get("blockers"):
            blockers.append(f"Stage-1 blockers missing for {isin}")

    decision = state.get("stage_1_decision") if isinstance(state.get("stage_1_decision"), dict) else {}
    if decision.get("value") != "blocked" or decision.get("status") != "blocked_not_activation_ready":
        blockers.append("Stage-1 decision must remain explicitly blocked")
    if decision.get("stage_1_activation_authorized") is not False:
        blockers.append("Stage-1 activation authority must be false")
    if decision.get("official_state_applied") is not False:
        blockers.append("official state must not be applied")
    if decision.get("executable_trade_intents") != []:
        blockers.append("executable trade intents must be empty")
    if int(decision.get("blocker_count") or 0) < 1:
        blockers.append("blocked decision must expose blockers")

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
            blockers.append(f"authority {key} must be false")

    validation = state.get("validation") if isinstance(state.get("validation"), dict) else {}
    if validation.get("protected_state_unchanged") is not True:
        blockers.append("protected-state unchanged proof is missing")
    if validation.get("stage_1_blocked") is not True:
        blockers.append("state validation must confirm Stage 1 is blocked")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    state = load(args.path)
    blockers = validate(state)
    result = {
        "artifact_type": "etf_eu_production_convergence_state_validation",
        "valid": not blockers,
        "blockers": blockers,
        "funded_tickers": sorted({ticker(row) for row in state.get("official_portfolio", {}).get("positions") or [] if isinstance(row, dict)}),
        "promoted_exposure_count": len(state.get("promoted_exposures") or []),
        "stage_1_decision": state.get("stage_1_decision", {}).get("value"),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
