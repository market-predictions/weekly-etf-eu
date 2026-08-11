from __future__ import annotations

import argparse
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
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected object: {path}")
    return payload


def _identity(isin: Any, ticker: Any) -> tuple[str, str]:
    return str(isin or "").strip().upper(), str(ticker or "").strip().upper()


def select_candidates(
    donor_lane_artifact: Path,
    proxy_map: Path,
    provider_registry: Path,
    portfolio_state: Path,
    *,
    max_candidates: int,
) -> dict[str, Any]:
    donor = _load_json(donor_lane_artifact)
    mappings = _load_yaml(proxy_map)
    registry = _load_yaml(provider_registry)
    portfolio = _load_json(portfolio_state)

    funded_ids = {
        _identity(row.get("isin"), row.get("exchange_ticker") or row.get("ticker"))
        for row in portfolio.get("positions") or []
        if isinstance(row, dict)
    }
    registry_index = {
        _identity(row.get("isin"), row.get("ticker")): row
        for row in registry.get("trading_lines") or []
        if isinstance(row, dict)
    }
    mapping_rows = [row for row in mappings.get("proxy_mappings") or [] if isinstance(row, dict)]

    ranked: list[dict[str, Any]] = []
    for lane in donor.get("assessed_lanes") or []:
        if not isinstance(lane, dict) or not bool(lane.get("is_fundable_candidate")):
            continue
        proxies = {
            str(lane.get("primary_etf") or "").strip().upper(),
            str(lane.get("alternative_etf") or "").strip().upper(),
        }
        proxies.discard("")
        score = float(lane.get("total_score") or 0.0)
        for mapping in mapping_rows:
            donor_proxies = {str(value).strip().upper() for value in mapping.get("donor_proxies") or []}
            if not (proxies & donor_proxies):
                continue
            status = str(mapping.get("status") or "mapping_required")
            if status.startswith("policy_blocked") or "mapping_incomplete" in status or status == "mapping_required":
                continue
            for order, candidate in enumerate(mapping.get("ucits_candidates") or []):
                if not isinstance(candidate, dict):
                    continue
                identity_status = str(candidate.get("identity_status") or "").lower()
                exchange = str(candidate.get("exchange") or "").lower()
                isin, ticker = _identity(candidate.get("isin"), candidate.get("exchange_ticker"))
                if not isin or not ticker or "unresolved" in isin.lower() or "unresolved" in ticker.lower():
                    continue
                if "incomplete" in identity_status or "unresolved" in exchange:
                    continue
                if (isin, ticker) in funded_ids:
                    continue
                registry_row = registry_index.get((isin, ticker))
                if not registry_row:
                    continue
                ranked.append({
                    "basket_id": registry_row.get("basket_id"),
                    "ticker": ticker,
                    "isin": isin,
                    "lane_name": lane.get("lane_name"),
                    "bucket": lane.get("bucket"),
                    "donor_primary_etf": lane.get("primary_etf"),
                    "donor_alternative_etf": lane.get("alternative_etf"),
                    "donor_total_score": score,
                    "donor_fundability_status": lane.get("fundability_status"),
                    "mapping_exposure_id": mapping.get("exposure_id"),
                    "mapping_status": status,
                    "candidate_order": order,
                    "selection_authority": "pricing_capacity_only_not_allocation_authority",
                })

    dedup: dict[str, dict[str, Any]] = {}
    for row in sorted(ranked, key=lambda item: (-item["donor_total_score"], item["candidate_order"], item["basket_id"])):
        basket_id = str(row.get("basket_id") or "")
        if basket_id and basket_id not in dedup:
            dedup[basket_id] = row
    selected = list(dedup.values())[: max(0, max_candidates)]
    return {
        "schema_version": "etf_eu_allocation_pricing_candidate_selection_v1",
        "donor_report_date": donor.get("report_date"),
        "donor_discovery_engine_version": donor.get("discovery_engine_version"),
        "max_candidates": max_candidates,
        "eligible_candidate_count": len(dedup),
        "selected_candidate_count": len(selected),
        "selected_basket_ids": [row["basket_id"] for row in selected],
        "selected": selected,
        "authority": {
            "pricing_capacity_only": True,
            "funding_authority": False,
            "allocation_authority": False,
            "portfolio_mutation": False,
            "delivery_authority": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--donor-lane-artifact", type=Path, required=True)
    parser.add_argument("--proxy-map", type=Path, default=Path("config/ucits_benchmark_proxy_map.yml"))
    parser.add_argument("--provider-registry", type=Path, default=Path("config/ucits_price_provider_registry.yml"))
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--max-candidates", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = select_candidates(
        args.donor_lane_artifact,
        args.proxy_map,
        args.provider_registry,
        args.portfolio_state,
        max_candidates=args.max_candidates,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "ETF_EU_ALLOCATION_PRICING_CANDIDATES_OK"
        f" | selected={','.join(payload['selected_basket_ids']) or 'none'}"
        f" | eligible={payload['eligible_candidate_count']}"
        f" | authority=pricing_only"
    )


if __name__ == "__main__":
    main()
