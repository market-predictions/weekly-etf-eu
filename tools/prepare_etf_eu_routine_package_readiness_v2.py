from __future__ import annotations

from pathlib import Path
from typing import Any

import tools.prepare_etf_eu_routine_package_readiness as base


V2_RENDERER_MODES = {"client_grade_v2", "client_grade_v2_funded_aware"}
V2_HTML_MARKERS = {
    "dutch_primary_html": ["WEKELIJKSE ETF EU-REVIEW", "Beleggersrapport", "Analistenrapport"],
    "english_companion_html": ["WEEKLY ETF EU REVIEW", "Investor report", "Analyst report"],
}
LEGACY_MARKDOWN_MARKERS = {
    "dutch_primary_markdown": "Weekly ETF EU Review | Nederlands",
    "english_companion_markdown": "Weekly ETF EU Review | English Companion",
}


def _check_v2_outputs(manifest: dict[str, Any]) -> None:
    for key, marker in LEGACY_MARKDOWN_MARKERS.items():
        path = Path(str(manifest.get(key) or ""))
        base._require(path.exists(), f"{key} missing: {path}")
        base._require(path.suffix == ".md", f"{key} suffix mismatch")
        text = path.read_text(encoding="utf-8")
        base._require(marker in text, f"{key} title marker missing")
        for token in base.STALE_TOKENS:
            base._require(token.lower() not in text.lower(), f"{key} contains stale token: {token}")
        for token in base.CLIENT_FORBIDDEN:
            base._require(token.lower() not in text.lower(), f"{key} contains internal client-surface token: {token}")

    for key, markers in V2_HTML_MARKERS.items():
        path = Path(str(manifest.get(key) or ""))
        base._require(path.exists(), f"{key} missing: {path}")
        base._require(path.suffix == ".html", f"{key} suffix mismatch")
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            base._require(marker in text, f"{key} missing client-grade v2 marker: {marker}")
        for token in base.STALE_TOKENS:
            base._require(token.lower() not in text.lower(), f"{key} contains stale token: {token}")
        for token in base.CLIENT_FORBIDDEN:
            base._require(token.lower() not in text.lower(), f"{key} contains internal client-surface token: {token}")

    for key in ["dutch_primary_pdf", "english_companion_pdf"]:
        path = Path(str(manifest.get(key) or ""))
        base._require(path.exists(), f"{key} missing: {path}")
        raw = path.read_bytes()
        base._require(raw.startswith(b"%PDF-"), f"{key} missing PDF header")
        base._require(b"%%EOF" in raw[-512:], f"{key} missing PDF EOF")

    state_path = Path(str(manifest.get("normalized_report_state") or ""))
    base._require(state_path.exists(), f"normalized report state missing: {state_path}")
    base._require(manifest.get("client_renderer_mode") in V2_RENDERER_MODES, "client renderer mode is not a supported v2 mode")
    base._require(manifest.get("investor_brief_present") is True, "investor brief missing")
    base._require(manifest.get("analyst_appendix_present") is True, "analyst appendix missing")


def _v2_aware_check_outputs(manifest: dict[str, Any]) -> None:
    if manifest.get("client_renderer_mode") in V2_RENDERER_MODES:
        _check_v2_outputs(manifest)
    else:
        ORIGINAL_CHECK_OUTPUTS(manifest)


ORIGINAL_CHECK_OUTPUTS = base._check_outputs
base._check_outputs = _v2_aware_check_outputs


if __name__ == "__main__":
    base.main()
