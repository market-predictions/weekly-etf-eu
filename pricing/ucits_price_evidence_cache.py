from __future__ import annotations

import json
from pathlib import Path
from statistics import median
from typing import Any


def _accepted(row: dict[str, Any], max_close_age_days: int) -> bool:
    return (
        row.get("pricing_status") == "priced"
        and row.get("close_price") is not None
        and row.get("close_date")
        and int(row.get("close_age_days") or 0) <= max_close_age_days
        and row.get("venue_match") is not False
        and row.get("currency_match") is not False
    )


def _recompute_line(line: dict[str, Any], max_close_age_days: int, tolerance_pct: float) -> None:
    accepted = [row for row in line.get("provider_results", []) or [] if isinstance(row, dict) and _accepted(row, max_close_age_days)]
    by_date: dict[str, list[dict[str, Any]]] = {}
    for row in accepted:
        by_date.setdefault(str(row["close_date"]), []).append(row)
    selected_date = max(by_date, key=lambda item: (len(by_date[item]), item)) if by_date else None
    comparable = by_date.get(selected_date, []) if selected_date else []
    prices = [float(row["close_price"]) for row in comparable]
    consensus = median(prices) if prices else None
    spread_pct = None
    if prices and consensus:
        spread_pct = (max(prices) - min(prices)) / consensus * 100.0
    if len(comparable) >= 2 and spread_pct is not None and spread_pct <= tolerance_pct:
        status = "qualified_development_consensus"
    elif len(comparable) == 1:
        status = "single_source_only"
    elif len(comparable) >= 2:
        status = "provider_disagreement"
    else:
        status = "unpriced"
    line["qualification_status"] = status
    line["selected_close_date"] = selected_date
    line["consensus_close_price"] = round(float(consensus), 8) if consensus is not None else None
    line["agreement_spread_pct"] = round(float(spread_pct), 6) if spread_pct is not None else None
    line["agreeing_providers"] = [row["provider"] for row in comparable]
    line["accepted_provider_count"] = len(accepted)
    line["same_date_provider_count"] = len(comparable)


def apply_provider_evidence_cache(qualification_path: Path, cache_path: Path | None) -> dict[str, Any]:
    payload = json.loads(qualification_path.read_text(encoding="utf-8"))
    if cache_path is None or not cache_path.exists():
        payload["provider_cache_status"] = "not_configured"
        qualification_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return payload

    cache = json.loads(cache_path.read_text(encoding="utf-8"))
    report_date = str(payload.get("report_date") or "")
    if str(cache.get("report_date") or "") != report_date:
        payload["provider_cache_status"] = "ignored_report_date_mismatch"
        payload["provider_cache_path"] = str(cache_path)
        qualification_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return payload

    entries = {
        (str(row.get("basket_id")), str(row.get("provider")), str(row.get("provider_symbol"))): row
        for row in cache.get("entries", []) or []
        if isinstance(row, dict) and str(row.get("report_date") or "") == report_date
    }
    used = 0
    for line in payload.get("lines", []) or []:
        if not isinstance(line, dict):
            continue
        for provider_row in line.get("provider_results", []) or []:
            if not isinstance(provider_row, dict) or provider_row.get("pricing_status") == "priced":
                if isinstance(provider_row, dict):
                    provider_row.setdefault("retrieval_mode", "live")
                continue
            key = (
                str(line.get("basket_id")),
                str(provider_row.get("provider")),
                str(provider_row.get("provider_symbol")),
            )
            cached = entries.get(key)
            if cached is None:
                provider_row.setdefault("retrieval_mode", "live_failed")
                continue
            provider_row["live_fetch_status"] = provider_row.get("pricing_status")
            provider_row["live_fetch_blockers"] = list(provider_row.get("blockers") or [])
            provider_row.update({
                "pricing_status": "priced",
                "close_date": cached.get("close_date"),
                "close_price": cached.get("close_price"),
                "close_age_days": 0,
                "returned_symbol": cached.get("returned_symbol"),
                "returned_exchange": cached.get("returned_exchange"),
                "returned_mic": cached.get("returned_mic"),
                "returned_currency": cached.get("returned_currency"),
                "venue_match": cached.get("venue_match"),
                "currency_match": cached.get("currency_match"),
                "retrieval_mode": "cached_accepted_historical_evidence",
                "cache_provenance": cache.get("provenance"),
                "blockers": ["provider_cache_used_after_live_fetch_unavailable"],
            })
            used += 1
        _recompute_line(
            line,
            int(payload.get("max_close_age_days") or 7),
            float(payload.get("agreement_tolerance_pct") or 1.0),
        )

    payload["provider_cache_status"] = "applied" if used else "configured_no_entries_used"
    payload["provider_cache_path"] = str(cache_path)
    payload["provider_cache_used_count"] = used
    payload["provider_cache_provenance"] = cache.get("provenance")
    payload["provider_cache_authority"] = cache.get("authority")
    qualification_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload
