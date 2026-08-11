from __future__ import annotations

import json
from pathlib import Path

import yaml

from runtime.build_etf_eu_donor_discovery_bridge import build_bridge
from tools.select_etf_eu_allocation_pricing_candidates import select_candidates


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_yaml(path: Path, payload: dict) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def test_selector_prioritizes_donor_fundable_exact_mapped_lines(tmp_path: Path) -> None:
    donor = tmp_path / "donor.json"
    proxy = tmp_path / "proxy.yml"
    registry = tmp_path / "registry.yml"
    portfolio = tmp_path / "portfolio.json"
    _write_json(donor, {
        "report_date": "2026-08-07",
        "discovery_engine_version": "v5",
        "assessed_lanes": [
            {"lane_name": "Defense", "primary_etf": "PPA", "alternative_etf": "ITA", "total_score": 4.59, "is_fundable_candidate": True, "fundability_status": "funding_candidate_valuation_grade"},
            {"lane_name": "Water", "primary_etf": "FIW", "alternative_etf": "PHO", "total_score": 4.34, "is_fundable_candidate": True, "fundability_status": "funding_candidate_valuation_grade"},
            {"lane_name": "Healthcare", "primary_etf": "XLV", "alternative_etf": "VHT", "total_score": 4.42, "is_fundable_candidate": False},
        ],
    })
    _write_yaml(proxy, {"proxy_mappings": [
        {"exposure_id": "defense", "donor_proxies": ["PPA", "ITA"], "status": "mapped_verified_line_watch_only_until_current_decision", "ucits_candidates": [{"isin": "D1", "exchange_ticker": "DFEN", "exchange": "Xetra", "identity_status": "verified"}]},
        {"exposure_id": "water", "donor_proxies": ["FIW", "PHO"], "status": "mapped_verified_lines_market_evidence_required", "ucits_candidates": [{"isin": "W1", "exchange_ticker": "XMLC", "exchange": "Xetra", "identity_status": "verified"}, {"isin": "W2", "exchange_ticker": "IQQQ", "exchange": "Xetra", "identity_status": "verified"}]},
        {"exposure_id": "health", "donor_proxies": ["XLV", "VHT"], "status": "mapped_verified_line", "ucits_candidates": [{"isin": "H1", "exchange_ticker": "CBUF", "exchange": "Xetra", "identity_status": "verified"}]},
    ]})
    _write_yaml(registry, {"trading_lines": [
        {"basket_id": "dfen_xetra_eur", "isin": "D1", "ticker": "DFEN"},
        {"basket_id": "xmlc_xetra_eur", "isin": "W1", "ticker": "XMLC"},
        {"basket_id": "iqqq_xetra_eur", "isin": "W2", "ticker": "IQQQ"},
        {"basket_id": "cbuff_xetra_eur", "isin": "H1", "ticker": "CBUF"},
    ]})
    _write_json(portfolio, {"positions": []})

    payload = select_candidates(donor, proxy, registry, portfolio, max_candidates=4)
    assert payload["selected_basket_ids"] == ["dfen_xetra_eur", "xmlc_xetra_eur", "iqqq_xetra_eur"]
    assert payload["authority"]["allocation_authority"] is False


def test_bridge_requires_two_provider_consensus_before_new_allocation(tmp_path: Path) -> None:
    donor = tmp_path / "donor.json"
    proxy = tmp_path / "proxy.yml"
    pricing = tmp_path / "pricing.json"
    portfolio = tmp_path / "portfolio.json"
    _write_json(donor, {
        "report_date": "2026-08-07",
        "discovery_engine_version": "v5",
        "required_breadth_buckets": ["defense_resilience"],
        "assessed_lanes": [{
            "lane_name": "Defense", "taxonomy_tag": "defense_resilience", "bucket": "defense_resilience",
            "primary_etf": "PPA", "alternative_etf": "ITA", "total_score": 4.59,
            "is_fundable_candidate": True, "fundability_status": "funding_candidate_valuation_grade",
        }],
    })
    _write_yaml(proxy, {"proxy_mappings": [{
        "exposure_id": "defense_resilience", "donor_proxies": ["PPA", "ITA"], "status": "mapped_verified_line_watch_only_until_current_decision",
        "ucits_candidates": [{"isin": "D1", "exchange_ticker": "DFEN", "exchange": "Xetra", "identity_status": "verified"}],
    }]})
    _write_json(portfolio, {"positions": []})

    single_source = {
        "rows": [{
            "isin": "D1", "ticker": "DFEN", "close_date": "2026-08-10", "close_price": 55.0,
            "completed_close_on_or_before_report_date": True,
            "source_agreement_status": "single_source_only", "agreeing_providers": ["yahoo_chart"],
            "pricing_status": "priced_non_authoritative",
        }]
    }
    _write_json(pricing, single_source)
    bridge = build_bridge(donor, proxy, pricing, portfolio)
    candidate = bridge["assessed_lanes"][0]["ucits_candidates"][0]
    assert candidate["fundability_status"] == "PRICING_CONSENSUS_REQUIRED"
    assert bridge["assessed_lanes"][0]["donor_is_fundable_candidate"] is True

    consensus = single_source
    consensus["rows"][0]["source_agreement_status"] = "qualified_development_consensus"
    consensus["rows"][0]["agreeing_providers"] = ["alpha_vantage", "yahoo_chart"]
    _write_json(pricing, consensus)
    bridge = build_bridge(donor, proxy, pricing, portfolio)
    candidate = bridge["assessed_lanes"][0]["ucits_candidates"][0]
    assert candidate["pricing_two_provider_consensus"] is True
    assert candidate["fundability_status"] == "FUNDABLE_REQUIRES_ALLOCATION_DECISION"
