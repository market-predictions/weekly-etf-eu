from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def normalized_ticker(value: Any) -> str:
    ticker = str(value or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def qualified_price_rows(pricing: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    """Index provider-agnostic WP11A consensus rows by exact instrument identity.

    The transition overlay must consume the qualification contract, not a historical
    provider pair. A pricing row is eligible here only when it carries the WP11A
    qualified-consensus status, at least two agreeing providers, and a completed
    close value/date. Exact-line identity is enforced separately against the
    qualification artifact before any transition row is updated.
    """
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for row in pricing.get("rows") or []:
        if not isinstance(row, dict):
            continue
        if row.get("source_agreement_status") != "qualified_development_consensus":
            continue
        providers = {str(value).strip() for value in row.get("agreeing_providers") or [] if str(value).strip()}
        if len(providers) < 2:
            continue
        if row.get("close_price") is None or not row.get("close_date"):
            continue
        isin = str(row.get("isin") or "").strip().upper()
        ticker = normalized_ticker(row.get("ticker"))
        if isin and ticker:
            result[(isin, ticker)] = row
    return result


def qualification_rows(qualification: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for row in qualification.get("lines") or []:
        if not isinstance(row, dict):
            continue
        isin = str(row.get("isin") or "").strip().upper()
        ticker = normalized_ticker(row.get("ticker"))
        if isin and ticker:
            result[(isin, ticker)] = row
    return result


def exchange_turnover_evidence(row: dict[str, Any]) -> dict[str, Any] | None:
    """Return optional exchange-turnover corroboration when a provider exposes it.

    This remains optional and does not determine price qualification. The current
    WP11A Alpha+Yahoo route has no Börse turnover payload, so absence must not block
    a valid same-date two-provider close consensus.
    """
    for provider in row.get("provider_results") or []:
        if not isinstance(provider, dict) or provider.get("provider") != "boerse_frankfurt_xetra":
            continue
        evidence_rows = provider.get("identity_evidence") or []
        first = evidence_rows[0] if evidence_rows and isinstance(evidence_rows[0], dict) else {}
        turnover = first.get("turnover_eur")
        pieces = first.get("turnover_pieces")
        if turnover is None and pieces is None:
            return None
        return {
            "provider": "boerse_frankfurt_xetra",
            "report_date_turnover_eur": turnover,
            "report_date_turnover_pieces": pieces,
            "price_fixings": first.get("price_fixings"),
            "session_close_field": first.get("session_close_field"),
            "observed_after_session_end": first.get("observed_after_session_end"),
        }
    return None


def apply(
    transition_path: Path,
    pricing_path: Path,
    qualification_path: Path,
) -> None:
    transition = load_object(transition_path)
    pricing = load_object(pricing_path)
    qualification = load_object(qualification_path)

    transition_report_date = date.fromisoformat(str(transition.get("report_date")))
    if str(pricing.get("report_date")) != transition_report_date.isoformat():
        raise RuntimeError("Pricing and transition report dates differ")
    if str(qualification.get("report_date")) != transition_report_date.isoformat():
        raise RuntimeError("Qualification and transition report dates differ")

    prices = qualified_price_rows(pricing)
    qualification_index = qualification_rows(qualification)
    updated = 0
    updated_exposures: list[str] = []

    for row in transition.get("rows") or []:
        if not isinstance(row, dict):
            continue
        key = (
            str(row.get("isin") or "").strip().upper(),
            normalized_ticker(row.get("ticker")),
        )
        price = prices.get(key)
        qualified = qualification_index.get(key)
        if not price or not qualified:
            continue
        if qualified.get("qualification_status") != "qualified_development_consensus":
            continue
        if qualified.get("identity_anchor_passed") is not True:
            continue
        agreeing_providers = [str(value) for value in price.get("agreeing_providers") or [] if str(value)]
        if len(set(agreeing_providers)) < 2:
            continue

        close_date = date.fromisoformat(str(price.get("close_date")))
        if close_date > transition_report_date:
            raise RuntimeError(f"Future close for {key[1]}: {close_date}")
        retained_liquidity = {
            "median_daily_volume_20d": row.get("median_daily_volume_20d"),
            "median_daily_traded_value_eur_20d": row.get("median_daily_traded_value_eur_20d"),
            "annualized_close_volatility_pct_20d": row.get("annualized_close_volatility_pct_20d"),
            "liquidity_window_rows": row.get("liquidity_window_rows"),
            "prior_price_date": row.get("close_date"),
            "prior_source": row.get("source"),
            "prior_source_quality": row.get("source_quality"),
            "cache_path": row.get("cache_path"),
            "cache_fallback_applied": row.get("cache_fallback_applied"),
        }
        original_status = row.get("status")
        original_blockers = list(row.get("blockers") or [])
        current_turnover = exchange_turnover_evidence(qualified)
        row.update(
            {
                "status": "priced_current_exact_line_consensus",
                "completed_close": True,
                "close_date": close_date.isoformat(),
                "close_price": float(price["close_price"]),
                "whole_share_price_eur": float(price["close_price"]),
                "price_age_calendar_days": (transition_report_date - close_date).days,
                "source": "WP11A qualified same-date completed-close consensus",
                "source_quality": "development_two_source_exact_line_consensus",
                "source_agreement_status": price.get("source_agreement_status"),
                "agreeing_providers": agreeing_providers,
                "agreement_spread_pct": price.get("agreement_spread_pct"),
                "identity_anchor_passed": qualified.get("identity_anchor_passed"),
                "identity_anchor_providers": list(qualified.get("identity_anchor_providers") or []),
                "valuation_grade": False,
                "funding_authority": False,
                "execution_authority": False,
                "production_delivery_authority": False,
                "blockers": [],
                "current_close_overlay": {
                    "applied": True,
                    "pricing_artifact": str(pricing_path),
                    "qualification_artifact": str(qualification_path),
                    "original_status": original_status,
                    "original_blockers": original_blockers,
                    "close_contract": "same_date_two_provider_consensus_with_exact_line_identity_anchor",
                    "commercial_redistribution_authority": False,
                },
                "liquidity_evidence": {
                    "twenty_day_metric_retained": retained_liquidity,
                    "current_report_date_exchange_corroboration": current_turnover,
                    "interpretation": (
                        "The 20-day median remains the policy metric; optional current exchange turnover is corroborating evidence only."
                    ),
                },
            }
        )
        updated += 1
        updated_exposures.append(str(row.get("exposure_id") or ""))

    transition["current_close_overlay"] = {
        "applied": updated > 0,
        "updated_row_count": updated,
        "updated_exposures": sorted(value for value in updated_exposures if value),
        "pricing_artifact": str(pricing_path),
        "qualification_artifact": str(qualification_path),
        "report_date": transition_report_date.isoformat(),
        "authority": "development_price_and_liquidity_input_only",
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
        "production_delivery_authority": False,
    }
    transition["priced_line_count"] = sum(
        1
        for row in transition.get("rows") or []
        if isinstance(row, dict) and str(row.get("status") or "").startswith("priced_")
    )
    transition["completed_close_gate_passed"] = bool(
        transition["priced_line_count"]
        and all(
            row.get("completed_close") is True
            for row in transition.get("rows") or []
            if isinstance(row, dict) and str(row.get("status") or "").startswith("priced_")
        )
    )
    transition_path.write_text(json.dumps(transition, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "CURRENT_CLOSE_TRANSITION_OVERLAY_OK"
        f" | updated={updated}"
        f" | exposures={','.join(sorted(updated_exposures))}"
        f" | output={transition_path}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("transition", type=Path)
    parser.add_argument("--pricing", type=Path, required=True)
    parser.add_argument("--qualification", type=Path, required=True)
    args = parser.parse_args()
    apply(args.transition, args.pricing, args.qualification)


if __name__ == "__main__":
    main()
