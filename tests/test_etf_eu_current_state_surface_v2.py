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


def test_dutch_section_9_full_sentences_are_translated_at_final_writer(tmp_path) -> None:
    html_path = tmp_path / "nl.html"
    pdf_path = tmp_path / "nl.pdf"
    rows = "".join(
        f"<tr><td>{index}</td><td>{sentence}</td></tr>"
        for index, sentence in enumerate(surface.NL_SECTION9_SENTENCE_MAP, start=1)
    )
    html_path.write_text(
        f"<html><body><section id='section-9'><table><tbody>{rows}</tbody></table></section></body></html>",
        encoding="utf-8",
    )
    surface._sync_nl_section9_language(html_path, pdf_path)
    rendered = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser").get_text(" ", strip=True)
    for source, translation in surface.NL_SECTION9_SENTENCE_MAP.items():
        assert source not in rendered
        assert translation in rendered
    assert pdf_path.is_file()
    assert pdf_path.stat().st_size > 0


def test_delegated_patch_path_does_not_recurse() -> None:
    soup = _soup()
    positions = {"L0CK": {"client_weight_pct": 10.158455}}
    original = surface.legacy._sync_8
    surface.legacy._sync_8 = surface._sync_8_with_authoritative_coverage
    try:
        surface.legacy._sync_8(soup, positions, "en")
    finally:
        surface.legacy._sync_8 = original
    summary = soup.select_one("#section-8 .alignment-summary").get_text(" ", strip=True)
    assert "10.16%" in summary
    assert "10.41%" not in summary
    vvsm = next(row for row in soup.select("#section-8 tbody tr") if "VVSM" in row.get_text(" ", strip=True))
    assert "Monitored / unfunded" in vvsm.get_text(" ", strip=True)


def test_section_13_resync_accepts_canonical_l0ck_exposure_without_legacy_incumbent() -> None:
    soup = BeautifulSoup(
        """
        <html><body><section id="section-13"><table class="final-alignment-table"><tbody>
          <tr><td>AI compute</td><td>VVSM · IE00BMC38736</td><td>0.00%</td><td>14.88%</td><td>+14.88%</td><td>Review</td><td>Cash</td><td>3.92</td><td>stale</td><td>Blocked</td></tr>
          <tr><td>Cyber</td><td>L0CK · IE00BG0J4C88</td><td>10.16%</td><td>10.16%</td><td>0.00%</td><td>Hold</td><td>No allocation</td><td>4.93</td><td>authoritative</td><td>active</td></tr>
          <tr><td>Cash</td><td>CASH</td><td>49.95%</td><td>49.95%</td><td>0.00%</td><td>Hold</td><td>No allocation</td><td>—</td><td>stale</td><td>No change</td></tr>
          <tr><td>VWCE</td><td>Fund</td><td>25.24%</td><td>25.24%</td><td>0.00%</td><td>Hold</td><td>No change</td><td>—</td><td>stale</td><td>No change</td></tr>
          <tr><td>EUNA</td><td>Fund</td><td>7.46%</td><td>7.46%</td><td>0.00%</td><td>Hold</td><td>No change</td><td>—</td><td>stale</td><td>No change</td></tr>
          <tr><td>SXR8</td><td>Fund</td><td>7.19%</td><td>7.19%</td><td>0.00%</td><td>Hold</td><td>No change</td><td>—</td><td>stale</td><td>No change</td></tr>
        </tbody></table></section></body></html>
        """,
        "html.parser",
    )
    contract = {"cash_weight_pct": 49.95}
    positions = {
        "VWCE": {"client_weight_pct": 25.244729},
        "EUNA": {"client_weight_pct": 7.456904},
        "SXR8": {"client_weight_pct": 7.187384},
        "L0CK": {"client_weight_pct": 10.158455},
    }

    surface._sync_13_after_client_surface_supersession(soup, contract, positions, "en")

    table = soup.select_one("#section-13 table.final-alignment-table")
    rows = table.select("tbody tr")
    ticker_l0ck_rows = [
        row for row in rows if row.find_all("td", recursive=False)[0].get_text(" ", strip=True).upper() == "L0CK"
    ]
    assert ticker_l0ck_rows == []
    exposure_rows = [row for row in rows if surface.legacy.L0CK_ISIN in row.get_text(" ", strip=True)]
    assert len(exposure_rows) == 1
    exposure_text = exposure_rows[0].get_text(" ", strip=True)
    assert "10.16% 10.16% 0.00%" in exposure_text
    assert "Model position active; no execution" in exposure_text

# CI retrigger: validate persisted V3 package lineage on exact PR head.
