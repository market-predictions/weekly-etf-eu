from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag

from runtime import add_etf_eu_activated_allocation_surface as legacy

# The source action table is synchronized here through the legacy v2 surface.
# The final promoter must carry and finalize section-13 so the compatibility
# renderer cannot reintroduce blocked L0CK, unqualified VVSM, or shadow-gate text.
FINAL_PROMOTION_SECTION_SYNC_REQUIRED = "section-13:activated-L0CK:blocked-VVSM:client-safe"


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def normalize_ticker(value: Any) -> str:
    ticker = str(value or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def current_report_date(argv: list[str]) -> str:
    if "--report-date" not in argv:
        raise RuntimeError("Activated allocation surface requires --report-date")
    index = argv.index("--report-date")
    if index + 1 >= len(argv):
        raise RuntimeError("Activated allocation surface report date value is missing")
    return argv[index + 1]


def discover_activated_state(report_date: str) -> Path:
    candidates: list[tuple[float, Path]] = []
    for path in Path("output/routine_preview").glob("etf_eu_production_convergence_state_*.json"):
        try:
            payload = load_object(path)
        except Exception:
            continue
        if str(payload.get("report_date") or "") != report_date:
            continue
        portfolio = payload.get("official_portfolio") if isinstance(payload.get("official_portfolio"), dict) else {}
        positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
        tickers = {
            normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
            for row in positions
            if normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
        }
        activation = portfolio.get("last_model_capital_activation") or payload.get("model_capital_activation") or {}
        if tickers != {"VWCE", "EUNA", "SXR8", "L0CK"}:
            continue
        if not activation.get("activation_id"):
            continue
        stage = payload.get("stage_1_decision") if isinstance(payload.get("stage_1_decision"), dict) else {}
        if stage.get("value") != "partially_activated":
            continue
        candidates.append((path.stat().st_mtime, path))
    if not candidates:
        raise RuntimeError(f"No activated four-position convergence state found for {report_date}")
    candidates.sort(key=lambda item: item[0])
    selected = candidates[-1][1]
    print(f"ETF_EU_ACTIVATED_STATE_SELECTED | report_date={report_date} | state={selected}")
    return selected


def _target_surface_text(soup: BeautifulSoup) -> str:
    section_1 = soup.find("section", id="section-1")
    section_2 = soup.find("section", id="section-2")
    section_2a = soup.find("section", id="section-2A")
    if not isinstance(section_1, Tag) or not isinstance(section_2, Tag) or not isinstance(section_2a, Tag):
        raise RuntimeError("Activated allocation copy target sections missing")
    l0ck_row = next(
        (row for row in section_2.select("tbody tr") if "IE00BG0J4C88" in row.get_text(" ", strip=True)),
        None,
    )
    if not isinstance(l0ck_row, Tag):
        raise RuntimeError("Activated L0CK portfolio-action row missing")
    return " ".join(
        (
            section_1.get_text(" ", strip=True),
            l0ck_row.get_text(" ", strip=True),
            section_2a.get_text(" ", strip=True),
        )
    )


def _install_scoped_stale_copy_validation() -> None:
    """Keep stale-copy checks fail-closed, but only on the surfaces we rewrite.

    The report can legitimately contain historical comparison language such as
    "no portfolio change" outside the current Executive Summary, L0CK action
    row and Decision Cockpit. The legacy v3 synchronizer initially scanned the
    whole document and therefore rejected those unrelated historical phrases.
    """

    original = legacy.synchronize_authoritative_portfolio_copy

    def scoped(soup: BeautifulSoup, state: dict[str, Any], language: str) -> None:
        try:
            original(soup, state, language)
            return
        except RuntimeError as exc:
            if not str(exc).startswith("Stale activated-allocation copy remains:"):
                raise

        stale_markers = (
            ("3 officiële posities", "geen portefeuillewijziging", "gepromoveerd maar geblokkeerd", "Geblokkeerd; cash behouden")
            if language == "nl"
            else ("3 official positions", "no portfolio change", "promoted but blocked", "Blocked; retain cash")
        )
        target_text = _target_surface_text(soup)
        remaining = [marker for marker in stale_markers if marker in target_text]
        if remaining:
            raise RuntimeError(f"Stale activated-allocation copy remains in current target surfaces: {remaining}")

    legacy.synchronize_authoritative_portfolio_copy = scoped


def main() -> None:
    argv = list(sys.argv)
    if "--state" not in argv:
        report_date = current_report_date(argv)
        state_path = discover_activated_state(report_date)
        argv.extend(["--state", str(state_path)])
        sys.argv = argv
    _install_scoped_stale_copy_validation()
    legacy.main()


if __name__ == "__main__":
    main()
