from __future__ import annotations

import pytest
from bs4 import BeautifulSoup

from runtime.add_etf_eu_activated_allocation_surface import synchronize_authoritative_portfolio_copy


STATE = {
    "official_portfolio": {
        "cash_eur": 50208.40,
        "positions": [
            {"ticker": "VWCE"},
            {"ticker": "EUNA"},
            {"ticker": "SXR8"},
            {"ticker": "L0CK"},
        ],
    },
    "stage_1_decision": {"activated_tickers": ["L0CK"]},
}


@pytest.mark.parametrize(
    ("language", "html", "required", "forbidden"),
    [
        (
            "en",
            """
            <section id="section-1"><ul>
              <li>Official model portfolio: 3 positions and € 50,208.40 cash.</li>
              <li>Current outcome: no change; blocked capacity remains cash.</li>
            </ul></section>
            <section id="section-2"><table><tbody><tr>
              <td>1</td><td>Cybersecurity</td><td>L0CK · IE00BG0J4C88</td><td>19.02%</td>
              <td>Blocked; retain cash</td><td>Currently promoted, but current evidence and donor gates do not pass.</td>
            </tr></tbody></table></section>
            <section id="section-2A"><div class="cockpit-grid">
              <div class="cockpit-card">6 current donor exposures.</div>
              <div class="cockpit-card">3 official positions; no portfolio change.</div>
              <div class="cockpit-card">VVSM is not currently promoted; L0CK is promoted but blocked.</div>
              <div class="cockpit-card">Cash remains € 50,208.40 while required gates do not pass.</div>
            </div></section>
            """,
            (
                "Official model portfolio: 4 positions",
                "L0CK has been added as the fourth model position",
                "Active model position",
                "4 official model positions; L0CK is activated",
                "L0CK is active as a model position",
            ),
            ("3 official positions", "no portfolio change", "promoted but blocked", "Blocked; retain cash"),
        ),
        (
            "nl",
            """
            <section id="section-1"><ul>
              <li>Officiële modelportefeuille: 3 posities en € 50.208,40 cash.</li>
              <li>Actuele uitkomst: geen wijziging; geblokkeerde ruimte blijft cash.</li>
            </ul></section>
            <section id="section-2"><table><tbody><tr>
              <td>1</td><td>Cybersecurity</td><td>L0CK · IE00BG0J4C88</td><td>19,02%</td>
              <td>Geblokkeerd; cash behouden</td><td>Actueel gepromoveerd, maar actuele bewijs- en donorpoorten slagen niet.</td>
            </tr></tbody></table></section>
            <section id="section-2A"><div class="cockpit-grid">
              <div class="cockpit-card">6 actuele donor-exposures.</div>
              <div class="cockpit-card">3 officiële posities; geen portefeuillewijziging.</div>
              <div class="cockpit-card">VVSM niet actueel gepromoveerd; L0CK gepromoveerd maar geblokkeerd.</div>
              <div class="cockpit-card">Cash blijft € 50.208,40 zolang vereiste poorten niet slagen.</div>
            </div></section>
            """,
            (
                "Officiële modelportefeuille: 4 posities",
                "L0CK is toegevoegd als vierde modelpositie",
                "Actieve modelpositie",
                "4 officiële modelposities; L0CK is in deze modelallocatie geactiveerd",
                "L0CK is actief als modelpositie",
            ),
            ("3 officiële posities", "geen portefeuillewijziging", "gepromoveerd maar geblokkeerd", "Geblokkeerd; cash behouden"),
        ),
    ],
)
def test_authoritative_activated_portfolio_copy_is_bilingual_and_not_stale(
    language: str,
    html: str,
    required: tuple[str, ...],
    forbidden: tuple[str, ...],
) -> None:
    soup = BeautifulSoup(html, "html.parser")

    synchronize_authoritative_portfolio_copy(soup, STATE, language)

    visible = soup.get_text(" ", strip=True)
    for text in required:
        assert text in visible
    for text in forbidden:
        assert text not in visible
