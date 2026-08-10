from __future__ import annotations

import csv
from pathlib import Path

import yaml

from runtime import build_etf_eu_production_convergence_state_v3 as state_v3
from runtime import build_etf_eu_current_reunderwriting_scorecard as scorecard
from runtime import synchronize_etf_eu_current_state_surface_v2 as surface
from tools import audit_etf_eu_donor_parity as parity


REQUIRED_BUCKETS = {
    "ai_digital_infrastructure",
    "defense_resilience",
    "grid_power_electrification",
    "uranium_nuclear",
    "agriculture_food_security",
    "water",
    "china",
    "india_regional_industrialization",
    "biotech_healthcare_innovation",
    "fintech_financial_infrastructure",
    "robotics_automation",
    "critical_minerals_materials",
}


def test_transition_policy_is_historical_and_non_authoritative() -> None:
    payload = yaml.safe_load(Path("config/etf_eu_transition_policy_v1.yml").read_text(encoding="utf-8"))
    assert payload["status"] == "historical_shadow_only"
    assert payload["current_allocation_authority"] is False
    assert payload["client_control_authority"] is False
    assert payload["current_funding_authority"] is False
    assert payload["stage_1"]["current_candidate_gate_authority"] is False
    assert payload["stage_1"]["current_allocation_authority"] is False
    assert payload["stage_1"]["historical_value_authority"]["minimum_post_stage_cash_pct_nav"] == "retired_unsupported_shadow_rule"
    assert payload["stage_1"]["historical_value_authority"]["maximum_new_direct_position_pct_nav"] == "retired_unsupported_shadow_rule"


def test_discovery_preserves_donor_breadth_without_fake_mappings() -> None:
    payload = yaml.safe_load(Path("config/etf_eu_discovery_universe.yml").read_text(encoding="utf-8"))
    rules = payload["rules"]
    assert rules["historical_stage1_allowlist_is_discovery_gate"] is False
    assert rules["missing_ucits_mapping_blocks_funding_not_research"] is True
    assert set(payload["required_breadth_buckets"]) == REQUIRED_BUCKETS
    lanes = payload["lanes"]
    assert REQUIRED_BUCKETS <= {lane["bucket"] for lane in lanes}
    assert any(lane["bucket"] == "china" and lane["mapping_status"] == "mapping_required" for lane in lanes)
    assert any(lane["bucket"] == "india_regional_industrialization" and lane["mapping_status"] == "mapping_required" for lane in lanes)
    for lane in lanes:
        if lane.get("benchmark_proxy"):
            assert lane.get("proxy_authority") == "research_only"


def test_historical_stage1_blockers_do_not_survive_current_candidate_gate() -> None:
    assert state_v3._current_blockers([
        "stage_1_candidate_not_allowlisted",
        "liquidity_below_threshold",
        "exact_line_price_missing",
    ]) == ["exact_line_price_missing"]


def test_section14_replaces_shadow_policy_with_current_authority(tmp_path, monkeypatch) -> None:
    html = tmp_path / "report.html"
    pdf = tmp_path / "report.pdf"
    html.write_text(
        """
        <html><body><section id="section-14">
          <h2>Policy transition</h2>
          <div class="alignment-summary">Cash-first (vaste 50%) · beleidsgestuurd</div>
          <table class="allocator-policy-table"><tbody>
            <tr><td>Omzetplafond</td><td>25,00%</td></tr>
            <tr><td>Halfgeleiderlimiet</td><td>18,00%</td></tr>
            <tr><td>Ingebedde semis (min.)</td><td>3,10%</td></tr>
            <tr><td>Max. nieuwe ETF</td><td>15,00%</td></tr>
          </tbody></table>
          <table><tbody><tr><td>VVSM</td><td>14,88%</td><td>35,44% cash</td></tr></tbody></table>
        </section></body></html>
        """,
        encoding="utf-8",
    )

    class DummyHTML:
        def __init__(self, *args, **kwargs):
            pass

        def write_pdf(self, path):
            Path(path).write_bytes(b"pdf")

    monkeypatch.setattr(surface, "HTML", DummyHTML)
    surface._sync_section14_current_authority(html, pdf, "nl")
    rendered = html.read_text(encoding="utf-8")
    folded = rendered.casefold()
    for forbidden in ["25,00%", "18,00%", "15,00%", "14,88%", "35,44%", "cash-first (vaste 50%)"]:
        assert forbidden.casefold() not in folded
    assert "gemeten ingebedde semiconductor-exposure (ondergrens)" in folded
    assert "3,10%" in rendered
    assert "geen minimumdoel" in folded
    assert "brokerneutraal" in folded


def test_current_reunderwriting_scorecard_covers_all_funded_positions(tmp_path) -> None:
    portfolio = {
        "cash_eur": 50_000.0,
        "nav_eur": 100_000.0,
        "positions": [
            {"ticker": "VWCE", "isin": "IE00BK5BQT80", "fund_name": "VWCE", "shares": 10, "current_weight_pct": 20.0, "current_price_local": 100.0, "price_date": "2026-08-07", "trading_currency": "EUR", "market_value_eur": 1000, "ucits_status": "confirmed", "priips_kid_status": "available", "investability_status": "funded_model_position", "portfolio_role": "Global core"},
            {"ticker": "EUNA", "isin": "IE00BDBRDM35", "fund_name": "EUNA", "shares": 20, "current_weight_pct": 10.0, "current_price_local": 5.0, "price_date": "2026-08-07", "trading_currency": "EUR", "market_value_eur": 100, "ucits_status": "confirmed", "priips_kid_status": "available", "investability_status": "funded_model_position", "portfolio_role": "Bond stabiliser"},
            {"ticker": "SXR8", "isin": "IE00B5BMR087", "fund_name": "SXR8", "shares": 2, "current_weight_pct": 10.0, "current_price_local": 700.0, "price_date": "2026-08-07", "trading_currency": "EUR", "market_value_eur": 1400, "ucits_status": "confirmed", "priips_kid_status": "available", "investability_status": "funded_model_position", "portfolio_role": "US core"},
            {"ticker": "L0CK", "isin": "IE00BG0J4C88", "fund_name": "L0CK", "shares": 100, "current_weight_pct": 10.0, "current_price_local": 11.0, "price_date": "2026-08-07", "trading_currency": "EUR", "market_value_eur": 1100, "ucits_status": "confirmed", "priips_kid_status": "available", "investability_status": "funded_model_position", "portfolio_role": "Cybersecurity satellite"},
        ],
    }
    rows = scorecard.build_rows(portfolio, {}, {}, "2026-08-07", "unit-test")
    assert {row["exchange_ticker"] for row in rows} == {"VWCE", "EUNA", "SXR8", "L0CK"}
    assert all(row["cash_policy_flag"].startswith("Meaningful cash position") for row in rows)
    assert all(row["would_initiate_today"] for row in rows)
    out = tmp_path / "scorecard.csv"
    scorecard.write(rows, out)
    with out.open(newline="", encoding="utf-8") as handle:
        assert len(list(csv.DictReader(handle))) == 4


def test_static_parity_audit_has_no_blocking_gaps_for_convergence_source() -> None:
    payload = parity.audit(Path("."))
    blockers = [item for item in payload["items"] if item["status"] == "GAP_BLOCKING"]
    assert blockers == [], blockers
    assert payload["valid"] is True
