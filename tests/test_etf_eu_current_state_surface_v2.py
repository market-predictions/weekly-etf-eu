from __future__ import annotations

from bs4 import BeautifulSoup

from runtime.synchronize_etf_eu_current_state_surface_v2 import _sync_8_with_authoritative_coverage


def _soup() -> BeautifulSoup:
    return BeautifulSoup(
        """
        <html><body><section id="section-8">
          <table><tbody>
            <tr><td>Thematic satellites</td><td>Underweight / blocked</td><td>stale</td></tr>
          </tbody></table>
          <div class="alignment-summary">
            Exact donor-exposure coverage in the current EU portfolio: <strong>10.41%</strong>.
            This measures the same exposures; broad core funds do not count as substitutes for another thematic exposure.
          </div>
          <table><tbody>
            <tr><td>Cybersecurity resilience</td><td>19.02%</td><td>0.00%</td><td>-19.02%</td><td>L0CK</td><td>Weight gap</td><td>stale</td></tr>
          </tbody></table>
        </section></body></html>
        """,
        "html.parser",
    )


def test_section_8_coverage_is_replaced_by_authoritative_l0ck_weight() -> None:
    soup = _soup()
    positions = {"L0CK": {"client_weight_pct": 10.158455}}
    _sync_8_with_authoritative_coverage(soup, positions, "en")
    summary = soup.select_one("#section-8 .alignment-summary").get_text(" ", strip=True)
    assert "10.16%" in summary
    assert "10.41%" not in summary
    row = soup.select_one("#section-8 table:nth-of-type(2) tbody tr").get_text(" ", strip=True)
    assert "10.16%" in row
    assert "-8.86%" in row


def test_dutch_section_8_coverage_uses_localized_authoritative_weight() -> None:
    soup = _soup()
    positions = {"L0CK": {"client_weight_pct": 10.158455}}
    _sync_8_with_authoritative_coverage(soup, positions, "nl")
    summary = soup.select_one("#section-8 .alignment-summary").get_text(" ", strip=True)
    assert "Exacte donor-exposuredekking" in summary
    assert "10,16%" in summary
    assert "10,41%" not in summary
