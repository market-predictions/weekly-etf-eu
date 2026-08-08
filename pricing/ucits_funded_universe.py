from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

import yaml


def _text(value: Any) -> str:
    return str(value or "").strip()


def _norm_exchange(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", _text(value).lower())


def _position_key(row: Mapping[str, Any]) -> tuple[str, str, str, str]:
    return (
        _text(row.get("isin")).upper(),
        _text(row.get("exchange_ticker") or row.get("ticker")).upper(),
        _norm_exchange(row.get("primary_exchange")),
        _text(row.get("trading_currency")).upper(),
    )


def _registry_key(row: Mapping[str, Any]) -> tuple[str, str, str, str]:
    return (
        _text(row.get("isin")).upper(),
        _text(row.get("ticker")).upper(),
        _norm_exchange(row.get("exchange")),
        _text(row.get("currency")).upper(),
    )


def resolve_provider_registry_funded_universe(
    *,
    registry_path: Path,
    portfolio_state_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Resolve registry funding flags from the authoritative portfolio state.

    Registry `funded` values are compatibility hints only. The current funded universe
    is derived from exact trading-line identity in `output/etf_eu_portfolio_state.json`.
    Missing or ambiguous matches fail closed so a newly funded line can never bypass
    the multi-provider gate because a static registry flag was not updated.
    """

    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    portfolio = json.loads(portfolio_state_path.read_text(encoding="utf-8"))

    trading_lines = [dict(row) for row in registry.get("trading_lines", []) if isinstance(row, Mapping)]
    positions = [dict(row) for row in portfolio.get("positions", []) if isinstance(row, Mapping)]
    funded_positions = [
        row for row in positions
        if _text(row.get("investability_status")).lower() == "funded_model_position"
    ]
    if not funded_positions:
        raise RuntimeError("AUTHORITATIVE_FUNDED_UNIVERSE_EMPTY")

    registry_by_key: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for row in trading_lines:
        key = _registry_key(row)
        registry_by_key.setdefault(key, []).append(row)

    duplicate_registry_keys = [key for key, rows in registry_by_key.items() if len(rows) != 1]
    if duplicate_registry_keys:
        raise RuntimeError(f"PROVIDER_REGISTRY_AMBIGUOUS_TRADING_LINE:{duplicate_registry_keys}")

    funded_keys: list[tuple[str, str, str, str]] = []
    for position in funded_positions:
        key = _position_key(position)
        if not all(key):
            raise RuntimeError(f"PORTFOLIO_FUNDED_LINE_IDENTITY_INCOMPLETE:{position}")
        matches = registry_by_key.get(key, [])
        if len(matches) != 1:
            raise RuntimeError(f"PORTFOLIO_FUNDED_LINE_NOT_EXACTLY_ONE_REGISTRY_MATCH:{key}:matches={len(matches)}")
        funded_keys.append(key)

    if len(set(funded_keys)) != len(funded_keys):
        raise RuntimeError("PORTFOLIO_FUNDED_LINE_DUPLICATE_IDENTITY")

    funded_key_set = set(funded_keys)
    stale_registry_flags: list[str] = []
    resolved_lines: list[dict[str, Any]] = []
    for source_row in trading_lines:
        row = dict(source_row)
        key = _registry_key(row)
        declared = bool(row.get("funded"))
        derived = key in funded_key_set
        if declared != derived:
            stale_registry_flags.append(_text(row.get("basket_id")))
        row["funded"] = derived
        resolved_lines.append(row)

    authority = {
        "authority": "output/etf_eu_portfolio_state.json",
        "portfolio_state_path": str(portfolio_state_path),
        "portfolio_schema_version": portfolio.get("schema_version"),
        "portfolio_mode": portfolio.get("portfolio_mode"),
        "model_portfolio_only": portfolio.get("model_portfolio_only"),
        "real_broker_execution": portfolio.get("real_broker_execution"),
        "funded_position_count": len(funded_positions),
        "funded_basket_ids": sorted(
            _text(registry_by_key[key][0].get("basket_id")) for key in funded_key_set
        ),
        "stale_registry_funded_flags_overridden": sorted(stale_registry_flags),
        "match_contract": "isin+ticker+primary_exchange+trading_currency",
    }

    resolved = dict(registry)
    resolved["funded_universe_authority"] = authority
    resolved["trading_lines"] = resolved_lines
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.safe_dump(resolved, sort_keys=False), encoding="utf-8")
    return authority
