from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from runtime import add_etf_eu_activated_allocation_surface as legacy

# The source action table is synchronized here through the legacy v2 surface.
# The final promoter must carry section-13 into the client candidate so the
# compatibility renderer cannot reintroduce a blocked L0CK row.
FINAL_PROMOTION_SECTION_SYNC_REQUIRED = "section-13"


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


def main() -> None:
    argv = list(sys.argv)
    if "--state" not in argv:
        report_date = current_report_date(argv)
        state_path = discover_activated_state(report_date)
        argv.extend(["--state", str(state_path)])
        sys.argv = argv
    legacy.main()


if __name__ == "__main__":
    main()
