from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from runtime import add_etf_eu_activated_allocation_surface as legacy
from runtime.synchronize_etf_eu_activated_front_page import synchronize_manifest

# The source action table is synchronized here through the legacy v2 surface.
# The final promoter must carry and finalize section-13 so the compatibility
# renderer cannot reintroduce blocked L0CK, unqualified VVSM, or shadow-gate text.
FINAL_PROMOTION_SECTION_SYNC_REQUIRED = "section-13:activated-L0CK:blocked-VVSM:client-safe"
FRONT_PAGE_STATE_SYNC_REQUIRED = "section-1+section-2:authoritative-four-position:L0CK-active"


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


def argument_value(argv: list[str], flag: str) -> str:
    if flag not in argv:
        raise RuntimeError(f"Activated allocation surface requires {flag}")
    index = argv.index(flag)
    if index + 1 >= len(argv):
        raise RuntimeError(f"Activated allocation surface value is missing for {flag}")
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


def main() -> None:
    argv = list(sys.argv)
    if len(argv) < 2 or argv[1].startswith("-"):
        raise RuntimeError("Activated allocation surface requires manifest path as first argument")
    manifest_path = Path(argv[1])
    if "--state" not in argv:
        report_date = current_report_date(argv)
        state_path = discover_activated_state(report_date)
        argv.extend(["--state", str(state_path)])
        sys.argv = argv
    else:
        state_path = Path(argument_value(argv, "--state"))
    legacy.main()
    synchronize_manifest(manifest_path, state_path)


if __name__ == "__main__":
    main()
