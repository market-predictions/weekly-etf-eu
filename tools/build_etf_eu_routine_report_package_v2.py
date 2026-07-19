from __future__ import annotations

import argparse
import json
from argparse import Namespace
from pathlib import Path
from typing import Any

from runtime.apply_etf_eu_cockpit_to_package import apply_cockpit_to_package, configured_feature_value
from runtime.build_etf_eu_client_grade_report_state import build_state
from runtime.inject_etf_eu_funded_identity_strip import inject_funded_identity_strip
from runtime.polish_etf_eu_client_grade_html import polish
from runtime.reconcile_etf_eu_funded_markdown import reconcile_funded_markdown
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
    nl_browser_html = output_dir / f"weekly_etf_eu_review_nl_{args.report_suffix}_browser.html"
    en_browser_html = output_dir / f"weekly_etf_eu_review_{args.report_suffix}_browser.html"

    render(state_path, "nl", nl_html, nl_pdf)
    render(state_path, "en", en_html, en_pdf)

    nl_polished = polish(nl_html.read_text(encoding="utf-8"), language="nl")
    en_polished = polish(en_html.read_text(encoding="utf-8"), language="en")
    nl_polished = inject_funded_identity_strip(nl_polished, language="nl")
    en_polished = inject_funded_identity_strip(en_polished, language="en")
    nl_html.write_text(nl_polished, encoding="utf-8")
    en_html.write_text(en_polished, encoding="utf-8")
    HTML(string=nl_polished, base_url=str(nl_html.parent.resolve())).write_pdf(str(nl_pdf))
    HTML(string=en_polished, base_url=str(en_html.parent.resolve())).write_pdf(str(en_pdf))

    funded_state = _load(state_path)
    cockpit_result = apply_cockpit_to_package(
        state=funded_state,
        dutch_html=nl_html,
        english_html=en_html,
        dutch_pdf=nl_pdf,
        english_pdf=en_pdf,
        dutch_browser_html=nl_browser_html,
        english_browser_html=en_browser_html,
        feature_value=configured_feature_value(),
    )

    manifest_path = Path(legacy_outputs["manifest"])
    ready_path = Path(legacy_outputs["ready"])
    routine_path = Path(legacy_outputs["routine"])
    manifest = _load(manifest_path)
    ready = _load(ready_path)
    routine = _load(routine_path)

    nl_md = Path(str(manifest["dutch_primary_markdown"]))
    en_md = Path(str(manifest["english_companion_markdown"]))
    nl_md.write_text(reconcile_funded_markdown(nl_md.read_text(encoding="utf-8"), funded_state, language="nl"), encoding="utf-8")
    en_md.write_text(reconcile_funded_markdown(en_md.read_text(encoding="utf-8"), funded_state, language="en"), encoding="utf-8")

    renderer_mode = "client_grade_v2_funded_aware_with_cockpit" if cockpit_result.enabled else "client_grade_v2_funded_aware"
    promotion_fields = {
        "client_renderer_mode": renderer_mode,
        "production_renderer": "runtime/render_etf_eu_client_grade_v2_funded.py",
        "cockpit_integration_layer": "runtime/apply_etf_eu_cockpit_to_package.py",
        "cockpit_email_inliner": "runtime/inline_etf_eu_email_report_styles.py",
        "cockpit_feature_flag": "MRKT_RPRTS_ETF_EU_COCKPIT_FRONT_PAGE",
        "cockpit_feature_value": cockpit_result.feature_value,
        "cockpit_front_page_status": cockpit_result.status,
        "cockpit_front_page_enabled": cockpit_result.enabled,
        "cockpit_front_page_count_nl": cockpit_result.dutch_front_page_count,
        "cockpit_front_page_count_en": cockpit_result.english_front_page_count,
        "cockpit_investor_summary_suppressed_nl": cockpit_result.dutch_summary_suppressed,
        "cockpit_investor_summary_suppressed_en": cockpit_result.english_summary_suppressed,
        "cockpit_document_order": "cockpit_then_investor_then_analyst" if cockpit_result.enabled else "investor_then_analyst",
        "cockpit_email_safe_surface_available": cockpit_result.enabled,
        "cockpit_email_safe_surface_is_primary_html": cockpit_result.enabled,
        "cockpit_full_report_email_inline_styled": cockpit_result.enabled,
        "cockpit_browser_html_retained_for_pdf_audit": cockpit_result.enabled,
        "cockpit_fallback_diagnostic": cockpit_result.diagnostic,
        "renderer_engine": "weasyprint",
        "render_source_authority": "normalized_report_state",
        "normalized_report_state": str(state_path),
        "markdown_role": "funded_state_reconciled_audit_companion_not_v2_render_source",
        "markdown_generation_status": "generated_funded_state_reconciled_audit_companion",
        "macro_policy_pack": args.macro_pack,
        "ucits_registry": args.registry,
        "investor_brief_present": True,
        "analyst_appendix_present": True,
        "report_section_count": 15,
        "conditional_equity_curve_enabled": True,
        "equity_surface": "chart" if funded_state["equity_curve"]["show_chart"] else "cash_preservation_callout",
        "funded_position_count": funded_state["portfolio"]["position_count"],
        "full_generation_status": "client_grade_v2_generated_pending_quality_gates",
        "upstream_pattern_adapted": "weekly-etf normalized report state, investor/analyst hierarchy, additive cockpit and full-report email-safe surface adapted for EU/UCITS production",
    }
    manifest.update(promotion_fields)
    manifest["renderer"] = "runtime/render_etf_eu_client_grade_v2_funded.py"
    manifest["client_surface_sanitizer"] = "runtime/polish_etf_eu_client_grade_html.py"
    manifest["html_generation_status"] = "client_grade_v2_generated"
    manifest["pdf_generation_status"] = "client_grade_v2_generated_pending_quality_gates"
    if cockpit_result.enabled:
        manifest["dutch_primary_browser_html"] = str(nl_browser_html)
        manifest["english_companion_browser_html"] = str(en_browser_html)
    else:
        manifest.pop("dutch_primary_browser_html", None)
        manifest.pop("english_companion_browser_html", None)
    ready.update(promotion_fields)
    routine.update(promotion_fields)
    if cockpit_result.enabled:
        ready["dutch_primary_browser_html"] = str(nl_browser_html)
        ready["english_companion_browser_html"] = str(en_browser_html)
        routine["dutch_primary_browser_html"] = str(nl_browser_html)
        routine["english_companion_browser_html"] = str(en_browser_html)
    routine["routine_stage"] = "routine_client_grade_v2_generation_completed_pending_quality_gates"
    routine["workflow_status"] = "routine_client_grade_v2_generation_completed_pending_quality_gates"

    _write(manifest_path, manifest)
    _write(ready_path, ready)
    _write(routine_path, routine)
    outputs = {
        **legacy_outputs,
        "state": state_path,
        "dutch_html": nl_html,
        "english_html": en_html,
        "dutch_pdf": nl_pdf,
        "english_pdf": en_pdf,
    }
    if cockpit_result.enabled:
        outputs["dutch_browser_html"] = nl_browser_html
        outputs["english_browser_html"] = en_browser_html
    return outputs


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
