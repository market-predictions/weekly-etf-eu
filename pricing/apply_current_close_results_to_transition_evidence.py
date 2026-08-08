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


def current_price_rows(pricing: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    """Index usable same-date WP11A price rows by exact instrument identity.

    Funded-vs-unfunded authority is enforced later from the native qualification
    artifact. Both two-provider consensus rows and identity-anchored single-source
    candidate rows are retained here; the latter remain non-authoritative and can
    never satisfy the funded valuation gate.
    """
    result: dict[tuple[str, str], dict[str, Any]] = {}
    allowed = {"qualified_development_consensus", "single_source_only"}
    for row in pricing.get("rows") or []:
        if not isinstance(row, dict):
            continue
        if row.get("source_agreement_status") not in allowed:
            continue
        providers = {str(value).strip() for value in row.get("agreeing_providers") or [] if str(value).strip()}
        if not providers or row.get("close_price") is None or not row.get("close_date"):
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
        isin = str(row.get("expected_isin") or row.get("isin") or "").strip().upper()
        ticker = normalized_ticker(row.get("ticker"))
        if isin and ticker:
            result[(isin, ticker)] = row
    return result


def exact_line_identity_anchored(row: dict[str, Any]) -> bool:
    return bool(
        row.get("identity_assurance_status") == "metadata_anchored_exact_line"
        or int(row.get("identity_anchor_provider_count") or 0) > 0
        or row.get("identity_anchor_providers")
    )


def exchange_turnover_evidence(row: dict[str, Any]) -> dict[str, Any] | None:
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


def apply(transition_path: Path, pricing_path: Path, qualification_path: Path) -> None:
    transition = load_object(transition_path)
    pricing = load_object(pricing_path)
    qualification = load_object(qualification_path)
    transition_report_date = date.fromisoformat(str(transition.get("report_date")))
    if str(pricing.get("report_date")) != transition_report_date.isoformat():
        raise RuntimeError("Pricing and transition report dates differ")
    if str(qualification.get("report_date")) != transition_report_date.isoformat():
        raise RuntimeError("Qualification and transition report dates differ")

    prices = current_price_rows(pricing)
    qualification_index = qualification_rows(qualification)
    updated = 0
    updated_exposures: list[str] = []

    for row in transition.get("rows") or []:
        if not isinstance(row, dict):
            continue
        key = (str(row.get("isin") or "").strip().upper(), normalized_ticker(row.get("ticker")))
        price = prices.get(key)
        qualified = qualification_index.get(key)
        if not price or not qualified or not exact_line_identity_anchored(qualified):
            continue

        agreeing_providers = [str(value) for value in price.get("agreeing_providers") or [] if str(value)]
        provider_count = len(set(agreeing_providers))
        qualification_status = str(qualified.get("qualification_status") or "")
        # Missing funded authority is treated conservatively as funded so old
        # artifacts cannot gain a weaker path by omission.
        is_funded = qualified.get("funded") is not False
        if is_funded:
            if qualification_status != "qualified_development_consensus" or provider_count < 2:
                continue
            evidence_status = "priced_current_exact_line_consensus"
            source_quality = "development_two_source_exact_line_consensus"
            close_contract = "funded_same_date_two_provider_consensus_with_exact_line_identity_anchor"
        else:
            if qualification_status not in {"qualified_development_consensus", "single_source_only"} or provider_count < 1:
                continue
            evidence_status = (
                "priced_current_exact_line_consensus"
                if provider_count >= 2
                else "priced_current_exact_line_identity_anchored_single_source"
            )
            source_quality = (
                "development_two_source_exact_line_consensus"
                if provider_count >= 2
                else "development_identity_anchored_single_source_non_authoritative"
            )
            close_contract = (
                "unfunded_same_date_two_provider_consensus_with_exact_line_identity_anchor"
                if provider_count >= 2
                else "unfunded_same_date_identity_anchored_single_source_shadow"
            )

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
        row.update({
            "status": evidence_status,
            "completed_close": True,
            "close_date": close_date.isoformat(),
            "close_price": float(price["close_price"]),
            "whole_share_price_eur": float(price["close_price"]),
            "price_age_calendar_days": (transition_report_date - close_date).days,
            "source": "WP11A completed-close evidence",
            "source_quality": source_quality,
            "source_agreement_status": price.get("source_agreement_status"),
            "agreeing_providers": agreeing_providers,
            "agreement_spread_pct": price.get("agreement_spread_pct"),
            "identity_assurance_status": qualified.get("identity_assurance_status"),
            "identity_anchor_providers": list(qualified.get("identity_anchor_providers") or []),
            "wp11a_funded_line": is_funded,
            "valuation_grade": bool(is_funded and provider_count >= 2),
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
                "close_contract": close_contract,
                "commercial_redistribution_authority": False,
            },
            "liquidity_evidence": {
                "twenty_day_metric_retained": retained_liquidity,
                "current_report_date_exchange_corroboration": current_turnover,
                "interpretation": "The 20-day median remains the policy metric; current close evidence replaces stale price fields only.",
            },
        })
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
        "funded_lines_keep_two_provider_gate": True,
        "unfunded_candidate_single_source_requires_exact_line_identity_anchor": True,
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
        "production_delivery_authority": False,
    }
    transition["priced_line_count"] = sum(
        1 for row in transition.get("rows") or []
        if isinstance(row, dict) and str(row.get("status") or "").startswith("priced_")
    )
    transition["completed_close_gate_passed"] = bool(
        transition["priced_line_count"] and all(
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
