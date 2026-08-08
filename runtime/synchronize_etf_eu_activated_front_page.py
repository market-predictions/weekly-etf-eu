from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag
from weasyprint import HTML


L0CK_ISIN = "IE00BG0J4C88"
EXPECTED_ACTIVATED_TICKERS = {"VWCE", "EUNA", "SXR8", "L0CK"}


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def normalize_ticker(value: Any) -> str:
    ticker = str(value or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def euro(value: Any, language: str) -> str:
    rendered = f"{float(value or 0):,.2f}"
    if language == "nl":
        rendered = rendered.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"€ {rendered}"


def authoritative_contract(state: dict[str, Any]) -> dict[str, Any]:
    portfolio = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    tickers = {
        normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
        for row in positions
        if normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
    }
    stage = state.get("stage_1_decision") if isinstance(state.get("stage_1_decision"), dict) else {}
    activated = {
        normalize_ticker(value)
        for value in stage.get("activated_tickers") or []
        if normalize_ticker(value)
    }
    monitored = {
        normalize_ticker(value)
        for value in stage.get("remaining_monitored_tickers") or []
        if normalize_ticker(value)
    }
    declared_count = int(portfolio.get("position_count") or 0)
    if tickers != EXPECTED_ACTIVATED_TICKERS:
        raise RuntimeError(f"Front-page activation contract requires exact funded set {sorted(EXPECTED_ACTIVATED_TICKERS)}; got {sorted(tickers)}")
    if declared_count != len(positions) or declared_count != 4:
        raise RuntimeError(f"Front-page activation contract requires four official positions; got {declared_count}")
    if activated != {"L0CK"}:
        raise RuntimeError(f"Front-page activation contract requires L0CK activation; got {sorted(activated)}")
    if monitored != {"VVSM"}:
        raise RuntimeError(f"Front-page activation contract requires VVSM monitored; got {sorted(monitored)}")
    if portfolio.get("model_portfolio_only") is not True or portfolio.get("real_broker_execution") is not False:
        raise RuntimeError("Front-page activation authority boundary is invalid")
    return {
        "position_count": declared_count,
        "cash_eur": float(portfolio.get("cash_eur") or 0),
        "tickers": tickers,
        "activated": activated,
        "monitored": monitored,
    }


def _replace_list_item(section: Tag, prefixes: tuple[str, ...], replacement: str) -> None:
    target = next(
        (
            item for item in section.find_all("li")
            if item.get_text(" ", strip=True).startswith(prefixes)
        ),
        None,
    )
    if not isinstance(target, Tag):
        raise RuntimeError(f"Front-page summary item missing for prefixes {prefixes}")
    target.clear()
    target.string = replacement


def synchronize_summary(soup: BeautifulSoup, contract: dict[str, Any], language: str) -> None:
    section = soup.find("section", id="section-1")
    if not isinstance(section, Tag):
        raise RuntimeError("Section 1 missing")
    count = int(contract["position_count"])
    cash = euro(contract["cash_eur"], language)
    if language == "nl":
        portfolio_line = f"Officiële modelportefeuille: {count} posities en {cash} cash."
        outcome_line = "Actuele uitkomst: L0CK is actief als vierde modelpositie; VVSM blijft gemonitord en niet gefinancierd."
        _replace_list_item(section, ("Officiële modelportefeuille:",), portfolio_line)
        _replace_list_item(section, ("Actuele uitkomst:",), outcome_line)
    else:
        portfolio_line = f"Official model portfolio: {count} positions and {cash} cash."
        outcome_line = "Current outcome: L0CK is active as the fourth model position; VVSM remains monitored and unfunded."
        _replace_list_item(section, ("Official model portfolio:",), portfolio_line)
        _replace_list_item(section, ("Current outcome:",), outcome_line)


def synchronize_l0ck_action_row(soup: BeautifulSoup, language: str) -> None:
    section = soup.find("section", id="section-2")
    if not isinstance(section, Tag):
        raise RuntimeError("Section 2 missing")
    table = section.find("table", class_="production-opportunity-table")
    if not isinstance(table, Tag):
        raise RuntimeError("Section 2 portfolio-action table missing")
    row = next(
        (candidate for candidate in table.select("tbody tr") if L0CK_ISIN in candidate.get_text(" ", strip=True)),
        None,
    )
    if not isinstance(row, Tag):
        raise RuntimeError("Section 2 L0CK action row missing")
    cells = row.find_all("td", recursive=False)
    if len(cells) < 6:
        raise RuntimeError("Section 2 L0CK action row has unexpected column count")
    if language == "nl":
        cells[4].string = "Modelpositie actief"
        cells[5].string = "L0CK is als vierde modelpositie geactiveerd; in deze review is geen nieuwe brokerorder uitgevoerd."
    else:
        cells[4].string = "Model position active"
        cells[5].string = "L0CK is active as the fourth model position; no new broker order was placed in this review."


def validate_front_page(soup: BeautifulSoup, contract: dict[str, Any], language: str) -> None:
    section_1 = soup.find("section", id="section-1")
    section_2 = soup.find("section", id="section-2")
    if not isinstance(section_1, Tag) or not isinstance(section_2, Tag):
        raise RuntimeError("Front-page sections missing after synchronization")
    section_1_text = " ".join(section_1.get_text(" ", strip=True).split())
    expected_count = f"{contract['position_count']} posities" if language == "nl" else f"{contract['position_count']} positions"
    if expected_count not in section_1_text:
        raise RuntimeError("Section 1 official position count does not match authoritative state")
    stale_counts = ("3 posities", "3 positions")
    if any(value in section_1_text for value in stale_counts):
        raise RuntimeError("Section 1 still contains stale three-position claim")
    if "L0CK" not in section_1_text or "VVSM" not in section_1_text:
        raise RuntimeError("Section 1 activated/monitored ticker summary is incomplete")
    if "geblokkeerde ruimte blijft cash" in section_1_text.casefold() or "blocked capacity remains cash" in section_1_text.casefold():
        raise RuntimeError("Section 1 still contains stale blocked-capacity outcome")

    table = section_2.find("table", class_="production-opportunity-table")
    row = next(
        (candidate for candidate in table.select("tbody tr") if L0CK_ISIN in candidate.get_text(" ", strip=True)),
        None,
    ) if isinstance(table, Tag) else None
    if not isinstance(row, Tag):
        raise RuntimeError("Section 2 L0CK action row missing after synchronization")
    row_text = " ".join(row.get_text(" ", strip=True).split()).casefold()
    required = ("modelpositie", "actief") if language == "nl" else ("model", "position", "active")
    if not all(token in row_text for token in required):
        raise RuntimeError("Section 2 L0CK row is not visibly active")
    if "geblokkeerd" in row_text or "blocked" in row_text or "retain cash" in row_text or "cash behouden" in row_text:
        raise RuntimeError("Section 2 L0CK row still contains stale blocked/retain-cash status")
    if ("geen nieuwe brokerorder uitgevoerd" if language == "nl" else "no new broker order was placed") not in row_text:
        raise RuntimeError("Section 2 L0CK row does not preserve broker-execution boundary")


def synchronize_html(html_path: Path, pdf_path: Path, state: dict[str, Any], language: str) -> None:
    contract = authoritative_contract(state)
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    synchronize_summary(soup, contract, language)
    synchronize_l0ck_action_row(soup, language)
    validate_front_page(soup, contract, language)
    html_path.write_text(str(soup), encoding="utf-8")
    HTML(filename=str(html_path), base_url=str(html_path.parent.resolve())).write_pdf(str(pdf_path))


def synchronize_manifest(manifest_path: Path, state_path: Path) -> None:
    manifest = load_object(manifest_path)
    state = load_object(state_path)
    for language in ("nl", "en"):
        record = manifest.get("languages", {}).get(language)
        if not isinstance(record, dict):
            raise RuntimeError(f"Manifest language record missing: {language}")
        synchronize_html(Path(str(record["html"])), Path(str(record["pdf"])), state, language)
        record["activated_front_page_contract"] = "authoritative_four_position_v1"
    manifest["activated_front_page_contract"] = {
        "applied": True,
        "state_path": str(state_path),
        "official_position_count": 4,
        "activated_tickers": ["L0CK"],
        "remaining_monitored_tickers": ["VVSM"],
        "portfolio_mutation": False,
        "real_broker_execution": False,
        "production_delivery_authority": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("ETF_EU_ACTIVATED_FRONT_PAGE_OK | positions=4 | active=L0CK | monitored=VVSM | broker_execution=false")


def main() -> None:
    parser = argparse.ArgumentParser(description="Synchronize activated ETF EU front page with authoritative model state")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--state", type=Path, required=True)
    args = parser.parse_args()
    synchronize_manifest(args.manifest, args.state)


if __name__ == "__main__":
    main()
