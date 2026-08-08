from __future__ import annotations

import unittest

from runtime.finalize_etf_eu_sister_report_nl_language import SECTION_16_MARKER, finalize


class DutchLanguageFinalizationTests(unittest.TestCase):
    def test_dynamic_promoted_exposure_count_is_translated(self):
        source = (
            '<html><body><section id="section-15"><p>5 promoted exposures are not represented</p></section>'
            + SECTION_16_MARKER
            + '><p>continuity evidence may remain English</p></section></body></html>'
        )
        result = finalize(source)
        client = result.split(SECTION_16_MARKER, 1)[0]
        self.assertIn("5 gepromoveerde exposures zijn niet vertegenwoordigd", client)
        self.assertNotIn("promoted exposures are not represented", client)

    def test_dynamic_reunderwriting_count_is_translated(self):
        source = (
            '<html><body><section id="section-15"><p>4 current positions require re-underwriting</p></section>'
            + SECTION_16_MARKER
            + '><p>continuity</p></section></body></html>'
        )
        result = finalize(source)
        client = result.split(SECTION_16_MARKER, 1)[0]
        self.assertIn("4 huidige posities moeten opnieuw worden beoordeeld", client)
        self.assertNotIn("current positions require re-underwriting", client)


if __name__ == "__main__":
    unittest.main()
