from __future__ import annotations

import unittest

from bs4 import BeautifulSoup

from runtime.apply_etf_eu_routine_valuation_to_client_report import build_current_performance


class ClientPerformanceReconciliationTests(unittest.TestCase):
    def _soup(self, lang: str):
        title = "Rendement huidige ETF-posities" if lang == "nl" else "Current ETF-position performance"
        html = f"""
        <html><body>
          <section id="section-7A"><div class="section-head"><span>7A</span><h2>{title}</h2></div>
            <table><tbody>
              <tr><td>World core</td><td>Vanguard thesis</td><td>VWCE</td><td>old</td></tr>
              <tr><td>Bond stabilizer</td><td>iShares bond thesis</td><td>EUNA</td><td>old</td></tr>
              <tr><td>US overweight</td><td>iShares S&amp;P thesis</td><td>SXR8</td><td>old</td></tr>
            </tbody></table>
          </section>
        </body></html>
        """
        return BeautifulSoup(html, "html.parser")

    def _state(self):
        return {
            "official_portfolio": {
                "positions": [
                    {
                        "ticker": "VWCE", "weight_pct": 24.741634,
                        "unrealized_pnl_pct": -1.427532, "unrealized_pnl_eur": -356.36,
                        "portfolio_contribution_pct_nav": -0.200411,
                    },
                    {
                        "ticker": "EUNA", "weight_pct": 7.487637,
                        "unrealized_pnl_pct": -0.671686, "unrealized_pnl_eur": -50.36,
                        "portfolio_contribution_pct_nav": -0.018259,
                    },
                    {
                        "ticker": "SXR8", "weight_pct": 7.000505,
                        "unrealized_pnl_pct": -1.938029, "unrealized_pnl_eur": -137.60,
                        "portfolio_contribution_pct_nav": -0.084058,
                    },
                ]
            }
        }

    def test_dutch_performance_table_uses_fresh_state_values(self):
        soup = self._soup("nl")
        build_current_performance(soup, self._state(), "nl")
        rows = soup.select("#section-7A tbody tr")
        self.assertEqual(len(rows), 3)
        cells = [[cell.get_text(" ", strip=True) for cell in row.find_all("td", recursive=False)] for row in rows]
        self.assertEqual(cells[0][0:3], ["World core", "Vanguard thesis", "VWCE"])
        self.assertEqual(cells[0][3:], ["24,74%", "n.v.t.", "n.v.t.", "n.v.t.", "-1,43%", "€ -356,36", "-0,20%"])
        self.assertEqual(cells[1][3:], ["7,49%", "n.v.t.", "n.v.t.", "n.v.t.", "-0,67%", "€ -50,36", "-0,02%"])
        self.assertEqual(cells[2][3:], ["7,00%", "n.v.t.", "n.v.t.", "n.v.t.", "-1,94%", "€ -137,60", "-0,08%"])
        self.assertNotIn("-157,04", soup.get_text(" "))
        self.assertNotIn("-32,20", soup.get_text(" "))
        self.assertNotIn("-54,00", soup.get_text(" "))

    def test_english_performance_table_uses_fresh_state_values(self):
        soup = self._soup("en")
        build_current_performance(soup, self._state(), "en")
        cells = [
            [cell.get_text(" ", strip=True) for cell in row.find_all("td", recursive=False)]
            for row in soup.select("#section-7A tbody tr")
        ]
        self.assertEqual(cells[0][3:], ["24.74%", "n/a", "n/a", "n/a", "-1.43%", "€ -356.36", "-0.20%"])
        self.assertEqual(cells[2][3:], ["7.00%", "n/a", "n/a", "n/a", "-1.94%", "€ -137.60", "-0.08%"])


if __name__ == "__main__":
    unittest.main()
