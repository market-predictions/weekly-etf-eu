from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from runtime.current.pricing import verification_status


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected YAML mapping: {path}")
    return payload


def _pricing_index(pricing: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for row in pricing.get("rows") or []:
        if not isinstance(row, dict):
            continue
        isin = str(row.get("isin") or "").strip().upper()
        ticker = str(row.get("ticker") or row.get("exchange_ticker") or "").strip().upper()
        if isin and ticker:
            rows[(isin, ticker)] = row
    return rows


def _funded_identities(portfolio: dict[str, Any]) -> set[tuple[str, str]]:
    return {
        (str(row.get("isin") or "").strip().upper(), str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper())
        for row in portfolio.get("positions") or []
        if isinstance(row, dict) and row.get("investability_status") == "funded_model_position"
    }


def _valuation_grade(price: dict[str, Any] | None, report_date: str) -> bool:
    return bool(
        price
        and price.get("valuation_grade") is True
        and not price.get("blockers")
        and str(price.get("close_date") or "") == report_date
        and float(price.get("close_price") or 0) > 0
    )


def _fundability(candidate: dict[str, Any], mapping_status: str, price: dict[str, Any] | None, funded: bool, report_date: str) -> str:
    if funded:
        return "FUNDED_MODEL_POSITION"
    if mapping_status.startswith("policy_blocked"):
        return "POLICY_BLOCKED"
    if not candidate or str(candidate.get("isin") or "").strip().lower() in {"", "unresolved", "tbd"}:
        return "MAPPING_REQUIRED"
    identity_status = str(candidate.get("identity_status") or "").lower()
    exchange = str(candidate.get("exchange") or "").lower()
    if "incomplete" in identity_status or "unresolved" in identity_status or "unresolved" in exchange:
        return "IDENTITY_OR_KID_INCOMPLETE"
    if not _valuation_grade(price, report_date):
        return "VALUATION_GRADE_EXACT_CLOSE_REQUIRED"
    return "FUNDABLE_REQUIRES_ALLOCATION_DECISION"


def build_discovery_bridge(
    *,
    donor_lane_artifact: Path,
    proxy_map_path: Path,
    pricing_artifact_path: Path,
    portfolio_state_path: Path,
    report_date: str,
) -> dict[str, Any]:
    donor = _load_json(donor_lane_artifact)
    mapping = _load_yaml(proxy_map_path)
    pricing = _load_json(pricing_artifact_path)
    portfolio = _load_json(portfolio_state_path)
    if str(pricing.get("report_date") or "") != report_date:
        raise RuntimeError("Discovery pricing artifact report date mismatch")
    mappings = [row for row in mapping.get("proxy_mappings") or [] if isinstance(row, dict)]
    prices = _pricing_index(pricing)
    funded = _funded_identities(portfolio)

    assessed: list[dict[str, Any]] = []
    for lane in donor.get("assessed_lanes") or []:
        if not isinstance(lane, dict):
            continue
        proxies = {str(lane.get("primary_etf") or "").strip().upper(), str(lane.get("alternative_etf") or "").strip().upper()} - {""}
        matched = [row for row in mappings if proxies & {str(value).strip().upper() for value in row.get("donor_proxies") or []}]
        candidates: list[dict[str, Any]] = []
        for mapping_row in matched:
            mapping_status = str(mapping_row.get("status") or "mapping_required")
            for candidate in mapping_row.get("ucits_candidates") or [{}]:
                if not isinstance(candidate, dict):
                    continue
                isin = str(candidate.get("isin") or "").strip().upper()
                ticker = str(candidate.get("exchange_ticker") or "").strip().upper()
                price = prices.get((isin, ticker))
                is_funded = (isin, ticker) in funded
                candidates.append({
                    **candidate,
                    "exposure_id": mapping_row.get("exposure_id"),
                    "mapping_status": mapping_status,
                    "pricing_close_date": price.get("close_date") if price else None,
                    "pricing_close": price.get("close_price") if price else None,
                    "pricing_valuation_grade": _valuation_grade(price, report_date),
                    "pricing_verification_status": verification_status(price) if price else "no_pricing_evidence",
                    "pricing_agreeing_providers": list(price.get("agreeing_providers") or []) if price else [],
                    "fundability_status": _fundability(candidate, mapping_status, price, is_funded, report_date),
                    "funded_model_position": is_funded,
                })
        if not candidates:
            candidates = [{"exposure_id": lane.get("taxonomy_tag") or lane.get("bucket"), "mapping_status": "mapping_required", "fundability_status": "MAPPING_REQUIRED", "funded_model_position": False}]
        assessed.append({
            "lane_name": lane.get("lane_name"),
            "taxonomy_tag": lane.get("taxonomy_tag"),
            "bucket": lane.get("bucket"),
            "donor_primary_etf": lane.get("primary_etf"),
            "donor_alternative_etf": lane.get("alternative_etf"),
            "donor_total_score": lane.get("total_score"),
            "donor_promoted_to_live_radar": lane.get("promoted_to_live_radar"),
            "donor_challenger": lane.get("challenger"),
            "donor_return_1m_pct": lane.get("return_1m_pct"),
            "donor_return_3m_pct": lane.get("return_3m_pct"),
            "donor_relative_strength_score": lane.get("relative_strength_score"),
            "donor_tradability_status": lane.get("tradability_status"),
            "ucits_candidates": candidates,
        })

    fundable = []
    for lane in assessed:
        for candidate in lane.get("ucits_candidates") or []:
            if candidate.get("fundability_status") == "FUNDABLE_REQUIRES_ALLOCATION_DECISION":
                fundable.append({
                    "lane_name": lane.get("lane_name"),
                    "taxonomy_tag": lane.get("taxonomy_tag"),
                    "donor_total_score": lane.get("donor_total_score"),
                    "ticker": candidate.get("exchange_ticker"),
                    "isin": candidate.get("isin"),
                    "fund_name": candidate.get("fund_name"),
                    "fundability_status": candidate.get("fundability_status"),
                    "pricing_verification_status": candidate.get("pricing_verification_status"),
                })
    fundable.sort(key=lambda row: (float(row.get("donor_total_score") or -1), str(row.get("ticker") or "")), reverse=True)

    return {
        "schema_version": "etf_eu_current_discovery_bridge_v1",
        "report_date": report_date,
        "donor_report_date": donor.get("report_date"),
        "donor_discovery_engine_version": donor.get("discovery_engine_version"),
        "assessed_lane_count": len(assessed),
        "required_breadth_buckets": donor.get("required_breadth_buckets") or [],
        "assessed_lanes": assessed,
        "fundable_challengers": fundable,
        "best_fundable_challenger": fundable[0] if fundable else None,
        "authority": {
            "donor_is_opportunity_evidence_only": True,
            "mapping_is_funding_authority": False,
            "pricing_is_funding_authority": False,
            "exact_primary_close_can_be_valuation_grade_without_verifier": True,
            "same_date_provider_disagreement_fails_closed_upstream": True,
            "explicit_allocation_decision_required": True,
            "portfolio_mutation": False,
            "execution_authority": False,
        },
    }


def write_discovery_bridge(**kwargs: Any) -> dict[str, Any]:
    output_path = Path(kwargs.pop("output_path"))
    payload = build_discovery_bridge(**kwargs)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return payload
