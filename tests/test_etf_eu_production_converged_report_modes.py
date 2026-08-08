from __future__ import annotations

from tools.validate_etf_eu_production_converged_report import validate_manifest_state


def _position(ticker: str, isin: str) -> dict[str, object]:
    return {
        "ticker": ticker,
        "exchange_ticker": ticker,
        "isin": isin,
        "shares": 10,
        "model_portfolio_only": True,
        "real_broker_execution": False,
    }


def _authority() -> dict[str, bool]:
    return {
        "portfolio_mutation": False,
        "ledger_write": False,
        "funding_authority": False,
        "execution_authority": False,
        "activation_authority": False,
        "production_delivery_authority": False,
    }


def test_three_position_blocked_mode_is_valid() -> None:
    positions = [
        _position("VWCE", "IE00BK5BQT80"),
        _position("EUNA", "IE00BDBRDM35"),
        _position("SXR8", "IE00B5BMR087"),
    ]
    state = {
        "official_portfolio": {
            "position_count": 3,
            "positions": positions,
            "model_portfolio_only": True,
            "real_broker_execution": False,
        },
        "stage_1_decision": {
            "value": "blocked",
            "activated_tickers": [],
            "remaining_monitored_tickers": [],
            "executable_trade_intents": [],
        },
        "authority": _authority(),
    }
    manifest = {
        "schema_version": "etf_eu_production_converged_report_manifest_v1",
        "client_renderer_mode": "synchronized_premium_production_candidate",
        "official_portfolio_position_count": 3,
        "stage_1_decision": "blocked",
        "activated_tickers": [],
        "remaining_monitored_tickers": [],
        "executable_trade_intents": [],
        "model_portfolio_only": True,
        "real_broker_execution": False,
        "authority": _authority(),
    }

    blockers, contract = validate_manifest_state(manifest, state)

    assert blockers == []
    assert contract["position_count"] == 3
    assert contract["stage_value"] == "blocked"
    assert contract["funded_tickers"] == {"VWCE", "EUNA", "SXR8"}


def test_four_position_partial_activation_mode_is_valid() -> None:
    positions = [
        _position("VWCE", "IE00BK5BQT80"),
        _position("EUNA", "IE00BDBRDM35"),
        _position("SXR8", "IE00B5BMR087"),
        _position("L0CK", "IE00BG0J4C88"),
    ]
    activation = {"activation_id": "ETF-EU-STAGE1-TEST"}
    state = {
        "official_portfolio": {
            "position_count": 4,
            "positions": positions,
            "model_portfolio_only": True,
            "real_broker_execution": False,
            "last_model_capital_activation": activation,
        },
        "model_capital_activation": activation,
        "stage_1_decision": {
            "value": "partially_activated",
            "activated_tickers": ["L0CK"],
            "remaining_monitored_tickers": ["VVSM"],
            "executable_trade_intents": [],
        },
        "authority": _authority(),
    }
    manifest = {
        "schema_version": "etf_eu_production_converged_report_manifest_v1",
        "client_renderer_mode": "activated_four_position_premium_production_candidate",
        "official_portfolio_position_count": 4,
        "stage_1_decision": "partially_activated",
        "activated_tickers": ["L0CK"],
        "remaining_monitored_tickers": ["VVSM"],
        "executable_trade_intents": [],
        "model_portfolio_only": True,
        "real_broker_execution": False,
        "authority": _authority(),
    }

    blockers, contract = validate_manifest_state(manifest, state)

    assert blockers == []
    assert contract["position_count"] == 4
    assert contract["activated_tickers"] == {"L0CK"}
    assert contract["monitored_tickers"] == {"VVSM"}
    assert contract["funded_tickers"] == {"VWCE", "EUNA", "SXR8", "L0CK"}


def test_stale_three_position_manifest_is_rejected_for_activated_state() -> None:
    positions = [
        _position("VWCE", "IE00BK5BQT80"),
        _position("EUNA", "IE00BDBRDM35"),
        _position("SXR8", "IE00B5BMR087"),
        _position("L0CK", "IE00BG0J4C88"),
    ]
    state = {
        "official_portfolio": {
            "position_count": 4,
            "positions": positions,
            "model_portfolio_only": True,
            "real_broker_execution": False,
            "last_model_capital_activation": {"activation_id": "ETF-EU-STAGE1-TEST"},
        },
        "stage_1_decision": {
            "value": "partially_activated",
            "activated_tickers": ["L0CK"],
            "remaining_monitored_tickers": ["VVSM"],
            "executable_trade_intents": [],
        },
        "authority": _authority(),
    }
    manifest = {
        "schema_version": "etf_eu_production_converged_report_manifest_v1",
        "client_renderer_mode": "synchronized_premium_production_candidate",
        "official_portfolio_position_count": 3,
        "stage_1_decision": "blocked",
        "activated_tickers": [],
        "remaining_monitored_tickers": [],
        "executable_trade_intents": [],
        "authority": _authority(),
    }

    blockers, _ = validate_manifest_state(manifest, state)

    assert blockers
    assert any("renderer mode" in blocker for blocker in blockers)
    assert any("position count" in blocker for blocker in blockers)
    assert any("Stage-1 decision" in blocker for blocker in blockers)


def test_activated_state_without_provenance_is_rejected() -> None:
    state = {
        "official_portfolio": {
            "position_count": 4,
            "positions": [
                _position("VWCE", "IE00BK5BQT80"),
                _position("EUNA", "IE00BDBRDM35"),
                _position("SXR8", "IE00B5BMR087"),
                _position("L0CK", "IE00BG0J4C88"),
            ],
            "model_portfolio_only": True,
            "real_broker_execution": False,
        },
        "stage_1_decision": {
            "value": "partially_activated",
            "activated_tickers": ["L0CK"],
            "remaining_monitored_tickers": ["VVSM"],
            "executable_trade_intents": [],
        },
        "authority": _authority(),
    }
    manifest = {
        "schema_version": "etf_eu_production_converged_report_manifest_v1",
        "client_renderer_mode": "activated_four_position_premium_production_candidate",
        "official_portfolio_position_count": 4,
        "stage_1_decision": "partially_activated",
        "activated_tickers": ["L0CK"],
        "remaining_monitored_tickers": ["VVSM"],
        "executable_trade_intents": [],
        "authority": _authority(),
    }

    blockers, _ = validate_manifest_state(manifest, state)

    assert "activated portfolio provenance is missing" in blockers
