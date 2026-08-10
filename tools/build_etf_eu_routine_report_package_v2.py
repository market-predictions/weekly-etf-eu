from __future__ import annotations

import argparse
import csv
import json
from argparse import Namespace
from pathlib import Path
from typing import Any

from runtime.build_etf_eu_client_grade_report_state import build_state
from runtime.build_etf_eu_current_reunderwriting_scorecard import build_rows as build_reunderwriting_rows
from runtime.build_etf_eu_current_reunderwriting_scorecard import prior_index, write as write_reunderwriting
from runtime.inject_etf_eu_funded_identity_strip import inject_funded_identity_strip
from runtime.polish_etf_eu_client_grade_html import polish
from runtime.reconcile_etf_eu_funded_markdown import reconcile_funded_markdown
from runtime.render_etf_eu_client_grade_v3_converged import render
from tools.build_etf_eu_routine_report_package import build as build_legacy_package
from tools.validate_etf_eu_current_reunderwriting_scorecard import validate as validate_reunderwriting
from weasyprint import HTML


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Required artifact not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _pricing_index(pricing: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("ticker") or "").strip().upper(): dict(row)
        for row in pricing.get("rows") or []
        if isinstance(row, dict) and row.get("ticker")
    }


def _apply_current_funded_valuation(state: dict[str, Any], pricing: dict[str, Any], report_date: str) -> dict[str, Any]:
    portfolio = dict(state.get("portfolio") or {})
    positions = [dict(row) for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    prices = _pricing_index(pricing)
    blockers: list[str] = []
    invested = 0.0
    for row in positions:
        ticker = str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()
        price = prices.get(ticker)
        if not price:
            blockers.append(f"{ticker}:current_pricing_row_missing")
            continue
        if str(price.get("close_date") or "")[:10] != report_date:
            blockers.append(f"{ticker}:completed_close_date_mismatch")
            continue
        if price.get("completed_close_on_or_before_report_date") is not True or price.get("close_price") is None:
            blockers.append(f"{ticker}:completed_close_missing")
            continue
        if price.get("currency") != "EUR":
            blockers.append(f"{ticker}:non_eur_funded_line_requires_fx_revaluation")
            continue
        current_price = float(price["close_price"])
        shares = float(row.get("shares") or 0.0)
        value = round(shares * current_price, 2)
        row["current_price_local"] = current_price
        row["price_date"] = report_date
        row["market_value_local"] = value
        row["market_value_eur"] = value
        row["pricing_source"] = price.get("source_name") or price.get("source_id")
        row["pricing_status"] = "current_completed_close_from_run_pricing"
        row["pricing_source_quality"] = price.get("source_agreement_status")
        invested += value
    if blockers:
        raise RuntimeError("Current funded valuation failed closed: " + "; ".join(blockers))

    cash = float(portfolio.get("cash_eur") or 0.0)
    nav = round(invested + cash, 2)
    for row in positions:
        row["current_weight_pct"] = round(float(row.get("market_value_eur") or 0.0) / nav * 100.0, 6) if nav else 0.0
    portfolio["positions"] = positions
    portfolio["invested_market_value_eur"] = round(invested, 2)
    portfolio["nav_eur"] = nav
    portfolio["cash_weight_pct"] = round(cash / nav * 100.0, 6) if nav else 0.0
    state["portfolio"] = portfolio
    state.setdefault("valuation", {})["current_run_funded_revaluation"] = {
        "report_date": report_date,
        "invested_market_value_eur": round(invested, 2),
        "cash_eur": round(cash, 2),
        "nav_eur": nav,
        "funded_position_count": len(positions),
        "pricing_authority": "current_run_completed_close_artifact",
        "portfolio_quantity_mutation": False,
    }
    return state


def _persist_current_valuation_history(path: Path, state: dict[str, Any], report_date: str, source_report: str) -> list[dict[str, Any]]:
    portfolio = state["portfolio"]
    starting = float(portfolio.get("starting_capital_eur") or 100000.0)
    nav = float(portfolio.get("nav_eur") or 0.0)
    cash = float(portfolio.get("cash_eur") or 0.0)
    invested = float(portfolio.get("invested_market_value_eur") or 0.0)

    raw_rows: list[dict[str, str]] = []
    if path.exists():
        with path.open(newline="", encoding="utf-8") as handle:
            raw_rows = list(csv.DictReader(handle))
    prior = [row for row in raw_rows if str(row.get("date") or "") < report_date]
    prev_nav = float(prior[-1]["nav_eur"]) if prior else starting
    historic_navs = [float(row.get("nav_eur") or 0.0) for row in prior]
    peak = max([starting, nav, *historic_navs])
    daily = ((nav / prev_nav) - 1.0) * 100.0 if prev_nav else 0.0
    since = ((nav / starting) - 1.0) * 100.0 if starting else 0.0
    drawdown = ((nav / peak) - 1.0) * 100.0 if peak else 0.0
    current = {
        "date": report_date,
        "nav_eur": f"{nav:.2f}",
        "cash_eur": f"{cash:.2f}",
        "invested_market_value_eur": f"{invested:.2f}",
        "daily_return_pct": f"{daily:.6f}",
        "since_inception_return_pct": f"{since:.6f}",
        "drawdown_pct": f"{drawdown:.6f}",
        "comment": "Current completed-close four-position EU/UCITS routine valuation",
        "source_report": source_report,
    }
    merged = [row for row in raw_rows if str(row.get("date") or "") != report_date] + [current]
    merged.sort(key=lambda row: str(row.get("date") or ""))
    fields = [
        "date", "nav_eur", "cash_eur", "invested_market_value_eur", "daily_return_pct",
        "since_inception_return_pct", "drawdown_pct", "comment", "source_report",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(merged)

    return [
        {
            "date": row["date"],
            "nav_eur": float(row["nav_eur"]),
            "cash_eur": float(row["cash_eur"]),
            "invested_market_value_eur": float(row["invested_market_value_eur"]),
            "since_inception_return_pct": float(row["since_inception_return_pct"]),
            "drawdown_pct": float(row["drawdown_pct"]),
            "comment": row["comment"],
            "source_report": row["source_report"],
        }
        for row in merged
    ]


def _equity_from_history(history: list[dict[str, Any]], portfolio: dict[str, Any]) -> dict[str, Any]:
    points = [{"date": row["date"], "nav_eur": row["nav_eur"]} for row in history]
    meaningful = len(points) >= 2 and (portfolio.get("position_count", 0) > 0 or len({round(row["nav_eur"], 2) for row in history}) > 1)
    latest_matches = bool(points) and abs(points[-1]["nav_eur"] - float(portfolio.get("nav_eur") or 0.0)) <= 0.05
    return {
        "show_chart": meaningful,
        "points": points,
        "point_count": len(points),
        "latest_nav_matches_state": latest_matches,
        "fallback_nl": "Er zijn nog onvoldoende gevalideerde NAV-observaties voor een betekenisvolle curve.",
        "fallback_en": "There are not yet enough validated NAV observations for a meaningful curve.",
        "activation_rule": "show after at least two meaningful validated NAV observations or a funded position",
    }


def build(args: argparse.Namespace) -> dict[str, Path]:
    legacy_outputs = build_legacy_package(args)
    output_dir = Path(args.output_dir)
    state_path = Path("output/runtime") / f"etf_eu_client_grade_report_state_{args.run_id}.json"
    reunderwriting_path = Path("output/runtime") / f"etf_eu_reunderwriting_scorecard_{args.run_id}.csv"
    reunderwriting_validation_path = Path("output/quality") / f"etf_eu_reunderwriting_validation_{args.run_id}.json"

    portfolio_raw = _load(Path(args.portfolio_state))
    pricing_raw = _load(Path(args.pricing_artifact))
    prior = prior_index(Path(args.recommendation_scorecard))
    review_rows = build_reunderwriting_rows(
        portfolio_raw,
        {},
        prior,
        args.report_date,
        f"routine-current-reunderwriting:{args.run_id}",
        pricing_raw,
    )
    write_reunderwriting(review_rows, reunderwriting_path)
    review_validation = validate_reunderwriting(reunderwriting_path, Path(args.portfolio_state), args.report_date)
    _write(reunderwriting_validation_path, review_validation)

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
        raise RuntimeError(f"Client-grade state is invalid before convergence overlay: {state.get('blockers')}")

    state = _apply_current_funded_valuation(state, pricing_raw, args.report_date)
    history = _persist_current_valuation_history(
        Path(args.valuation_history),
        state,
        args.report_date,
        f"routine-client-grade-v3-{args.run_id}",
    )
    state["valuation_history"] = history
    state["equity_curve"] = _equity_from_history(history, state["portfolio"])
    if state["equity_curve"]["latest_nav_matches_state"] is not True:
        raise RuntimeError("Current valuation history does not reconcile to revalued portfolio state")
    state["current_reunderwriting"] = review_rows
    state.setdefault("sources", {})["current_reunderwriting_scorecard"] = str(reunderwriting_path)
    state.setdefault("authority", {}).update(
        {
            "allocation_authority_contract": "control/ETF_EU_ALLOCATION_AUTHORITY_CONVERGENCE_V1.md",
            "shadow_policy_used_for_current_allocation": False,
            "retired_fixed_percentage_used": False,
            "historical_target_used_for_current_trade": False,
            "broker_specific_permission_required_for_model": False,
            "broker_permission_required_for_real_execution": True,
            "portfolio_mutation": False,
            "real_broker_execution": False,
        }
    )
    state["schema_version"] = "etf_eu_client_grade_report_state_v3_donor_converged"
    _write(state_path, state)

    nl_html = output_dir / f"weekly_etf_eu_review_nl_{args.report_suffix}.html"
    en_html = output_dir / f"weekly_etf_eu_review_{args.report_suffix}.html"
    nl_pdf = output_dir / f"weekly_etf_eu_review_nl_{args.report_suffix}.pdf"
    en_pdf = output_dir / f"weekly_etf_eu_review_{args.report_suffix}.pdf"

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

    promotion_fields = {
        "client_renderer_mode": "client_grade_v3_donor_converged",
        "production_renderer": "runtime/render_etf_eu_client_grade_v3_converged.py",
        "renderer_engine": "weasyprint",
        "render_source_authority": "normalized_report_state_v3_donor_converged",
        "normalized_report_state": str(state_path),
        "current_reunderwriting_scorecard": str(reunderwriting_path),
        "current_reunderwriting_validation": str(reunderwriting_validation_path),
        "current_reunderwriting_position_count": len(review_rows),
        "shadow_policy_used_for_current_allocation": False,
        "retired_fixed_percentage_used": False,
        "historical_target_used_for_current_trade": False,
        "broker_specific_permission_required_for_model": False,
        "markdown_role": "funded_state_reconciled_audit_companion_not_v3_render_source",
        "markdown_generation_status": "generated_funded_state_reconciled_audit_companion",
        "macro_policy_pack": args.macro_pack,
        "ucits_registry": args.registry,
        "investor_brief_present": True,
        "analyst_appendix_present": True,
        "report_section_count": 15,
        "conditional_equity_curve_enabled": True,
        "equity_surface": "chart" if funded_state["equity_curve"]["show_chart"] else "cash_preservation_callout",
        "funded_position_count": funded_state["portfolio"]["position_count"],
        "full_generation_status": "client_grade_v3_generated_pending_quality_gates",
        "upstream_pattern_adapted": "weekly-etf discovery/re-underwriting/runtime-state discipline adapted to EU/UCITS authority without importing U.S. fundability or state",
    }
    manifest.update(promotion_fields)
    manifest["renderer"] = "runtime/render_etf_eu_client_grade_v3_converged.py"
    manifest["client_surface_sanitizer"] = "runtime/polish_etf_eu_client_grade_html.py"
    manifest["html_generation_status"] = "client_grade_v3_generated"
    manifest["pdf_generation_status"] = "client_grade_v3_generated_pending_quality_gates"
    ready.update(promotion_fields)
    routine.update(promotion_fields)
    routine["routine_stage"] = "routine_client_grade_v3_generation_completed_pending_quality_gates"
    routine["workflow_status"] = "routine_client_grade_v3_generation_completed_pending_quality_gates"

    _write(manifest_path, manifest)
    _write(ready_path, ready)
    _write(routine_path, routine)
    return {
        **legacy_outputs,
        "state": state_path,
        "reunderwriting": reunderwriting_path,
        "reunderwriting_validation": reunderwriting_validation_path,
        "dutch_html": nl_html,
        "english_html": en_html,
        "dutch_pdf": nl_pdf,
        "english_pdf": en_pdf,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the donor-converged Weekly ETF EU client-grade routine package.")
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
    print("ETF_EU_ROUTINE_CLIENT_GRADE_V3_PACKAGE_OK | " + " | ".join(f"{key}={value}" for key, value in outputs.items()))


if __name__ == "__main__":
    main()
