from __future__ import annotations

import unittest

from bs4 import BeautifulSoup

from runtime.synchronize_etf_eu_activated_front_page import (
    authoritative_contract,
    synchronize_l0ck_action_row,
    synchronize_summary,
    validate_front_page,
)


def state() -> dict:
    return {
        "official_portfolio": {
            "position_count": 4,
            "cash_eur": 50208.40,
            "model_portfolio_only": True,
            "real_broker_execution": False,
            "positions": [
                {"ticker": "VWCE", "isin": "IE00BK5BQT80"},
                {"ticker": "EUNA", "isin": "IE00BDBRDM35"},
                {"ticker": "SXR8", "isin": "IE00B5BMR087"},
                {"ticker": "L0CK", "isin": "IE00BG0J4C88"},
            ],
        },
        "stage_1_decision": {
            "value": "partially_activated",
            "activated_tickers": ["L0CK"],
            "remaining_monitored_tickers": ["VVSM"],
        },
    }


def page(language: str) -> BeautifulSoup:
    if language == "nl":
        summary = (
            "<li>Officiële modelportefeuille: 3 posities en € 50.208,40 cash.</li>"
            "<li>Actuele uitkomst: geen wijziging; geblokkeerde ruimte blijft cash.</li>"
        )
        status = "Geblokkeerd; cash behouden"
        reason = "Actueel gepromoveerd, maar actuele bewijs- en donorpoorten slagen niet."
    else:
        summary = (
            "<li>Official model portfolio: 3 positions and € 50,208.40 cash.</li>"
            "<li>Current outcome: no change; blocked capacity remains cash.</li>"
        )
        status = "Blocked; retain cash"
        reason = "Currently promoted, but current evidence and donor gates do not pass."
    return BeautifulSoup(
        "<html><body>"
        f'<section id="section-1"><ul>{summary}</ul></section>'
        '<section id="section-2">'
        '<table class="wide-table production-opportunity-table"><tbody>'
        '<tr><td>1</td><td>Cybersecurity resilience</td>'
        '<td>L0CK · iShares Digital Security UCITS ETF USD (Acc) · IE00BG0J4C88</td>'
        f'<td>19.02%</td><td>{status}</td><td>{reason}</td></tr>'
        '</tbody></table></section>'
        "</body></html>",
        "html.parser",
    )


class ActivatedFrontPageContractTests(unittest.TestCase):
    def test_dutch_front_page_is_reconciled_to_authoritative_state(self):
        soup = page("nl")
        contract = authoritative_contract(state())
        synchronize_summary(soup, contract, "nl")
        synchronize_l0ck_action_row(soup, "nl")
        validate_front_page(soup, contract, "nl")
        text = soup.get_text(" ", strip=True)
        self.assertIn("Officiële modelportefeuille: 4 posities en € 50.208,40 cash.", text)
        self.assertIn("L0CK is actief als vierde modelpositie", text)
        self.assertIn("VVSM blijft gemonitord en niet gefinancierd", text)
        self.assertIn("Modelpositie actief", text)
        self.assertIn("geen nieuwe brokerorder uitgevoerd", text)
        self.assertNotIn("3 posities", text)
        self.assertNotIn("Geblokkeerd; cash behouden", text)

    def test_english_front_page_is_reconciled_to_authoritative_state(self):
        soup = page("en")
        contract = authoritative_contract(state())
        synchronize_summary(soup, contract, "en")
        synchronize_l0ck_action_row(soup, "en")
        validate_front_page(soup, contract, "en")
        text = soup.get_text(" ", strip=True)
        self.assertIn("Official model portfolio: 4 positions and € 50,208.40 cash.", text)
        self.assertIn("L0CK is active as the fourth model position", text)
        self.assertIn("VVSM remains monitored and unfunded", text)
        self.assertIn("Model position active", text)
        self.assertIn("no new broker order was placed", text)
        self.assertNotIn("3 positions", text)
        self.assertNotIn("Blocked; retain cash", text)

    def test_front_page_contract_fails_closed_on_non_authoritative_portfolio(self):
        broken = state()
        broken["official_portfolio"]["positions"] = broken["official_portfolio"]["positions"][:3]
        broken["official_portfolio"]["position_count"] = 3
        with self.assertRaisesRegex(RuntimeError, "requires exact funded set"):
            authoritative_contract(broken)


if __name__ == "__main__":
    unittest.main()
