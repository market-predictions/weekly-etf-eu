from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

VERIFIED_LINE_STATUS = "verified_ucits_trading_line"
PROVIDER_SYMBOL_FIELDS = {
    "leeway": "provider_symbol_leeway",
    "eodhd": "provider_symbol_eodhd",
    "marketstack": "provider_symbol_marketstack",
    "alpha_vantage": "provider_symbol_alpha_vantage",
    "yahoo_chart": "pricing_symbol_yahoo",
}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _upper(value: Any) -> str:
    return _text(value).upper()


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected YAML object: {path}")
    return payload


def _registry_lines(symbol_registry: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fund in symbol_registry.get("funds") or []:
        if not isinstance(fund, dict):
            continue
        isin = _upper(fund.get("isin"))
        for line in fund.get("trading_lines") or []:
            if not isinstance(line, dict):
                continue
            rows.append(
                {
                    "registry_id": _text(fund.get("registry_id")),
                    "isin": isin,
                    "exchange": _text(line.get("exchange")),
                    "venue_code": _upper(line.get("venue_code")),
                    "ticker": _upper(line.get("exchange_ticker")),
                    "currency": _upper(line.get("trading_currency")),
                    "line_verification_status": _text(line.get("line_verification_status")),
                    "line": line,
                }
            )
    return rows


def build_provider_identity_binding(
    *,
    symbol_registry_path: Path,
    provider_registry_path: Path,
    provider_scope: list[str],
) -> dict[str, Any]:
    """Bind provider symbols to the canonical static UCITS trading-line registry.

    This is identity evidence only. It never creates pricing, funding, portfolio,
    execution or delivery authority. Live price providers may verify a close, but
    they do not need to re-prove stable ISIN/MIC/ticker/currency identity each run.
    """

    symbol_registry = _load_yaml(symbol_registry_path)
    provider_registry = _load_yaml(provider_registry_path)
    canonical_lines = _registry_lines(symbol_registry)
    rows: list[dict[str, Any]] = []

    for provider_line in provider_registry.get("trading_lines") or []:
        if not isinstance(provider_line, dict):
            continue
        basket_id = _text(provider_line.get("basket_id"))
        isin = _upper(provider_line.get("isin"))
        ticker = _upper(provider_line.get("ticker"))
        venue_code = _upper(provider_line.get("venue_code"))
        currency = _upper(provider_line.get("currency"))
        exchange = _text(provider_line.get("exchange"))
        funded = bool(provider_line.get("funded"))

        matches = [
            row
            for row in canonical_lines
            if row["isin"] == isin
            and row["ticker"] == ticker
            and row["venue_code"] == venue_code
            and row["currency"] == currency
            and row["exchange"].casefold() == exchange.casefold()
        ]
        blockers: list[str] = []
        provider_symbol_bindings: dict[str, dict[str, Any]] = {}

        if len(matches) != 1:
            blockers.append(f"canonical_trading_line_match_count:{len(matches)}")
            matched = None
        else:
            matched = matches[0]
            if matched["line_verification_status"] != VERIFIED_LINE_STATUS:
                blockers.append("canonical_trading_line_not_verified")

        configured_symbols = provider_line.get("provider_symbols") or {}
        for provider in provider_scope:
            expected_field = PROVIDER_SYMBOL_FIELDS.get(provider)
            provider_symbol = _text(configured_symbols.get(provider))
            canonical_symbol = _text((matched or {}).get("line", {}).get(expected_field)) if expected_field else ""
            symbol_blockers: list[str] = []
            if expected_field is None:
                symbol_blockers.append("unsupported_provider_identity_mapping")
            if not provider_symbol:
                symbol_blockers.append("provider_registry_symbol_missing")
            if not canonical_symbol:
                symbol_blockers.append("canonical_provider_symbol_missing")
            if provider_symbol and canonical_symbol and provider_symbol != canonical_symbol:
                symbol_blockers.append("provider_symbol_mismatch")
            provider_symbol_bindings[provider] = {
                "provider_registry_symbol": provider_symbol or None,
                "canonical_registry_symbol": canonical_symbol or None,
                "matched": not symbol_blockers,
                "blockers": symbol_blockers,
            }
            blockers.extend(f"{provider}:{item}" for item in symbol_blockers)

        bound = not blockers
        rows.append(
            {
                "basket_id": basket_id,
                "funded": funded,
                "isin": isin,
                "ticker": ticker,
                "exchange": exchange,
                "venue_code": venue_code,
                "currency": currency,
                "registry_id": (matched or {}).get("registry_id"),
                "line_verification_status": (matched or {}).get("line_verification_status"),
                "provider_symbol_bindings": provider_symbol_bindings,
                "static_identity_binding": bound,
                "binding_status": "verified_static_exact_line" if bound else "identity_binding_failed",
                "blockers": sorted(set(blockers)),
            }
        )

    funded_rows = [row for row in rows if row["funded"]]
    return {
        "schema_version": "ucits_provider_identity_binding_v1",
        "symbol_registry": str(symbol_registry_path),
        "provider_registry": str(provider_registry_path),
        "canonical_identity": symbol_registry.get("canonical_identity"),
        "provider_scope": provider_scope,
        "line_count": len(rows),
        "bound_line_count": sum(bool(row["static_identity_binding"]) for row in rows),
        "funded_line_count": len(funded_rows),
        "funded_bound_line_count": sum(bool(row["static_identity_binding"]) for row in funded_rows),
        "all_funded_identity_bound": bool(funded_rows) and all(bool(row["static_identity_binding"]) for row in funded_rows),
        "funding_authority": False,
        "portfolio_mutation": False,
        "real_broker_execution": False,
        "delivery_authority": False,
        "rows": rows,
    }
