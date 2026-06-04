from __future__ import annotations

from typing import Any

from pricing.price_agreement_gate import evaluate_price_agreement
from pricing.price_result_schema import PriceIdentity, PriceResult, SourceLineage


def _identity(candidate: dict[str, Any]) -> PriceIdentity:
    return PriceIdentity(
        registry_id=str(candidate.get("registry_id") or ""),
        isin=str(candidate.get("isin") or ""),
        exchange=str(candidate.get("exchange") or ""),
        exchange_ticker=str(candidate.get("exchange_ticker") or ""),
        trading_currency=str(candidate.get("trading_currency") or ""),
        provider_symbol=str(candidate.get("provider_symbol") or ""),
    )


def _observed_result(
    *,
    candidate: dict[str, Any],
    evidence: dict[str, Any],
    source_id: str,
    provider_name: str,
    license_class: str,
    authority_tier: str,
) -> PriceResult | None:
    if evidence.get("close") in (None, "") or not evidence.get("observed_date") or not evidence.get("currency"):
        return None
    try:
        return PriceResult.observed(
            identity=_identity(candidate),
            lineage=SourceLineage.now(
                source_id=source_id,
                provider_name=provider_name,
                license_class=license_class,
                authority_tier=authority_tier,
                raw_evidence=evidence,
            ),
            observed_date=str(evidence.get("observed_date"))[:10],
            close=evidence.get("close"),
            currency=str(evidence.get("currency")),
        )
    except (TypeError, ValueError):
        return None


def build_agreement_gate_evidence(
    candidate: dict[str, Any],
    *,
    non_authoritative_preflight_evidence: dict[str, Any] | None = None,
    twelve_data_candidate_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return agreement-gate evidence for a valuation artifact row.

    This helper is evidence-only. It never promotes a row to valuation-grade,
    funding authority, portfolio mutation, report rendering, PDF, email or delivery.
    """

    price_results: list[PriceResult] = []
    if non_authoritative_preflight_evidence:
        yahoo_result = _observed_result(
            candidate=candidate,
            evidence=non_authoritative_preflight_evidence,
            source_id="yahoo_yfinance",
            provider_name="Yahoo Finance via yfinance",
            license_class="provider_free_personal",
            authority_tier="non_authoritative_connectivity_only",
        )
        if yahoo_result:
            price_results.append(yahoo_result)

    if twelve_data_candidate_evidence and twelve_data_candidate_evidence.get("status") == "candidate_price_observed":
        twelve_result = _observed_result(
            candidate=candidate,
            evidence=twelve_data_candidate_evidence,
            source_id="twelve_data",
            provider_name="Twelve Data",
            license_class="provider_paid",
            authority_tier="diagnostic_candidate_source",
        )
        if twelve_result:
            price_results.append(twelve_result)

    result = evaluate_price_agreement(price_results)
    payload = result.as_dict()
    payload["valuation_artifact_action"] = "evidence_only_no_promotion"
    payload["valuation_grade_promoted_by_artifact"] = False
    payload["funding_authority"] = False
    payload["portfolio_mutation"] = False
    payload["production_delivery"] = False
    return payload
