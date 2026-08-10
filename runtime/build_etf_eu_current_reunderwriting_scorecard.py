from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


FIELDS = [
    "report_date", "isin", "exchange_ticker", "fund_name", "weight_pct", "shares",
    "current_price_local", "trading_currency", "market_value_eur", "price_date",
    "current_price_status", "pricing_source", "pricing_agreement_status", "total_score",
    "suggested_action", "conviction_tier", "portfolio_role", "fresh_cash_test",
    "would_initiate_today", "would_initiate_at_current_weight", "thesis_score",
    "implementation_score", "replaceable_status", "weeks_replaceable", "best_alternative",
    "contribution_quality", "factor_overlap_flag", "hedge_validity_status",
    "cash_policy_flag", "required_next_action", "override_reason", "discipline_flags",
    "ucits_status", "priips_kid_status", "investability_status",
    "reunderwriting_status", "source_report",
]


def load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def normalize_ticker(value: Any) -> str:
    ticker = str(value or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def positions_from_sources(portfolio: dict[str, Any], state: dict[str, Any]) -> list[dict[str, Any]]:
    official = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    rows = official.get("positions") if isinstance(official.get("positions"), list) else None
    if rows is None:
        rows = portfolio.get("positions") or []
    result = [dict(row) for row in rows if isinstance(row, dict)]
    if not result:
        raise RuntimeError("No funded positions available for current re-underwriting")
    seen: set[str] = set()
    for row in result:
        ticker = normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
        if not ticker or ticker in seen:
            raise RuntimeError(f"Invalid or duplicate funded ticker in re-underwriting source: {ticker!r}")
        seen.add(ticker)
    return result


def donor_index(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in state.get("promoted_exposures") or []:
        if not isinstance(row, dict):
            continue
        ticker = normalize_ticker(row.get("exchange_symbol") or row.get("portfolio_label"))
        if ticker:
            result[ticker] = dict(row)
    for row in state.get("stage_1_review_candidates") or []:
        if not isinstance(row, dict):
            continue
        ticker = normalize_ticker(row.get("exchange_symbol") or row.get("portfolio_label"))
        if ticker:
            result.setdefault(ticker, {}).update({
                "donor_review_status": row.get("donor_review_status"),
                "current_promotion_score": row.get("current_promotion_score"),
                "currently_promoted": row.get("currently_promoted"),
            })
    return result


def prior_index(path: Path | None) -> dict[str, dict[str, str]]:
    if path is None or not path.exists():
        return {}
    result: dict[str, dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            ticker = normalize_ticker(row.get("exchange_ticker") or row.get("ticker"))
            if ticker:
                result[ticker] = dict(row)
    return result


def pricing_index(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in payload.get("rows") or []:
        if not isinstance(row, dict):
            continue
        ticker = normalize_ticker(row.get("ticker"))
        if ticker:
            result[ticker] = dict(row)
    return result


def cash_policy(portfolio: dict[str, Any], state: dict[str, Any]) -> str:
    official = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else portfolio
    nav = float(official.get("nav_eur") or portfolio.get("nav_eur") or 0.0)
    cash = float(official.get("cash_eur") or portfolio.get("cash_eur") or 0.0)
    pct = cash / nav * 100.0 if nav else 0.0
    if pct > 5.0:
        return f"Meaningful cash position ({pct:.2f}%); deploy-or-explain against current fundable opportunities"
    if pct > 3.0:
        return f"Cash {pct:.2f}% requires deploy-or-explain review when actionable opportunities exist"
    return f"Cash {pct:.2f}% within routine residual range"


def factor_flag(ticker: str) -> str:
    if ticker in {"VWCE", "SXR8"}:
        return "Review measured embedded semiconductor overlap lower bound; no hard cap implied"
    if ticker == "L0CK":
        return "Review measured embedded cybersecurity overlap lower bound; incomplete holdings coverage"
    if ticker == "EUNA":
        return "Role diversifier / bond stabiliser; equity-overlap test not primary"
    return "Current overlap review required"


def hedge_status(ticker: str, role: str) -> str:
    text = role.casefold()
    if ticker == "EUNA" or "bond" in text or "stabilis" in text:
        return "Ballast role requires current contribution/drawdown review"
    return "Not designated hedge/ballast sleeve"


def selected_price(position: dict[str, Any], pricing: dict[str, Any] | None, report_date: str) -> dict[str, Any]:
    pricing = pricing or {}
    close = pricing.get("close_price")
    close_date = str(pricing.get("close_date") or "")[:10]
    current = (
        close is not None
        and close_date == report_date
        and pricing.get("completed_close_on_or_before_report_date") is True
    )
    if current:
        price = float(close)
        shares = float(position.get("shares") or 0.0)
        currency = str(pricing.get("currency") or position.get("trading_currency") or position.get("currency") or "")
        # Current funded lines are EUR in the protected portfolio. If a future
        # funded line is non-EUR, NAV conversion must come from normalized state;
        # do not fabricate FX here.
        market_value = round(shares * price, 2) if currency == "EUR" else position.get("market_value_eur")
        return {
            "price": price,
            "price_date": close_date,
            "status": "current_report_date_completed_close",
            "source": pricing.get("source_name") or pricing.get("source_id") or "current_pricing_artifact",
            "agreement": pricing.get("source_agreement_status") or "",
            "currency": currency,
            "market_value_eur": market_value,
        }

    price = position.get("current_price_local") or position.get("selected_close")
    price_date = str(position.get("price_date") or position.get("last_valuation_report_date") or "")[:10]
    status = "missing" if not price else "prior_or_stale_requires_current_evidence"
    return {
        "price": price,
        "price_date": price_date,
        "status": status,
        "source": position.get("pricing_source") or "protected_portfolio_state",
        "agreement": position.get("pricing_source_quality") or "",
        "currency": position.get("trading_currency") or position.get("currency"),
        "market_value_eur": position.get("market_value_eur"),
    }


def build_rows(
    portfolio: dict[str, Any],
    state: dict[str, Any],
    prior: dict[str, dict[str, str]],
    report_date: str,
    source_report: str,
    pricing_payload: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    donor = donor_index(state)
    prices = pricing_index(pricing_payload or {})
    cash_flag = cash_policy(portfolio, state)
    rows: list[dict[str, Any]] = []
    for position in positions_from_sources(portfolio, state):
        ticker = normalize_ticker(position.get("ticker") or position.get("exchange_ticker"))
        donor_row = donor.get(ticker, {})
        old = prior.get(ticker, {})
        price = selected_price(position, prices.get(ticker), report_date)
        donor_score = donor_row.get("shared_score") or donor_row.get("current_promotion_score")
        donor_review = str(donor_row.get("donor_review_status") or "")
        currently_promoted = donor_row.get("currently_promoted")
        evidence_current = price["status"] == "current_report_date_completed_close"

        if donor_review:
            fresh_cash = donor_review
        elif evidence_current:
            fresh_cash = "Current completed-close evidence available; explicit fresh-cash re-underwriting required"
        else:
            fresh_cash = "Unresolved until current completed-close re-underwriting is complete"

        if donor_review and "hold" in donor_review.casefold():
            initiate_today = "Smaller/monitor" if "smaller" in donor_review.casefold() else "Hold/monitor"
        elif evidence_current:
            initiate_today = "Unresolved"
        else:
            initiate_today = "Unresolved"

        current_weight = float(position.get("current_weight_pct") or position.get("weight_pct") or 0.0)
        initiate_weight = "No/Review" if current_weight > 0 and initiate_today in {"Smaller/monitor", "Unresolved"} else "Unresolved"

        replaceable = old.get("replaceable_status") or "Current review required"
        try:
            weeks = int(float(old.get("weeks_replaceable") or 0))
        except (TypeError, ValueError):
            weeks = 0
        if replaceable.casefold() not in {"none", "", "current review required"}:
            weeks += 1

        role = str(position.get("portfolio_role") or "")
        action = "hold_current_state_pending_reunderwriting"
        if ticker == "L0CK" and currently_promoted is True:
            action = "hold_monitor_current_position"

        rows.append({
            "report_date": report_date,
            "isin": position.get("isin"),
            "exchange_ticker": ticker,
            "fund_name": position.get("fund_name"),
            "weight_pct": round(current_weight, 6),
            "shares": int(float(position.get("shares") or 0)),
            "current_price_local": price["price"],
            "trading_currency": price["currency"],
            "market_value_eur": price["market_value_eur"],
            "price_date": price["price_date"],
            "current_price_status": price["status"],
            "pricing_source": price["source"],
            "pricing_agreement_status": price["agreement"],
            "total_score": donor_score if donor_score is not None else "",
            "suggested_action": action,
            "conviction_tier": position.get("conviction_tier") or "",
            "portfolio_role": role,
            "fresh_cash_test": fresh_cash,
            "would_initiate_today": initiate_today,
            "would_initiate_at_current_weight": initiate_weight,
            "thesis_score": old.get("thesis_score") or "",
            "implementation_score": old.get("implementation_score") or "",
            "replaceable_status": replaceable,
            "weeks_replaceable": weeks,
            "best_alternative": old.get("best_alternative") or "",
            "contribution_quality": old.get("contribution_quality") or "Current contribution review required",
            "factor_overlap_flag": factor_flag(ticker),
            "hedge_validity_status": hedge_status(ticker, role),
            "cash_policy_flag": cash_flag,
            "required_next_action": "Complete current re-underwriting before any new add/reduce/replace decision",
            "override_reason": "No portfolio mutation authorized by convergence/report reconstruction",
            "discipline_flags": "current_reunderwriting_required" + (";price_refresh_required" if not evidence_current else ""),
            "ucits_status": position.get("ucits_status"),
            "priips_kid_status": position.get("priips_kid_status"),
            "investability_status": position.get("investability_status"),
            "reunderwriting_status": "CURRENT_EVIDENCE_READY_FOR_REVIEW" if evidence_current else "CURRENT_REVIEW_REQUIRED",
            "source_report": source_report,
        })
    return rows


def write(rows: list[dict[str, Any]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build current-run ETF EU capital re-underwriting memory for every funded position")
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--convergence-state", type=Path)
    parser.add_argument("--pricing-artifact", type=Path)
    parser.add_argument("--prior-scorecard", type=Path, default=Path("output/etf_eu_recommendation_scorecard.csv"))
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--source-report", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    portfolio = load_json(args.portfolio_state)
    state = load_json(args.convergence_state)
    pricing_payload = load_json(args.pricing_artifact)
    prior = prior_index(args.prior_scorecard)
    rows = build_rows(portfolio, state, prior, args.report_date, args.source_report, pricing_payload)
    write(rows, args.output)
    current_prices = sum(row["current_price_status"] == "current_report_date_completed_close" for row in rows)
    print(
        "ETF_EU_CURRENT_REUNDERWRITING_SCORECARD_OK"
        f" | funded_positions={len(rows)} | current_prices={current_prices}"
        f" | tickers={','.join(row['exchange_ticker'] for row in rows)}"
        " | portfolio_mutation=false"
    )


if __name__ == "__main__":
    main()
