from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag
from weasyprint import HTML

L0CK_ISIN = "IE00BG0J4C88"
VVSM_ISIN = "IE00BMC38736"
FUNDED = {"VWCE", "EUNA", "SXR8", "L0CK"}
SECTIONS = ["1", "2", "2A", "4", "5", "6", "8", "9", "10", "11", "12", "13"]


def _norm(value: Any) -> str:
    value = str(value or "").strip().upper()
    return "L0CK" if value == "LOCK" else value


def _pct(value: float, lang: str) -> str:
    text = f"{float(value):.2f}%"
    return text.replace(".", ",") if lang == "nl" else text


def _euro(value: float, lang: str) -> str:
    text = f"{float(value):,.2f}"
    if lang == "nl":
        text = text.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"€ {text}"


def contract(state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    portfolio = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    rows = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    positions: dict[str, dict[str, Any]] = {}
    for row in rows:
        ticker = _norm(row.get("ticker") or row.get("exchange_ticker"))
        if ticker in positions:
            raise RuntimeError(f"Duplicate authoritative position: {ticker}")
        weight = row.get("weight_pct", row.get("current_weight_pct"))
        if ticker and weight is not None:
            item = dict(row)
            item["client_weight_pct"] = float(weight)
            positions[ticker] = item
    if set(positions) != FUNDED or int(portfolio.get("position_count") or 0) != 4:
        raise RuntimeError(f"Current client-state contract requires funded set {sorted(FUNDED)}")
    stage = state.get("stage_1_decision") if isinstance(state.get("stage_1_decision"), dict) else {}
    if {_norm(x) for x in stage.get("activated_tickers") or []} != {"L0CK"}:
        raise RuntimeError("Current client-state contract requires L0CK activated")
    if {_norm(x) for x in stage.get("remaining_monitored_tickers") or []} != {"VVSM"}:
        raise RuntimeError("Current client-state contract requires VVSM monitored")
    if portfolio.get("model_portfolio_only") is not True or portfolio.get("real_broker_execution") is not False:
        raise RuntimeError("Current client-state authority boundary invalid")
    cash = float(portfolio.get("cash_eur") or 0)
    nav = float(portfolio.get("nav_eur") or 0)
    if nav <= 0:
        raise RuntimeError("Authoritative NAV missing or non-positive")
    cash_weight = portfolio.get("cash_weight_pct")
    cash_weight = float(cash_weight) if cash_weight is not None else cash / nav * 100.0
    if not 0 <= cash_weight <= 100.000001:
        raise RuntimeError("Authoritative cash weight outside [0,100]")
    return {"cash_eur": cash, "nav_eur": nav, "cash_weight_pct": cash_weight}, positions


def _section(soup: BeautifulSoup, suffix: str) -> Tag:
    target = f"section-{suffix}".casefold()
    section = next((s for s in soup.find_all("section") if str(s.get("id") or "").casefold() == target), None)
    if not isinstance(section, Tag):
        raise RuntimeError(f"Required client section missing: {suffix}")
    return section


def _row(scope: Tag, needle: str) -> Tag:
    needle = needle.casefold()
    row = next((r for r in scope.select("tbody tr") if needle in r.get_text(" ", strip=True).casefold()), None)
    if not isinstance(row, Tag):
        raise RuntimeError(f"Required row missing: {needle}")
    return row


def _cells(row: Tag, minimum: int, label: str) -> list[Tag]:
    cells = row.find_all("td", recursive=False)
    if len(cells) < minimum:
        raise RuntimeError(f"{label} has unexpected column count: {len(cells)}")
    return cells


def _set(cells: list[Tag], index: int, value: str) -> None:
    cells[index].clear()
    cells[index].string = value


def _sync_cockpit(soup: BeautifulSoup, c: dict[str, Any], lang: str) -> None:
    section = _section(soup, "2A")
    cards = section.select("div.cockpit-grid > div.cockpit-card")
    if len(cards) < 4:
        raise RuntimeError("Section 2A production cockpit contract missing")
    values = (
        [
            "4 officiële modelposities; L0CK actief.",
            "L0CK actief; VVSM gemonitord en niet gefinancierd.",
            f"Cash {_euro(c['cash_eur'], lang)} ({_pct(c['cash_weight_pct'], lang)}); geen nieuwe brokerorder uitgevoerd.",
        ]
        if lang == "nl"
        else [
            "4 official model positions; L0CK active.",
            "L0CK active; VVSM monitored and unfunded.",
            f"Cash {_euro(c['cash_eur'], lang)} ({_pct(c['cash_weight_pct'], lang)}); no new broker order placed.",
        ]
    )
    for card, value in zip(cards[-3:], values):
        card.clear()
        card.string = value


def _sync_5_6(soup: BeautifulSoup, lang: str) -> None:
    row = _row(_section(soup, "5"), "legacy")
    cells = _cells(row, 2, "Section 5 legacy row")
    _set(cells, 1, (
        "De drie oudere kernposities VWCE, EUNA en SXR8 blijven historische portefeuillecontext; L0CK is inmiddels de vierde actieve modelpositie."
        if lang == "nl" else
        "The three older core positions VWCE, EUNA and SXR8 remain historical portfolio context; L0CK is now the fourth active model position."
    ))
    section6 = _section(soup, "6")
    p = section6.find("p")
    if not isinstance(p, Tag):
        raise RuntimeError("Section 6 conclusion paragraph missing")
    p.clear()
    p.string = (
        "De gedeelde Weekly ETF-engine levert strategie en kansen. De EU-laag koppelt deze aan exacte UCITS-handelslijnen en houdt rapportage, bewijs en allocatie gescheiden. De actuele rapportuitkomst bevat vier officiële modelposities; L0CK is actief, VVSM blijft gemonitord en niet gefinancierd, en in deze review is geen nieuwe brokerorder uitgevoerd."
        if lang == "nl" else
        "The shared Weekly ETF engine supplies strategy and opportunities. The EU layer maps them to exact UCITS trading lines and keeps reporting, evidence and allocation separate. The current report outcome contains four official model positions; L0CK is active, VVSM remains monitored and unfunded, and no new broker order was placed in this review."
    )


def _sync_8(soup: BeautifulSoup, positions: dict[str, dict[str, Any]], lang: str) -> None:
    tables = _section(soup, "8").find_all("table")
    if len(tables) < 2:
        raise RuntimeError("Section 8 tables missing")
    satellite = _row(tables[0], "satell")
    cells = _cells(satellite, 3, "Section 8 satellite row")
    _set(cells, 1, "Deels geïmplementeerd / onderwogen" if lang == "nl" else "Partially implemented / underweight")
    _set(cells, 2, (
        "L0CK is gefinancierd; overige gepromoveerde donor-exposures zijn niet automatisch gefinancierd."
        if lang == "nl" else
        "L0CK is funded; other promoted donor exposures are not automatically funded."
    ))
    row = _row(tables[1], "L0CK")
    cells = _cells(row, 7, "Section 8 L0CK alignment row")
    current = positions["L0CK"]["client_weight_pct"]
    target = float(cells[1].get_text(" ", strip=True).replace("%", "").replace(",", "."))
    _set(cells, 2, _pct(current, lang))
    _set(cells, 3, _pct(current - target, lang))
    _set(cells, 5, "Strategische gewichtsafwijking" if lang == "nl" else "Strategic weight gap")
    _set(cells, 6, (
        "Donordoel is strategiecontext; L0CK is reeds gefinancierd en extra kapitaal vereist afzonderlijke autorisatie."
        if lang == "nl" else
        "Donor target is strategy context; L0CK is already funded and additional capital requires separate authorization."
    ))


def _sync_9_11(soup: BeautifulSoup, lang: str) -> None:
    row9 = _row(_section(soup, "9"), L0CK_ISIN)
    cells9 = _cells(row9, 7, "Section 9 L0CK row")
    _set(cells9, 2, "Actieve gefinancierde modelpositie" if lang == "nl" else "Active funded model position")
    _set(cells9, 4, "Aanhouden; geen nieuwe brokerorder" if lang == "nl" else "Hold; no new broker order")
    if lang == "nl":
        _set(cells9, 1, "Biedt blootstelling aan digitale infrastructuur met minder directe halfgeleidercycliciteit.")
    row11 = _row(_section(soup, "11"), L0CK_ISIN)
    cells11 = _cells(row11, 5, "Section 11 L0CK row")
    _set(cells11, 2, "Actieve gefinancierde modelpositie" if lang == "nl" else "Active funded model position")
    _set(cells11, 3, (
        "Exacte identiteit, KID en actuele slotkoers zijn bevestigd; L0CK is reeds gefinancierd."
        if lang == "nl" else
        "Exact identity, KID and current completed close are confirmed; L0CK is already funded."
    ))
    _set(cells11, 4, "Aanhouden; geen nieuwe brokerorder" if lang == "nl" else "Hold; no new broker order")


def _sync_10(soup: BeautifulSoup, positions: dict[str, dict[str, Any]], lang: str) -> None:
    tables = _section(soup, "10").find_all("table")
    if len(tables) < 2:
        raise RuntimeError("Section 10 tables missing")
    for ticker in FUNDED:
        row = _row(tables[0], ticker)
        cells = _cells(row, 6, f"Section 10 {ticker} row")
        _set(cells, 1, "Aanhouden" if lang == "nl" else "Hold")
        if ticker == "L0CK":
            _set(cells, 3, "Actieve positie beoordelen" if lang == "nl" else "Review active position")
            _set(cells, 5, "Geen nieuwe brokerorder; bewaken binnen strategie- en risicokaders" if lang == "nl" else "No new broker order; monitor within strategy and risk limits")
    for ticker in ("VWCE", "EUNA", "SXR8"):
        row = _row(tables[1], ticker)
        _set(_cells(row, 2, f"Section 10 overlap {ticker}"), 1, _pct(positions[ticker]["client_weight_pct"], lang))


def _sync_12(soup: BeautifulSoup, lang: str) -> None:
    table = _section(soup, "12").find("table")
    if not isinstance(table, Tag):
        raise RuntimeError("Section 12 table missing")
    row = next(iter(table.select("tbody tr")), None)
    if not isinstance(row, Tag):
        raise RuntimeError("Section 12 action row missing")
    cells = _cells(row, 6, "Section 12 action row")
    _set(cells, 3, (
        "Geen; VVSM blijft gemonitord en niet gefinancierd; L0CK is reeds actief"
        if lang == "nl" else
        "None; VVSM remains monitored and unfunded; L0CK is already active"
    ))
    _set(cells, 5, "Actuele beslissing: geen nieuwe transactie" if lang == "nl" else "Current decision: no new trade")


def _sync_13(soup: BeautifulSoup, c: dict[str, Any], positions: dict[str, dict[str, Any]], lang: str) -> None:
    table = _section(soup, "13").find("table", class_="final-alignment-table")
    if not isinstance(table, Tag):
        raise RuntimeError("Section 13 final action table missing")
    zero = _pct(0, lang)
    vvsm = _cells(_row(table, VVSM_ISIN), 10, "Section 13 VVSM row")
    for idx in (2, 3, 4):
        _set(vvsm, idx, zero)
    _set(vvsm, 5, "Bewaken; geen allocatie" if lang == "nl" else "Monitor; no allocation")
    _set(vvsm, 6, "Geen toewijzing" if lang == "nl" else "No allocation")
    _set(vvsm, 8, (
        "Donordoel blijft strategiecontext; VVSM is gemonitord en niet gefinancierd."
        if lang == "nl" else
        "Donor target remains strategy context; VVSM is monitored and unfunded."
    ))
    _set(vvsm, 9, "Geen uitvoering" if lang == "nl" else "No execution")

    l0ck = _cells(_row(table, L0CK_ISIN), 10, "Section 13 L0CK exposure row")
    lw = _pct(positions["L0CK"]["client_weight_pct"], lang)
    _set(l0ck, 2, lw)
    _set(l0ck, 3, lw)
    _set(l0ck, 4, zero)
    _set(l0ck, 5, "Aanhouden; geen nieuwe brokerorder" if lang == "nl" else "Hold; no new broker order")
    _set(l0ck, 6, "Geen toewijzing" if lang == "nl" else "No allocation")
    _set(l0ck, 8, (
        "Donordoel 19,02% is strategiecontext; L0CK is gefinancierd en op actuele slotkoers gewaardeerd; extra kapitaal is niet geautoriseerd."
        if lang == "nl" else
        "Donor target 19.02% is strategy context; L0CK is funded and valued at the current completed close; additional capital is not authorized."
    ))
    _set(l0ck, 9, "Modelpositie actief; geen uitvoering" if lang == "nl" else "Model position active; no execution")

    cash = _cells(_row(table, "CASH"), 10, "Section 13 cash row")
    cw = _pct(c["cash_weight_pct"], lang)
    _set(cash, 2, cw)
    _set(cash, 3, cw)
    _set(cash, 4, zero)
    _set(cash, 8, "Cashreserve blijft ongewijzigd; geen nieuwe brokerorder in deze review." if lang == "nl" else "Cash reserve remains unchanged; no new broker order in this review.")

    for ticker in FUNDED:
        rows = [r for r in table.select("tbody tr") if _cells(r, 1, "Section 13 row")[0].get_text(" ", strip=True).upper() == ticker]
        if len(rows) != 1:
            raise RuntimeError(f"Section 13 incumbent row count mismatch for {ticker}: {len(rows)}")
        cells = _cells(rows[0], 10, f"Section 13 incumbent {ticker}")
        weight = _pct(positions[ticker]["client_weight_pct"], lang)
        _set(cells, 2, weight)
        _set(cells, 3, weight)
        _set(cells, 4, zero)
        _set(cells, 5, "Huidige positie aanhouden" if lang == "nl" else "Hold current position")
        _set(cells, 6, "Geen wijziging" if lang == "nl" else "No change")
        _set(cells, 8, "Officiële positie blijft ongewijzigd in de actuele beoordeling." if lang == "nl" else "Official position remains unchanged in the current review.")


def validate(soup: BeautifulSoup, c: dict[str, Any], positions: dict[str, dict[str, Any]], lang: str) -> None:
    current_text = " ".join(_section(soup, sid).get_text(" ", strip=True) for sid in ["5", "6", "8", "9", "10", "11", "12", "13"]).casefold()
    forbidden = [
        "three official positions", "drie officiële posities", "l0ck promoted but blocked", "l0ck gepromoveerd maar geblokkeerd",
        "l0ck remain blocked", "l0ck blijven geblokkeerde", "currently promoted, but not deployable", "actueel gepromoveerd, maar niet inzetbaar",
    ]
    if any(token in current_text for token in forbidden):
        raise RuntimeError("Current client sections still contain stale three-position/blocked-L0CK language")
    cockpit = _section(soup, "2A").get_text(" ", strip=True)
    if _pct(c["cash_weight_pct"], lang) not in cockpit:
        raise RuntimeError("Section 2A cash weight is not derived from authoritative cash/NAV")
    table13 = _section(soup, "13").find("table", class_="final-alignment-table")
    if not isinstance(table13, Tag):
        raise RuntimeError("Section 13 validation table missing")
    vvsm = _cells(_row(table13, VVSM_ISIN), 10, "Section 13 VVSM validation")
    if any(vvsm[i].get_text(" ", strip=True) != _pct(0, lang) for i in (2, 3, 4)):
        raise RuntimeError("Section 13 gives VVSM an executable target")
    l0ck = _cells(_row(table13, L0CK_ISIN), 10, "Section 13 L0CK validation")
    expected = _pct(positions["L0CK"]["client_weight_pct"], lang)
    if l0ck[2].get_text(" ", strip=True) != expected or l0ck[3].get_text(" ", strip=True) != expected or l0ck[4].get_text(" ", strip=True) != _pct(0, lang):
        raise RuntimeError("Section 13 L0CK current/target weights contradict authoritative state")


def synchronize_html(html_path: Path, pdf_path: Path, state: dict[str, Any], lang: str) -> dict[str, Any]:
    c, positions = contract(state)
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    _sync_cockpit(soup, c, lang)
    _sync_5_6(soup, lang)
    _sync_8(soup, positions, lang)
    _sync_9_11(soup, lang)
    _sync_10(soup, positions, lang)
    _sync_12(soup, lang)
    _sync_13(soup, c, positions, lang)
    validate(soup, c, positions, lang)
    html_path.write_text(str(soup), encoding="utf-8")
    HTML(filename=str(html_path), base_url=str(html_path.parent.resolve())).write_pdf(str(pdf_path))
    return c


def synchronize_manifest(manifest_path: Path, state_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    state = json.loads(state_path.read_text(encoding="utf-8"))
    c, _ = contract(state)
    for lang in ("nl", "en"):
        record = manifest.get("languages", {}).get(lang)
        if not isinstance(record, dict):
            raise RuntimeError(f"Manifest language record missing: {lang}")
        synchronize_html(Path(record["html"]), Path(record["pdf"]), state, lang)
        record["activated_client_state_contract"] = "authoritative_four_position_current_state_v1"
    if isinstance(manifest.get("activated_front_page_contract"), dict):
        manifest["activated_front_page_contract"]["cash_weight_pct"] = c["cash_weight_pct"]
    manifest["activated_client_state_contract"] = {
        "applied": True,
        "state_path": str(state_path),
        "official_position_count": 4,
        "cash_eur": c["cash_eur"],
        "cash_weight_pct": c["cash_weight_pct"],
        "activated_tickers": ["L0CK"],
        "remaining_monitored_tickers": ["VVSM"],
        "synchronized_sections": SECTIONS,
        "historical_strategy_context_preserved": ["7"],
        "non_actionable_allocator_context_preserved": ["14"],
        "portfolio_mutation": False,
        "real_broker_execution": False,
        "production_delivery_authority": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("ETF_EU_CURRENT_CLIENT_STATE_OK | positions=4 | active=L0CK | monitored=VVSM | cash_weight=derived | sections=5,6,8,9,10,11,12,13 | history=7 | scenario=14")
