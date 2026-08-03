from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag
from weasyprint import HTML


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def sec(soup: BeautifulSoup, sid: str) -> Tag:
    value = soup.find("section", id=sid)
    if not isinstance(value, Tag):
        raise RuntimeError(f"Missing report section: {sid}")
    return value


def tag(soup: BeautifulSoup, name: str, text: str | None = None) -> Tag:
    value = soup.new_tag(name)
    if text is not None:
        value.string = text
    return value


def reset(section: Tag) -> None:
    head = section.find(class_="section-head")
    if not isinstance(head, Tag):
        raise RuntimeError(f"Section header missing: {section.get('id')}")
    for child in list(section.children):
        if child is not head:
            child.extract()


def euro(value: Any, lang: str, decimals: int = 2) -> str:
    text = f"{float(value or 0):,.{decimals}f}"
    if lang == "nl":
        text = text.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"€ {text}"


def pct(value: Any, lang: str) -> str:
    text = f"{float(value or 0):.2f}%"
    return text.replace(".", ",") if lang == "nl" else text


def signed_pct(value: Any, lang: str) -> str:
    number = float(value or 0)
    text = f"{number:+.2f}%" if number else "0.00%"
    return text.replace(".", ",") if lang == "nl" else text


def ticker(row: dict[str, Any]) -> str:
    return str(row.get("ticker") or row.get("exchange_ticker") or "").strip().upper()


def reconcile_report_date(soup: BeautifulSoup, state: dict[str, Any]) -> None:
    report_date = str(state.get("report_date") or "").strip()
    if not report_date:
        raise RuntimeError("Routine state report date is missing")
    hero_date = soup.find(class_="hero-date")
    if not isinstance(hero_date, Tag):
        raise RuntimeError("Report hero date is missing")
    hero_date.clear()
    hero_date.append(report_date)


def localize_latest_history_note(soup: BeautifulSoup, state: dict[str, Any], lang: str) -> None:
    report_date = str(state.get("report_date") or "").strip()
    section = sec(soup, "section-7")
    localized_note = (
        "Verse rungebonden waardering op basis van voltooide EUR-slotkoersen; officiële stukken en cash ongewijzigd."
        if lang == "nl"
        else "Fresh run-scoped valuation from completed EUR closes; official share quantities and cash unchanged."
    )
    for row in section.find_all("tr"):
        cells = row.find_all(["td", "th"], recursive=False)
        if len(cells) < 2 or cells[0].get_text(" ", strip=True) != report_date:
            continue
        cells[-1].clear()
        cells[-1].append(localized_note)
        return
    raise RuntimeError(f"Valuation-history row missing for report date {report_date} ({lang})")


def build_current_performance(soup: BeautifulSoup, state: dict[str, Any], lang: str) -> None:
    """Rebuild section 7A from the reconciled run-scoped valuation state.

    The source report contains historical placeholder values. Those values may not
    survive a fresh completed-close overlay. Segment and thesis labels are retained,
    while every numeric position field is replaced from the current state.
    """
    section = sec(soup, "section-7A")
    existing_labels: dict[str, tuple[str, str]] = {}
    for row in section.find_all("tr"):
        cells = row.find_all("td", recursive=False)
        if len(cells) < 3:
            continue
        symbol = cells[2].get_text(" ", strip=True).upper()
        if symbol:
            existing_labels[symbol] = (
                cells[0].get_text(" ", strip=True),
                cells[1].get_text(" ", strip=True),
            )

    reset(section)
    portfolio = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    headers = (
        [
            "Portefeuillesegment",
            "Beleggingsthese",
            "ETF",
            "Gewicht %",
            "1w rendement",
            "1m rendement",
            "3m rendement",
            "Sinds instap",
            "P/L EUR",
            "Bijdrage %",
        ]
        if lang == "nl"
        else [
            "Portfolio segment",
            "Investment thesis",
            "ETF",
            "Weight %",
            "1w return",
            "1m return",
            "3m return",
            "Since entry",
            "P/L EUR",
            "Contribution %",
        ]
    )
    table = tag(soup, "table")
    table["class"] = ["wide-table", "routine-current-performance-table"]
    thead = tag(soup, "thead")
    header_row = tag(soup, "tr")
    for heading in headers:
        header_row.append(tag(soup, "th", heading))
    thead.append(header_row)
    table.append(thead)

    tbody = tag(soup, "tbody")
    missing_labels: list[str] = []
    for position in positions:
        symbol = ticker(position)
        labels = existing_labels.get(symbol)
        if labels is None:
            missing_labels.append(symbol)
            labels = (symbol, str(position.get("fund_name") or position.get("name") or symbol))
        unavailable = "n.v.t." if lang == "nl" else "n/a"
        values = [
            labels[0],
            labels[1],
            symbol,
            pct(position.get("weight_pct"), lang),
            unavailable,
            unavailable,
            unavailable,
            signed_pct(position.get("unrealized_pnl_pct"), lang),
            euro(position.get("unrealized_pnl_eur"), lang),
            signed_pct(position.get("portfolio_contribution_pct_nav"), lang),
        ]
        row = tag(soup, "tr")
        for value in values:
            row.append(tag(soup, "td", value))
        tbody.append(row)
    table.append(tbody)
    section.append(table)

    if missing_labels:
        raise RuntimeError(f"Performance-table source labels missing for: {', '.join(missing_labels)} ({lang})")


def build_current_positions(soup: BeautifulSoup, state: dict[str, Any], lang: str) -> None:
    section = sec(soup, "section-15")
    reset(section)
    portfolio = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    headers = (
        ["Positie", "ISIN", "Stukken", "Slotkoers", "Koersdatum", "Waarde", "Gewicht", "Actuele actie"]
        if lang == "nl"
        else ["Position", "ISIN", "Shares", "Completed close", "Close date", "Value", "Weight", "Current action"]
    )
    table = tag(soup, "table")
    table["class"] = ["wide-table", "routine-current-position-table"]
    thead = tag(soup, "thead")
    tr = tag(soup, "tr")
    for heading in headers:
        tr.append(tag(soup, "th", heading))
    thead.append(tr)
    table.append(thead)
    tbody = tag(soup, "tbody")
    for row in positions:
        symbol = ticker(row)
        action = "Aanhouden; geen wijziging" if lang == "nl" else "Hold; no change"
        values = [
            symbol,
            str(row.get("isin") or "—"),
            f"{float(row.get('shares') or 0):,.0f}".replace(",", ".") if lang == "nl" else f"{float(row.get('shares') or 0):,.0f}",
            euro(row.get("current_price_eur"), lang, 4 if symbol == "EUNA" else 2),
            str(row.get("pricing_close_date") or "—"),
            euro(row.get("market_value_eur"), lang),
            pct(row.get("weight_pct"), lang),
            action,
        ]
        tr = tag(soup, "tr")
        for value in values:
            tr.append(tag(soup, "td", value))
        tbody.append(tr)
    table.append(tbody)
    section.append(table)

    nav = float(portfolio.get("nav_eur") or 0)
    cash = float(portfolio.get("cash_eur") or 0)
    cash_weight = cash / nav * 100.0 if nav else 0.0
    note = tag(
        soup,
        "div",
        (
            f"Runwaardering: NAV {euro(nav, lang)} · cash {euro(cash, lang)} ({pct(cash_weight, lang)}) · officiële stukken ongewijzigd."
            if lang == "nl"
            else f"Run valuation: NAV {euro(nav, lang)} · cash {euro(cash, lang)} ({pct(cash_weight, lang)}) · official share quantities unchanged."
        ),
    )
    note["class"] = ["note-box", "routine-valuation-summary"]
    section.append(note)


def add_valuation_lineage(soup: BeautifulSoup, state: dict[str, Any], lang: str) -> None:
    section = sec(soup, "section-7")
    portfolio = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    dates = portfolio.get("pricing_close_dates") or []
    text = (
        f"Actuele rapportwaardering {state.get('report_date')}: NAV {euro(portfolio.get('nav_eur'), lang)}; prijsdatum/-data {', '.join(str(x) for x in dates) or '—'}. Officiële stukken en cash zijn niet gewijzigd."
        if lang == "nl"
        else f"Current report valuation {state.get('report_date')}: NAV {euro(portfolio.get('nav_eur'), lang)}; pricing close date(s) {', '.join(str(x) for x in dates) or '—'}. Official share quantities and cash are unchanged."
    )
    box = tag(soup, "div", text)
    box["class"] = ["continuity-box", "routine-valuation-lineage"]
    head = section.find(class_="section-head")
    if isinstance(head, Tag):
        head.insert_after(box)
    else:
        section.insert(0, box)


def apply(manifest_path: Path, state_path: Path) -> None:
    manifest = load(manifest_path)
    state = load(state_path)
    if state.get("validation", {}).get("fresh_run_valuation_applied") is not True:
        raise RuntimeError("Fresh routine valuation was not applied to convergence state")
    for lang in ("nl", "en"):
        record = (manifest.get("languages") or {}).get(lang)
        if not isinstance(record, dict):
            raise RuntimeError(f"Missing report language: {lang}")
        html_path = Path(str(record.get("html") or ""))
        pdf_path = Path(str(record.get("pdf") or ""))
        soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
        reconcile_report_date(soup, state)
        localize_latest_history_note(soup, state, lang)
        build_current_performance(soup, state, lang)
        build_current_positions(soup, state, lang)
        add_valuation_lineage(soup, state, lang)
        output = str(soup)
        html_path.write_text(output, encoding="utf-8")
        HTML(string=output, base_url=str(html_path.parent.resolve())).write_pdf(str(pdf_path))
        record["wp11_routine_valuation_reconciliation"] = "fresh_eur_close_overlay_v3_report_date_localization_and_performance"
    manifest["wp11_routine_valuation_reconciliation"] = {
        "applied": True,
        "report_date": state.get("report_date"),
        "pricing_close_dates": state.get("official_portfolio", {}).get("pricing_close_dates"),
        "hero_report_date_reconciled": True,
        "valuation_history_note_localized": True,
        "current_performance_table_reconciled": True,
        "portfolio_mutation": False,
        "ledger_write": False,
        "production_delivery_authority": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(manifest_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--state", type=Path, required=True)
    args = parser.parse_args()
    apply(args.manifest, args.state)


if __name__ == "__main__":
    main()
