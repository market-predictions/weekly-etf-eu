from __future__ import annotations

import json
from pathlib import Path

import yaml

from runtime.build_etf_eu_donor_discovery_bridge import build_bridge


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_bridge_maps_donor_proxy_but_does_not_create_funding_authority(tmp_path: Path) -> None:
    donor = tmp_path / "donor.json"
    mapping = tmp_path / "map.yml"
    pricing = tmp_path / "pricing.json"
    portfolio = tmp_path / "portfolio.json"
    write_json(donor, {
        "report_date": "2026-08-07",
        "discovery_engine_version": "test",
        "required_breadth_buckets": ["ai_digital_infrastructure", "water"],
        "assessed_lanes": [
            {"lane_name": "Cyber", "taxonomy_tag": "cyber_security", "bucket": "ai_digital_infrastructure", "primary_etf": "CIBR", "alternative_etf": "BUG", "total_score": 4.9, "promoted_to_live_radar": True},
            {"lane_name": "Water", "taxonomy_tag": "water", "bucket": "water", "primary_etf": "FIW", "alternative_etf": "PHO", "total_score": 4.3, "promoted_to_live_radar": True},
        ],
    })
    mapping.write_text(yaml.safe_dump({"proxy_mappings": [
        {"exposure_id": "cyber_security", "donor_proxies": ["CIBR", "BUG"], "status": "mapped_verified_line", "ucits_candidates": [{"isin": "IE00BG0J4C88", "exchange_ticker": "L0CK", "exchange": "Xetra", "identity_status": "verified"}]},
        {"exposure_id": "water_infrastructure", "donor_proxies": ["FIW", "PHO"], "status": "mapping_required", "ucits_candidates": []},
    ]}), encoding="utf-8")
    write_json(pricing, {"rows": [{"isin": "IE00BG0J4C88", "ticker": "L0CK", "completed_close": True, "close_price": 10.93, "close_date": "2026-08-07", "pricing_status": "priced_consensus"}]})
    write_json(portfolio, {"positions": []})

    bridge = build_bridge(donor, mapping, pricing, portfolio)
    cyber = bridge["assessed_lanes"][0]["ucits_candidates"][0]
    water = bridge["assessed_lanes"][1]["ucits_candidates"][0]
    assert cyber["fundability_status"] == "FUNDABLE_REQUIRES_ALLOCATION_DECISION"
    assert water["fundability_status"] == "MAPPING_REQUIRED"
    assert bridge["authority"]["mapping_is_funding_authority"] is False
    assert bridge["authority"]["explicit_allocation_decision_required"] is True


def test_existing_exact_line_is_recognized_as_funded(tmp_path: Path) -> None:
    donor = tmp_path / "donor.json"
    mapping = tmp_path / "map.yml"
    pricing = tmp_path / "pricing.json"
    portfolio = tmp_path / "portfolio.json"
    write_json(donor, {"assessed_lanes": [{"lane_name": "Cyber", "bucket": "ai", "primary_etf": "CIBR"}]})
    mapping.write_text(yaml.safe_dump({"proxy_mappings": [{"exposure_id": "cyber", "donor_proxies": ["CIBR"], "status": "mapped_verified_line", "ucits_candidates": [{"isin": "IE00BG0J4C88", "exchange_ticker": "L0CK", "exchange": "Xetra", "identity_status": "verified"}]}]}), encoding="utf-8")
    write_json(pricing, {"rows": []})
    write_json(portfolio, {"positions": [{"isin": "IE00BG0J4C88", "ticker": "L0CK", "shares": 934}]})
    bridge = build_bridge(donor, mapping, pricing, portfolio)
    assert bridge["assessed_lanes"][0]["ucits_candidates"][0]["fundability_status"] == "FUNDED_MODEL_POSITION"
