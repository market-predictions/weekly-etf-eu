from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag
from weasyprint import HTML

from runtime import synchronize_etf_eu_current_state_surface as legacy


CLIENT_STATE_CONTRACT = "authoritative_four_position_current_state_v4"
# Capture the v1 implementation once, before synchronize_manifest temporarily
# replaces legacy._sync_8. Calling legacy._sync_8 from the wrapper after that
# replacement would recurse into the wrapper itself.
_BASE_SYNC_8 = legacy._sync_8

NL_SECTION9_SENTENCE_MAP = {
    "More useful if broad equity leadership narrows further.":
        "Wordt relevanter als het leiderschap binnen de brede aandelenmarkt versmalt.",
    "Becomes more relevant if energy, fertilizer or crop stress rises.":
        "Wordt relevanter als de druk op energie, kunstmest of landbouwgewassen toeneemt.",
    "Moves up if relative strength improves versus PAVE/GRID.":
        "Wordt aantrekkelijker als de relatieve sterkte verbetert ten opzichte van PAVE/GRID.",
    "More useful if equity beta weakens and defensive infrastructure improves.":
        "Wordt relevanter als aandelenbeta verzwakt en defensieve infrastructuur relatief verbetert.",
    "The lane remains relevant, but PPA must justify itself versus ITA.":
        "Het thema blijft relevant, maar PPA moet zijn relatieve meerwaarde ten opzichte van ITA aantonen.",
}


def _sync_8_with_authoritative_coverage(
    soup: BeautifulSoup,
    positions: dict[str, dict[str, Any]],
    lang: str,
) -> None:
    _BASE_SYNC_8(soup, positions, lang)
    section = legacy._section(soup, "8")
    summary = section.find("div", class_="alignment-summary")
    if not isinstance(summary, Tag):
        raise RuntimeError("Section 8 exact donor-exposure coverage summary missing")

    coverage_pct = float(positions["L0CK"]["client_weight_pct"])
    strong = soup.new_tag("strong")
    strong.string = legacy._pct(coverage_pct, lang)
    summary.clear()
    if lang == "nl":
        summary.append("Exacte donor-exposuredekking in de huidige EU-portefeuille: ")
        summary.append(strong)
        summary.append(". Dit meet dezelfde exposures; brede kernfondsen tellen niet als vervanging voor een andere thematische exposure.")
    else:
        summary.append("Exact donor-exposure coverage in the current EU portfolio: ")
        summary.append(strong)
        summary.append(". This measures the same exposures; broad core funds do not count as substitutes for another thematic exposure.")

    # VVSM is an exact mapped analytical line with a current close, but the
    # authoritative Stage-1 contract keeps it monitored and unfunded because
    # the strategy/promotion gate has not passed. Do not misdescribe the gap as
    # missing pricing evidence.
    tables = section.find_all("table")
    if len(tables) < 2:
        raise RuntimeError("Section 8 exposure-alignment table missing")
    vvsm_row = next(
        (row for row in tables[-1].select("tbody tr") if "VVSM" in row.get_text(" ", strip=True)),
        None,
    )
    if not isinstance(vvsm_row, Tag):
        raise RuntimeError("Section 8 VVSM alignment row missing")
    cells = vvsm_row.find_all("td", recursive=False)
    if len(cells) < 7:
        raise RuntimeError("Section 8 VVSM alignment row has unexpected column count")
    if lang == "nl":
        legacy._set(cells, 5, "Gemonitord / niet gefinancierd")
        legacy._set(
            cells,
            6,
            "Actuele slotkoers beschikbaar; donordoel blijft strategiecontext en de huidige strategie-/promotiepoort is niet geslaagd.",
        )
    else:
        legacy._set(cells, 5, "Monitored / unfunded")
        legacy._set(
            cells,
            6,
            "Current completed close available; donor target remains strategy context and the current strategy/promotion gate has not passed.",
        )


def _sync_nl_section9_language(html_path: Path, pdf_path: Path) -> None:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    section = legacy._section(soup, "9")
    changed = False
    for cell in section.find_all("td"):
        text = cell.get_text(" ", strip=True)
        replacement = NL_SECTION9_SENTENCE_MAP.get(text)
        if replacement is None:
            continue
        cell.clear()
        cell.string = replacement
        changed = True
    section_text = " ".join(section.get_text(" ", strip=True).split())
    leaked = [source for source in NL_SECTION9_SENTENCE_MAP if source in section_text]
    if leaked:
        raise RuntimeError(f"Dutch Section 9 still contains English client sentences: {leaked}")
    if changed:
        html_path.write_text(str(soup), encoding="utf-8")
        HTML(filename=str(html_path), base_url=str(html_path.parent.resolve())).write_pdf(str(pdf_path))


def _validate_section_8_current_state(
    html_path: Path,
    positions: dict[str, dict[str, Any]],
    lang: str,
) -> None:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    section = legacy._section(soup, "8")
    summary = section.find("div", class_="alignment-summary")
    if not isinstance(summary, Tag):
        raise RuntimeError("Section 8 exact donor-exposure coverage summary missing after synchronization")
    expected = legacy._pct(positions["L0CK"]["client_weight_pct"], lang)
    if expected not in summary.get_text(" ", strip=True):
        raise RuntimeError(
            f"Section 8 exact donor-exposure coverage does not match authoritative L0CK weight: expected {expected}"
        )

    vvsm_row = next(
        (row for row in section.select("tbody tr") if "VVSM" in row.get_text(" ", strip=True)),
        None,
    )
    if not isinstance(vvsm_row, Tag):
        raise RuntimeError("Section 8 VVSM row missing after synchronization")
    vvsm_text = " ".join(vvsm_row.get_text(" ", strip=True).split()).casefold()
    forbidden = ("current pricing basis missing", "actuele prijsbasis ontbreekt")
    if any(token in vvsm_text for token in forbidden):
        raise RuntimeError("Section 8 VVSM row still claims missing current pricing")
    required = (
        ("gemonitord", "niet gefinancierd", "slotkoers beschikbaar", "promotiepoort")
        if lang == "nl"
        else ("monitored", "unfunded", "completed close available", "promotion gate")
    )
    if not all(token in vvsm_text for token in required):
        raise RuntimeError("Section 8 VVSM row does not match authoritative monitored/unfunded semantics")


def synchronize_manifest(manifest_path: Path, state_path: Path) -> None:
    state = json.loads(state_path.read_text(encoding="utf-8"))
    _, positions = legacy.contract(state)
    original_sync_8 = legacy._sync_8
    legacy._sync_8 = _sync_8_with_authoritative_coverage
    try:
        legacy.synchronize_manifest(manifest_path, state_path)
    finally:
        legacy._sync_8 = original_sync_8

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for lang in ("nl", "en"):
        record = manifest.get("languages", {}).get(lang)
        if not isinstance(record, dict):
            raise RuntimeError(f"Manifest language record missing: {lang}")
        html_path = Path(str(record["html"]))
        pdf_path = Path(str(record["pdf"]))
        if lang == "nl":
            _sync_nl_section9_language(html_path, pdf_path)
        _validate_section_8_current_state(html_path, positions, lang)
        record["activated_client_state_contract"] = CLIENT_STATE_CONTRACT
    contract = manifest.get("activated_client_state_contract")
    if isinstance(contract, dict):
        contract["contract_version"] = CLIENT_STATE_CONTRACT
        contract["section_8_exact_donor_exposure_coverage"] = "derived_from_authoritative_l0ck_weight"
        contract["section_8_vvsm_status"] = "monitored_unfunded_current_close_available_strategy_promotion_gate_not_passed"
        contract["nl_section_9_client_language"] = "deterministic_dutch_sentences_v1"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "ETF_EU_CURRENT_CLIENT_STATE_V4_OK | authority=current_L0CK_weight | "
        "VVSM=monitored_unfunded_current_close_available | nl_section9=dutch | broad_core_substitution=false"
    )
