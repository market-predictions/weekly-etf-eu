from __future__ import annotations

from bs4 import BeautifulSoup

from runtime import synchronize_etf_eu_current_state_surface_v2 as surface


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
            <tr><td>AI compute and semiconductors</td><td>25.20%</td><td>0.00%</td><td>-25.20%</td><td>VVSM</td><td>Target exposure missing</td><td>current pricing basis missing</td></tr>
          </tbody></table>
        </section></body></html>
        """,
        "html.parser",
    )


def test_section_8_coverage_is_replaced_by_authoritative_l0ck_weight() -> None:
    soup = _soup()
    positions = {"L0CK": {"client_weight_pct": 10.158455}}
    surface._sync_8_with_authoritative_coverage(soup, positions, "en")
    summary = soup.select_one("#section-8 .alignment-summary").get_text(" ", strip=True)
    assert "10.16%" in summary
    assert "10.41%" not in summary
    row = soup.select_one("#section-8 table:nth-of-type(2) tbody tr").get_text(" ", strip=True)
    assert "10.16%" in row
    assert "-8.86%" in row


def test_english_vvsm_row_uses_monitored_unfunded_current_close_semantics() -> None:
    soup = _soup()
    positions = {"L0CK": {"client_weight_pct": 10.158455}}
    surface._sync_8_with_authoritative_coverage(soup, positions, "en")
    vvsm = next(row for row in soup.select("#section-8 tbody tr") if "VVSM" in row.get_text(" ", strip=True))
    text = vvsm.get_text(" ", strip=True)
    assert "Monitored / unfunded" in text
    assert "Current completed close available" in text
    assert "strategy/promotion gate has not passed" in text
    assert "current pricing basis missing" not in text
    # Donor target and zero current exposure remain strategy context; no hidden allocation rewrite.
    assert "25.20%" in text
    assert "0.00%" in text


def test_dutch_section_8_coverage_and_vvsm_semantics_are_localized() -> None:
    soup = _soup()
    positions = {"L0CK": {"client_weight_pct": 10.158455}}
    surface._sync_8_with_authoritative_coverage(soup, positions, "nl")
    summary = soup.select_one("#section-8 .alignment-summary").get_text(" ", strip=True)
    assert "Exacte donor-exposuredekking" in summary
    assert "10,16%" in summary
    assert "10,41%" not in summary
    vvsm = next(row for row in soup.select("#section-8 tbody tr") if "VVSM" in row.get_text(" ", strip=True))
    text = vvsm.get_text(" ", strip=True)
    assert "Gemonitord / niet gefinancierd" in text
    assert "Actuele slotkoers beschikbaar" in text
    assert "strategie-/promotiepoort is niet geslaagd" in text
    assert "actuele prijsbasis ontbreekt" not in text
    assert "25.20%" in text
    assert "0.00%" in text


def test_delegated_patch_path_does_not_recurse() -> None:
    soup = _soup()
    positions = {"L0CK": {"client_weight_pct": 10.158455}}
    original = surface.legacy._sync_8
    surface.legacy._sync_8 = surface._sync_8_with_authoritative_coverage
    try:
        # This mirrors the delegation used by synchronize_manifest. Before the
        # captured-base fix, this call recursed until RecursionError.
        surface.legacy._sync_8(soup, positions, "en")
    finally:
        surface.legacy._sync_8 = original
    summary = soup.select_one("#section-8 .alignment-summary").get_text(" ", strip=True)
    assert "10.16%" in summary
    assert "10.41%" not in summary
    vvsm = next(row for row in soup.select("#section-8 tbody tr") if "VVSM" in row.get_text(" ", strip=True))
    assert "Monitored / unfunded" in vvsm.get_text(" ", strip=True)
