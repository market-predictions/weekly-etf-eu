from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag
from weasyprint import HTML

from runtime import synchronize_etf_eu_current_state_surface as legacy


CLIENT_STATE_CONTRACT = "authoritative_four_position_current_state_v6_donor_convergence"
# Capture the v1 implementations once, before synchronize_manifest temporarily
# replaces them. Calling legacy._sync_8 or legacy._sync_13 from a wrapper after
# replacement would recurse into the wrapper itself.
_BASE_SYNC_8 = legacy._sync_8
_BASE_SYNC_13 = legacy._sync_13

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

RETIRED_OR_SHADOW_CONTROL_MARKERS = {
    "max. nieuwe etf",
    "max nieuwe etf",
    "max. new etf",
    "max new etf",
    "omzetplafond",
    "turnover ceiling",
    "halfgeleiderlimiet",
    "effective semiconductor cap",
}

SHADOW_VARIANT_MARKERS = {
    "cash-first (vaste 50%)",
    "policy-driven cash-first migration",
    "beleidsgestuurd",
    "policy-driven",
    "strikte replicatie",
    "strict mapped replication",
    "efficiënt, max. 8 posities",
    "efficient portfolio, maximum 8 positions",
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


def _sync_13_after_client_surface_supersession(
    soup: BeautifulSoup,
    contract: dict[str, Any],
    positions: dict[str, dict[str, Any]],
    lang: str,
) -> None:
    """Keep v1 Section-13 logic idempotent after stale L0CK-row removal."""
    table = legacy._section(soup, "13").find("table", class_="final-alignment-table")
    if not isinstance(table, Tag):
        raise RuntimeError("Section 13 final action table missing")

    incumbent_rows = [
        row
        for row in table.select("tbody tr")
        if legacy._cells(row, 1, "Section 13 row")[0].get_text(" ", strip=True).upper() == "L0CK"
    ]
    if len(incumbent_rows) > 1:
        raise RuntimeError(f"Section 13 duplicate L0CK incumbent rows before synchronization: {len(incumbent_rows)}")

    synthetic_row: Tag | None = None
    if not incumbent_rows:
        exposure_row = legacy._row(table, legacy.L0CK_ISIN)
        clone = BeautifulSoup(str(exposure_row), "html.parser").find("tr")
        if not isinstance(clone, Tag):
            raise RuntimeError("Unable to clone authoritative Section 13 L0CK exposure row")
        cells = legacy._cells(clone, 10, "Synthetic Section 13 L0CK incumbent")
        legacy._set(cells, 0, "L0CK")
        tbody = table.find("tbody")
        if not isinstance(tbody, Tag):
            raise RuntimeError("Section 13 table body missing")
        tbody.append(clone)
        synthetic_row = clone

    try:
        _BASE_SYNC_13(soup, contract, positions, lang)
    finally:
        if synthetic_row is not None and synthetic_row.parent is not None:
            synthetic_row.decompose()


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


def _extract_embedded_semiconductor_lower_bound(section: Tag) -> str | None:
    for row in section.select("tbody tr"):
        cells = row.find_all("td", recursive=False)
        if len(cells) < 2:
            continue
        label = " ".join(cells[0].get_text(" ", strip=True).casefold().split())
        if "ingebedde semis" in label or "embedded semiconductors" in label:
            return cells[1].get_text(" ", strip=True)
    return None


def _new_row(soup: BeautifulSoup, label: str, value: str) -> Tag:
    row = soup.new_tag("tr")
    left = soup.new_tag("td")
    right = soup.new_tag("td")
    left.string = label
    right.string = value
    row.append(left)
    row.append(right)
    return row


def _sync_section14_current_authority(html_path: Path, pdf_path: Path, lang: str) -> None:
    """Replace the historical transition-allocator surface with current authority.

    The legacy allocator remains reproducible internal evidence, but no 35/15/50,
    turnover/theme cap, position-count scenario or policy-sized order is allowed to
    appear as a current client control. Embedded semiconductor overlap remains as a
    measured lower-bound analytical observation only.
    """
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    section = legacy._section(soup, "14")
    embedded = _extract_embedded_semiconductor_lower_bound(section)

    heading = section.find("h2")
    if isinstance(heading, Tag):
        heading.string = "Huidige allocatiereview / monitoring" if lang == "nl" else "Current allocation review / monitoring"

    # Remove every historical allocator/scenario table and explanatory block from
    # the client surface. The evidence remains in machine artifacts, not as policy.
    for table in list(section.find_all("table")):
        table.decompose()
    for summary in list(section.find_all("div", class_="alignment-summary")):
        summary.decompose()

    intro = soup.new_tag("div")
    intro["class"] = "alignment-summary current-allocation-authority-summary"
    intro.string = (
        "De historische Stage-1 allocator en vaste transitiewaarden zijn interne scenario-evidence en hebben geen actuele allocatiebevoegdheid. Deze rapport-run wijzigt geen aandelen of cash."
        if lang == "nl"
        else "The historical Stage-1 allocator and fixed transition values are internal scenario evidence and have no current allocation authority. This report run does not change shares or cash."
    )
    section.append(intro)

    table = soup.new_tag("table")
    table["class"] = "allocator-policy-table current-authority-table"
    thead = soup.new_tag("thead")
    head_row = soup.new_tag("tr")
    for text in (("Huidige discipline", "Betekenis") if lang == "nl" else ("Current discipline", "Meaning")):
        th = soup.new_tag("th")
        th.string = text
        head_row.append(th)
    thead.append(head_row)
    table.append(thead)
    tbody = soup.new_tag("tbody")

    if lang == "nl":
        rows = [
            ("Allocatiebevoegdheid", "Run-specifieke beslissing + beschermde portefeuillestatus; historische scenario's zijn niet leidend."),
            ("Cashdiscipline", "Inzetten of uitleggen op basis van actuele fundable kansen; geen vast minimum uit het transitiebeleid."),
            ("Concentratie / overlap", "Beoordelen op actuele evidence; geen vaste turnover-, positie- of themalimiet uit het shadowbeleid."),
            ("Brokergrens", "Modelbelegbaarheid is brokerneutraal; accounttoestemming is alleen vereist voor echte uitvoering."),
        ]
        if embedded:
            rows.append(("Gemeten ingebedde semiconductor-exposure (ondergrens)", f"{embedded} · analytische ondergrens; geen minimumdoel en geen allocatiecontrole."))
    else:
        rows = [
            ("Allocation authority", "Run-scoped decision + protected portfolio state; historical scenarios are not controlling."),
            ("Cash discipline", "Deploy or explain against current fundable opportunities; no fixed minimum from transition policy."),
            ("Concentration / overlap", "Review current evidence; no fixed turnover, position or theme limit from shadow policy."),
            ("Broker boundary", "Model investability is broker-neutral; account permission is required only for real execution."),
        ]
        if embedded:
            rows.append(("Measured embedded semiconductor exposure (lower bound)", f"{embedded} · analytical lower bound; not a minimum target or allocation control."))

    for label, value in rows:
        tbody.append(_new_row(soup, label, value))
    table.append(tbody)
    section.append(table)

    monitor = soup.new_tag("div")
    monitor["class"] = "alignment-summary current-allocation-monitoring"
    monitor.string = (
        "VVSM blijft gemonitord en niet gefinancierd totdat actuele re-underwriting, UCITS/fundability- en allocatie-evidence een nieuwe beslissing ondersteunt."
        if lang == "nl"
        else "VVSM remains monitored and unfunded until current re-underwriting, UCITS/fundability and allocation evidence supports a new decision."
    )
    section.append(monitor)

    current_text = " ".join(section.get_text(" ", strip=True).casefold().split())
    forbidden = RETIRED_OR_SHADOW_CONTROL_MARKERS | SHADOW_VARIANT_MARKERS | {
        "35,00%",
        "35.00%",
        "14,88%",
        "14.88%",
        "25,00%",
        "25.00%",
        "18,00%",
        "18.00%",
    }
    leaked = sorted(marker for marker in forbidden if marker in current_text)
    if leaked:
        raise RuntimeError(f"Section 14 still exposes historical/shadow allocation controls: {leaked}")
    required = (
        ("geen vast minimum", "brokerneutraal", "ondergrens", "geen minimumdoel")
        if lang == "nl"
        else ("no fixed minimum", "broker-neutral", "lower bound", "not a minimum target")
    )
    if not all(token in current_text for token in required):
        raise RuntimeError("Section 14 current authority wording is incomplete")

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
    original_sync_13 = legacy._sync_13
    legacy._sync_8 = _sync_8_with_authoritative_coverage
    legacy._sync_13 = _sync_13_after_client_surface_supersession
    try:
        legacy.synchronize_manifest(manifest_path, state_path)
    finally:
        legacy._sync_8 = original_sync_8
        legacy._sync_13 = original_sync_13

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for lang in ("nl", "en"):
        record = manifest.get("languages", {}).get(lang)
        if not isinstance(record, dict):
            raise RuntimeError(f"Manifest language record missing: {lang}")
        html_path = Path(str(record["html"]))
        pdf_path = Path(str(record["pdf"]))
        if lang == "nl":
            _sync_nl_section9_language(html_path, pdf_path)
        _sync_section14_current_authority(html_path, pdf_path, lang)
        _validate_section_8_current_state(html_path, positions, lang)
        record["activated_client_state_contract"] = CLIENT_STATE_CONTRACT
    contract = manifest.get("activated_client_state_contract")
    if isinstance(contract, dict):
        contract["contract_version"] = CLIENT_STATE_CONTRACT
        contract["section_8_exact_donor_exposure_coverage"] = "derived_from_authoritative_l0ck_weight"
        contract["section_8_vvsm_status"] = "monitored_unfunded_current_close_available_strategy_promotion_gate_not_passed"
        contract["nl_section_9_client_language"] = "deterministic_dutch_sentences_v1"
        contract["section_13_l0ck_incumbent_semantics"] = "canonical_exposure_row_only_after_supersession"
        contract["section_14_transition_allocator_client_authority"] = "removed"
        contract["section_14_current_authority"] = "run_scoped_decision_plus_protected_state"
        contract["section_14_embedded_semiconductor_semantics"] = "measured_lower_bound_not_target_or_control"
        contract["section_14_broker_model_boundary"] = "broker_neutral_model_execution_permission_separate"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "ETF_EU_CURRENT_CLIENT_STATE_V6_OK | authority=current_L0CK_weight | "
        "VVSM=monitored_unfunded_current_close_available | nl_section9=dutch | broad_core_substitution=false | "
        "section13_L0CK=canonical_exposure_row_only | section14=transition_allocator_removed_from_client_authority"
    )
