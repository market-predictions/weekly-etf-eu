import json
from pathlib import Path

from runtime.etf_eu_pricing_surface import production_report_maturity_section
from runtime.render_etf_eu_report_with_pricing_surface import write_reports_with_pricing_surface
from tools.validate_etf_eu_fundability_surface import validate_fundability_surface
from tools.validate_etf_eu_output_contract import validate
from tools.validate_etf_eu_pricing_surface import validate_pricing_surface


def _write_inputs(tmp_path: Path) -> tuple[Path, Path, Path, Path, Path, Path]:
    output = tmp_path / "out"
    state = tmp_path / "state.json"
    proxy = tmp_path / "proxy.yml"
    registry = tmp_path / "registry.yml"
    valuation = tmp_path / "valuation.json"
    fundability = tmp_path / "fundability.json"

    state.write_text(json.dumps({"cash_eur": 100000, "nav_eur": 100000}), encoding="utf-8")
    proxy.write_text("proxy_mappings: []\n", encoding="utf-8")
    registry.write_text("funds: []\n", encoding="utf-8")
    valuation.write_text(json.dumps({"rows": []}), encoding="utf-8")
    fundability.write_text(
        json.dumps(
            {
                "candidate_promotion": False,
                "funding_authority": False,
                "portfolio_mutation": False,
                "production_delivery": False,
                "candidate_count": 1,
                "not_fundable_count": 1,
                "rows": [
                    {
                        "fund_name": "iShares Core S&P 500 UCITS ETF USD (Acc)",
                        "isin": "IE00B5BMR087",
                        "fundability_gate_status": "not_fundable_blocked",
                        "gate_blockers": ["pricing_quality:valuation_grade_false"],
                        "gates": {"pricing_quality": {"status": "blocked", "blockers": ["valuation_grade_false"]}},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return output, state, proxy, registry, valuation, fundability


def test_production_maturity_section_is_dutch_first_and_non_delivery():
    section = production_report_maturity_section(language="nl")

    assert "Productierapport-volwassenheid" in section
    assert "Nederlandse hoofdrapportage" in section
    assert "primaire clientrapportage" in section
    assert "Engelse rapportage is companion/operator-facing" in section
    assert "geen gefinancierde UCITS-posities" in section
    assert "geen koopadvies" in section
    assert "geen portefeuille-mutatie" in section
    assert "geen productielevering" in section
    assert "geen delivery receipt" in section
    assert "fundability gate status zichtbaar" in section
    assert "funding_authority=true" not in section
    assert "production_delivery=true" not in section


def test_wrapper_renders_strict_dutch_first_maturity_reports(tmp_path: Path):
    output, state, proxy, registry, valuation, fundability = _write_inputs(tmp_path)

    en_path, nl_path = write_reports_with_pricing_surface(output, state, proxy, registry, None, valuation, "2026-06-04", fundability)
    en_text = en_path.read_text(encoding="utf-8")
    nl_text = nl_path.read_text(encoding="utf-8")

    assert "Productierapport-volwassenheid" in nl_text
    assert "Agreement-gate pricing oppervlak" in nl_text
    assert "Fundability gate status" in nl_text
    assert "fundability gate status is zichtbaar" in nl_text
    assert "candidate_promotion=false" in nl_text
    assert "## 8. Leveringsstatus" in nl_text
    assert nl_text.index("Productierapport-volwassenheid") < nl_text.index("Agreement-gate pricing oppervlak")
    assert nl_text.index("Agreement-gate pricing oppervlak") < nl_text.index("Fundability gate status")
    assert nl_text.index("Fundability gate status") < nl_text.index("## 8. Leveringsstatus")

    assert "Production report maturity" in en_text
    assert "Dutch report is the primary client report" in en_text
    assert "Agreement-gate pricing surface" in en_text
    assert "Fundability gate status" in en_text
    assert "does not promote any candidate to fundable" in en_text
    assert "delivery=false" not in en_text
    assert "delivery=false" not in nl_text

    validate(output, require_production_dutch_first=True)
    validate_pricing_surface(en_path, require_production_dutch_first=True)
    validate_pricing_surface(nl_path, require_production_dutch_first=True)
    validate_fundability_surface(en_path)
    validate_fundability_surface(nl_path)


def test_strict_validation_can_target_current_report_pair_with_historical_outputs(tmp_path: Path):
    output, state, proxy, registry, valuation, fundability = _write_inputs(tmp_path)
    output.mkdir(parents=True, exist_ok=True)
    (output / "weekly_etf_eu_review_260531.md").write_text(
        "# Weekly ETF EU Review — 2026-05-31\n\n"
        "cash-only bootstrap\n\n"
        "Funded UCITS holdings: none\n\n"
        "research proxies only\n\n"
        "require ISIN, KID/PRIIPs and trading-line verification\n\n"
        "Production delivery: disabled\n\n"
        "No PDF rendering, portfolio execution or email delivery was performed\n",
        encoding="utf-8",
    )
    (output / "weekly_etf_eu_review_nl_260531.md").write_text(
        "# Weekly ETF EU Review NL — 2026-05-31\n\n"
        "cash-only bootstrap\n\n"
        "Gefinancierde UCITS-posities: geen\n\n"
        "alleen onderzoeksproxy\n\n"
        "vereisen ISIN-, KID-/PRIIPs- en handelslijnverificatie\n\n"
        "Productielevering: uitgeschakeld\n\n"
        "geen PDF-rendering, portefeuille-executie of e-mailverzending uitgevoerd\n",
        encoding="utf-8",
    )

    write_reports_with_pricing_surface(output, state, proxy, registry, None, valuation, "2026-06-04", fundability)

    validate(output, require_production_dutch_first=True, report_suffix="260604")
