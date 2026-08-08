from __future__ import annotations

import unittest

from runtime.compact_etf_eu_policy_transition_surface import compact_section


def order_table(rows: str) -> str:
    return (
        '<table class="wide-table allocator-order-table"><thead><tr><th>x</th></tr></thead>'
        f'<tbody>{rows}</tbody></table>'
    )


def legacy_block(tickers: list[str], language: str = "nl") -> str:
    heading = "Behandeling huidige posities" if language == "nl" else "Treatment of current positions"
    rows = "".join(f"<tr><td>{ticker}</td><td>1</td><td>HOLD</td><td>role</td></tr>" for ticker in tickers)
    return (
        f'<h3>{heading}</h3>'
        '<table class="data-table allocator-legacy-table"><tbody>' + rows + '</tbody></table>'
        '<div class="alignment-summary">summary</div>'
    )


class PolicyTransitionCompactionTests(unittest.TestCase):
    def test_activated_four_position_surface_accepts_one_new_buy_intent(self):
        rows = (
            '<tr><td>Cash</td><td>VVSM</td><td>Fase-1 schaduwintentie</td></tr>'
            '<tr><td>Cash</td><td>Cybersecurityweerbaarheid</td><td>Geblokkeerd / uitgesteld</td></tr>'
            '<tr><td>Cash</td><td>Biotech</td><td>Geblokkeerd / uitgesteld</td></tr>'
        )
        body = order_table(rows) + legacy_block(["L0CK", "VWCE", "EUNA", "SXR8"])
        compacted, removed, legacy_removed, funded_compacted = compact_section(body, "nl")
        self.assertEqual(removed, 2)
        self.assertTrue(legacy_removed)
        self.assertTrue(funded_compacted)
        self.assertIn("VVSM", compacted)
        self.assertNotIn("Cybersecurityweerbaarheid", compacted)
        self.assertIn("L0CK is al gefinancierd", compacted)
        self.assertIn("Bestaande posities blijven ongewijzigd", compacted)

    def test_legacy_three_position_surface_still_requires_two_actionable_rows(self):
        rows = (
            '<tr><td>Cash</td><td>VVSM</td><td>Fase-1 schaduwintentie</td></tr>'
            '<tr><td>Cash</td><td>LOCK</td><td>Fase-1 schaduwintentie</td></tr>'
            '<tr><td>Cash</td><td>Biotech</td><td>Geblokkeerd / uitgesteld</td></tr>'
        )
        body = order_table(rows) + legacy_block(["VWCE", "EUNA", "SXR8"])
        compacted, removed, _, funded_compacted = compact_section(body, "nl")
        self.assertEqual(removed, 1)
        self.assertFalse(funded_compacted)
        self.assertIn("VVSM", compacted)
        self.assertIn("LOCK", compacted)

    def test_one_actionable_row_without_funded_l0ck_fails_closed(self):
        rows = (
            '<tr><td>Cash</td><td>VVSM</td><td>Fase-1 schaduwintentie</td></tr>'
            '<tr><td>Cash</td><td>Cybersecurityweerbaarheid</td><td>Geblokkeerd / uitgesteld</td></tr>'
        )
        body = order_table(rows) + legacy_block(["VWCE", "EUNA", "SXR8"])
        with self.assertRaisesRegex(RuntimeError, "Expected 2 actionable Stage-1 rows"):
            compact_section(body, "nl")


if __name__ == "__main__":
    unittest.main()
