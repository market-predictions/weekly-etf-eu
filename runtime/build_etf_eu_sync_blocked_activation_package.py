from __future__ import annotations

import argparse
import csv
import hashlib
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def preferred_variant(allocator: dict[str, Any]) -> dict[str, Any]:
    preferred_id = str(allocator.get("preferred_shadow_variant") or "")
    for variant in allocator.get("variants") or []:
        if isinstance(variant, dict) and variant.get("variant_id") == preferred_id:
            return variant
    raise RuntimeError("Preferred shadow allocator variant missing")


def indexed_candidates(product_evidence: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("ticker")): row
        for row in product_evidence.get("candidates") or []
        if isinstance(row, dict) and row.get("ticker")
    }


def product_blockers(candidate: dict[str, Any]) -> list[str]:
    ticker = str(candidate.get("ticker") or "UNKNOWN").lower()
    blockers: list[str] = []
    for grade_name in ("identity_grade", "document_grade", "valuation_grade", "tradability_grade"):
        grade = candidate.get(grade_name) if isinstance(candidate.get(grade_name), dict) else {}
        if grade.get("status") != "pass":
            blockers.append(f"{ticker}_{grade_name}_not_pass")
            if grade.get("blocker"):
                blockers.append(f"{ticker}_{grade.get('blocker')}")
    if candidate.get("activation_ready") is not True:
        blockers.append(f"{ticker}_not_activation_ready")
    return blockers


def ledger_row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def build(
    sources: dict[str, Any],
    portfolio: dict[str, Any],
    portfolio_path: Path,
    ledger_path: Path,
    allocator: dict[str, Any],
    stage_2: dict[str, Any],
    product_evidence: dict[str, Any],
    receipt: dict[str, Any],
    output: Path,
) -> None:
    if sources.get("schema_version") != "etf_eu_sync_cutover_package_sources_v1":
        raise RuntimeError("Unexpected cutover source lock")
    boundary = sources.get("activation_boundary") if isinstance(sources.get("activation_boundary"), dict) else {}
    if any(boundary.get(key) is not False for key in (
        "activation_ready",
        "authorization_present",
        "executable_trade_intents_allowed",
        "official_portfolio_mutation_allowed",
        "official_ledger_write_allowed",
        "production_delivery_authority",
    )):
        raise RuntimeError("Cutover source lock violates blocked boundary")
    if portfolio.get("schema_version") != "etf_eu_portfolio_state_v2":
        raise RuntimeError("Unexpected official portfolio state")
    if allocator.get("schema_version") != "etf_eu_target_allocator_shadow_v3":
        raise RuntimeError("Unexpected allocator contract")
    allocator_authority = allocator.get("authority") if isinstance(allocator.get("authority"), dict) else {}
    for key in ("portfolio_mutation", "funding_authority", "execution_authority", "production_delivery_authority"):
        if allocator_authority.get(key) is not False:
            raise RuntimeError(f"Allocator authority {key} must be false")
    if stage_2.get("schema_version") != "etf_eu_stage_2_readiness_v1" or stage_2.get("readiness") != "blocked":
        raise RuntimeError("Stage-2 artifact must be valid and blocked")
    if stage_2.get("executable_trade_intents") not in ([], None):
        raise RuntimeError("Stage-2 artifact contains executable intents")
    if receipt.get("schema_version") != "etf_eu_shadow_cid_mailbox_receipt_v1":
        raise RuntimeError("Mailbox receipt contract mismatch")
    if receipt.get("sent_match_observed") is not True or receipt.get("inbox_match_observed") is not True:
        raise RuntimeError("Mailbox receipt is incomplete")

    variant = preferred_variant(allocator)
    summary = variant.get("summary") if isinstance(variant.get("summary"), dict) else {}
    selected_rows = [
        row for row in variant.get("allocation_rows") or []
        if isinstance(row, dict) and row.get("selected") is True
    ]
    selected_by_exposure = {str(row.get("exposure_id")): row for row in selected_rows}
    required_selected = {"ai_compute_infrastructure", "cyber_security"}
    if set(selected_by_exposure) != required_selected:
        raise RuntimeError("Stage-1 selected exposure set changed")

    current_positions = [
        {
            "ticker": row.get("ticker") or row.get("exchange_ticker"),
            "isin": row.get("isin"),
            "shares": int(row.get("shares") or 0),
            "market_value_eur": round(float(row.get("market_value_eur") or 0.0), 2),
            "state": "official_pre_cutover_position_unchanged",
        }
        for row in portfolio.get("positions") or []
        if isinstance(row, dict)
    ]
    simulated_additions: list[dict[str, Any]] = []
    simulated_ledger_blueprint: list[dict[str, Any]] = []
    for exposure_id in sorted(required_selected):
        row = selected_by_exposure[exposure_id]
        candidate = row.get("candidate") if isinstance(row.get("candidate"), dict) else {}
        order = row.get("order") if isinstance(row.get("order"), dict) else {}
        addition = {
            "exposure_id": exposure_id,
            "ticker": candidate.get("ticker"),
            "isin": candidate.get("isin"),
            "exchange": candidate.get("exchange"),
            "currency": candidate.get("currency"),
            "simulated_target_shares": int(order.get("target_shares") or 0),
            "simulated_market_value_eur": round(float(order.get("target_market_value_eur") or 0.0), 2),
            "simulated_weight_pct_nav": round(float(row.get("variant_target_weight_pct") or 0.0), 6),
            "state": "shadow_simulation_only_not_authorized",
        }
        simulated_additions.append(addition)
        simulated_ledger_blueprint.append({
            "record_type": "proposed_model_ledger_append_blueprint",
            "ticker": addition["ticker"],
            "isin": addition["isin"],
            "simulated_shares_delta": addition["simulated_target_shares"],
            "source": "policy_allocator_shadow",
            "write_performed": False,
            "authorization_present": False,
            "executable_order": False,
        })

    candidates = indexed_candidates(product_evidence)
    blockers = {
        "stage_1_activation_authorization_missing",
        "stage_1_official_portfolio_mutation_not_performed",
        "stage_1_official_ledger_write_not_performed",
        "stage_1_execution_receipt_missing",
        "connectivity_pricing_is_not_accepted_activation_valuation",
    }
    for ticker in ("VVSM", "LOCK"):
        blockers.update(product_blockers(candidates.get(ticker, {"ticker": ticker})))
    blockers.update(f"stage_2:{code}" for code in stage_2.get("blockers") or [])

    source_artifacts = sources.get("source_artifacts") if isinstance(sources.get("source_artifacts"), dict) else {}
    payload = {
        "schema_version": "etf_eu_sync_blocked_activation_package_v1",
        "artifact_type": "etf_eu_sync_blocked_activation_package",
        "package_id": sources.get("package_id"),
        "generated_at_utc": utc_now(),
        "status": "blocked_not_activation_ready",
        "activation_ready": False,
        "authorization": {
            "authorization_present": False,
            "stage_1_activation_authorized": False,
            "stage_2_activation_authorized": False,
            "send_or_execute_command_allowed": False,
        },
        "immutable_lineage": {
            "donor_contract": sources.get("donor_contract"),
            "validated_eu_design": sources.get("validated_eu_design"),
            "source_artifacts": source_artifacts,
        },
        "official_pre_cutover_state": {
            "portfolio_state_path": str(portfolio_path),
            "portfolio_state_sha256": sha256(portfolio_path),
            "portfolio_state_git_blob_sha": "16b7f88efb80b711dabec1e4a44a95ae8810a663",
            "trade_ledger_path": str(ledger_path),
            "trade_ledger_sha256": sha256(ledger_path),
            "trade_ledger_git_blob_sha": "30441db15d2f064dd05749f3a58765a00a12b4b6",
            "ledger_record_count": ledger_row_count(ledger_path),
            "nav_eur": portfolio.get("nav_eur"),
            "cash_eur": portfolio.get("cash_eur"),
            "invested_market_value_eur": portfolio.get("invested_market_value_eur"),
            "position_count": len(current_positions),
            "positions": current_positions,
            "preserved_unchanged": True,
        },
        "stage_1_shadow_target": {
            "variant_id": variant.get("variant_id"),
            "current_positions_retained": True,
            "simulated_additions": simulated_additions,
            "simulated_position_count": summary.get("position_count"),
            "simulated_projected_cash_eur": summary.get("projected_cash_eur"),
            "simulated_projected_cash_weight_pct": summary.get("projected_cash_weight_pct"),
            "simulated_gross_turnover_eur": summary.get("gross_turnover_eur"),
            "simulated_gross_turnover_pct_nav": summary.get("gross_turnover_pct_nav"),
            "simulated_transaction_cost_eur": summary.get("estimated_transaction_cost_eur"),
            "official_state_applied": False,
        },
        "proposed_ledger_blueprint": {
            "records": simulated_ledger_blueprint,
            "record_count": len(simulated_ledger_blueprint),
            "write_performed": False,
            "executable_trade_intents": [],
        },
        "stage_2_readiness": {
            "readiness": stage_2.get("readiness"),
            "destination": stage_2.get("destination"),
            "capacity_analysis": stage_2.get("capacity_analysis"),
            "entry_gate_results": stage_2.get("entry_gate_results"),
            "blockers": stage_2.get("blockers"),
            "executable_trade_intents": [],
        },
        "product_evidence": {
            "source": "config/etf_eu_cutover_product_evidence_20260728.yml",
            "status": product_evidence.get("status"),
            "summary": product_evidence.get("summary"),
            "activation_ready_count": (product_evidence.get("summary") or {}).get("activation_ready_count"),
        },
        "delivery_validation": {
            "transport_workflow_run_id": receipt.get("source_delivery_workflow_run_id"),
            "shadow_run_id": receipt.get("shadow_run_id"),
            "sent_match_observed": receipt.get("sent_match_observed"),
            "inbox_match_observed": receipt.get("inbox_match_observed"),
            "attachment_count": receipt.get("attachment_count"),
            "inline_image_count": receipt.get("inline_image_count"),
            "inline_image_sha256": (receipt.get("inline_image") or {}).get("sha256"),
            "cid_content_id": (receipt.get("inline_image") or {}).get("content_id"),
            "recipient_plaintext_stored": False,
            "raw_mime_stored": False,
        },
        "rollback": {
            "method": "state_oriented_separate_authorization",
            "last_accepted_state_path": str(portfolio_path),
            "last_accepted_state_sha256": sha256(portfolio_path),
            "post_stage_1_official_state_exists": False,
            "automatic_reverse_orders": False,
            "automatic_ledger_rewrite": False,
            "separate_rollback_authorization_required": True,
        },
        "blockers": sorted(blockers),
        "executable_trade_intents": [],
        "portfolio_mutation": False,
        "ledger_write": False,
        "funding_authority": False,
        "execution_authority": False,
        "activation_authority": False,
        "production_delivery_authority": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--portfolio", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--allocator", type=Path, required=True)
    parser.add_argument("--stage-2", type=Path, required=True)
    parser.add_argument("--product-evidence", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(
        load_yaml(args.sources),
        load_json(args.portfolio),
        args.portfolio,
        args.ledger,
        load_json(args.allocator),
        load_json(args.stage_2),
        load_yaml(args.product_evidence),
        load_json(args.receipt),
        args.output,
    )


if __name__ == "__main__":
    main()
