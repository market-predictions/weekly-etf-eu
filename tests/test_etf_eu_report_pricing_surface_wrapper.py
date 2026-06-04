import json
from pathlib import Path

from runtime.render_etf_eu_report_with_pricing_surface import write_reports_with_pricing_surface


def test_report_wrapper_inserts_pricing_surface_without_authority(tmp_path: Path):
    output = tmp_path / "out"
    state = tmp_path / "state.json"
    proxy = tmp_path / "proxy.yml"
    registry = tmp_path / "registry.yml"
    valuation = tmp_path / "valuation.json"

    state.write_text(json.dumps({"cash_eur": 100000, "nav_eur": 100000}), encoding="utf-8")
    proxy.write_text("proxy_mappings: []\n", encoding="utf-8")
    registry.write_text("funds: []\n", encoding="utf-8")
    valuation.write_text(json.dumps({"rows": []}), encoding="utf-8")

    en_path, nl_path = write_reports_with_pricing_surface(output, state, proxy, registry, None, valuation, "2026-06-04")
    en_text = en_path.read_text(encoding="utf-8")
    nl_text = nl_path.read_text(encoding="utf-8")

    assert "Agreement-gate pricing surface" in en_text
    assert "Agreement-gate pricing oppervlak" in nl_text
    assert "not valuation authority" in en_text
    assert "geen waarderingsautoriteit" in nl_text
    assert "delivery=false" not in en_text
