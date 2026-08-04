from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path
from typing import Any

import yaml


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def apply(evidence_path: Path, cache_path: Path) -> None:
    evidence = load_json(evidence_path)
    cache = load_yaml(cache_path)
    cache_rows = cache.get("rows") if isinstance(cache.get("rows"), dict) else {}
    report_date = date.fromisoformat(str(evidence.get("report_date")))
    fallback_count = 0
    for row in evidence.get("rows") or []:
        if not isinstance(row, dict) or row.get("status") != "fetch_failed":
            continue
        cached = cache_rows.get(str(row.get("exposure_id")))
        if not isinstance(cached, dict):
            continue
        close_date = date.fromisoformat(str(cached.get("close_date")))
        if close_date >= report_date:
            continue
        original_blockers = list(row.get("blockers") or [])
        row.update({
            "status": "priced_from_dated_non_authoritative_cache",
            "completed_close": True,
            "close_date": close_date.isoformat(),
            "close_price": float(cached.get("close_price")),
            "price_age_calendar_days": (report_date - close_date).days,
            "median_daily_traded_value_eur_20d": float(cached.get("median_daily_traded_value_eur_20d")),
            "source": "dated prior successful Yahoo/yfinance connectivity evidence cache",
            "source_quality": "cached_prior_successful_non_authoritative_connectivity_only",
            "valuation_grade": False,
            "funding_authority": False,
            "live_fetch_blockers": original_blockers,
            "blockers": [],
            "cache_fallback_applied": True,
            "cache_path": str(cache_path),
        })
        fallback_count += 1
    evidence["cache_fallback"] = {
        "applied": fallback_count > 0,
        "fallback_row_count": fallback_count,
        "cache_path": str(cache_path),
        "cache_observation_date": str(cache.get("observation_date") or ""),
        "valuation_grade": False,
        "funding_authority": False,
    }
    evidence["priced_line_count"] = sum(1 for row in evidence.get("rows") or [] if str(row.get("status")).startswith("priced_"))
    evidence["completed_close_gate_passed"] = bool(
        evidence["priced_line_count"] and all(
            row.get("completed_close") is True
            for row in evidence.get("rows") or []
            if str(row.get("status")).startswith("priced_")
        )
    )
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    # A current routine run may already have produced stronger exact-line
    # completed-close consensus. Apply it after the dated cache so the cache
    # continues to supply the 20-day liquidity metric while current pricing
    # replaces only stale price fields. Exact report-date, provider-agreement
    # and identity checks remain enforced by the overlay implementation.
    run_id = os.environ.get("WP11_RUN_ID", "").strip() or os.environ.get("RUN_ID", "").strip()
    if run_id:
        pricing = Path(f"output/pricing/ucits_close_price_validation_basket_results_{run_id}.json")
        qualification = Path(f"output/pricing/ucits_price_provider_qualification_{run_id}.json")
        if pricing.exists() and qualification.exists():
            from pricing.apply_current_close_results_to_transition_evidence import apply as apply_current_close

            apply_current_close(evidence_path, pricing, qualification)

    print(evidence_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--cache", type=Path, default=Path("config/etf_eu_transition_evidence_cache_20260724.yml"))
    args = parser.parse_args()
    apply(args.evidence, args.cache)


if __name__ == "__main__":
    main()
