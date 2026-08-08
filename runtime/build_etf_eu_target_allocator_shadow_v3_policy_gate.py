from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import build_etf_eu_target_allocator_shadow_v3 as base


BLOCKER = "stage_1_candidate_not_allowlisted"
ALREADY_FUNDED_BLOCKER = "already_funded_model_position_no_incremental_trade"


def normalize_ticker(value: Any) -> str:
    ticker = str(value or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def candidate_identity(row: dict[str, Any]) -> tuple[str, str] | None:
    candidate = row.get("preferred_ucits_candidate") if isinstance(row.get("preferred_ucits_candidate"), dict) else {}
    isin = str(candidate.get("isin") or "").strip().upper()
    line = base.verified_candidate_line(row) or {}
    ticker = normalize_ticker(line.get("exchange_ticker"))
    return (isin, ticker) if isin and ticker else None


def funded_position_index(portfolio: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for position in portfolio.get("positions") or []:
        if not isinstance(position, dict):
            continue
        isin = str(position.get("isin") or "").strip().upper()
        ticker = normalize_ticker(position.get("ticker") or position.get("exchange_ticker"))
        if not isin or not ticker:
            continue
        key = (isin, ticker)
        if key in result:
            raise RuntimeError(f"Duplicate funded portfolio identity: {isin}/{ticker}")
        result[key] = position
    return result


def install_candidate_gate(policy: dict[str, Any]) -> set[str]:
    stage = policy.get("stage_1") if isinstance(policy.get("stage_1"), dict) else {}
    allowlist = {
        str(value)
        for value in stage.get("candidate_exposures") or []
        if str(value)
    }
    if allowlist != {"ai_compute_infrastructure", "cyber_security"}:
        raise RuntimeError("Stage-1 candidate exposure set is missing or unexpected")
    if stage.get("registry_expansion_must_not_reopen_stage_1_selection") is not True:
        raise RuntimeError("Registry-expansion Stage-1 boundary is missing")

    original_eligibility = base.eligibility

    def gated_eligibility(
        row: dict[str, Any],
        evidence: dict[str, Any],
        stage_policy: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        eligible, blockers = original_eligibility(row, evidence, stage_policy)
        exposure_id = str(row.get("exposure_id") or "")
        blockers = list(blockers)
        if exposure_id not in allowlist:
            blockers.append(BLOCKER)
        blockers = sorted(set(blockers))
        return not blockers, blockers

    base.eligibility = gated_eligibility
    return allowlist


def install_already_funded_gate(portfolio: dict[str, Any]) -> set[tuple[str, str]]:
    """Prevent an existing exact-line model position from consuming a new-trade budget.

    The temporary blocker is allocation-mechanics only. After the base allocator has
    sized genuinely unfunded candidates, reconciliation removes this blocker and
    restores strategy eligibility when no real evidence/policy blocker remains.
    """
    funded = funded_position_index(portfolio)
    original_eligibility = base.eligibility

    def gated_eligibility(
        row: dict[str, Any],
        evidence: dict[str, Any],
        stage_policy: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        eligible, blockers = original_eligibility(row, evidence, stage_policy)
        identity = candidate_identity(row)
        blockers = list(blockers)
        if eligible and identity in funded:
            blockers.append(ALREADY_FUNDED_BLOCKER)
        blockers = sorted(set(blockers))
        return not blockers, blockers

    base.eligibility = gated_eligibility
    return set(funded)


def reconcile_already_funded_rows(output: Path, portfolio: dict[str, Any]) -> None:
    payload = base.load_json(output)
    funded = funded_position_index(portfolio)
    variants = {
        str(row.get("variant_id")): row
        for row in payload.get("variants") or []
        if isinstance(row, dict)
    }
    preferred = variants.get("staged_policy_driven_v1")
    if not isinstance(preferred, dict):
        raise RuntimeError("Policy-driven allocator variant missing during funded-candidate reconciliation")

    reconciled: list[dict[str, Any]] = []
    for row in preferred.get("allocation_rows") or []:
        if not isinstance(row, dict):
            continue
        candidate = row.get("candidate") if isinstance(row.get("candidate"), dict) else {}
        identity = (
            str(candidate.get("isin") or "").strip().upper(),
            normalize_ticker(candidate.get("ticker")),
        )
        position = funded.get(identity)
        if not position:
            continue

        blockers = [value for value in row.get("blockers") or [] if value != ALREADY_FUNDED_BLOCKER]
        row["blockers"] = sorted(set(blockers))
        row["eligible"] = not row["blockers"]
        row["selected"] = False
        row["already_funded_model_position"] = True
        current_weight = base.num(position.get("current_weight_pct"))
        embedded = base.num(row.get("embedded_incumbent_exposure_lower_bound_pct_nav"))
        row["existing_direct_position_weight_pct_nav"] = round(current_weight, 6)
        row["effective_post_stage_exposure_lower_bound_pct_nav"] = round(embedded + current_weight, 6)
        row["existing_model_position"] = {
            "ticker": normalize_ticker(position.get("ticker") or position.get("exchange_ticker")),
            "isin": position.get("isin"),
            "shares": int(base.num(position.get("shares"))),
            "current_weight_pct": round(current_weight, 6),
            "market_value_eur": round(base.num(position.get("market_value_eur")), 2),
            "investability_status": position.get("investability_status"),
        }
        order = row.get("order") if isinstance(row.get("order"), dict) else {}
        order.update(
            {
                "current_shares": 0,
                "target_shares": 0,
                "share_delta": 0,
                "side": "ALREADY_FUNDED_NO_NEW_TRADE",
                "gross_trade_value_eur": 0.0,
                "estimated_cost_eur": 0.0,
                "target_market_value_eur": 0.0,
                "rounding_residual_eur": 0.0,
                "incremental_order_only": True,
            }
        )
        row["order"] = order
        reconciled.append(
            {
                "exposure_id": row.get("exposure_id"),
                "ticker": identity[1],
                "isin": identity[0],
                "strategy_eligible": row["eligible"],
                "incremental_trade_selected": False,
                "existing_direct_position_weight_pct_nav": row["existing_direct_position_weight_pct_nav"],
            }
        )

    checks = preferred.get("policy_checks") if isinstance(preferred.get("policy_checks"), dict) else {}
    checks["effective_theme_caps_met"] = all(
        base.num(row.get("effective_post_stage_exposure_lower_bound_pct_nav"))
        <= base.num(row.get("effective_theme_cap_pct_nav")) + 0.0001
        for row in preferred.get("allocation_rows") or []
        if isinstance(row, dict)
    )
    preferred["policy_checks"] = checks
    payload["activated_candidate_reconciliation"] = {
        "applied": bool(reconciled),
        "identity_contract": "exact_isin_plus_normalized_exchange_ticker",
        "rows": reconciled,
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
        "production_delivery_authority": False,
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build policy-gated EU target allocator shadow")
    parser.add_argument("--base-allocator", type=Path, required=True)
    parser.add_argument("--sync-shadow", type=Path, required=True)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--transition-evidence", type=Path, required=True)
    parser.add_argument("--overlap-review", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=Path("config/etf_eu_transition_policy_v1.yml"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    policy = base.load_yaml(args.policy)
    portfolio = base.load_json(args.portfolio_state)
    install_candidate_gate(policy)
    install_already_funded_gate(portfolio)
    base.build(
        base.load_json(args.base_allocator),
        base.load_json(args.sync_shadow),
        portfolio,
        base.load_json(args.transition_evidence),
        base.load_json(args.overlap_review),
        policy,
        args.output,
    )
    reconcile_already_funded_rows(args.output, portfolio)


if __name__ == "__main__":
    main()
