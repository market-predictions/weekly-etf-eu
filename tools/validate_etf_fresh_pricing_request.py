from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path
from typing import Any

EXACT_STATUSES = {"fresh_exact_close", "fresh_exact_unverified", "fresh_close"}
PRIOR_STATUSES = {"prior_valid_close", "fresh_fallback_source"}
BAD_STATUSES = {"carried_forward", "unresolved", "blocked"}


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default


def _to_int(value: str | None, default: int) -> int:
    try:
        return int(str(value)) if value not in {None, ""} else default
    except ValueError:
        return default


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _date_or_none(value: Any) -> date | None:
    try:
        if not value:
            return None
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _close_lag(requested: str, returned: Any) -> int | None:
    req = _date_or_none(requested)
    ret = _date_or_none(returned)
    if req is None or ret is None:
        return None
    return (req - ret).days


def _latest_audit_from_pointer(pricing_dir: Path) -> Path:
    pointer = pricing_dir / "latest_price_audit_path.txt"
    if pointer.exists():
        raw = pointer.read_text(encoding="utf-8").strip()
        path = Path(raw)
        if path.exists():
            return path
        candidate = pricing_dir / path.name
        if candidate.exists():
            return candidate
    files = sorted(pricing_dir.glob("price_audit_*.json"))
    if not files:
        raise RuntimeError(f"No price_audit_*.json files found in {pricing_dir}")
    return files[-1]


def _holding_weights(audit: dict[str, Any]) -> dict[str, float]:
    holdings = audit.get("holdings") or []
    total = 0.0
    values: dict[str, float] = {}
    for h in holdings:
        symbol = str(h.get("ticker") or "").upper()
        if not symbol:
            continue
        value = _to_float(h.get("previous_market_value_eur"), 0.0)
        values[symbol] = value
        total += value
    if total <= 0:
        return {symbol: 0.0 for symbol in values}
    return {symbol: round(value / total * 100.0, 4) for symbol, value in values.items()}


def validate(audit: dict[str, Any], audit_path: Path) -> None:
    requested = os.environ.get("ETF_REQUESTED_CLOSE_DATE") or str(audit.get("requested_close_date") or "")
    audit_requested = str(audit.get("requested_close_date") or "")
    if requested and audit_requested and requested != audit_requested:
        raise RuntimeError(
            f"Fresh pricing request mismatch: workflow requested {requested}, but pricing audit {audit_path.name} used {audit_requested}."
        )
    if not requested:
        requested = audit_requested
    if not requested:
        raise RuntimeError("Fresh pricing validation failed: no requested close date found in env or audit.")

    strict = _to_bool(os.environ.get("ETF_STRICT_FRESH_PRICING_REQUIRED"), False)
    min_count_pct = _to_float(os.environ.get("ETF_FRESH_PRICE_MIN_COUNT_PCT"), 83.34)
    min_weight_pct = _to_float(os.environ.get("ETF_FRESH_PRICE_MIN_WEIGHT_PCT"), 85.0)
    max_stale_holdings = _to_int(os.environ.get("ETF_MAX_STALE_HOLDINGS"), 1)
    max_stale_weight_pct = _to_float(os.environ.get("ETF_MAX_STALE_WEIGHT_PCT"), 20.0)
    max_lag_days = _to_int(os.environ.get("ETF_MAX_ACCEPTABLE_CLOSE_LAG_DAYS"), 1)

    weights = _holding_weights(audit)
    holding_symbols = set(weights)
    price_rows = audit.get("price_results") or audit.get("prices") or []

    exact: list[str] = []
    tolerated: list[str] = []
    blocked: list[str] = []
    tolerated_weight = 0.0
    exact_weight = 0.0

    by_symbol: dict[str, dict[str, Any]] = {}
    for row in price_rows:
        symbol = str(row.get("symbol") or "").upper()
        if symbol in holding_symbols:
            by_symbol[symbol] = row

    for symbol in sorted(holding_symbols):
        row = by_symbol.get(symbol)
        if not row:
            blocked.append(f"{symbol}:missing_price_row")
            continue
        status = str(row.get("status") or "")
        returned = row.get("returned_close_date")
        lag = _close_lag(requested, returned)
        weight = weights.get(symbol, 0.0)
        if status in EXACT_STATUSES and lag == 0 and row.get("price") is not None:
            exact.append(symbol)
            exact_weight += weight
        elif status in PRIOR_STATUSES and row.get("price") is not None and lag is not None and 0 < lag <= max_lag_days:
            tolerated.append(f"{symbol}:{returned}:{status}")
            tolerated_weight += weight
        elif status in BAD_STATUSES:
            blocked.append(f"{symbol}:{returned or 'missing'}:{status}")
        else:
            blocked.append(f"{symbol}:{returned or 'missing'}:{status or 'unknown'}")

    holdings_count = len(holding_symbols)
    exact_count_pct = round(len(exact) / holdings_count * 100.0, 2) if holdings_count else 0.0
    exact_weight_pct = round(exact_weight, 2)
    tolerated_weight_pct = round(tolerated_weight, 2)

    if strict:
        if len(exact) != holdings_count or blocked or tolerated:
            raise RuntimeError(
                "Strict fresh pricing failed: all holdings must have exact requested-close pricing. "
                f"requested_close={requested}; exact={exact}; tolerated={tolerated}; blocked={blocked}"
            )
    else:
        if blocked:
            raise RuntimeError(
                "Balanced fresh pricing failed: unresolved/carried/blocked holding prices are not allowed. "
                f"requested_close={requested}; blocked={blocked}; tolerated={tolerated}"
            )
        if len(tolerated) > max_stale_holdings or tolerated_weight_pct > max_stale_weight_pct:
            raise RuntimeError(
                "Balanced fresh pricing failed: stale/prior-valid tolerance exceeded. "
                f"requested_close={requested}; tolerated={tolerated}; tolerated_weight_pct={tolerated_weight_pct:.2f}; "
                f"limits=max_holdings={max_stale_holdings}, max_weight_pct={max_stale_weight_pct:.2f}"
            )
        if exact_count_pct < min_count_pct and exact_weight_pct < min_weight_pct:
            raise RuntimeError(
                "Balanced fresh pricing failed: exact-close coverage too weak. "
                f"requested_close={requested}; exact_count_pct={exact_count_pct:.2f}; exact_weight_pct={exact_weight_pct:.2f}; "
                f"min_count_pct={min_count_pct:.2f}; min_weight_pct={min_weight_pct:.2f}; tolerated={tolerated}"
            )

    print(
        "ETF_FRESH_PRICING_REQUEST_OK | "
        f"audit={audit_path.name} | requested_close={requested} | strict={strict} | "
        f"holdings={holdings_count} | exact={len(exact)} | exact_count_pct={exact_count_pct:.2f} | "
        f"exact_weight_pct={exact_weight_pct:.2f} | tolerated={len(tolerated)} | tolerated_weight_pct={tolerated_weight_pct:.2f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pricing-dir", default="output/pricing")
    parser.add_argument("--audit", default="")
    args = parser.parse_args()

    audit_path = Path(args.audit) if args.audit else _latest_audit_from_pointer(Path(args.pricing_dir))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    validate(audit, audit_path)


if __name__ == "__main__":
    main()
