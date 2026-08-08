from __future__ import annotations

import unittest

from bs4 import BeautifulSoup

from runtime.synchronize_etf_eu_activated_front_page import (
    authoritative_contract,
    synchronize_cockpit_summary,
    synchronize_l0ck_action_row,
    synchronize_l0ck_radar_row,
    synchronize_summary,
    validate_front_page,
)


def state() -> dict:
    return {
        "official_portfolio": {
            "position_count": 4,
            "cash_eur": 50208.40,
            "cash_weight_pct": 49.95,
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
        cockpit = (
            "<div class='cockpit-card'>6 actuele donor-exposures; 6 exacte UCITS-koppelingen.</div>"
            "<div class='cockpit-card'>3 officiële posities; geen portefeuillewijziging.</div>"
            "<div class='cockpit-card'>VVSM niet actueel gepromoveerd; L0CK gepromoveerd maar geblokkeerd.</div>"
            "<div class='cockpit-card'>Cash blijft beschikbaar zolang de activeringspoorten niet slagen.</div>"
        )
        radar_status = "Geblokkeerd"
        radar_action = "Cash behouden"
        radar_reason = "Activeringspoort faalt"
    else:
        summary = (
            "<li>Official model portfolio: 3 positions and € 50,208.40 cash.</li>"
            "<li>Current outcome: no change; blocked capacity remains cash.</li>"
        )
        status = "Blocked; retain cash"
        reason = "Currently promoted, but current evidence and donor gates do not pass."
        cockpit = (
            "<div class='cockpit-card'>6 current donor exposures; 6 exact UCITS mappings.</div>"
            "<div class='cockpit-card'>3 official positions; no portfolio change.</div>"
            "<div class='cockpit-card'>VVSM not currently promoted; L0CK promoted but blocked.</div>"
            "<div class='cockpit-card'>Cash remains available while activation gates fail.</div>"
        )
        radar_status = "Blocked"
        radar_action = "Retain cash"
        radar_reason = "Activation gate fails"

    return BeautifulSoup(
        "<html><body>"
        f'<section id="section-1"><ul>{summary}</ul></section>'
        '<section id="section-2">'
        '<table class="wide-table production-opportunity-table"><tbody>'
        '<tr><td>1</td><td>Cybersecurity resilience</td>'
        '<td>L0CK · iShares Digital Security UCITS ETF USD (Acc) · IE00BG0J4C88</td>'
        f'<td>19.02%</td><td>{status}</td><td>{reason}</td></tr>'
        '</tbody></table></section>'
        f'<section id="section-2A"><div class="cockpit-grid">{cockpit}</div></section>'
        '<section id="section-4">'
        '<table class="wide-table promoted-mapping-table"><tbody>'
        '<tr><td>1</td><td>Cybersecurity resilience</td>'
        '<td>L0CK · iShares Digital Security UCITS ETF USD (Acc) · IE00BG0J4C88</td>'
        f'<td>19.02%</td><td>{radar_status}</td><td>{radar_action}</td><td>{radar_reason}</td><td>Evidence</td></tr>'
        '</tbody></table></section>'
        "</body></html>",
        "html.parser",
    )


def synchronize(page_soup: BeautifulSoup, language: str) -> dict:
    contract = authoritative_contract(state())
    synchronize_summary(page_soup, contract, language)
    synchronize_l0ck_action_row(page_soup, language)
    synchronize_cockpit_summary(page_soup, contract, language)
    synchronize_l0ck_radar_row(page_soup, language)
    validate_front_page(page_soup, contract, language)
    return contract


class ActivatedFrontPageContractTests(unittest.TestCase):
    def test_dutch_front_page_is_reconciled_to_authoritative_state(self):
        soup = page("nl")
        synchronize(soup, "nl")
        text = soup.get_text(" ", strip=True)
        self.assertIn("Officiële modelportefeuille: 4 posities en € 50.208,40 cash.", text)
        self.assertIn("L0CK is actief als vierde modelpositie", text)
        self.assertIn("VVSM blijft gemonitord en niet gefinancierd", text)
        self.assertIn("4 officiële modelposities; L0CK actief.", text)
        self.assertIn("Cash € 50.208,40 (49.95%); geen nieuwe brokerorder uitgevoerd.", text)
        self.assertIn("Modelpositie actief", text)
        self.assertNotIn("3 posities", text)
        self.assertNotIn("Geblokkeerd; cash behouden", text)
        self.assertNotIn("L0CK gepromoveerd maar geblokkeerd", text)

    def test_english_front_page_is_reconciled_to_authoritative_state(self):
        soup = page("en")
        synchronize(soup, "en")
        text = soup.get_text(" ", strip=True)
        self.assertIn("Official model portfolio: 4 positions and € 50,208.40 cash.", text)
        self.assertIn("L0CK is active as the fourth model position", text)
        self.assertIn("VVSM remains monitored and unfunded", text)
        self.assertIn("4 official model positions; L0CK active.", text)
        self.assertIn("Cash € 50,208.40 (49.95%); no new broker order placed.", text)
        self.assertIn("Model position active", text)
        self.assertNotIn("3 positions", text)
        self.assertNotIn("Blocked; retain cash", text)
        self.assertNotIn("L0CK promoted but blocked", text)

    def test_real_production_cockpit_preserves_donor_card(self):
        soup = page("nl")
        contract = authoritative_contract(state())
        synchronize_cockpit_summary(soup, contract, "nl")
        cards = [card.get_text(" ", strip=True) for card in soup.select("#section-2A .cockpit-card")]
        self.assertEqual(cards[0], "6 actuele donor-exposures; 6 exacte UCITS-koppelingen.")
        self.assertEqual(cards[1], "4 officiële modelposities; L0CK actief.")
        self.assertIn("VVSM gemonitord en niet gefinancierd", cards[2])
        self.assertIn("geen nieuwe brokerorder uitgevoerd", cards[3])

    def test_front_page_contract_fails_closed_on_non_authoritative_portfolio(self):
        broken = state()
        broken["official_portfolio"]["positions"] = broken["official_portfolio"]["positions"][:3]
        broken["official_portfolio"]["position_count"] = 3
        with self.assertRaisesRegex(RuntimeError, "requires exact funded set"):
            authoritative_contract(broken)


if __name__ == "__main__":
    unittest.main()
