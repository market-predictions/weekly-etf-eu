from __future__ import annotations

from bs4 import BeautifulSoup

from tools.validate_etf_eu_production_converged_report_v2 import monitored_row_is_non_actionable


def _row(text: str):
    soup = BeautifulSoup(f"<table><tbody><tr>{text}</tr></tbody></table>", "html.parser")
    return soup.find("tr")


def test_english_monitored_unfunded_zero_allocation_row_passes() -> None:
    row = _row(
        "<td>AI compute</td><td>VVSM · IE00BMC38736</td>"
        "<td>0.00%</td><td>0.00%</td><td>0.00%</td>"
        "<td>Monitor; no allocation</td><td>No allocation</td><td>3.92</td>"
        "<td>VVSM is monitored and unfunded.</td><td>No execution</td>"
    )
    valid, blockers = monitored_row_is_non_actionable("en", row)
    assert valid is True
    assert blockers == []


def test_dutch_monitored_unfunded_zero_allocation_row_passes() -> None:
    row = _row(
        "<td>AI compute</td><td>VVSM · IE00BMC38736</td>"
        "<td>0,00%</td><td>0,00%</td><td>0,00%</td>"
        "<td>Bewaken; geen allocatie</td><td>Geen toewijzing</td><td>3,92</td>"
        "<td>VVSM is gemonitord en niet gefinancierd.</td><td>Geen uitvoering</td>"
    )
    valid, blockers = monitored_row_is_non_actionable("nl", row)
    assert valid is True
    assert blockers == []


def test_monitored_row_with_nonzero_target_fails() -> None:
    row = _row(
        "<td>AI compute</td><td>VVSM · IE00BMC38736</td>"
        "<td>0.00%</td><td>14.88%</td><td>+14.88%</td>"
        "<td>Monitor</td><td>No allocation</td><td>3.92</td>"
        "<td>VVSM is monitored and unfunded.</td><td>No execution</td>"
    )
    valid, blockers = monitored_row_is_non_actionable("en", row)
    assert valid is False
    assert "current/target/delta are not all zero" in blockers


def test_monitored_row_with_buy_instruction_fails() -> None:
    row = _row(
        "<td>AI compute</td><td>VVSM · IE00BMC38736</td>"
        "<td>0.00%</td><td>0.00%</td><td>0.00%</td>"
        "<td>Monitor; buy later</td><td>No allocation</td><td>3.92</td>"
        "<td>VVSM is monitored and unfunded.</td><td>No execution</td>"
    )
    valid, blockers = monitored_row_is_non_actionable("en", row)
    assert valid is False
    assert any("buy" in blocker for blocker in blockers)
