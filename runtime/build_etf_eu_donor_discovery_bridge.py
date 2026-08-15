from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected object: {path}")
    return payload


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected object: {path}")
    return payload


def _mapping_index(mapping: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in mapping.get("proxy_mappings") or [] if isinstance(row, dict)]


def _pricing_index(pricing: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for row in pricing.get("rows") or []:
        if not isinstance(row, dict):
            continue
        isin = str(row.get("isin") or "").strip().upper()
        ticker = str(row.get("ticker") or row.get("exchange_ticker") or "").strip().upper()
        if isin and ticker:
            result[(isin, ticker)] = row
    return result


def _portfolio_identities(portfolio: dict[str, Any]) -> set[tuple[str, str]]:
    return {
        (
            str(row.get("isin") or "").strip().upper(),
            str(row.get("ticker") or row.get("exchange_ticker") or "").strip().upper(),
        )
        for row in portfolio.get("positions") or []
        if isinstance(row, dict)
    }


def _two_provider_consensus(pricing: dict[str, Any] | None) -> bool:
    if not pricing:
        return False
    providers = pricing.get("agreeing_providers") or []
    return (
        pricing.get("completed_close_on_or_before_report_date") is True
        and pricing.get("close_price") not in (None, "")
        and str(pricing.get("source_agreement_status") or "") == "qualified_development_consensus"
        and len(providers) >= 2
    )


def _fundability(candidate: dict[str, Any], mapping_status: str, pricing: dict[str, Any] | None, funded: bool) -> str:
    if funded:
        return "FUNDED_MODEL_POSITION"
    if mapping_status.startswith("policy_blocked"):
        return "POLICY_BLOCKED"
    if not candidate or str(candidate.get("isin") or "").lower() in {"", "unresolved", "tbd"}:
        return "MAPPING_REQUIRED"
    if "incomplete" in str(candidate.get("identity_status") or "").lower() or "unresolved" in str(candidate.get("exchange") or "").lower():
        return "IDENTITY_OR_KID_INCOMPLETE"
    if not pricing or pricing.get("completed_close_on_or_before_report_date") is not True or not pricing.get("close_price"):
        return "PRICING_REQUIRED"
    if not _two_provider_consensus(pricing):
        return "PRICING_CONSENSUS_REQUIRED"
    return "FUNDABLE_REQUIRES_ALLOCATION_DECISION"


def build_bridge(
    donor_lane_artifact: Path,
    proxy_map: Path,
    pricing_artifact: Path,
    portfolio_state: Path,
) -> dict[str, Any]:
    donor = _load_json(donor_lane_artifact)
    mapping = _load_yaml(proxy_map)
    pricing = _load_json(pricing_artifact)
    portfolio = _load_json(portfolio_state)
    maps = _mapping_index(mapping)
    prices = _pricing_index(pricing)
    funded_ids = _portfolio_identities(portfolio)

    assessed: list[dict[str, Any]] = []
    for lane in donor.get("assessed_lanes") or []:
        if not isinstance(lane, dict):
            continue
        proxies = {
            str(lane.get("primary_etf") or "").strip().upper(),
            str(lane.get("alternative_etf") or "").strip().upper(),
        }
        proxies.discard("")
        matched = [
            row for row in maps
            if proxies & {str(value).strip().upper() for value in row.get("donor_proxies") or []}
        ]
        candidate_rows: list[dict[str, Any]] = []
        for mapping_row in matched:
            mapping_status = str(mapping_row.get("status") or "mapping_required")
            for candidate in mapping_row.get("ucits_candidates") or [{}]:
                if not isinstance(candidate, dict):
                    continue
                isin = str(candidate.get("isin") or "").strip().upper()
                ticker = str(candidate.get("exchange_ticker") or "").strip().upper()
                price = prices.get((isin, ticker))
                funded = (isin, ticker) in funded_ids
                candidate_rows.append({
                    **candidate,
                    "exposure_id": mapping_row.get("exposure_id"),
                    "mapping_status": mapping_status,
                    "pricing_close_date": price.get("close_date") if price else None,
                    "pricing_close": price.get("close_price") if price else None,
                    "pricing_status": price.get("pricing_status") if price else None,
                    "pricing_source_agreement_status": price.get("source_agreement_status") if price else None,
                    "pricing_agreeing_providers": price.get("agreeing_providers") if price else [],
                    "pricing_two_provider_consensus": _two_provider_consensus(price),
                    "fundability_status": _fundability(candidate, mapping_status, price, funded),
                })
        if not candidate_rows:
            candidate_rows = [{
                "exposure_id": lane.get("taxonomy_tag") or lane.get("bucket"),
                "mapping_status": "mapping_required",
                "fundability_status": "MAPPING_REQUIRED",
            }]
        assessed.append({
            "lane_name": lane.get("lane_name"),
            "taxonomy_tag": lane.get("taxonomy_tag"),
            "bucket": lane.get("bucket"),
            "donor_primary_etf": lane.get("primary_etf"),
            "donor_alternative_etf": lane.get("alternative_etf"),
            "donor_total_score": lane.get("total_score"),
            "donor_promoted_to_live_radar": lane.get("promoted_to_live_radar"),
            "donor_challenger": lane.get("challenger"),
            "donor_fundability_status": lane.get("fundability_status"),
            "donor_is_fundable_candidate": bool(lane.get("is_fundable_candidate")),
            "donor_return_1m_pct": lane.get("return_1m_pct"),
            "donor_return_3m_pct": lane.get("return_3m_pct"),
            "donor_relative_strength_score": lane.get("relative_strength_score"),
            "donor_tradability_status": lane.get("tradability_status"),
            "ucits_candidates": candidate_rows,
        })

    buckets = sorted({str(row.get("bucket") or "") for row in assessed if row.get("bucket")})
    return {
        "schema_version": "etf_eu_donor_discovery_bridge_v2",
        "donor_report_date": donor.get("report_date"),
        "donor_discovery_engine_version": donor.get("discovery_engine_version"),
        "assessed_lane_count": len(assessed),
        "assessed_buckets": buckets,
        "required_breadth_buckets": donor.get("required_breadth_buckets") or [],
        "assessed_lanes": assessed,
        "authority": {
            "mapping_is_funding_authority": False,
            "pricing_is_funding_authority": False,
            "new_allocation_requires_two_provider_consensus": True,
            "explicit_allocation_decision_required": True,
            "portfolio_mutation": False,
            "execution_authority": False,
        },
    }


def write_bridge(donor_lane_artifact: Path, proxy_map: Path, pricing_artifact: Path, portfolio_state: Path, output: Path) -> dict[str, Any]:
    payload = build_bridge(donor_lane_artifact, proxy_map, pricing_artifact, portfolio_state)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return payload
