from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from pricing.ucits_close_price_validation_contract_v2 import AUTHORIZED_EXACT_STATUSES


def _ticker(row: dict[str, Any]) -> str:
    value = str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()
    return "L0CK" if value == "LOCK" else value


def _num(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Expected numeric value, got {value!r}") from exc


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Required valuation input not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Valuation input must be a JSON object: {path}")
    return payload


def revalue_portfolio(
    portfolio: dict[str, Any],
    pricing: dict[str, Any],
    *,
    report_date: str,
) -> dict[str, Any]:
    """Return a derived report valuation without mutating protected portfolio state.

    Shares, cash, entry basis and trade lineage are inherited unchanged. Current
    price, market value, weight, P/L and NAV are recomputed only from exact funded
    lines authorized by the canonical primary-plus-verification pricing contract.
    A second provider increases verification confidence but is not a universal
    liveness requirement. V1 deliberately supports EUR trading lines only because
    every currently funded Weekly ETF EU position is EUR-denominated; any future
    non-EUR funded line fails closed until an explicit FX conversion contract exists.
    """

    if str(pricing.get("report_date") or "") != report_date:
        raise RuntimeError(
            f"Pricing report_date mismatch for derived valuation: "
            f"pricing={pricing.get('report_date')} expected={report_date}"
        )
    if pricing.get("report_pricing_gate_passed") is not True:
        raise RuntimeError("Canonical pricing gate is not PASS for derived valuation")

    price_index: dict[tuple[str, str], dict[str, Any]] = {}
    for row in pricing.get("rows") or []:
        if not isinstance(row, dict):
            continue
        ticker = _ticker(row)
        isin = str(row.get("isin") or "").strip().upper()
        if not ticker or not isin:
            continue
        price_index[(isin, ticker)] = row

    derived = copy.deepcopy(portfolio)
    positions = [row for row in derived.get("positions") or [] if isinstance(row, dict)]
    if not positions:
        raise RuntimeError("Cannot derive fresh valuation without funded positions")

    invested = 0.0
    valuation_rows: list[dict[str, Any]] = []
    for position in positions:
        ticker = _ticker(position)
        isin = str(position.get("isin") or "").strip().upper()
        evidence = price_index.get((isin, ticker))
        if evidence is None:
            raise RuntimeError(f"Missing exact funded pricing evidence for {ticker} / {isin}")
        if evidence.get("valuation_grade") is not True:
            raise RuntimeError(f"Funded pricing evidence is not valuation-grade for {ticker}")

        authority_status = str(evidence.get("source_agreement_status") or "")
        if authority_status not in AUTHORIZED_EXACT_STATUSES:
            raise RuntimeError(
                f"Funded pricing evidence lacks authorized exact primary close for {ticker}: "
                f"status={authority_status or 'missing'}"
            )
        primary_provider = str(evidence.get("primary_provider") or "").strip()
        if not primary_provider:
            raise RuntimeError(f"Funded pricing evidence lacks primary provider for {ticker}")
        verification_providers = [
            str(value).strip()
            for value in evidence.get("verification_providers") or []
            if str(value).strip()
        ]
        providers = list(dict.fromkeys([primary_provider, *verification_providers]))
        if authority_status == "fresh_exact_verified" and len(providers) < 2:
            raise RuntimeError(f"Verified funded pricing evidence lacks verifier for {ticker}")
        if authority_status == "fresh_exact_unverified" and len(providers) != 1:
            raise RuntimeError(f"Unverified funded pricing evidence must have exactly one provider for {ticker}")

        if str(evidence.get("close_date") or "") != report_date:
            raise RuntimeError(
                f"Funded close date mismatch for {ticker}: "
                f"{evidence.get('close_date')} != {report_date}"
            )
        # Historical portfolio fixtures predate the explicit per-position trading_currency
        # field. For those EUR-only model states, the portfolio base currency is the
        # authoritative compatibility fallback. A present per-position currency always
        # wins, and any mismatch or non-EUR funded line still fails closed below.
        trading_currency = str(
            position.get("trading_currency") or portfolio.get("base_currency") or ""
        ).strip().upper()
        pricing_currency = str(evidence.get("currency") or "").strip().upper()
        if trading_currency != pricing_currency:
            raise RuntimeError(
                f"Trading/pricing currency mismatch for {ticker}: "
                f"portfolio={trading_currency} pricing={pricing_currency}"
            )
        if pricing_currency != "EUR":
            raise RuntimeError(
                f"Derived valuation requires explicit FX contract for non-EUR funded line {ticker}"
            )

        shares = _num(position.get("shares"))
        price = _num(evidence.get("close_price"))
        market_value = shares * price
        previous_price = position.get("current_price_local")
        previous_market_value = position.get("market_value_eur")

        position["previous_price_local"] = previous_price
        position["previous_market_value_local"] = position.get("market_value_local")
        position["previous_market_value_eur"] = previous_market_value
        position["previous_weight_pct"] = position.get("current_weight_pct")
        position["current_price_local"] = price
        position["market_value_local"] = round(market_value, 2)
        position["market_value_eur"] = round(market_value, 2)
        position["price_date"] = report_date
        position["pricing_completed_close"] = True
        position["pricing_status"] = "qualified_completed_close_primary_plus_verification"
        position["verification_status"] = authority_status
        position["pricing_source"] = "canonical v2 completed-close primary plus verification contract"
        position["pricing_source_quality"] = f"valuation_grade_{authority_status}"
        position["valuation_source"] = "canonical_v2_completed_close_contract"
        position["model_execution_price_basis"] = (
            f"{report_date} exact-line completed-close primary pricing authority; "
            f"verification_status={authority_status}; model valuation only, no broker order"
        )
        avg_entry = _num(position.get("avg_entry_local")) if position.get("avg_entry_local") not in (None, "") else 0.0
        pnl = (price - avg_entry) * shares if avg_entry else 0.0
        position["unrealized_pnl_eur"] = round(pnl, 2)
        position["unrealized_pnl_pct"] = round(((price / avg_entry) - 1.0) * 100.0, 6) if avg_entry else 0.0
        invested += market_value
        valuation_rows.append(
            {
                "ticker": ticker,
                "isin": isin,
                "shares": int(shares),
                "close_price_eur": price,
                "market_value_eur": round(market_value, 2),
                "close_date": report_date,
                "primary_provider": primary_provider,
                "verification_providers": verification_providers,
                "source_agreement_status": authority_status,
                "agreeing_providers": providers,
            }
        )

    cash = _num(derived.get("cash_eur"))
    nav = cash + invested
    if nav <= 0:
        raise RuntimeError("Derived NAV must be positive")
    for position in positions:
        position["current_weight_pct"] = round(_num(position.get("market_value_eur")) / nav * 100.0, 6)
        position["portfolio_contribution_pct_nav"] = round(_num(position.get("unrealized_pnl_eur")) / nav * 100.0, 6)

    derived["positions"] = positions
    derived["invested_market_value_eur"] = round(invested, 2)
    derived["nav_eur"] = round(nav, 2)
    derived["last_valuation_report_date"] = report_date
    derived["last_valuation_run_id"] = str(pricing.get("run_id") or "") or None
    derived["last_valuation_source"] = "canonical_v2_completed_close_contract_derived_report_state"
    derived["derived_valuation"] = {
        "report_date": report_date,
        "pricing_artifact_report_date": pricing.get("report_date"),
        "portfolio_mutation": False,
        "trade_ledger_write": False,
        "shares_changed": False,
        "cash_changed": False,
        "real_broker_execution": False,
        "funded_position_count": len(positions),
        "invested_market_value_eur": round(invested, 2),
        "cash_eur": round(cash, 2),
        "nav_eur": round(nav, 2),
        "lines": valuation_rows,
    }
    return derived


def revalue_from_files(*, portfolio_path: Path, pricing_path: Path, report_date: str) -> dict[str, Any]:
    return revalue_portfolio(_load(portfolio_path), _load(pricing_path), report_date=report_date)
