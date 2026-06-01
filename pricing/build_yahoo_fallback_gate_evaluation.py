from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "yahoo_fallback_gate_evaluation_v1"
MAX_STALENESS_DAYS = 5


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def positive_float(value: Any) -> float | None:
    try:
        result = float(value)
    except Exception:
        return None
    return result if result > 0 else None


def parse_date(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value or "")[:10])
    except ValueError:
        return None


def evaluate_row(row: dict[str, Any]) -> dict[str, Any]:
    observed = row.get("observed") if isinstance(row.get("observed"), dict) else {}
    mapping = row.get("mapping_diagnostics") if isinstance(row.get("mapping_diagnostics"), dict) else {}
    close = positive_float(observed.get("observed_last_close"))
    close_date = parse_date(observed.get("observed_last_close_date"))
    staleness_days = (datetime.now(timezone.utc).date() - close_date).days if close_date else None
    gates = {
        "registry_symbol_present": bool(row.get("yahoo_symbol") and row.get("source_policy_status") == "connectivity_preflight_only"),
        "fallback_policy_enabled": False,
        "currency_matches_registry": mapping.get("currency_matches_registry") is True,
        "fresh_close_present": bool(close is not None and staleness_days is not None and 0 <= staleness_days <= MAX_STALENESS_DAYS),
        "completed_session_validated": False,
        "cross_source_check_passed": False,
        "lineage_recorded": bool(row.get("registry_id") and row.get("isin") and row.get("yahoo_symbol") and close is not None and close_date is not None),
        "valuation_use_blocked": True,
    }
    failed = [key for key, value in gates.items() if value is not True]
    return {
        "registry_id": row.get("registry_id"),
        "isin": row.get("isin"),
        "exchange": row.get("exchange"),
        "exchange_ticker": row.get("exchange_ticker"),
        "trading_currency": row.get("trading_currency"),
        "provider_symbol": row.get("provider_symbol"),
        "yahoo_symbol": row.get("yahoo_symbol"),
        "observed_close_date": close_date.isoformat() if close_date else None,
        "observed_currency": observed.get("observed_currency"),
        "staleness_days": staleness_days,
        "gates": gates,
        "failed_gates": failed,
        "eligible_for_fallback_review": len(failed) == 0,
        "status": "blocked" if failed else "eligible_for_review",
        "diagnostic_only": True,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
    }


def build(yahoo_diagnostics: Path, output_dir: Path, run_id: str) -> Path:
    source = load_json(yahoo_diagnostics)
    rows = [evaluate_row(row) for row in source.get("rows", []) if isinstance(row, dict)]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_yahoo_diagnostics": str(yahoo_diagnostics),
        "contract": "control/YAHOO_VERIFIED_FALLBACK_CONTRACT_V1.md",
        "diagnostic_only": True,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "eligible_for_fallback_review_count": sum(1 for row in rows if row.get("eligible_for_fallback_review") is True),
            "blocked_count": sum(1 for row in rows if row.get("eligible_for_fallback_review") is not True),
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"yahoo_fallback_gate_evaluation_{run_id}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"YAHOO_FALLBACK_GATE_EVALUATION_OK | artifact={path} | rows={len(rows)}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--yahoo-diagnostics", required=True)
    parser.add_argument("--output-dir", default="output/pricing")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    build(Path(args.yahoo_diagnostics), Path(args.output_dir), args.run_id)


if __name__ == "__main__":
    main()
