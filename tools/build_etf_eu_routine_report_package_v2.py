from __future__ import annotations

import argparse
import json
from argparse import Namespace
from pathlib import Path
from typing import Any

from runtime.build_etf_eu_client_grade_report_state import build_state
from runtime.polish_etf_eu_client_grade_html import polish
from runtime.render_etf_eu_client_grade_v2_funded import render
from tools.build_etf_eu_routine_report_package import build as build_legacy_package
from weasyprint import HTML


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Required artifact not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def build(args: argparse.Namespace) -> dict[str, Path]:
    legacy_outputs = build_legacy_package(args)
    output_dir = Path(args.output_dir)
    state_path = Path("output/runtime") / f"etf_eu_client_grade_report_state_{args.run_id}.json"

    state_args = Namespace(
        portfolio_state=args.portfolio_state,
        valuation_history=args.valuation_history,
        pricing_artifact=args.pricing_artifact,
        macro_pack=args.macro_pack,
        registry=args.registry,
        run_id=args.run_id,
        source_run_id=args.run_id,
        report_date=args.report_date,
        report_suffix=args.report_suffix,
    )
    state = build_state(state_args)
    if state.get("state_valid") is not True:
        raise RuntimeError(f"Client-grade v2 state is invalid: {state.get('blockers')}")
    _write(state_path, state)

    nl_html = output_dir / f"weekly_etf_eu_review_nl_{args.report_suffix}.html"
    en_html = output_dir / f"weekly_etf_eu_review_{args.report_suffix}.html"
    nl_pdf = output_dir / f"weekly_etf_eu_review_nl_{args.report_suffix}.pdf"
    en_pdf = output_dir / f"weekly_etf_eu_review_{args.report_suffix}.pdf"

    render(state_path, "nl", nl_html, nl_pdf)
    render(state_path, "en", en_html, en_pdf)

    nl_polished = polish(nl_html.read_text(encoding="utf-8"), language="nl")
    en_polished = polish(en_html.read_text(encoding="utf-8"), language="en")
    nl_html.write_text(nl_polished, encoding="utf-8")
    en_html.write_text(en_polished, encoding="utf-8")
    HTML(string=nl_polished, base_url=str(nl_html.parent.resolve())).write_pdf(str(nl_pdf))
    HTML(string=en_polished, base_url=str(en_html.parent.resolve())).write_pdf(str(en_pdf))

    manifest_path = Path(legacy_outputs["manifest"])
    ready_path = Path(legacy_outputs["ready"])
    routine_path = Path(legacy_outputs["routine"])
    manifest = _load(manifest_path)
    ready = _load(ready_path)
    routine = _load(routine_path)

    promotion_fields = {
        "client_renderer_mode": "client_grade_v2_funded_aware",
        "production_renderer": "runtime/render_etf_eu_client_grade_v2_funded.py",
        "renderer_engine": "weasyprint",
        "render_source_authority": "normalized_report_state",
        "normalized_report_state": str(state_path),
        "markdown_role": "decision_summary_audit_companion_not_v2_render_source",
        "macro_policy_pack": args.macro_pack,
        "ucits_registry": args.registry,
        "investor_brief_present": True,
        "analyst_appendix_present": True,
        "report_section_count": 15,
        "conditional_equity_curve_enabled": True,
        "equity_surface": "chart" if state["equity_curve"]["show_chart"] else "cash_preservation_callout",
        "funded_position_count": state["portfolio"]["position_count"],
        "full_generation_status": "client_grade_v2_generated_pending_quality_gates",
        "upstream_pattern_adapted": "weekly-etf normalized report state, investor/analyst hierarchy, macro surface, conditional equity curve and component renderer adapted for EU/UCITS production",
    }
    manifest.update(promotion_fields)
    manifest["renderer"] = "runtime/render_etf_eu_client_grade_v2_funded.py"
    manifest["client_surface_sanitizer"] = "runtime/polish_etf_eu_client_grade_html.py"
    manifest["html_generation_status"] = "client_grade_v2_generated"
    manifest["pdf_generation_status"] = "client_grade_v2_generated_pending_quality_gates"
    ready.update(promotion_fields)
    routine.update(promotion_fields)
    routine["routine_stage"] = "routine_client_grade_v2_generation_completed_pending_quality_gates"
    routine["workflow_status"] = "routine_client_grade_v2_generation_completed_pending_quality_gates"

    _write(manifest_path, manifest)
    _write(ready_path, ready)
    _write(routine_path, routine)
    return {
        **legacy_outputs,
        "state": state_path,
        "dutch_html": nl_html,
        "english_html": en_html,
        "dutch_pdf": nl_pdf,
        "english_pdf": en_pdf,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the promoted Weekly ETF EU client-grade v2 routine package.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--pricing-artifact", required=True)
    parser.add_argument("--macro-pack", required=True)
    parser.add_argument("--registry", default="config/ucits_symbol_registry.yml")
    parser.add_argument("--output-dir", default="output/fresh_generation")
    parser.add_argument("--portfolio-state", default="output/etf_eu_portfolio_state.json")
    parser.add_argument("--valuation-history", default="output/etf_eu_valuation_history.csv")
    parser.add_argument("--trade-ledger", default="output/etf_eu_trade_ledger.csv")
    parser.add_argument("--recommendation-scorecard", default="output/etf_eu_recommendation_scorecard.csv")
    parser.add_argument("--previous-routine-manifest", required=True)
    parser.add_argument("--previous-delivery-closeout-manifest", required=True)
    args = parser.parse_args()
    outputs = build(args)
    print("ETF_EU_ROUTINE_CLIENT_GRADE_V2_PACKAGE_OK | " + " | ".join(f"{key}={value}" for key, value in outputs.items()))


if __name__ == "__main__":
    main()
