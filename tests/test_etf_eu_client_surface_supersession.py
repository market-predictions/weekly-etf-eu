from __future__ import annotations

import pytest
from bs4 import BeautifulSoup

from runtime.add_etf_eu_activated_allocation_surface_v2 import _enforce_authoritative_client_surface


STATE = {
    "official_portfolio": {
        "cash_eur": 50208.40,
        "positions": [
            {"ticker": "VWCE", "current_weight_pct": 25.0},
            {"ticker": "EUNA", "current_weight_pct": 7.5},
            {"ticker": "SXR8", "current_weight_pct": 7.0},
            {"ticker": "L0CK", "current_weight_pct": 10.15},
        ],
    },
    "stage_1_decision": {"activated_tickers": ["L0CK"]},
}


@pytest.mark.parametrize(
    ("language", "section6", "active_weight", "stale_row", "policy_rows", "required_count"),
    [
        (
            "en",
            "The current outcome contains three official positions.",
            "10.15%",
            "<tr><td>L0CK</td><td>0.00%</td><td>0.00%</td><td>Hold in Stage 1</td></tr>",
            """
              <tr><td>Migration</td><td>Staged cash-first migration (fixed 50%)</td></tr>
              <tr><td>Minimum cash</td><td>35.00%</td></tr>
              <tr><td>Maximum new ETF</td><td>15.00%</td></tr>
            """,
            "4 official positions",
        ),
        (
            "nl",
            "De actuele uitkomst bevat drie officiële posities.",
            "10,15%",
            "<tr><td>L0CK</td><td>0,00%</td><td>0,00%</td><td>Aanhouden in fase 1</td></tr>",
            """
              <tr><td>Migratie</td><td>Staged cash-first migration (fixed 50%)</td></tr>
              <tr><td>Minimale cash</td><td>35,00%</td></tr>
              <tr><td>Maximale nieuwe ETF</td><td>15,00%</td></tr>
            """,
            "4 officiële posities",
        ),
    ],
)
def test_authoritative_state_supersedes_stale_client_fragments(
    language: str,
    section6: str,
    active_weight: str,
    stale_row: str,
    policy_rows: str,
    required_count: str,
) -> None:
    soup = BeautifulSoup(
        f"""
        <section id="section-6"><p>{section6}</p></section>
        <section id="section-13"><table><tbody>
          <tr><td>VWCE</td><td>25.00%</td></tr>
          <tr><td>EUNA</td><td>7.50%</td></tr>
          <tr><td>SXR8</td><td>7.00%</td></tr>
          <tr><td>L0CK</td><td>{active_weight}</td><td>Model position active</td></tr>
          {stale_row}
        </tbody></table></section>
        <section id="section-14"><p>Current allocator control</p><table><tbody>
          {policy_rows}
          <tr><td>Authority</td><td>State-bound review</td></tr>
        </tbody></table></section>
        """,
        "html.parser",
    )

    _enforce_authoritative_client_surface(soup, STATE, language)

    visible = soup.get_text(" ", strip=True)
    assert required_count in visible
    assert visible.casefold().count("l0ck") == 1
    assert "fixed 50%" not in visible.casefold()
    assert "minimum cash" not in visible.casefold()
    assert "maximum new etf" not in visible.casefold()
    assert "minimale cash" not in visible.casefold()
    assert "maximale nieuwe etf" not in visible.casefold()
    assert "state-bound review" in visible


def test_duplicate_funded_row_without_authoritative_weight_fails_closed() -> None:
    state = {
        "official_portfolio": {
            "positions": [{"ticker": "L0CK"}],
        }
    }
    soup = BeautifulSoup(
        """
        <section id="section-6"><p>4 official positions</p></section>
        <section id="section-13"><table><tbody>
          <tr><td>L0CK</td><td>10.15%</td></tr>
          <tr><td>L0CK</td><td>0.00%</td></tr>
        </tbody></table></section>
        <section id="section-14"><p>State-bound allocation review</p></section>
        """,
        "html.parser",
    )

    with pytest.raises(RuntimeError, match="without authoritative weight"):
        _enforce_authoritative_client_surface(soup, state, "en")
