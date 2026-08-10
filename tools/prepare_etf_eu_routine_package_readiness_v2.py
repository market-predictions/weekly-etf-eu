from __future__ import annotations

from pathlib import Path
from typing import Any

import tools.prepare_etf_eu_routine_package_readiness as base


SUPPORTED_RENDERER_MODES = {"client_grade_v2", "client_grade_v2_funded_aware", "client_grade_v3_donor_converged"}
CLIENT_HTML_MARKERS = {
    "dutch_primary_html": ["WEKELIJKSE ETF EU-REVIEW", "Beleggersrapport", "Analistenrapport"],
    "english_companion_html": ["WEEKLY ETF EU REVIEW", "Investor report", "Analyst report"],
}
LEGACY_MARKDOWN_MARKERS = {
    "dutch_primary_markdown": "Weekly ETF EU Review | Nederlands",
    "english_companion_markdown": "Weekly ETF EU Review | English Companion",
}


def _check_current_outputs(manifest: dict[str, Any]) -> None:
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

    for key, markers in CLIENT_HTML_MARKERS.items():
        path = Path(str(manifest.get(key) or ""))
        base._require(path.exists(), f"{key} missing: {path}")
        base._require(path.suffix == ".html", f"{key} suffix mismatch")
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            base._require(marker in text, f"{key} missing client-grade marker: {marker}")
        for token in base.STALE_TOKENS:
            base._require(token.lower() not in text.lower(), f"{key} contains stale token: {token}")
        for token in base.CLIENT_FORBIDDEN:
            base._require(token.lower() not in text.lower(), f"{key} contains internal client-surface token: {token}")
        if manifest.get("client_renderer_mode") == "client_grade_v3_donor_converged":
            for token in [
                "35% minimum cash", "15% maximum new", "50% cash-first",
                "25% turnover ceiling", "18% semiconductor cap",
                "reserve minimaal 7,50%", "reserve at least 7.50%",
            ]:
                base._require(token.casefold() not in text.casefold(), f"{key} contains retired/shadow allocation authority: {token}")

    for key in ["dutch_primary_pdf", "english_companion_pdf"]:
        path = Path(str(manifest.get(key) or ""))
        base._require(path.exists(), f"{key} missing: {path}")
        raw = path.read_bytes()
        base._require(raw.startswith(b"%PDF-"), f"{key} missing PDF header")
        base._require(b"%%EOF" in raw[-512:], f"{key} missing PDF EOF")

    state_path = Path(str(manifest.get("normalized_report_state") or ""))
    base._require(state_path.exists(), f"normalized report state missing: {state_path}")
    base._require(manifest.get("client_renderer_mode") in SUPPORTED_RENDERER_MODES, "client renderer mode is not supported")
    base._require(manifest.get("investor_brief_present") is True, "investor brief missing")
    base._require(manifest.get("analyst_appendix_present") is True, "analyst appendix missing")

    if manifest.get("client_renderer_mode") == "client_grade_v3_donor_converged":
        review_path = Path(str(manifest.get("current_reunderwriting_scorecard") or ""))
        validation_path = Path(str(manifest.get("current_reunderwriting_validation") or ""))
        base._require(review_path.exists(), f"current re-underwriting scorecard missing: {review_path}")
        base._require(validation_path.exists(), f"current re-underwriting validation missing: {validation_path}")
        base._require(manifest.get("shadow_policy_used_for_current_allocation") is False, "shadow policy current-allocation flag must be false")
        base._require(manifest.get("retired_fixed_percentage_used") is False, "retired fixed percentage flag must be false")
        base._require(manifest.get("historical_target_used_for_current_trade") is False, "historical target current-trade flag must be false")
        base._require(manifest.get("broker_specific_permission_required_for_model") is False, "broker-specific model permission flag must be false")


def _current_aware_check_outputs(manifest: dict[str, Any]) -> None:
    if manifest.get("client_renderer_mode") in SUPPORTED_RENDERER_MODES:
        _check_current_outputs(manifest)
    else:
        ORIGINAL_CHECK_OUTPUTS(manifest)


ORIGINAL_CHECK_OUTPUTS = base._check_outputs
base._check_outputs = _current_aware_check_outputs


if __name__ == "__main__":
    base.main()
