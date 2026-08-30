from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_pricing_artifact(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected pricing object in {path}")
    if payload.get("report_pricing_gate_passed") is not True:
        raise RuntimeError(f"Pricing gate did not pass in {path}")
    return payload


def find_exact_price_row(
    pricing: dict[str, Any],
    *,
    isin: str,
    ticker: str,
    venue_code: str | None,
    currency: str,
    report_date: str,
) -> dict[str, Any]:
    ticker = ticker.strip().upper()
    isin = isin.strip().upper()
    currency = currency.strip().upper()
    venue = (venue_code or "").strip().upper()
    matches: list[dict[str, Any]] = []
    for row in pricing.get("rows") or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("isin") or "").strip().upper() != isin:
            continue
        if str(row.get("ticker") or "").strip().upper() != ticker:
            continue
        if str(row.get("currency") or "").strip().upper() != currency:
            continue
        row_venue = str(row.get("venue_code") or "").strip().upper()
        if venue and row_venue != venue:
            continue
        if str(row.get("close_date") or "") != report_date:
            continue
        matches.append(row)
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one exact-line price row for {isin}/{ticker}/{venue}/{currency} on {report_date}; got {len(matches)}"
        )
    row = matches[0]
    if row.get("valuation_grade") is not True:
        raise RuntimeError(f"Price row is not valuation-grade for {isin}/{ticker}")
    if row.get("blockers"):
        raise RuntimeError(f"Price row has blockers for {isin}/{ticker}: {row.get('blockers')}")
    if float(row.get("close_price") or 0) <= 0:
        raise RuntimeError(f"Price row has non-positive close for {isin}/{ticker}")
    return row


def verification_status(row: dict[str, Any]) -> str:
    providers = [str(item) for item in row.get("agreeing_providers") or [] if item]
    agreement = str(row.get("source_agreement_status") or "").lower()
    if len(providers) >= 2 and "disagree" not in agreement:
        return "exact_close_independently_verified"
    if len(providers) == 1:
        return "exact_close_primary_only_verifier_unavailable"
    # Current pricing contract can still be valuation-grade through a correctly
    # bound exact primary even when provider-list metadata is sparse.
    return "valuation_grade_exact_close_verification_not_recorded"


def pricing_authority_summary(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "close_date": row.get("close_date"),
        "close_price": float(row.get("close_price")),
        "valuation_grade": row.get("valuation_grade") is True,
        "verification_status": verification_status(row),
        "agreeing_providers": list(row.get("agreeing_providers") or []),
        "source_id": row.get("source_id"),
        "source_name": row.get("source_name"),
        "source_quality_status": row.get("source_quality_status"),
        "agreement_spread_pct": row.get("agreement_spread_pct"),
        "blockers": list(row.get("blockers") or []),
    }
