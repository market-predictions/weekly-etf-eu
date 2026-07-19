from __future__ import annotations

import hashlib
from pathlib import Path

from weasyprint import HTML

import runtime.apply_etf_eu_cockpit_to_package as integration
from runtime.inline_etf_eu_email_report_styles import MARKER_ATTRIBUTE
from runtime.render_etf_eu_cockpit_front_page import FRONT_PAGE_MARKER


def _state() -> dict:
    return {
        "state_valid": True,
        "run_id": "20260717_141500",
        "report_date": "2026-07-17",
        "portfolio": {
            "starting_capital_eur": 100000.0,
            "nav_eur": 100016.6,
            "cash_eur": 60439.44,
            "position_count": 3,
            "positions": [
                {"ticker": "VWCE", "isin": "IE00BK5BQT80", "shares": 151, "shares_delta_this_run": 151, "current_weight_pct": 24.959177, "verification_status": "verified_ucits_trading_line"},
                {"ticker": "EUNA", "isin": "IE00BDBRDM35", "shares": 1526, "shares_delta_this_run": 1526, "current_weight_pct": 7.495996, "verification_status": "verified_ucits_trading_line"},
                {"ticker": "SXR8", "isin": "IE00B5BMR087", "shares": 10, "shares_delta_this_run": 0, "current_weight_pct": 7.115419, "verification_status": "verified_ucits_trading_line"},
            ],
        },
        "pricing": {"as_of": "2026-07-17"},
        "macro": {"regime": "Risk-on growth", "regime_nl": "Risk-on groei", "confidence_pct": 66},
        "equity_curve": {"points": [
            {"date": "2026-05-30", "nav_eur": 100000.0},
            {"date": "2026-07-16", "nav_eur": 100016.6},
            {"date": "2026-07-17", "nav_eur": 100016.6},
        ]},
    }


def _classic(language: str) -> str:
    investor = "Beleggersrapport" if language == "nl" else "Investor report"
    analyst = "Analistenrapport" if language == "nl" else "Analyst report"
    sections = "".join(
        '<section class="panel"><div class="section-head">'
        f'<span class="badge">{number}</span><span class="section-title">Section {number}</span>'
        '</div><table><thead><tr><th>Key</th><th>Value</th></tr></thead>'
        f'<tbody><tr><td>{number}</td><td>Evidence</td></tr></tbody></table></section>'
        for number in range(1, 16)
    )
    return (
        '<!doctype html><html><head><meta charset="utf-8"><style>'
        '@page{size:A4;margin:12mm}.hero-secondary{break-before:page}.panel{margin:8px}'
        '</style></head><body><main>'
        f'<header class="hero"><div class="hero-row"><div><div class="masthead">ETF EU</div></div><div class="hero-type">{investor}</div></div></header>'
        '<div class="hero-rule"></div><div class="summary-strip"><div class="mini-card">summary</div></div>'
        + sections[: len(sections) // 2]
        + f'<header class="hero hero-secondary"><div class="hero-row"><div><div class="masthead">ETF EU</div></div><div class="hero-type">{analyst}</div></div></header>'
        + sections[len(sections) // 2 :]
        + '</main></body></html>'
    )


def _package(tmp_path: Path) -> dict[str, Path]:
    paths = {
        "nl_html": tmp_path / "report_nl.html",
        "en_html": tmp_path / "report_en.html",
        "nl_pdf": tmp_path / "report_nl.pdf",
        "en_pdf": tmp_path / "report_en.pdf",
        "nl_browser": tmp_path / "report_nl_browser.html",
        "en_browser": tmp_path / "report_en_browser.html",
    }
    for language, key in (("nl", "nl"), ("en", "en")):
        text = _classic(language)
        paths[f"{key}_html"].write_text(text, encoding="utf-8")
        HTML(string=text).write_pdf(str(paths[f"{key}_pdf"]))
    return paths


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _apply(paths: dict[str, Path], feature: str):
    return integration.apply_cockpit_to_package(
        state=_state(),
        dutch_html=paths["nl_html"],
        english_html=paths["en_html"],
        dutch_pdf=paths["nl_pdf"],
        english_pdf=paths["en_pdf"],
        dutch_browser_html=paths["nl_browser"],
        english_browser_html=paths["en_browser"],
        feature_value=feature,
    )


def test_disabled_mode_is_byte_identical(tmp_path: Path) -> None:
    paths = _package(tmp_path)
    before = {key: _hash(path) for key, path in paths.items() if key in {"nl_html", "en_html", "nl_pdf", "en_pdf"}}
    result = _apply(paths, "disabled")
    after = {key: _hash(path) for key, path in paths.items() if key in before}
    assert result.status == "disabled" and result.enabled is False
    assert before == after
    assert not paths["nl_browser"].exists() and not paths["en_browser"].exists()


def test_enabled_mode_inlines_full_client_body_and_retains_browser_pdf_source(tmp_path: Path) -> None:
    paths = _package(tmp_path)
    result = _apply(paths, "enabled")
    assert result.status == "enabled" and result.enabled is True
    nl_primary = paths["nl_html"].read_text(encoding="utf-8")
    en_primary = paths["en_html"].read_text(encoding="utf-8")
    nl_browser = paths["nl_browser"].read_text(encoding="utf-8")
    en_browser = paths["en_browser"].read_text(encoding="utf-8")
    marker = f'{MARKER_ATTRIBUTE}="true"'
    for primary in (nl_primary, en_primary):
        assert primary.count(FRONT_PAGE_MARKER) == 1
        assert 'data-render-mode="email"' in primary and "style=" in primary
        assert marker in primary
        assert 'class="hero" style="' in primary
        assert 'class="panel" style="' in primary
        assert '<th style="' in primary and '<td style="' in primary
        assert "display:none!important" in primary
    assert 'data-render-mode="browser"' in nl_browser and '<svg' in nl_browser
    assert 'data-render-mode="browser"' in en_browser and '<svg' in en_browser
    assert paths["nl_pdf"].stat().st_size > 0 and paths["en_pdf"].stat().st_size > 0


def test_invalid_feature_falls_back_without_mutation(tmp_path: Path) -> None:
    paths = _package(tmp_path)
    before = {key: _hash(path) for key, path in paths.items() if key in {"nl_html", "en_html", "nl_pdf", "en_pdf"}}
    result = _apply(paths, "yes")
    after = {key: _hash(path) for key, path in paths.items() if key in before}
    assert result.status == "fallback" and result.enabled is False
    assert before == after


def test_pdf_failure_is_all_or_nothing(tmp_path: Path, monkeypatch) -> None:
    paths = _package(tmp_path)
    before = {key: _hash(path) for key, path in paths.items() if key in {"nl_html", "en_html", "nl_pdf", "en_pdf"}}

    def fail(*_args, **_kwargs):
        raise RuntimeError("planted PDF failure")

    monkeypatch.setattr(integration, "_render_pdf_bytes", fail)
    result = _apply(paths, "enabled")
    after = {key: _hash(path) for key, path in paths.items() if key in before}
    assert result.status == "fallback" and result.enabled is False
    assert before == after
    assert not paths["nl_browser"].exists() and not paths["en_browser"].exists()
