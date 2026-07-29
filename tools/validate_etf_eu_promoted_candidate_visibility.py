from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any


SECTION_RE = re.compile(r'<section id="section-(?P<id>2|4|9|11|13)"[^>]*>(?P<body>.*?)</section>', re.DOTALL)
MARKER_RE = re.compile(
    r'<span class="ucits-candidate"[^>]*data-exposure-id="(?P<exposure>[^"]*)"[^>]*'
    r'data-ticker="(?P<ticker>[^"]*)"[^>]*data-isin="(?P<isin>[^"]*)"[^>]*>'
)
REQUIRED_MARKER_SECTIONS = {"2", "4", "11", "13"}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def primary_candidate(row: dict[str, Any]) -> tuple[str, str, str]:
    candidate = row.get("preferred_ucits_candidate") if isinstance(row.get("preferred_ucits_candidate"), dict) else {}
    lines = [line for line in (candidate.get("trading_lines") or []) if isinstance(line, dict)]
    preferred = [
        line for line in lines
        if str(line.get("trading_currency") or "").upper() == "EUR"
        and str(line.get("exchange") or "") in {"Xetra", "Euronext Amsterdam", "Borsa Italiana"}
    ]
    line = (preferred or lines or [{}])[0]
    return (
        str(line.get("exchange_ticker") or "").strip(),
        str(candidate.get("isin") or "").strip(),
        str(candidate.get("fund_name") or "").strip(),
    )


def section_bodies(text: str) -> dict[str, str]:
    return {match.group("id"): match.group("body") for match in SECTION_RE.finditer(text)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate promoted UCITS candidate visibility independently of allocator selection")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()

    manifest = load_json(args.manifest)
    metadata = manifest.get("promoted_candidate_visibility") if isinstance(manifest.get("promoted_candidate_visibility"), dict) else {}
    blockers: list[str] = []
    if metadata.get("applied") is not True:
        blockers.append("promoted candidate visibility overlay not applied")
    if metadata.get("candidate_identity_source") != "synchronization_registry":
        blockers.append("candidate identity is not sourced from the synchronization registry")
    if metadata.get("target_and_stage_source") != "policy_allocator":
        blockers.append("target and Stage-1 status are not sourced from the policy allocator")

    sync_path = Path(str(metadata.get("source_sync_shadow") or ""))
    allocator_path = Path(str(metadata.get("source_allocator") or ""))
    if not sync_path.is_file():
        blockers.append("source synchronization artifact missing")
        sync = {}
    else:
        sync = load_json(sync_path)
    if not allocator_path.is_file():
        blockers.append("source allocator artifact missing")
        allocator = {}
    else:
        allocator = load_json(allocator_path)

    promoted = [row for row in sync.get("promoted_exposure_comparison") or [] if isinstance(row, dict)]
    preferred_id = str(allocator.get("preferred_shadow_variant") or "")
    preferred = next(
        (row for row in allocator.get("variants") or [] if isinstance(row, dict) and str(row.get("variant_id")) == preferred_id),
        {},
    )
    allocations = {
        str(row.get("exposure_id")): row
        for row in preferred.get("allocation_rows") or []
        if isinstance(row, dict)
    }

    expected_mapped = 0
    expected_unmapped = 0
    for language, files in (manifest.get("languages") or {}).items():
        if language not in {"nl", "en"} or not isinstance(files, dict):
            continue
        html_path = Path(str(files.get("html") or ""))
        if not html_path.is_file():
            blockers.append(f"{language}: HTML file missing")
            continue
        text = html_path.read_text(encoding="utf-8")
        sections = section_bodies(text)
        missing_sections = sorted({"2", "4", "9", "11", "13"} - set(sections))
        if missing_sections:
            blockers.append(f"{language}: missing sections {', '.join(missing_sections)}")
            continue

        markers_by_section: dict[str, dict[str, tuple[str, str]]] = {}
        for section_id in REQUIRED_MARKER_SECTIONS:
            markers_by_section[section_id] = {
                html.unescape(match.group("exposure")): (
                    html.unescape(match.group("ticker")),
                    html.unescape(match.group("isin")),
                )
                for match in MARKER_RE.finditer(sections[section_id])
            }

        for row in promoted:
            exposure_id = str(row.get("exposure_id") or "")
            ticker, isin, fund_name = primary_candidate(row)
            is_mapped = bool(ticker and isin)
            if language == "nl":
                if is_mapped:
                    expected_mapped += 1
                else:
                    expected_unmapped += 1

            for section_id in REQUIRED_MARKER_SECTIONS:
                marker = markers_by_section[section_id].get(exposure_id)
                if marker is None:
                    blockers.append(f"{language}: section {section_id} missing candidate marker for {exposure_id}")
                    continue
                if marker != (ticker, isin):
                    blockers.append(
                        f"{language}: section {section_id} candidate mismatch for {exposure_id}: {marker} != {(ticker, isin)}"
                    )

            section9_text = html.unescape(re.sub(r"<[^>]+>", " ", sections["9"]))
            if is_mapped and (ticker not in section9_text or fund_name not in section9_text):
                blockers.append(f"{language}: section 9 does not preserve mapped candidate {ticker} for {exposure_id}")

            allocation = allocations.get(exposure_id)
            if is_mapped and allocation is None:
                expected_phrase = (
                    "geen huidig portefeuilledoel" if language == "nl" else "no current portfolio target"
                )
                combined = " ".join(
                    html.unescape(re.sub(r"<[^>]+>", " ", sections[section_id])).lower()
                    for section_id in ("2", "4", "11", "13")
                )
                if expected_phrase not in combined:
                    blockers.append(f"{language}: mapped non-target opportunity {exposure_id} lacks explicit no-target status")

        if "geen geschikt UCITS-equivalent" in html.unescape(text) or "no suitable UCITS equivalent" in html.unescape(text):
            for row in promoted:
                ticker, isin, _ = primary_candidate(row)
                if ticker and isin:
                    exposure_id = str(row.get("exposure_id") or "")
                    for section_id in REQUIRED_MARKER_SECTIONS:
                        body_text = html.unescape(re.sub(r"<[^>]+>", " ", sections[section_id])).lower()
                        if exposure_id.lower() in body_text and (
                            "geen geschikt ucits-equivalent" in body_text or "no suitable ucits equivalent" in body_text
                        ):
                            blockers.append(f"{language}: mapped exposure {exposure_id} is mislabeled as having no UCITS equivalent")

    if metadata.get("promoted_exposure_count") != len(promoted):
        blockers.append("manifest promoted exposure count mismatch")
    if metadata.get("mapped_promoted_exposure_count") != expected_mapped:
        blockers.append("manifest mapped promoted exposure count mismatch")
    if metadata.get("unmapped_promoted_exposure_count") != expected_unmapped:
        blockers.append("manifest unmapped promoted exposure count mismatch")
    if allocator.get("official_portfolio_mutation") is True:
        blockers.append("allocator claims official portfolio mutation")

    payload = {
        "schema_version": "etf_eu_promoted_candidate_visibility_validation_v1",
        "artifact_type": "etf_eu_promoted_candidate_visibility_validation",
        "valid": not blockers,
        "blockers": blockers,
        "promoted_exposure_count": len(promoted),
        "mapped_promoted_exposure_count": expected_mapped,
        "unmapped_promoted_exposure_count": expected_unmapped,
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
