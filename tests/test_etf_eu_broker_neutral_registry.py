from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def fund_by_isin(registry: dict[str, Any], isin: str) -> dict[str, Any]:
    matches = [row for row in registry.get("funds") or [] if row.get("isin") == isin]
    assert len(matches) == 1
    return dict(matches[0])


def basket_line(basket: dict[str, Any], basket_id: str) -> dict[str, Any]:
    matches = [row for row in basket.get("trading_lines") or [] if row.get("basket_id") == basket_id]
    assert len(matches) == 1
    return dict(matches[0])


def test_vwce_and_euna_model_gates_are_broker_neutral() -> None:
    registry = load_yaml(ROOT / "config/ucits_symbol_registry.yml")
    basket = load_yaml(ROOT / "config/ucits_close_price_validation_basket.yml")
    targets = load_yaml(ROOT / "config/etf_eu_target_allocation.yml")

    vwce = fund_by_isin(registry, "IE00BK5BQT80")
    assert vwce["fundable_status"] == "blocked_pending_fresh_xetra_close_and_new_allocation_decision"
    assert "broker" not in vwce["fundable_status"]
    vwce_line = dict(vwce["trading_lines"][0])
    assert vwce_line["exchange"] == "Xetra"
    assert vwce_line["exchange_ticker"] == "VWCE"
    assert vwce_line["line_verification_status"] == "verified_ucits_trading_line"

    euna = fund_by_isin(registry, "IE00BDBRDM35")
    assert euna["fundable_status"] == "blocked_pending_fresh_xetra_close_and_new_allocation_decision"
    euna_line = dict(euna["trading_lines"][0])
    assert euna_line["exchange"] == "Xetra"
    assert euna_line["venue_code"] == "XETR"
    assert euna_line["exchange_ticker"] == "EUNA"
    assert euna_line["issuer_exchange_ticker"] == "AGGH"
    assert euna_line["reuters_ric"] == "EUNA.DE"
    assert euna_line["pricing_symbol_yahoo"] == "EUNA.DE"
    assert euna_line["line_verification_status"] == "verified_ucits_trading_line"
    assert euna_line["alias_reconciliation_status"] == "completed_broker_neutral"
    assert all("broker" not in str(value).lower() for value in euna_line.values())

    for row in (basket_line(basket, "vwce_xetra_eur"), basket_line(basket, "euna_xetra_eur")):
        assert row["verification_status"] == "verified_ucits_trading_line"
        blockers = row.get("funding_blockers") or []
        assert blockers == ["fresh_completed_xetra_close_required", "separate_allocation_decision_required"]
        assert all("broker" not in str(blocker).lower() for blocker in blockers)

    activation = targets["activation"]
    assert activation["broker_specific_permission_required_for_model"] is False
    assert activation["broker_permission_required_for_real_execution"] is True

    target_by_ticker = {row.get("exchange_ticker"): row for row in targets.get("strategic_targets") or []}
    assert target_by_ticker["VWCE"]["isin"] == "IE00BK5BQT80"
    assert target_by_ticker["EUNA"]["isin"] == "IE00BDBRDM35"
