from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools import validate_etf_eu_target_allocator_shadow_v3 as legacy

CORE_TICKERS = {"VWCE", "EUNA", "SXR8"}
ACTIVATED_TICKERS = CORE_TICKERS | {"L0CK"}


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def normalize_ticker(value: Any) -> str:
    ticker = str(value or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def activated_portfolio(path: Path) -> bool:
    portfolio = load_object(path)
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    tickers = {
        normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
        for row in positions
        if normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
    }
    if tickers != ACTIVATED_TICKERS:
        return False
    if portfolio.get("schema_version") != "etf_eu_portfolio_state_v2":
        raise RuntimeError("Activated allocator validation requires portfolio state v2")
    if portfolio.get("model_portfolio_only") is not True or portfolio.get("real_broker_execution") is not False:
        raise RuntimeError("Activated allocator portfolio authority boundary is invalid")
    activation = portfolio.get("last_model_capital_activation") or {}
    if not activation.get("activation_id"):
        raise RuntimeError("Activated allocator portfolio provenance is missing")
    return True


def validate_activated(payload: dict[str, Any], portfolio_path: Path) -> list[str]:
    blockers = legacy.validate(payload)
    if not activated_portfolio(portfolio_path):
        return blockers

    permitted_legacy_blockers = {
        "eligible stage-one exposure not selected: cyber_security",
        "legacy position set changed",
    }
    blockers = [blocker for blocker in blockers if blocker not in permitted_legacy_blockers]

    variants = {
        str(row.get("variant_id")): row
        for row in payload.get("variants") or []
        if isinstance(row, dict)
    }
    preferred = variants.get("staged_policy_driven_v1") or {}
    rows = {
        str(row.get("exposure_id")): row
        for row in preferred.get("allocation_rows") or []
        if isinstance(row, dict)
    }
    cyber = rows.get("cyber_security") or {}
    if not cyber:
        blockers.append("activated cybersecurity allocator row missing")
    else:
        if cyber.get("selected") is True:
            blockers.append("activated cybersecurity must not be selected as a new Stage-1 trade")
        if num((cyber.get("order") or {}).get("target_shares")) > 0:
            blockers.append("activated cybersecurity received a duplicate target-share order")
        if num((cyber.get("order") or {}).get("share_delta")) != 0:
            blockers.append("activated cybersecurity received a duplicate share delta")
        if cyber.get("eligible") is not True:
            blockers.append("activated cybersecurity must remain strategy-eligible")

    ai = rows.get("ai_compute_infrastructure") or {}
    if ai.get("selected") is not True or ai.get("eligible") is not True:
        blockers.append("unfunded VVSM must remain the selected eligible Stage-1 candidate")
    if num((ai.get("order") or {}).get("target_shares")) <= 0:
        blockers.append("unfunded VVSM analytical target shares are missing")

    legacy_rows = [row for row in preferred.get("legacy_rows") or [] if isinstance(row, dict)]
    legacy_tickers = {normalize_ticker(row.get("ticker")) for row in legacy_rows}
    if legacy_tickers != ACTIVATED_TICKERS:
        blockers.append(f"activated legacy position set mismatch: {sorted(legacy_tickers)}")
    if any(row.get("side") != "HOLD" or num(row.get("share_delta")) != 0 for row in legacy_rows):
        blockers.append("activated incumbent hold boundary violated")

    checks = preferred.get("policy_checks") if isinstance(preferred.get("policy_checks"), dict) else {}
    for key in ("incumbents_retained", "cash_nonnegative", "within_position_limit"):
        if checks.get(key) is not True:
            blockers.append(f"activated policy check failed: {key}")
    return sorted(set(blockers))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    args = parser.parse_args()
    payload = load_object(args.artifact)
    blockers = validate_activated(payload, args.portfolio_state)
    print(
        json.dumps(
            {
                "valid": not blockers,
                "blockers": blockers,
                "activated_portfolio": activated_portfolio(args.portfolio_state),
                "model_portfolio_only": True,
                "real_broker_execution": False,
            },
            indent=2,
        )
    )
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
