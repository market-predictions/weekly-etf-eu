import json
from pathlib import Path

from runtime.etf_eu_pricing_surface import production_report_maturity_section
from runtime.render_etf_eu_report_with_pricing_surface import write_reports_with_pricing_surface
from tools.validate_etf_eu_output_contract import validate
from tools.validate_etf_eu_pricing_surface import validate_pricing_surface


def _write_inputs(tmp_path: Path) -> tuple[Path, Path, Path, Path, Path]:
    output = tmp_path / "out"
    state = tmp_path / "state.json"
    proxy = tmp_path / "proxy.yml"
    registry = tmp_path / "registry.yml"
    valuation = tmp_path / "valuation.json"

    state.write_text(json.dumps({"cash_eur": 100000, "nav_eur": 100000}), encoding="utf-8")
    proxy.write_text("proxy_mappings: []\n", encoding="utf-8")
    registry.write_text("funds: []\n", encoding="utf-8")
    valuation.write_text(json.dumps({"rows": []}), encoding="utf-8")
    return output, state, proxy, registry, valuation


def test_production_maturity_section_is_dutch_first_and_non_delivery():
    section = production_report_maturity_section(language="nl")

    assert "Productierapport-volwassenheid" in section
    assert "Nederlandse hoofdrapportage" in section
    assert "primaire clientrapportage" in section
    assert "geen gefinancierde UCITS-posities" in section
    assert "geen koopadvies" in section
    assert "geen portefeuille-mutatie" in section
    assert "geen productielevering" in section
    assert "geen delivery receipt" in section
    assert "funding_authority=true" not in section
    assert "production_delivery=true" not in section


def test_wrapper_renders_strict_dutch_first_maturity_reports(tmp_path: Path):
    output, state, proxy, registry, valuation = _write_inputs(tmp_path)

    en_path, nl_path = write_reports_with_pricing_surface(output, state, proxy, registry, None, valuation, "2026-06-04")
    en_text = en_path.read_text(encoding="utf-8")
    nl_text = nl_path.read_text(encoding="utf-8")

    assert "Productierapport-volwassenheid" in nl_text
    assert "Agreement-gate pricing oppervlak" in nl_text
    assert "## 8. Leveringsstatus" in nl_text
    assert nl_text.index("Productierapport-volwassenheid") < nl_text.index("Agreement-gate pricing oppervlak")
    assert nl_text.index("Agreement-gate pricing oppervlak") < nl_text.index("## 8. Leveringsstatus")

    assert "Production report maturity" in en_text
    assert "Dutch report is the primary client report" in en_text
    assert "Agreement-gate pricing surface" in en_text
    assert "delivery=false" not in en_text
    assert "delivery=false" not in nl_text

    validate(output, require_production_dutch_first=True)
    validate_pricing_surface(en_path, require_production_dutch_first=True)
    validate_pricing_surface(nl_path, require_production_dutch_first=True)
