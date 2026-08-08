from bs4 import BeautifulSoup

from runtime.add_etf_eu_activated_allocation_surface import (
    synchronize_activated_final_action_row,
)


def _state() -> dict:
    return {
        "stage_1_decision": {
            "value": "partially_activated",
            "activated_tickers": ["L0CK"],
            "remaining_monitored_tickers": ["VVSM"],
        }
    }


def _html(status: str, action: str) -> BeautifulSoup:
    return BeautifulSoup(
        f"""
        <html><body>
          <section id="section-13">
            <table><tbody>
              <tr>
                <td>L0CK</td>
                <td>IE00BG0J4C88</td>
                <td>{status}</td>
                <td>{action}</td>
              </tr>
            </tbody></table>
          </section>
        </body></html>
        """,
        "html.parser",
    )


def test_english_activated_row_loses_blocked_status() -> None:
    soup = _html("Blocked", "Retain cash")

    synchronize_activated_final_action_row(soup, _state(), "en")

    row_text = soup.select_one("#section-13 tbody tr").get_text(" ", strip=True).lower()
    assert "blocked" not in row_text
    assert "active" in row_text
    assert "model" in row_text


def test_dutch_activated_row_loses_blocked_status() -> None:
    soup = _html("Geblokkeerd", "Cash aanhouden")

    synchronize_activated_final_action_row(soup, _state(), "nl")

    row_text = soup.select_one("#section-13 tbody tr").get_text(" ", strip=True).lower()
    assert "geblokkeerd" not in row_text
    assert "actief" in row_text
    assert "model" in row_text


def test_nonactivated_state_does_not_rewrite_row() -> None:
    soup = _html("Blocked", "Retain cash")
    state = {
        "stage_1_decision": {
            "value": "blocked",
            "activated_tickers": [],
            "remaining_monitored_tickers": ["L0CK", "VVSM"],
        }
    }

    synchronize_activated_final_action_row(soup, state, "en")

    row_text = soup.select_one("#section-13 tbody tr").get_text(" ", strip=True).lower()
    assert "blocked" in row_text
    assert "retain cash" in row_text
