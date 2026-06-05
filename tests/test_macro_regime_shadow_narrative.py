import json
from pathlib import Path

import pytest

from runtime.render_macro_regime_shadow_narrative import (
    build_macro_regime_shadow_narrative,
    write_macro_regime_shadow_narrative,
)
from tools.validate_macro_regime_shadow_narrative import validate_macro_regime_shadow_narrative


def test_macro_regime_shadow_narrative_artifact_is_valid(tmp_path: Path):
    current_en = """# Weekly ETF EU Review

## Macro narrative
Current macro wording says risk is balanced and remains descriptive.

## Delivery status
No delivery.
"""
    current_nl = """# Weekly ETF EU Review

## Macro-narratief
Huidige macrotekst zegt dat het risico gebalanceerd is en beschrijvend blijft.

## Leveringsstatus
Geen levering.
"""
    macro_payload = {
        "deterministic_regime": "risk_on_watchful",
        "confidence": "medium",
        "trend": "uptrend",
        "breadth": "mixed",
        "credit": "stable",
        "volatility": "contained",
        "liquidity": "normal",
        "policy": "restrictive_hold",
        "deterministic_evidence": {
            "equity_trend": "positive",
            "breadth_confirmation": "partial",
            "credit_stress": "absent",
        },
    }

    artifact = build_macro_regime_shadow_narrative(
        run_id="20260605_000000",
        report_date="2026-06-05",
        current_report_en_text=current_en,
        current_report_nl_text=current_nl,
        macro_regime_payload=macro_payload,
        created_at_utc="2026-06-05T00:00:00Z",
    )
    path = tmp_path / "macro_regime_shadow_narrative_20260605_000000.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")

    validate_macro_regime_shadow_narrative(path)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "macro_regime_shadow_narrative_v1"
    assert payload["status"] == "shadow_candidate_only"
    assert payload["shadow_only"] is True
    assert payload["client_facing"] is False
    assert payload["production_report"] is False
    assert payload["portfolio_action_authority"] is False
    assert payload["lane_scoring_authority"] is False
    assert payload["fundability_authority"] is False
    assert payload["current_macro_narrative"]["en"]["status"] == "found"
    assert "risk_on_watchful" in payload["deterministic_regime_shadow_narrative_candidate"]["en"]
    assert "SHADOW-ONLY" in payload["comparison_markdown"]


def test_write_macro_regime_shadow_narrative_compares_report_files_and_regime_file(tmp_path: Path):
    report_en = tmp_path / "weekly_etf_eu_review_260605.md"
    report_nl = tmp_path / "weekly_etf_eu_review_nl_260605.md"
    regime = tmp_path / "macro_regime.json"

    report_en.write_text("## Macro regime\nCurrent English macro paragraph.\n\n## Delivery status\nNo send.\n", encoding="utf-8")
    report_nl.write_text("## Macroregime\nHuidige Nederlandse macroparagraaf.\n\n## Leveringsstatus\nGeen verzending.\n", encoding="utf-8")
    regime.write_text(
        json.dumps(
            {
                "macro_regime": {
                    "regime_label": "neutral_defensive",
                    "confidence_level": "high",
                    "trend_state": "sideways",
                    "market_breadth": "weak",
                }
            }
        ),
        encoding="utf-8",
    )

    path = write_macro_regime_shadow_narrative(
        tmp_path / "output",
        run_id="20260605_010203",
        report_date="2026-06-05",
        current_report_en_path=report_en,
        current_report_nl_path=report_nl,
        macro_regime_artifact_path=regime,
        created_at_utc="2026-06-05T01:02:03Z",
    )

    validate_macro_regime_shadow_narrative(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert path.name == "macro_regime_shadow_narrative_20260605_010203.json"
    assert payload["inputs"]["current_report_en_path"] == str(report_en)
    assert payload["inputs"]["macro_regime_artifact_path"] == str(regime)
    assert "neutral_defensive" in payload["deterministic_regime_shadow_narrative_candidate"]["en"]
    assert "Huidige Nederlandse macroparagraaf" in payload["comparison_markdown"]


def test_macro_regime_shadow_narrative_rejects_authority_escalation(tmp_path: Path):
    artifact = build_macro_regime_shadow_narrative(
        run_id="20260605_000000",
        report_date="2026-06-05",
        macro_regime_payload={"deterministic_regime": "risk_on"},
        created_at_utc="2026-06-05T00:00:00Z",
    )
    artifact["portfolio_action_authority"] = True
    path = tmp_path / "bad_macro_regime_shadow_narrative.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")

    with pytest.raises(RuntimeError, match="portfolio_action_authority must remain false"):
        validate_macro_regime_shadow_narrative(path)


def test_macro_regime_shadow_narrative_rejects_candidate_without_shadow_label(tmp_path: Path):
    artifact = build_macro_regime_shadow_narrative(
        run_id="20260605_000000",
        report_date="2026-06-05",
        macro_regime_payload={"deterministic_regime": "risk_off"},
        created_at_utc="2026-06-05T00:00:00Z",
    )
    artifact["deterministic_regime_shadow_narrative_candidate"]["en"] = "Production-ready macro text."
    path = tmp_path / "bad_macro_regime_shadow_narrative.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")

    with pytest.raises(RuntimeError, match="candidate must clearly state SHADOW-ONLY"):
        validate_macro_regime_shadow_narrative(path)
