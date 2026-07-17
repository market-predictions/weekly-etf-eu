from __future__ import annotations

from pathlib import Path

from tools.prepare_etf_eu_routine_package_readiness_v2 import V2_RENDERER_MODES, _check_v2_outputs


def _write_pdf(path: Path) -> None:
    path.write_bytes(b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\n%%EOF\n")


def test_funded_aware_renderer_is_supported_by_v2_readiness(tmp_path: Path) -> None:
    nl_md = tmp_path / "nl.md"
    en_md = tmp_path / "en.md"
    nl_html = tmp_path / "nl.html"
    en_html = tmp_path / "en.html"
    nl_pdf = tmp_path / "nl.pdf"
    en_pdf = tmp_path / "en.pdf"
    state = tmp_path / "state.json"

    nl_md.write_text("# Weekly ETF EU Review | Nederlands\n", encoding="utf-8")
    en_md.write_text("# Weekly ETF EU Review | English Companion\n", encoding="utf-8")
    nl_html.write_text("WEKELIJKSE ETF EU-REVIEW Beleggersrapport Analistenrapport", encoding="utf-8")
    en_html.write_text("WEEKLY ETF EU REVIEW Investor report Analyst report", encoding="utf-8")
    _write_pdf(nl_pdf)
    _write_pdf(en_pdf)
    state.write_text("{}\n", encoding="utf-8")

    manifest = {
        "client_renderer_mode": "client_grade_v2_funded_aware",
        "investor_brief_present": True,
        "analyst_appendix_present": True,
        "dutch_primary_markdown": str(nl_md),
        "english_companion_markdown": str(en_md),
        "dutch_primary_html": str(nl_html),
        "english_companion_html": str(en_html),
        "dutch_primary_pdf": str(nl_pdf),
        "english_companion_pdf": str(en_pdf),
        "normalized_report_state": str(state),
    }

    assert "client_grade_v2_funded_aware" in V2_RENDERER_MODES
    _check_v2_outputs(manifest)
