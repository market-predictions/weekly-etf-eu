from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag
from weasyprint import HTML


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"Expected object: {path}")
    return data


def sec(soup: BeautifulSoup, sid: str) -> Tag:
    value = soup.find("section", id=sid)
    if not isinstance(value, Tag):
        raise RuntimeError(f"Missing section {sid}")
    return value


def reset(section: Tag) -> None:
    head = section.find(class_="section-head")
    if not isinstance(head, Tag):
        raise RuntimeError(f"Missing section header {section.get('id')}")
    for child in list(section.children):
        if child is not head:
            child.extract()


def tag(soup: BeautifulSoup, name: str, text: str | None = None) -> Tag:
    value = soup.new_tag(name)
    if text is not None:
        value.string = text
    return value


def euro(value: Any, lang: str) -> str:
    amount = float(value or 0)
    text = f"{amount:,.2f}"
    if lang == "nl":
        text = text.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"€ {text}"


def pct(value: Any, lang: str) -> str:
    text = f"{float(value or 0):.2f}%"
    return text.replace(".", ",") if lang == "nl" else text


def action(row: dict[str, Any], lang: str) -> tuple[str, str]:
    exposure = str(row.get("exposure_id") or "")
    target = float(row.get("donor_target_weight_pct") or 0)
    blockers = row.get("blockers_nl") if lang == "nl" else row.get("blockers_en")
    detail = "; ".join(str(x) for x in blockers or [] if str(x))
    if exposure == "cyber_security":
        return (
            ("Geblokkeerd; cash behouden", "Actueel gepromoveerd, maar actuele bewijs- en donorpoorten slagen niet.")
            if lang == "nl"
            else ("Blocked; retain cash", "Currently promoted, but current evidence and donor gates do not pass.")
        )
    if target > 0:
        return (
            ("Bewaken; niet uitvoerbaar", f"Donordoel {pct(target, lang)}; buiten de huidige uitvoerbare set. {detail}")
            if lang == "nl"
            else ("Monitor; not actionable", f"Donor target {pct(target, lang)}; outside the current actionable set. {detail}")
        )
    return (
        ("Volgen; geen allocatie", "Gepromoveerd als onderzoekskans, maar zonder huidig donordoel.")
        if lang == "nl"
        else ("Monitor; no allocation", "Promoted as a research opportunity, but without a current donor target.")
    )


def build_summary(soup: BeautifulSoup, state: dict[str, Any], lang: str) -> None:
    section = sec(soup, "section-1")
    reset(section)
    strategy = state["strategy"]
    portfolio = state["official_portfolio"]
    promotion = {
        str(row.get("exchange_symbol")): row.get("currently_promoted") is True
        for row in state.get("stage_1_review_candidates") or []
    }
    lines = (
        [
            f"Primair regime: {strategy.get('regime') or '—'}",
            "Actuele kansenset: 6 donor-exposures en 6 exacte UCITS-koppelingen.",
            f"Officiële modelportefeuille: 3 posities en {euro(portfolio.get('cash_eur'), lang)} cash.",
            f"Reviewcontinuïteit: VVSM actueel gepromoveerd = {'ja' if promotion.get('VVSM') else 'nee'}; L0CK = {'ja' if promotion.get('L0CK') else 'nee'}.",
            "Actuele uitkomst: geen wijziging; geblokkeerde ruimte blijft cash.",
        ]
        if lang == "nl"
        else [
            f"Primary regime: {strategy.get('regime') or '—'}",
            "Current opportunity set: 6 donor exposures and 6 exact UCITS mappings.",
            f"Official model portfolio: 3 positions and {euro(portfolio.get('cash_eur'), lang)} cash.",
            f"Review continuity: VVSM currently promoted = {'yes' if promotion.get('VVSM') else 'no'}; L0CK = {'yes' if promotion.get('L0CK') else 'no'}.",
            "Current outcome: no change; blocked capacity remains cash.",
        ]
    )
    ul = tag(soup, "ul")
    for line in lines:
        ul.append(tag(soup, "li", line))
    section.append(ul)


def build_actions(soup: BeautifulSoup, state: dict[str, Any], lang: str) -> None:
    section = sec(soup, "section-2")
    reset(section)
    headers = (
        ["Rang", "Kans", "UCITS-handelslijn", "Donordoel", "Actuele status", "Reden"]
        if lang == "nl"
        else ["Rank", "Opportunity", "UCITS trading line", "Donor target", "Current status", "Reason"]
    )
    table = tag(soup, "table")
    table["class"] = ["wide-table", "production-opportunity-table"]
    thead = tag(soup, "thead")
    tr = tag(soup, "tr")
    for heading in headers:
        tr.append(tag(soup, "th", heading))
    thead.append(tr)
    table.append(thead)
    tbody = tag(soup, "tbody")
    rows = sorted(state.get("promoted_exposures") or [], key=lambda x: int(x.get("shared_rank") or 999))
    for item in rows:
        status, reason = action(item, lang)
        tr = tag(soup, "tr")
        values = [
            str(item.get("shared_rank") or "—"),
            str(item.get("lane_name") or "—"),
            f"{item.get('exchange_symbol') or '—'} · {item.get('fund_name') or '—'} · {item.get('isin') or '—'}",
            pct(item.get("donor_target_weight_pct"), lang),
            status,
            reason,
        ]
        for value in values:
            tr.append(tag(soup, "td", value))
        tbody.append(tr)
    table.append(tbody)
    section.append(table)


def build_cockpit(soup: BeautifulSoup, state: dict[str, Any], lang: str) -> None:
    section = sec(soup, "section-2A")
    reset(section)
    cash = euro(state["official_portfolio"].get("cash_eur"), lang)
    cards = (
        [
            "6 actuele donor-exposures; 6 exacte UCITS-koppelingen.",
            "3 officiële posities; geen portefeuillewijziging.",
            "VVSM niet actueel gepromoveerd; L0CK gepromoveerd maar geblokkeerd.",
            f"Cash blijft {cash} zolang vereiste poorten niet slagen.",
        ]
        if lang == "nl"
        else [
            "6 current donor exposures; 6 exact UCITS mappings.",
            "3 official positions; no portfolio change.",
            "VVSM is not currently promoted; L0CK is promoted but blocked.",
            f"Cash remains {cash} while required gates do not pass.",
        ]
    )
    grid = tag(soup, "div")
    grid["class"] = ["cockpit-grid"]
    for text in cards:
        card = tag(soup, "div", text)
        card["class"] = ["cockpit-card"]
        grid.append(card)
    section.append(grid)


def build_bottom_line(soup: BeautifulSoup, lang: str) -> None:
    section = sec(soup, "section-6")
    reset(section)
    text = (
        "De gedeelde Weekly ETF-engine levert strategie en kansen. De EU-laag koppelt deze aan exacte UCITS-handelslijnen en houdt rapportage, bewijs en allocatie gescheiden. De actuele rapportuitkomst bevat drie officiële posities, zes gekoppelde kansen en geen portefeuillewijziging."
        if lang == "nl"
        else "The shared Weekly ETF engine supplies strategy and opportunities. The EU layer maps them to exact UCITS trading lines and keeps reporting, evidence and allocation separate. The current report outcome contains three official positions, six mapped opportunities and no portfolio change."
    )
    section.append(tag(soup, "p", text))


def normalize_history(soup: BeautifulSoup, lang: str) -> None:
    replacements = (
        {
            "Three-position funded-aware non-delivery preview": "Officiële waardering van de driepositiemodelportefeuille",
            "Initial cash-only EU/UCITS bootstrap state": "Initiële cashpositie vóór portefeuilleopbouw",
        }
        if lang == "nl"
        else {
            "Three-position funded-aware non-delivery preview": "Official valuation of the three-position model portfolio",
            "Initial cash-only EU/UCITS bootstrap state": "Initial cash position before portfolio deployment",
        }
    )
    for node in list(sec(soup, "section-7").find_all(string=True)):
        updated = str(node)
        for old, new in replacements.items():
            updated = updated.replace(old, new)
        if updated != str(node):
            node.replace_with(updated)


def build_next_inputs(soup: BeautifulSoup, lang: str) -> None:
    section = sec(soup, "section-16")
    reset(section)
    box = tag(soup, "div")
    box["class"] = ["continuity-box", "client-next-run-inputs"]
    box.append(tag(soup, "strong", "Benodigde input voor de volgende beoordeling" if lang == "nl" else "Required input for the next review"))
    lines = (
        [
            "Bouw de meest recente gedeelde strategie en kansenset opnieuw op.",
            "Herbeoordeel de zes actuele UCITS-koppelingen en nieuwe promoties.",
            "Ververs exacte KID-, slotkoers-, bied/laat-, omvang- en liquiditeitsdata vóór een allocatiewijziging.",
            "Behoud de officiële portefeuille wanneer een vereiste poort niet slaagt.",
            "Maak rapportlevering als aparte, gecontroleerde stap.",
        ]
        if lang == "nl"
        else [
            "Rebuild the latest shared strategy and opportunity set.",
            "Re-underwrite the six current UCITS mappings and new promotions.",
            "Refresh exact KID, completed-close, bid/ask, size and liquidity data before an allocation change.",
            "Preserve the official portfolio whenever a required gate does not pass.",
            "Handle report delivery as a separate controlled step.",
        ]
    )
    ul = tag(soup, "ul")
    for line in lines:
        ul.append(tag(soup, "li", line))
    box.append(ul)
    section.append(box)


def apply(manifest_path: Path, state_path: Path) -> None:
    manifest = load(manifest_path)
    state = load(state_path)
    for lang in ("nl", "en"):
        record = manifest["languages"][lang]
        html_path = Path(record["html"])
        pdf_path = Path(record["pdf"])
        soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
        build_summary(soup, state, lang)
        build_actions(soup, state, lang)
        build_cockpit(soup, state, lang)
        build_bottom_line(soup, lang)
        normalize_history(soup, lang)
        build_next_inputs(soup, lang)
        output = str(soup)
        html_path.write_text(output, encoding="utf-8")
        HTML(string=output, base_url=str(html_path.parent.resolve())).write_pdf(str(pdf_path))
        record["wp10_client_executive_surface"] = "state_driven_v1"
    manifest["wp10_client_executive_surface"] = {
        "applied": True,
        "sections": ["1", "2", "2A", "6", "7", "16"],
        "official_state_changed": False,
        "delivery_performed": False,
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
