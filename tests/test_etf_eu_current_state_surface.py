from __future__ import annotations

import unittest

from bs4 import BeautifulSoup

from runtime import synchronize_etf_eu_current_state_surface as surface


def state() -> dict:
    return {
        "official_portfolio": {
            "position_count": 4,
            "cash_eur": 50208.40,
            "nav_eur": 100512.23,
            "model_portfolio_only": True,
            "real_broker_execution": False,
            "positions": [
                {"ticker": "VWCE", "weight_pct": 25.244729},
                {"ticker": "EUNA", "weight_pct": 7.456904},
                {"ticker": "SXR8", "weight_pct": 7.187384},
                {"ticker": "L0CK", "weight_pct": 10.158455},
            ],
        },
        "stage_1_decision": {
            "activated_tickers": ["L0CK"],
            "remaining_monitored_tickers": ["VVSM"],
        },
    }


def html() -> str:
    current_rows = "".join(
        f"<tr><td>{ticker}</td><td>Buy</td><td>Role</td><td>Re-underwrite</td><td>Role</td><td>Compare</td></tr>"
        for ticker in ("VWCE", "EUNA", "SXR8", "L0CK")
    )
    overlap_rows = "".join(
        f"<tr><td>{ticker}</td><td>1.00%</td><td>x</td><td>x</td><td>Hold</td><td>x</td><td>x</td></tr>"
        for ticker in ("VWCE", "EUNA", "SXR8")
    )
    incumbent_rows = "".join(
        f"<tr><td>{ticker}</td><td>Fund</td><td>0.00%</td><td>0.00%</td><td>0.00%</td><td>Hold</td><td>No change</td><td>—</td><td>stale</td><td>No change</td></tr>"
        for ticker in ("VWCE", "EUNA", "SXR8", "L0CK")
    )
    return f"""
    <html><body>
      <section id='section-2A'><div class='cockpit-grid'>
        <div class='cockpit-card'>donor</div><div class='cockpit-card'>3 official positions</div>
        <div class='cockpit-card'>L0CK promoted but blocked</div><div class='cockpit-card'>Cash 0.00%</div>
      </div></section>
      <section id='section-5'><table><tbody><tr><td>Legacy portfolio</td><td>3 current positions require re-underwriting</td></tr></tbody></table></section>
      <section id='section-6'><p>The current report outcome contains three official positions.</p></section>
      <section id='section-8'>
        <table><tbody><tr><td>Thematic satellites</td><td>Underweight / blocked</td><td>stale</td></tr></tbody></table>
        <table><tbody><tr><td>Cybersecurity resilience</td><td>19.02%</td><td>0.00%</td><td>-19.02%</td><td>L0CK</td><td>Weight gap</td><td>stale</td></tr></tbody></table>
      </section>
      <section id='section-9'><table><tbody><tr><td>Cyber</td><td>old</td><td>Mapped; evidence incomplete</td><td>L0CK · IE00BG0J4C88</td><td>Complete gates</td><td>Immediate</td><td>High</td></tr></tbody></table></section>
      <section id='section-10'><table><tbody>{current_rows}</tbody></table><table><tbody>{overlap_rows}</tbody></table></section>
      <section id='section-11'><table><tbody><tr><td>Cyber</td><td>L0CK · IE00BG0J4C88</td><td>Currently promoted, but not deployable</td><td>Activation remains blocked</td><td>Retain cash</td></tr></tbody></table></section>
      <section id='section-12'><table><tbody><tr><td>None</td><td>None</td><td>EUNA, L0CK, SXR8, VWCE</td><td>None; VVSM and L0CK remain blocked review candidates</td><td>None</td><td>Current decision: no trade</td></tr></tbody></table></section>
      <section id='section-13'><table class='final-alignment-table'><tbody>
        <tr><td>AI compute</td><td>VVSM · IE00BMC38736</td><td>0.00%</td><td>14.88%</td><td>+14.88%</td><td>Review Stage-1</td><td>Cash</td><td>3.92</td><td>stale</td><td>Blocked</td></tr>
        <tr><td>Cyber</td><td>L0CK · IE00BG0J4C88</td><td>10.16%</td><td>0.00%</td><td>-10.16%</td><td>Complete gates</td><td>No allocation</td><td>4.93</td><td>stale</td><td>active</td></tr>
        <tr><td>Cash</td><td>CASH</td><td>0.00%</td><td>0.00%</td><td>0.00%</td><td>Hold</td><td>No allocation</td><td>—</td><td>stale</td><td>No change</td></tr>
        {incumbent_rows}
      </tbody></table></section>
      <section id='section-7'><p>Historical three-position valuation context.</p></section>
      <section id='section-14'><p>Non-actionable VVSM scenario target 14.88%.</p></section>
    </body></html>
    """


class CurrentStateSurfaceTests(unittest.TestCase):
    def test_cash_weight_is_derived_from_authoritative_cash_and_nav(self):
        c, positions = surface.contract(state())
        self.assertAlmostEqual(c["cash_weight_pct"], 49.95252816498053)
        self.assertEqual(set(positions), {"VWCE", "EUNA", "SXR8", "L0CK"})

    def test_current_sections_reconcile_without_rewriting_history_or_scenario(self):
        payload = state()
        c, positions = surface.contract(payload)
        soup = BeautifulSoup(html(), "html.parser")
        history_before = surface._section(soup, "7").get_text(" ", strip=True)
        scenario_before = surface._section(soup, "14").get_text(" ", strip=True)

        surface._sync_cockpit(soup, c, "en")
        surface._sync_5_6(soup, "en")
        surface._sync_8(soup, positions, "en")
        surface._sync_9_11(soup, "en")
        surface._sync_10(soup, positions, "en")
        surface._sync_12(soup, "en")
        surface._sync_13(soup, c, positions, "en")
        surface.validate(soup, c, positions, "en")

        self.assertIn("Cash € 50,208.40 (49.95%)", surface._section(soup, "2A").get_text(" ", strip=True))
        self.assertIn("four official model positions", surface._section(soup, "6").get_text(" ", strip=True))
        self.assertIn("Hold", surface._section(soup, "10").get_text(" ", strip=True))
        final_text = surface._section(soup, "13").get_text(" ", strip=True)
        self.assertIn("VVSM · IE00BMC38736 0.00% 0.00% 0.00%", final_text)
        self.assertIn("L0CK · IE00BG0J4C88 10.16% 10.16% 0.00%", final_text)
        self.assertEqual(surface._section(soup, "7").get_text(" ", strip=True), history_before)
        self.assertEqual(surface._section(soup, "14").get_text(" ", strip=True), scenario_before)

    def test_authority_boundary_fails_closed(self):
        payload = state()
        payload["official_portfolio"]["real_broker_execution"] = True
        with self.assertRaisesRegex(RuntimeError, "authority boundary"):
            surface.contract(payload)


if __name__ == "__main__":
    unittest.main()
