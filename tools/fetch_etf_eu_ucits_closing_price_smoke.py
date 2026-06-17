from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

PENDING_VALUES = {"", "tbd", "pending_verification", "none", "null"}
AUTHORITY_FALSE = {
    "valuation_grade": False,
    "funding_authority": False,
    "portfolio_mutation": False,
    "production_delivery": False,
    "candidate_promotion": False,
    "recipient_activation": False,
    "real_recipients": False,
    "smtp_configured": False,
    "secrets_present": False,
    "mail_transport_enabled": False,
    "external_mail_api_enabled": False,
    "real_receipt": False,
    "proof_claimed": False,
    "send_attempted": False,
    "authority_granted": False,
    "wp14_authority": False,
}


@dataclass(frozen=True)
class PriceCandidate:
    registry_id: str
    isin: str
    fund_name: str
    exchange: str
    exchange_ticker: str
    trading_currency: str
    provider_symbol: str
    pricing_symbol: str


def _norm(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _is_pending(value: Any) -> bool:
    text = _norm(value).lower()
    return text in PENDING_VALUES or text.startswith("pending_")


def _created_at_from_run_id(run_id: str) -> str:
    if len(run_id) >= 8 and run_id[:8].isdigit():
        return f"{run_id[:4]}-{run_id[4:6]}-{run_id[6:8]}T00:00:00Z"
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Registry must be a YAML object: {path}")
    return payload


def extract_price_candidates(registry_path: Path) -> tuple[list[PriceCandidate], list[dict[str, Any]], dict[str, int]]:
    registry = _load_yaml(registry_path)
    candidates: list[PriceCandidate] = []
    failures: list[dict[str, Any]] = []
    funds = registry.get("funds") or []
    trading_lines_seen = 0
    for fund in funds:
        if not isinstance(fund, dict):
            continue
        for line in fund.get("trading_lines") or []:
            if not isinstance(line, dict):
                continue
            trading_lines_seen += 1
            pricing_symbol = _norm(line.get("pricing_symbol_yahoo"))
            base_failure = {
                "registry_id": _norm(fund.get("registry_id")),
                "exchange_ticker": _norm(line.get("exchange_ticker")),
                "pricing_symbol": pricing_symbol or "",
            }
            if _is_pending(pricing_symbol):
                failures.append(
                    {
                        **base_failure,
                        "status": "skipped_pending_symbol",
                        "reason": "pricing symbol is pending verification",
                    }
                )
                continue
            candidates.append(
                PriceCandidate(
                    registry_id=_norm(fund.get("registry_id")),
                    isin=_norm(fund.get("isin")),
                    fund_name=_norm(fund.get("fund_name")),
                    exchange=_norm(line.get("exchange")),
                    exchange_ticker=_norm(line.get("exchange_ticker")),
                    trading_currency=_norm(line.get("trading_currency")),
                    provider_symbol=_norm(line.get("provider_symbol")),
                    pricing_symbol=pricing_symbol,
                )
            )
    return candidates, failures, {"funds_seen": len(funds), "trading_lines_seen": trading_lines_seen}


def _load_fixture_prices(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Fixture prices must be a JSON object keyed by pricing symbol")
    return payload


def _fixture_fetch(candidate: PriceCandidate, fixture_prices: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    row = fixture_prices.get(candidate.pricing_symbol)
    if not isinstance(row, dict):
        return None
    return {
        "source": row.get("source", "fixture"),
        "close_date": row.get("close_date"),
        "close": row.get("close"),
    }


def _live_fetch(candidate: PriceCandidate) -> dict[str, Any] | None:
    try:
        import yfinance as yf  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(f"yfinance import failed: {exc}") from exc
    try:
        history = yf.Ticker(candidate.pricing_symbol).history(period="7d", interval="1d", auto_adjust=False)
    except Exception as exc:  # pragma: no cover - network/source dependent
        raise RuntimeError(f"source error for {candidate.pricing_symbol}: {exc}") from exc
    if history is None or history.empty or "Close" not in history:
        return None
    closes = history["Close"].dropna()
    if closes.empty:
        return None
    close = float(closes.iloc[-1])
    close_date = closes.index[-1]
    try:
        close_date_text = close_date.date().isoformat()
    except AttributeError:
        close_date_text = str(close_date)[:10]
    return {"source": "yfinance", "close_date": close_date_text, "close": close}


def _price_row(candidate: PriceCandidate, result: dict[str, Any]) -> dict[str, Any]:
    return {
        "registry_id": candidate.registry_id,
        "isin": candidate.isin,
        "fund_name": candidate.fund_name,
        "exchange": candidate.exchange,
        "exchange_ticker": candidate.exchange_ticker,
        "trading_currency": candidate.trading_currency,
        "provider_symbol": candidate.provider_symbol,
        "pricing_symbol": candidate.pricing_symbol,
        "source": result["source"],
        "close_date": result["close_date"],
        "close": result["close"],
        "currency_checked": True,
        "status": "price_found",
    }


def build_smoke_artifact(
    *,
    registry: Path,
    output: Path,
    run_id: str,
    fixture_prices_path: Path | None = None,
) -> dict[str, Any]:
    candidates, failures, seen = extract_price_candidates(registry)
    fixture_prices = _load_fixture_prices(fixture_prices_path)
    prices: list[dict[str, Any]] = []
    source_errors = 0
    prices_missing = 0
    for candidate in candidates:
        try:
            result = (
                _fixture_fetch(candidate, fixture_prices)
                if fixture_prices_path is not None
                else _live_fetch(candidate)
            )
        except Exception as exc:
            source_errors += 1
            failures.append(
                {
                    "registry_id": candidate.registry_id,
                    "exchange_ticker": candidate.exchange_ticker,
                    "pricing_symbol": candidate.pricing_symbol,
                    "status": "source_error",
                    "reason": str(exc),
                }
            )
            continue
        if result is None or not result.get("close_date") or float(result.get("close") or 0) <= 0:
            prices_missing += 1
            failures.append(
                {
                    "registry_id": candidate.registry_id,
                    "exchange_ticker": candidate.exchange_ticker,
                    "pricing_symbol": candidate.pricing_symbol,
                    "status": "price_unavailable",
                    "reason": "no positive latest daily close returned by source",
                }
            )
            continue
        prices.append(_price_row(candidate, result))

    skipped = sum(1 for failure in failures if failure.get("status") == "skipped_pending_symbol")
    selected_next = "WP14F" if prices else "WP14F_SOURCE_REVIEW"
    selected_title = (
        "First ETF EU draft report from UCITS identity and closing-price smoke data, review-only"
        if prices
        else "UCITS pricing source review and fallback selection"
    )
    artifact = {
        "schema_version": "etf_eu_ucits_closing_price_smoke_v1",
        "run_id": run_id,
        "created_at_utc": _created_at_from_run_id(run_id),
        "status": "completed",
        "purpose": "ucits_closing_price_source_smoke_test",
        "registry_path": str(registry),
        "source_policy": {
            "primary_source": "yahoo_or_yfinance",
            "fallback_source": "none_for_wp14e",
            "us_proxy_substitution_allowed": False,
            "paid_api_required": False,
            "secrets_required": False,
        },
        "summary": {
            "funds_seen": seen["funds_seen"],
            "trading_lines_seen": seen["trading_lines_seen"],
            "pricing_symbols_attempted": len(candidates),
            "prices_found": len(prices),
            "prices_missing": prices_missing,
            "symbols_skipped": skipped,
            "source_errors": source_errors,
        },
        "prices": prices,
        "failures": failures,
        "authority": dict(AUTHORITY_FALSE),
        "selected_next_package": selected_next,
        "selected_next_package_title": selected_title,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--fixture-prices")
    args = parser.parse_args()
    artifact = build_smoke_artifact(
        registry=Path(args.registry),
        output=Path(args.output),
        run_id=args.run_id,
        fixture_prices_path=Path(args.fixture_prices) if args.fixture_prices else None,
    )
    summary = artifact["summary"]
    print(
        "ETF_EU_UCITS_CLOSING_PRICE_SMOKE_FETCHED | "
        f"output={args.output} | attempted={summary['pricing_symbols_attempted']} | "
        f"prices_found={summary['prices_found']} | skipped={summary['symbols_skipped']} | "
        f"source_errors={summary['source_errors']} | selected_next_package={artifact['selected_next_package']}"
    )


if __name__ == "__main__":
    main()
