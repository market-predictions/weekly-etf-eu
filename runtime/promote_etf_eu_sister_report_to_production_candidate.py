from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag
from weasyprint import HTML


STAGE_1_ISINS = ("IE00BMC38736", "IE00BG0J4C88")


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def stage_1_index(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("isin") or "").upper(): row
        for row in state.get("stage_1_review_candidates") or []
        if isinstance(row, dict) and row.get("isin")
    }


def fmt_pct(value: Any, language: str) -> str:
    try:
        text = f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return "0,00%" if language == "nl" else "0.00%"
    return text.replace(".", ",") if language == "nl" else text


def joined(items: list[str]) -> str:
    return "; ".join(value for value in items if value)


def replace_text_nodes(soup: BeautifulSoup, replacements: dict[str, str]) -> None:
    for node in list(soup.find_all(string=True)):
        text = str(node)
        updated = text
        for old, new in replacements.items():
            updated = updated.replace(old, new)
        if updated != text:
            node.replace_with(updated)


def section(soup: BeautifulSoup, section_id: str) -> Tag:
    found = soup.find("section", id=section_id)
    if not isinstance(found, Tag):
        raise RuntimeError(f"Missing report section: {section_id}")
    return found


def table_rows(report_section: Tag) -> list[Tag]:
    return [row for row in report_section.select("tbody tr") if isinstance(row, Tag)]


def row_cells(row: Tag) -> list[Tag]:
    return [cell for cell in row.find_all("td", recursive=False) if isinstance(cell, Tag)]


def find_row_by_isin(report_section: Tag, isin: str) -> Tag | None:
    for row in table_rows(report_section):
        if isin in row.get_text(" ", strip=True):
            return row
    return None


def stage1_copy(review: dict[str, Any], language: str) -> dict[str, str]:
    donor_target = fmt_pct(review.get("donor_target_weight_pct"), language)
    blockers = review.get("blockers_nl") if language == "nl" else review.get("blockers_en")
    blocker_text = joined([str(value) for value in blockers or []])
    symbol = str(review.get("exchange_symbol") or review.get("portfolio_label") or "")
    currently_promoted = review.get("currently_promoted") is True
    if language == "nl":
        promotion_status = (
            "Actueel gepromoveerd, maar niet inzetbaar"
            if currently_promoted else
            "Niet in de actuele gepromoveerde set; eerdere fase-1 review blijft open"
        )
        return {
            "symbol": symbol,
            "status": promotion_status,
            "action": "Cash aanhouden en afhankelijkheden bewaken",
            "basis": f"Exacte identiteit en KID zijn bevestigd. {promotion_status}. Activering blijft geblokkeerd: {blocker_text}.",
            "explanation": f"Donordoel {donor_target}; uitvoerbaar doel 0,00%. {promotion_status}. {blocker_text}.",
            "override": "Geblokkeerd · geen transactie",
            "promotion": "Ja" if currently_promoted else "Nee",
            "donor_direction": "Geen nieuwe kooprichting",
        }
    promotion_status = (
        "Currently promoted, but not deployable"
        if currently_promoted else
        "Not in the current promoted set; the earlier Stage-1 review remains open"
    )
    return {
        "symbol": symbol,
        "status": promotion_status,
        "action": "Retain cash and monitor dependencies",
        "basis": f"Exact identity and KID are confirmed. {promotion_status}. Activation remains blocked: {blocker_text}.",
        "explanation": f"Donor target {donor_target}; actionable target 0.00%. {promotion_status}. {blocker_text}.",
        "override": "Blocked · no trade",
        "promotion": "Yes" if currently_promoted else "No",
        "donor_direction": "No fresh-add direction",
    }


def update_section_4(soup: BeautifulSoup, state: dict[str, Any], language: str) -> None:
    report_section = section(soup, "section-4")
    index = stage_1_index(state)
    for isin in STAGE_1_ISINS:
        row = find_row_by_isin(report_section, isin)
        if row is None:
            raise RuntimeError(f"Section 4 missing frozen Stage-1 review candidate {isin}")
        cells = row_cells(row)
        if len(cells) < 6:
            raise RuntimeError("Section 4 table contract changed")
        review = index[isin]
        copy = stage1_copy(review, language)
        cells[1].string = f"{copy['symbol']} · {review.get('fund_name') or ''} · {isin}"
        cells[3].string = copy["status"]
        cells[4].string = copy["action"]
        cells[5].string = copy["basis"]


def update_section_11(soup: BeautifulSoup, state: dict[str, Any], language: str) -> None:
    report_section = section(soup, "section-11")
    index = stage_1_index(state)
    for isin in STAGE_1_ISINS:
        row = find_row_by_isin(report_section, isin)
        if row is None:
            raise RuntimeError(f"Section 11 missing frozen Stage-1 review candidate {isin}")
        cells = row_cells(row)
        if len(cells) < 5:
            raise RuntimeError("Section 11 table contract changed")
        review = index[isin]
        copy = stage1_copy(review, language)
        cells[1].string = f"{copy['symbol']} · {review.get('fund_name') or ''} · {isin}"
        cells[2].string = copy["status"]
        cells[3].string = copy["basis"]
        cells[4].string = copy["action"]


def update_section_12(soup: BeautifulSoup, state: dict[str, Any], language: str) -> None:
    report_section = section(soup, "section-12")
    rows = table_rows(report_section)
    if not rows:
        raise RuntimeError("Section 12 rotation-plan row missing")
    cells = row_cells(rows[0])
    if len(cells) < 6:
        raise RuntimeError("Section 12 table contract changed")
    positions = state.get("official_portfolio", {}).get("positions") or []
    tickers = ", ".join(str(row.get("ticker") or row.get("exchange_ticker") or "") for row in positions)
    if language == "nl":
        values = [
            "Geen",
            "Geen",
            tickers,
            "Geen; VVSM en L0CK blijven geblokkeerde reviewkandidaten",
            "Geen",
            "Huidige beslissing: geen transactie",
        ]
    else:
        values = [
            "None",
            "None",
            tickers,
            "None; VVSM and L0CK remain blocked review candidates",
            "None",
            "Current decision: no trade",
        ]
    for cell, value in zip(cells[:6], values):
        cell.string = value


def update_section_13(soup: BeautifulSoup, state: dict[str, Any], language: str) -> None:
    report_section = section(soup, "section-13")
    index = stage_1_index(state)
    for isin in STAGE_1_ISINS:
        row = find_row_by_isin(report_section, isin)
        if row is None:
            raise RuntimeError(f"Section 13 missing frozen Stage-1 review candidate {isin}")
        cells = row_cells(row)
        if len(cells) < 10:
            raise RuntimeError("Section 13 table contract changed")
        review = index[isin]
        copy = stage1_copy(review, language)
        cells[1].string = f"{copy['symbol']} · {review.get('fund_name') or ''} · {isin}"
        cells[3].string = fmt_pct(review.get("actionable_target_weight_pct"), language)
        cells[4].string = fmt_pct(0, language)
        cells[5].string = copy["action"]
        cells[6].string = "Cash behouden" if language == "nl" else "Retain cash"
        cells[8].string = copy["explanation"]
        cells[9].string = copy["override"]

    for row in table_rows(report_section):
        cells = row_cells(row)
        if len(cells) >= 10 and not any(isin in row.get_text(" ", strip=True) for isin in STAGE_1_ISINS):
            cells[9].string = "Bewaken · geen transactie" if language == "nl" else "Monitor · no trade"


def new_tag(soup: BeautifulSoup, name: str, text: str | None = None, **attrs: Any) -> Tag:
    tag = soup.new_tag(name, **attrs)
    if text is not None:
        tag.string = text
    return tag


def replace_section_14(soup: BeautifulSoup, state: dict[str, Any], language: str) -> None:
    report_section = section(soup, "section-14")
    head = report_section.find(class_="section-head")
    if not isinstance(head, Tag):
        raise RuntimeError("Section 14 header missing")
    for child in list(report_section.children):
        if child is not head:
            child.extract()

    note_text = (
        "De allocator-scenario’s blijven analytische context. De actuele evidence- en donorpoorten blokkeren iedere nieuwe positie; de officiële portefeuille en cash blijven ongewijzigd."
        if language == "nl" else
        "Allocator scenarios remain analytical context. Current evidence and donor gates block every new position; the official portfolio and cash remain unchanged."
    )
    note = new_tag(soup, "div", note_text)
    note["class"] = ["continuity-box", "production-no-trade"]
    report_section.append(note)

    headers = (
        ["Handelslijn", "Actueel gepromoveerd", "Identiteit / KID", "Marktbewijs", "Donorrichting", "Actuele beslissing"]
        if language == "nl" else
        ["Trading line", "Currently promoted", "Identity / KID", "Market evidence", "Donor direction", "Current decision"]
    )
    table = new_tag(soup, "table")
    table["class"] = ["data-table", "production-decision-table"]
    thead = new_tag(soup, "thead")
    header_row = new_tag(soup, "tr")
    for value in headers:
        header_row.append(new_tag(soup, "th", value))
    thead.append(header_row)
    table.append(thead)
    tbody = new_tag(soup, "tbody")
    index = stage_1_index(state)
    for isin in STAGE_1_ISINS:
        review = index[isin]
        copy = stage1_copy(review, language)
        row = new_tag(soup, "tr")
        values = (
            [
                f"{copy['symbol']} · {isin}",
                copy["promotion"],
                "Geslaagd",
                "Slotkoers, bied/laat/omvang en liquiditeit ontbreken",
                copy["donor_direction"],
                "Geblokkeerd · cash aanhouden",
            ]
            if language == "nl" else
            [
                f"{copy['symbol']} · {isin}",
                copy["promotion"],
                "Passed",
                "Completed close, bid/ask/size and liquidity unavailable",
                copy["donor_direction"],
                "Blocked · retain cash",
            ]
        )
        for value in values:
            row.append(new_tag(soup, "td", value))
        tbody.append(row)
    table.append(tbody)
    report_section.append(table)

    footer_text = "Uitvoerbare handelsintenties: geen." if language == "nl" else "Executable trade intents: none."
    footer = new_tag(soup, "div", footer_text)
    footer["class"] = ["note-box"]
    report_section.append(footer)


def update_hero_and_notice(soup: BeautifulSoup, state: dict[str, Any], language: str) -> None:
    hero_type = soup.select_one(".hero-type")
    if not isinstance(hero_type, Tag):
        raise RuntimeError("Hero report type missing")
    hero_type.string = "Beleggersrapport" if language == "nl" else "Investor report"
    notice = soup.select_one(".notice")
    if not isinstance(notice, Tag):
        raise RuntimeError("Client notice missing")
    notice.string = (
        "Dit rapport is informatief en educatief. De officiële modelportefeuille bevat drie posities; nieuwe inzet blijft geblokkeerd totdat actuele markt- en donorpoorten slagen."
        if language == "nl" else
        "This report is informational and educational. The official model portfolio contains three positions; new deployment remains blocked until current market and donor gates pass."
    )
    banner = new_tag(
        soup,
        "div",
        (
            "Productiestatus: premium clientrapport · officiële portefeuille ongewijzigd · geen nieuwe transactie."
            if language == "nl" else
            "Production status: premium client report · official portfolio unchanged · no new trade."
        ),
    )
    banner["class"] = ["continuity-box", "production-convergence-banner"]
    notice.insert_after(banner)


def normalize_visible_copy(soup: BeautifulSoup, language: str) -> None:
    if language == "nl":
        replacements = {
            "Gesynchroniseerd schaduwrapport": "Beleggersrapport",
            "Schaduw – geen uitvoering": "Geblokkeerd · geen transactie",
            "schaduwpoort": "bewijsreview",
            "Schaduwpoort": "Bewijsreview",
            "schaduwplan": "analytisch scenario",
            "Schaduwplan": "Analytisch scenario",
            "schaduwintentie": "geblokkeerd scenario",
            "schaduwvarianten": "analytische varianten",
            "schaduwoutput": "analyse-output",
            "Schaduwoutput": "Analyse-output",
            "LOCK/LOCK": "L0CK",
            "LOCK · iShares Digital Security": "L0CK · iShares Digital Security",
        }
    else:
        replacements = {
            "Synchronized shadow report": "Investor report",
            "Shadow – no execution": "Blocked · no trade",
            "shadow gate": "evidence review",
            "Shadow gate": "Evidence review",
            "shadow plan": "analytical scenario",
            "Shadow plan": "Analytical scenario",
            "shadow intent": "blocked scenario",
            "shadow variants": "analytical variants",
            "shadow output": "analysis output",
            "Shadow output": "Analysis output",
            "LOCK/LOCK": "L0CK",
            "LOCK · iShares Digital Security": "L0CK · iShares Digital Security",
        }
    replace_text_nodes(soup, replacements)


def visible_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "head"]):
        tag.extract()
    return " ".join(soup.get_text(" ", strip=True).split())


def promote(source_manifest: Path, state_path: Path, output_dir: Path) -> Path:
    source = load_json(source_manifest)
    state = load_json(state_path)
    if state.get("schema_version") != "etf_eu_production_convergence_state_v1":
        raise RuntimeError("Invalid production-convergence state")
    if state.get("stage_1_decision", {}).get("value") != "blocked":
        raise RuntimeError("WP-SYNC-10 promoter requires the accepted blocked Stage-1 decision")
    if set(stage_1_index(state)) != set(STAGE_1_ISINS):
        raise RuntimeError("Frozen Stage-1 review candidate set is incomplete")

    output_dir.mkdir(parents=True, exist_ok=True)
    report_date = str(state.get("report_date") or "")
    token = report_date.replace("-", "")[2:]
    manifest: dict[str, Any] = {
        "schema_version": "etf_eu_production_converged_report_manifest_v1",
        "artifact_type": "etf_eu_production_converged_client_report",
        "report_date": report_date,
        "source_report_manifest": str(source_manifest),
        "production_convergence_state": str(state_path),
        "client_renderer_mode": "synchronized_premium_production_candidate",
        "official_portfolio_position_count": state.get("official_portfolio", {}).get("position_count"),
        "current_promoted_exposure_count": len(state.get("promoted_exposures") or []),
        "frozen_stage_1_review_candidate_count": len(state.get("stage_1_review_candidates") or []),
        "stage_1_decision": "blocked",
        "executable_trade_intents": [],
        "authority": dict(state.get("authority") or {}),
        "languages": {},
    }

    for language in ("nl", "en"):
        source_language = source.get("languages", {}).get(language)
        if not isinstance(source_language, dict):
            raise RuntimeError(f"Missing source language manifest: {language}")
        html_path = Path(str(source_language.get("html") or ""))
        if not html_path.is_file():
            raise RuntimeError(f"Source HTML missing: {html_path}")
        soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
        update_hero_and_notice(soup, state, language)
        update_section_4(soup, state, language)
        update_section_11(soup, state, language)
        update_section_12(soup, state, language)
        update_section_13(soup, state, language)
        replace_section_14(soup, state, language)
        normalize_visible_copy(soup, language)

        check_soup = BeautifulSoup(str(soup), "html.parser")
        text = visible_text(check_soup).casefold()
        prohibited = ["schaduwrapport", "shadow report", "funding_authority", "execution_authority", "portfolio_mutation"]
        leaked = [token_value for token_value in prohibited if token_value in text]
        if leaked:
            raise RuntimeError(f"Visible internal/development language remains in {language}: {leaked}")

        prefix = "weekly_etf_eu_review_nl" if language == "nl" else "weekly_etf_eu_review"
        out_html = output_dir / f"{prefix}_{token}_converged.html"
        out_pdf = output_dir / f"{prefix}_{token}_converged.pdf"
        out_html.write_text(str(soup), encoding="utf-8")
        HTML(string=str(soup), base_url=str(html_path.parent.resolve())).write_pdf(str(out_pdf))
        if not out_pdf.is_file() or out_pdf.stat().st_size <= 0:
            raise RuntimeError(f"PDF output missing: {out_pdf}")
        manifest["languages"][language] = {
            "html": str(out_html),
            "pdf": str(out_pdf),
            "role": "dutch_primary" if language == "nl" else "english_companion",
        }

    manifest_path = output_dir / f"etf_eu_production_converged_report_manifest_{token}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(manifest_path)
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Promote the finalized synchronized ETF EU report to a client-facing production candidate")
    parser.add_argument("source_manifest", type=Path)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    promote(args.source_manifest, args.state, args.output_dir)


if __name__ == "__main__":
    main()
