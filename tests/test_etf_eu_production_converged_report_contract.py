from __future__ import annotations

import copy
import unittest

from tools.validate_etf_eu_production_converged_report import validate_manifest_state_contract


CORE_POSITIONS = [
    {"ticker": "VWCE", "isin": "IE00BK5BQT80"},
    {"ticker": "EUNA", "isin": "IE00BDBRDM35"},
    {"ticker": "SXR8", "isin": "IE00B5BMR087"},
]
FALSE_AUTHORITY = {
    "portfolio_mutation": False,
    "ledger_write": False,
    "funding_authority": False,
    "execution_authority": False,
    "activation_authority": False,
    "production_delivery_authority": False,
}


def state(*, activated: bool) -> dict:
    positions = copy.deepcopy(CORE_POSITIONS)
    stage = {
        "value": "blocked",
        "activated_tickers": [],
        "remaining_monitored_tickers": ["VVSM", "L0CK"],
    }
    if activated:
        positions.append({"ticker": "L0CK", "isin": "IE000I8KRLL9"})
        stage = {
            "value": "partially_activated",
            "activated_tickers": ["L0CK"],
            "remaining_monitored_tickers": ["VVSM"],
        }
    return {
        "official_portfolio": {
            "position_count": len(positions),
            "positions": positions,
            "nav_eur": 100000.0,
            "cash_eur": 2500.0,
        },
        "stage_1_decision": stage,
        "authority": copy.deepcopy(FALSE_AUTHORITY),
        "promoted_exposures": [
            {"ticker": "VVSM", "isin": "IE0005BLPZV6"},
            {"ticker": "L0CK", "isin": "IE000I8KRLL9"},
        ],
    }


def manifest(*, activated: bool) -> dict:
    tickers = ["VWCE", "EUNA", "SXR8"]
    isins = ["IE00BK5BQT80", "IE00BDBRDM35", "IE00B5BMR087"]
    stage_value = "blocked"
    mode = "synchronized_premium_production_candidate"
    if activated:
        tickers.append("L0CK")
        isins.append("IE000I8KRLL9")
        stage_value = "partially_activated"
        mode = "activated_four_position_premium_production_candidate"
    return {
        "schema_version": "etf_eu_production_converged_report_manifest_v1",
        "client_renderer_mode": mode,
        "official_portfolio_position_count": len(tickers),
        "official_portfolio_tickers": tickers,
        "official_portfolio_isins": isins,
        "stage_1_decision": stage_value,
        "executable_trade_intents": [],
        "authority": copy.deepcopy(FALSE_AUTHORITY),
    }


class ProductionContractTests(unittest.TestCase):
    def test_blocked_three_position_state_passes(self) -> None:
        blockers, evidence = validate_manifest_state_contract(
            manifest(activated=False), state(activated=False)
        )
        self.assertEqual(blockers, [])
        self.assertEqual(evidence["position_count"], 3)
        self.assertEqual(evidence["stage_1_decision"], "blocked")

    def test_partially_activated_four_position_state_passes(self) -> None:
        blockers, evidence = validate_manifest_state_contract(
            manifest(activated=True), state(activated=True)
        )
        self.assertEqual(blockers, [])
        self.assertEqual(evidence["position_count"], 4)
        self.assertEqual(evidence["activated_tickers"], ["L0CK"])

    def test_planted_manifest_roster_mismatch_fails(self) -> None:
        candidate = manifest(activated=True)
        candidate["official_portfolio_tickers"] = ["VWCE", "EUNA", "SXR8"]
        blockers, _ = validate_manifest_state_contract(candidate, state(activated=True))
        self.assertTrue(any("ticker roster mismatch" in item for item in blockers))

    def test_planted_monitored_ticker_funded_fails(self) -> None:
        candidate_state = state(activated=True)
        candidate_state["stage_1_decision"]["remaining_monitored_tickers"] = ["L0CK"]
        blockers, _ = validate_manifest_state_contract(manifest(activated=True), candidate_state)
        self.assertTrue(any("incorrectly funded" in item for item in blockers))

    def test_planted_authority_escalation_fails(self) -> None:
        candidate = manifest(activated=True)
        candidate["authority"]["production_delivery_authority"] = True
        blockers, _ = validate_manifest_state_contract(candidate, state(activated=True))
        self.assertIn("manifest authority production_delivery_authority must be false", blockers)

    def test_planted_executable_intent_fails(self) -> None:
        candidate = manifest(activated=True)
        candidate["executable_trade_intents"] = [{"ticker": "L0CK", "side": "BUY"}]
        blockers, _ = validate_manifest_state_contract(candidate, state(activated=True))
        self.assertIn("pre-send report package contains executable trade intents", blockers)


if __name__ == "__main__":
    unittest.main()
