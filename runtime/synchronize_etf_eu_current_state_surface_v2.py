from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag

from runtime import synchronize_etf_eu_current_state_surface as legacy


CLIENT_STATE_CONTRACT = "authoritative_four_position_current_state_v2"
# Capture the v1 implementation once, before synchronize_manifest temporarily
# replaces legacy._sync_8. Calling legacy._sync_8 from the wrapper after that
# replacement would recurse into the wrapper itself.
_BASE_SYNC_8 = legacy._sync_8


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

    # Under the activated four-position contract, L0CK is the only funded line
    # that is an exact currently promoted donor exposure. Broad core positions
    # are explicitly not substitutes for another thematic exposure, so this
    # coverage metric must equal authoritative current L0CK portfolio weight.
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


def _validate_section_8_coverage(
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
        _validate_section_8_coverage(Path(str(record["html"])), positions, lang)
        record["activated_client_state_contract"] = CLIENT_STATE_CONTRACT
    contract = manifest.get("activated_client_state_contract")
    if isinstance(contract, dict):
        contract["contract_version"] = CLIENT_STATE_CONTRACT
        contract["section_8_exact_donor_exposure_coverage"] = "derived_from_authoritative_l0ck_weight"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("ETF_EU_SECTION8_COVERAGE_OK | authority=current_L0CK_weight | broad_core_substitution=false")
