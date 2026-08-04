from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from weasyprint import HTML

from runtime import compact_etf_eu_policy_transition_surface as legacy

CORE_TICKERS = {"VWCE", "EUNA", "SXR8"}
ACTIVATED_TICKERS = CORE_TICKERS | {"L0CK"}


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def normalize_ticker(value: Any) -> str:
    ticker = str(value or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def validate_activated_portfolio(path: Path) -> dict[str, Any]:
    portfolio = load_object(path)
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    tickers = {
        normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
        for row in positions
        if normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
    }
    if tickers != ACTIVATED_TICKERS:
        raise RuntimeError(f"Activated compactor requires exact four-position state: {sorted(tickers)}")
    if portfolio.get("schema_version") != "etf_eu_portfolio_state_v2":
        raise RuntimeError("Activated compactor requires portfolio schema v2")
    if portfolio.get("model_portfolio_only") is not True or portfolio.get("real_broker_execution") is not False:
        raise RuntimeError("Activated compactor portfolio authority boundary is invalid")
    activation = portfolio.get("last_model_capital_activation") or {}
    if not activation.get("activation_id"):
        raise RuntimeError("Activated compactor provenance is missing")
    return portfolio


def compact_activated_section(body: str, language: str) -> tuple[str, int, bool]:
    match = legacy.TABLE_RE.search(body)
    if not match:
        raise RuntimeError(f"Allocator transition table not found for {language}")
    rows = legacy.ROW_RE.findall(match.group(2))
    blocked_markers = ("Blocked / deferred", "Geblokkeerd / uitgesteld")
    kept = [row for row in rows if not any(marker in row for marker in blocked_markers)]
    removed = len(rows) - len(kept)
    if len(kept) != 1:
        raise RuntimeError(f"Expected one remaining unfunded Stage-1 row for {language}; found {len(kept)}")
    remaining = kept[0]
    if "VVSM" not in remaining:
        raise RuntimeError(f"Remaining Stage-1 row must be VVSM for {language}")
    if re.search(r"\bL0CK\b|\bLOCK\b", remaining):
        raise RuntimeError(f"Funded L0CK must not remain a new Stage-1 intent for {language}")

    rebuilt = match.group(1) + remaining + match.group(3)
    note = (
        f'<div class="alignment-summary">{removed} uitgestelde donor-exposures blijven volledig onderbouwd in secties 11 en 13. L0CK is inmiddels een gefinancierde modelpositie; deze tabel toont alleen de resterende VVSM-monitoring.</div>'
        if language == "nl"
        else f'<div class="alignment-summary">{removed} deferred donor exposures remain fully documented in Sections 11 and 13. L0CK is now a funded model position; this table shows only the remaining VVSM monitoring case.</div>'
    )
    updated = body[: match.start()] + rebuilt + note + body[match.end() :]

    replacement = (
        '<div class="alignment-summary">De huidige vier modelposities blijven in deze rapport-run ongewijzigd; zie secties 10, 13 en 15.</div>'
        if language == "nl"
        else '<div class="alignment-summary">The current four model positions remain unchanged during this report run; see Sections 10, 13 and 15.</div>'
    )
    updated, legacy_count = legacy.LEGACY_BLOCK_RE.subn(replacement, updated, count=1)
    if legacy_count != 1:
        raise RuntimeError(f"Expected one duplicate incumbent block in Section 14 for {language}")

    replacements = dict(legacy.NL_COMPACT_REPLACEMENTS)
    replacements.update(
        {
            "Voorgestelde beleidsgestuurde fase-1 allocatie": "Resterende fase-1 monitoring",
            "Beleidsgestuurde fase-1 schaduwintentie": "Resterende fase-1 monitoring",
            "Koop 156 hele aandelen VVSM. Effectieve exposure-ondergrens 17,91% versus limiet 18,00%. VanEck Semiconductor UCITS ETF": "VVSM blijft gemonitord; geen financierings- of uitvoeringsbevoegdheid.",
            "156 VVSM; effectieve exposure 17,91% / limiet 18,00%.": "VVSM blijft gemonitord; geen financierings- of uitvoeringsbevoegdheid.",
        }
    )
    if language == "nl":
        for source, compact in replacements.items():
            updated = updated.replace(source, compact)
    else:
        updated = updated.replace("Proposed policy-driven Stage-1 allocation", "Remaining Stage-1 monitoring")
        updated = updated.replace("Policy-driven Stage-1 shadow intent", "Remaining Stage-1 monitoring")
    return updated, removed, True


def main() -> None:
    parser = argparse.ArgumentParser(description="Compact activated policy transition table")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    args = parser.parse_args()
    portfolio = validate_activated_portfolio(args.portfolio_state)
    manifest = load_object(args.manifest)
    removed_by_language: dict[str, int] = {}
    duplicate_incumbent_block_removed: dict[str, bool] = {}

    for language, files in (manifest.get("languages") or {}).items():
        if language not in {"nl", "en"} or not isinstance(files, dict):
            continue
        html_path = Path(str(files.get("html") or ""))
        pdf_path = Path(str(files.get("pdf") or ""))
        text = html_path.read_text(encoding="utf-8")

        def replace(match: re.Match[str]) -> str:
            compacted, removed, legacy_removed = compact_activated_section(match.group(2), language)
            removed_by_language[language] = removed
            duplicate_incumbent_block_removed[language] = legacy_removed
            return match.group(1) + compacted + match.group(3)

        updated, count = legacy.SECTION_RE.subn(replace, text, count=1)
        if count != 1:
            raise RuntimeError(f"Could not compact activated Section 14 for {language}")
        html_path.write_text(updated, encoding="utf-8")
        HTML(string=updated, base_url=str(html_path.parent.resolve())).write_pdf(pdf_path)
        files["policy_transition_compaction"] = "activated_l0ck_remaining_vvsm_monitor_v1"

    manifest["policy_transition_compaction"] = {
        "applied": True,
        "mode": "activated_l0ck_remaining_vvsm_monitor",
        "funded_stage1_tickers": ["L0CK"],
        "remaining_monitored_tickers": ["VVSM"],
        "current_position_count": len(portfolio.get("positions") or []),
        "removed_deferred_row_count_by_language": removed_by_language,
        "duplicate_incumbent_block_removed_by_language": duplicate_incumbent_block_removed,
        "incumbent_evidence_remains_in_sections": ["10", "13", "15"],
        "deferred_exposures_remain_in_sections": ["11", "13"],
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
        "real_broker_execution": False,
    }
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "ETF_EU_ACTIVATED_POLICY_TRANSITION_COMPACT_OK"
        " | funded=L0CK | monitored=VVSM | actionable_rows=1"
        f" | manifest={args.manifest}"
    )


if __name__ == "__main__":
    main()
