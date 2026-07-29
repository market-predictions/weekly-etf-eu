from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected YAML object: {path}")
    return payload


def num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def text(value: Any) -> str | None:
    return None if value is None else str(value)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def holdings_index(fund: dict[str, Any]) -> dict[str, float]:
    result: dict[str, float] = {}
    for row in fund.get("documented_holdings") or []:
        if not isinstance(row, dict):
            continue
        ticker = str(row.get("ticker") or "").upper().strip()
        if ticker:
            result[ticker] = num(row.get("weight_pct"))
    return result


def documented_coverage(fund: dict[str, Any]) -> float:
    return round(sum(holdings_index(fund).values()), 6)


def pairwise_overlap(left_id: str, left: dict[str, Any], right_id: str, right: dict[str, Any]) -> dict[str, Any]:
    left_holdings = holdings_index(left)
    right_holdings = holdings_index(right)
    common = sorted(set(left_holdings) & set(right_holdings))
    rows = [
        {
            "ticker": ticker,
            "left_weight_pct": round(left_holdings[ticker], 6),
            "right_weight_pct": round(right_holdings[ticker], 6),
            "minimum_weight_overlap_pct": round(min(left_holdings[ticker], right_holdings[ticker]), 6),
        }
        for ticker in common
    ]
    overlap = round(sum(row["minimum_weight_overlap_pct"] for row in rows), 6)
    left_coverage = documented_coverage(left)
    right_coverage = documented_coverage(right)
    complete = bool(
        left.get("holding_count")
        and right.get("holding_count")
        and len(left_holdings) >= int(left.get("holding_count") or 0)
        and len(right_holdings) >= int(right.get("holding_count") or 0)
    )
    return {
        "left_fund": left_id,
        "right_fund": right_id,
        "method": "sum_of_minimum_documented_holding_weights",
        "measured_overlap_lower_bound_pct": overlap,
        "common_documented_holding_count": len(rows),
        "common_documented_holdings": rows,
        "left_documented_coverage_pct": left_coverage,
        "right_documented_coverage_pct": right_coverage,
        "full_holdings_coverage": complete,
        "zero_measured_overlap_means_zero_actual_overlap": bool(complete and overlap == 0),
        "interpretation": (
            "complete_documented_overlap_measure" if complete else "lower_bound_only_due_to_incomplete_documented_holdings"
        ),
    }


def position_index(portfolio: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("ticker") or row.get("exchange_ticker") or "").upper(): row
        for row in portfolio.get("positions") or []
        if isinstance(row, dict)
    }


def embedded_exposure(position_weight: float, overlap_pct: float) -> float:
    return round(position_weight * overlap_pct / 100.0, 6)


def build(portfolio: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    funds = evidence.get("funds") if isinstance(evidence.get("funds"), dict) else {}
    required = {"VWCE", "SXR8", "EUNA", "VVSM", "LOCK"}
    missing = sorted(required - set(funds))
    if missing:
        raise RuntimeError(f"Missing overlap evidence funds: {', '.join(missing)}")

    pairs = [
        pairwise_overlap("VWCE", funds["VWCE"], "SXR8", funds["SXR8"]),
        pairwise_overlap("VWCE", funds["VWCE"], "VVSM", funds["VVSM"]),
        pairwise_overlap("SXR8", funds["SXR8"], "VVSM", funds["VVSM"]),
        pairwise_overlap("VWCE", funds["VWCE"], "LOCK", funds["LOCK"]),
        pairwise_overlap("SXR8", funds["SXR8"], "LOCK", funds["LOCK"]),
    ]
    pair_index = {(row["left_fund"], row["right_fund"]): row for row in pairs}
    positions = position_index(portfolio)
    vwce_weight = num((positions.get("VWCE") or {}).get("current_weight_pct"))
    sxr8_weight = num((positions.get("SXR8") or {}).get("current_weight_pct"))
    euna_weight = num((positions.get("EUNA") or {}).get("current_weight_pct"))

    vwce_semiconductor_lb = num(pair_index[("VWCE", "VVSM")]["measured_overlap_lower_bound_pct"])
    sxr8_semiconductor_lb = num(pair_index[("SXR8", "VVSM")]["measured_overlap_lower_bound_pct"])
    vwce_cyber_lb = num(pair_index[("VWCE", "LOCK")]["measured_overlap_lower_bound_pct"])
    sxr8_cyber_lb = num(pair_index[("SXR8", "LOCK")]["measured_overlap_lower_bound_pct"])

    embedded_semiconductor = {
        "VWCE": embedded_exposure(vwce_weight, vwce_semiconductor_lb),
        "SXR8": embedded_exposure(sxr8_weight, sxr8_semiconductor_lb),
    }
    embedded_cyber = {
        "VWCE": embedded_exposure(vwce_weight, vwce_cyber_lb),
        "SXR8": embedded_exposure(sxr8_weight, sxr8_cyber_lb),
    }

    dispositions = [
        {
            "ticker": "VWCE",
            "current_weight_pct": round(vwce_weight, 6),
            "role": "global_equity_core",
            "shadow_disposition": "retain_as_core_candidate_and_cap_during_transition",
            "stage_1_action": "hold",
            "future_review": "set_permanent_core_weight_after_ex_us_and_theme_mapping_completion",
            "evidence": {
                "us_country_weight_pct": num((funds["VWCE"].get("country_exposure") or {}).get("US")),
                "documented_semiconductor_overlap_lower_bound_pct": vwce_semiconductor_lb,
                "portfolio_embedded_semiconductor_lower_bound_pct_nav": embedded_semiconductor["VWCE"],
            },
            "reasoning": "VWCE contributes broad global diversification and non-US exposure, but already embeds measurable semiconductor concentration.",
        },
        {
            "ticker": "SXR8",
            "current_weight_pct": round(sxr8_weight, 6),
            "role": "us_large_cap_core_overweight",
            "shadow_disposition": "retain_stage_1_then_prioritize_for_overlap_reduction_review",
            "stage_1_action": "hold",
            "future_review": "candidate_source_for_stage_2_reduction_after_ex_us_core_is_fundable",
            "evidence": {
                "vwce_pairwise_overlap_lower_bound_pct": num(pair_index[("VWCE", "SXR8")]["measured_overlap_lower_bound_pct"]),
                "documented_semiconductor_overlap_lower_bound_pct": sxr8_semiconductor_lb,
                "portfolio_embedded_semiconductor_lower_bound_pct_nav": embedded_semiconductor["SXR8"],
            },
            "reasoning": "SXR8 duplicates part of VWCE's US mega-cap sleeve and adds further documented overlap with the semiconductor satellite.",
        },
        {
            "ticker": "EUNA",
            "current_weight_pct": round(euna_weight, 6),
            "role": "aggregate_bond_stabiliser",
            "shadow_disposition": "retain_pending_explicit_risk_budget_decision",
            "stage_1_action": "hold",
            "future_review": "evaluate_against_required_portfolio_volatility_and_drawdown_budget_not_equity_overlap",
            "evidence": dict(funds["EUNA"].get("portfolio_characteristics") or {}),
            "reasoning": "EUNA is a role-diversifier rather than an equity duplicate; its disposition must be decided through risk-budget evidence.",
        },
    ]

    return {
        "schema_version": "etf_eu_incumbent_overlap_review_v1",
        "artifact_type": "etf_eu_incumbent_overlap_and_disposition_review",
        "generated_at_utc": utc_now(),
        "source_evidence": "config/etf_eu_incumbent_overlap_evidence_20260724.yml",
        "portfolio_report_date": text(portfolio.get("last_valuation_report_date")),
        "methodology": {
            "pairwise_overlap": "sum_of_minimum_documented_holding_weights",
            "portfolio_embedded_exposure": "current_portfolio_weight_times_pairwise_overlap_lower_bound",
            "lower_bound_only": True,
            "zero_overlap_guard": "zero_measured_overlap_is_not_zero_actual_overlap_when_documented_coverage_is_incomplete",
        },
        "fund_evidence_coverage": {
            ticker: {
                "documented_holding_count": len(holdings_index(fund)),
                "reported_holding_count": fund.get("holding_count"),
                "documented_coverage_pct": documented_coverage(fund),
                "holdings_as_of": text(fund.get("holdings_as_of")),
            }
            for ticker, fund in funds.items()
        },
        "pairwise_overlap_rows": pairs,
        "portfolio_embedded_exposure_lower_bounds": {
            "semiconductor_pct_nav": round(sum(embedded_semiconductor.values()), 6),
            "semiconductor_by_incumbent_pct_nav": embedded_semiconductor,
            "cybersecurity_pct_nav": round(sum(embedded_cyber.values()), 6),
            "cybersecurity_by_incumbent_pct_nav": embedded_cyber,
            "cybersecurity_measurement_warning": "LOCK documented holdings coverage is incomplete; measured overlap is not a complete estimate.",
        },
        "incumbent_dispositions": dispositions,
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
        "production_delivery_authority": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build incumbent overlap and disposition review")
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument(
        "--evidence",
        type=Path,
        default=Path("config/etf_eu_incumbent_overlap_evidence_20260724.yml"),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(load_json(args.portfolio_state), load_yaml(args.evidence))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
