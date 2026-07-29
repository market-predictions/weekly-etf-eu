from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REQUIRED_BLOCKERS = {
    "stage_1_activation_authorization_missing",
    "stage_1_official_portfolio_mutation_not_performed",
    "stage_1_official_ledger_write_not_performed",
    "stage_1_execution_receipt_missing",
    "connectivity_pricing_is_not_accepted_activation_valuation",
    "vvsm_valuation_grade_not_pass",
    "vvsm_tradability_grade_not_pass",
    "vvsm_not_activation_ready",
    "lock_document_grade_not_pass",
    "lock_valuation_grade_not_pass",
    "lock_tradability_grade_not_pass",
    "lock_not_activation_ready",
    "stage_2:donor_add_direction_not_confirmed",
    "stage_2:separate_stage_2_activation_authorization_missing",
    "stage_2:stage_1_not_authorized",
}


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Package must be a JSON object")
    return payload


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def validate(payload: dict[str, Any], portfolio: Path, ledger: Path) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_eu_sync_blocked_activation_package_v1":
        blockers.append("unexpected schema_version")
    if payload.get("artifact_type") != "etf_eu_sync_blocked_activation_package":
        blockers.append("unexpected artifact_type")
    if payload.get("status") != "blocked_not_activation_ready" or payload.get("activation_ready") is not False:
        blockers.append("package must be blocked and not activation-ready")

    authorization = payload.get("authorization") if isinstance(payload.get("authorization"), dict) else {}
    if any(authorization.get(key) is not False for key in (
        "authorization_present",
        "stage_1_activation_authorized",
        "stage_2_activation_authorized",
        "send_or_execute_command_allowed",
    )):
        blockers.append("authorization boundary violated")

    lineage = payload.get("immutable_lineage") if isinstance(payload.get("immutable_lineage"), dict) else {}
    donor = lineage.get("donor_contract") if isinstance(lineage.get("donor_contract"), dict) else {}
    if donor.get("release_id") != "weekly_etf_shared_contract_v1_0_0":
        blockers.append("donor release mismatch")
    if donor.get("commit_sha") != "455201b4736dda41df07644d78b6797282a29fc7":
        blockers.append("donor commit mismatch")
    design = lineage.get("validated_eu_design") if isinstance(lineage.get("validated_eu_design"), dict) else {}
    if design.get("source_commit_sha") != "d33169fa513e22ac9197efe4fab9857ebaa6f85f":
        blockers.append("EU design source mismatch")
    source_artifacts = lineage.get("source_artifacts") if isinstance(lineage.get("source_artifacts"), dict) else {}
    expected_runs = {
        "allocator_report": (30410361517, "sha256:4ae7cdfb0335587a6eb564434b40ef914775913c76dd3a9bc7b2b21799875b36"),
        "replay_and_stage_2": (30410361535, "sha256:4ae31bafd076e49b9a67c20e35425603ef0aac4ec2b89bdcb22d50bfd6437598"),
        "shadow_cid_delivery": (30410951339, "sha256:65410e095372a95cab77adbddc727fdd7c28ae49d548db6fc8b3729a78d203c6"),
    }
    for key, (run_id, digest) in expected_runs.items():
        row = source_artifacts.get(key) if isinstance(source_artifacts.get(key), dict) else {}
        if row.get("workflow_run_id") != run_id or row.get("artifact_digest") != digest:
            blockers.append(f"source artifact mismatch: {key}")

    official = payload.get("official_pre_cutover_state") if isinstance(payload.get("official_pre_cutover_state"), dict) else {}
    if official.get("portfolio_state_sha256") != sha256(portfolio):
        blockers.append("official portfolio state digest mismatch")
    if official.get("trade_ledger_sha256") != sha256(ledger):
        blockers.append("official trade ledger digest mismatch")
    if official.get("portfolio_state_git_blob_sha") != "16b7f88efb80b711dabec1e4a44a95ae8810a663":
        blockers.append("official portfolio blob mismatch")
    if official.get("trade_ledger_git_blob_sha") != "30441db15d2f064dd05749f3a58765a00a12b4b6":
        blockers.append("official ledger blob mismatch")
    if official.get("preserved_unchanged") is not True:
        blockers.append("official state preservation missing")
    if official.get("position_count") != 3 or official.get("ledger_record_count") != 4:
        blockers.append("official state counts mismatch")
    if abs(num(official.get("nav_eur")) - 99756.76) > 0.001 or abs(num(official.get("cash_eur")) - 60439.44) > 0.001:
        blockers.append("official state values mismatch")

    stage_1 = payload.get("stage_1_shadow_target") if isinstance(payload.get("stage_1_shadow_target"), dict) else {}
    if stage_1.get("variant_id") != "staged_policy_driven_v1":
        blockers.append("Stage-1 variant mismatch")
    if stage_1.get("official_state_applied") is not False or stage_1.get("current_positions_retained") is not True:
        blockers.append("Stage-1 state boundary mismatch")
    if stage_1.get("simulated_position_count") != 5:
        blockers.append("Stage-1 position count mismatch")
    if abs(num(stage_1.get("simulated_projected_cash_eur")) - 35483.06) > 0.01:
        blockers.append("Stage-1 cash mismatch")
    if abs(num(stage_1.get("simulated_gross_turnover_pct_nav")) - 24.992241) > 0.001:
        blockers.append("Stage-1 turnover mismatch")
    additions = {str(row.get("ticker")): row for row in stage_1.get("simulated_additions") or [] if isinstance(row, dict)}
    if set(additions) != {"VVSM", "LOCK"}:
        blockers.append("Stage-1 additions mismatch")
    if (additions.get("VVSM") or {}).get("simulated_target_shares") != 156:
        blockers.append("VVSM share simulation mismatch")
    if (additions.get("LOCK") or {}).get("simulated_target_shares") != 995:
        blockers.append("LOCK share simulation mismatch")
    if any(row.get("state") != "shadow_simulation_only_not_authorized" for row in additions.values()):
        blockers.append("Stage-1 addition authority mismatch")

    ledger_plan = payload.get("proposed_ledger_blueprint") if isinstance(payload.get("proposed_ledger_blueprint"), dict) else {}
    if ledger_plan.get("write_performed") is not False or ledger_plan.get("executable_trade_intents") != []:
        blockers.append("ledger blueprint boundary violated")
    if ledger_plan.get("record_count") != 2:
        blockers.append("ledger blueprint record count mismatch")
    for row in ledger_plan.get("records") or []:
        if not isinstance(row, dict) or row.get("write_performed") is not False or row.get("authorization_present") is not False or row.get("executable_order") is not False:
            blockers.append("ledger blueprint row authority mismatch")

    stage_2 = payload.get("stage_2_readiness") if isinstance(payload.get("stage_2_readiness"), dict) else {}
    if stage_2.get("readiness") != "blocked" or stage_2.get("executable_trade_intents") != []:
        blockers.append("Stage-2 must remain blocked")
    gates = stage_2.get("entry_gate_results") if isinstance(stage_2.get("entry_gate_results"), dict) else {}
    if gates.get("donor_add_direction_pass") is not False or gates.get("euna_risk_budget_pass") is not True:
        blockers.append("Stage-2 authority or EUNA gate mismatch")

    delivery = payload.get("delivery_validation") if isinstance(payload.get("delivery_validation"), dict) else {}
    if delivery.get("transport_workflow_run_id") != 30410951339:
        blockers.append("delivery workflow mismatch")
    if delivery.get("sent_match_observed") is not True or delivery.get("inbox_match_observed") is not True:
        blockers.append("mailbox receipt mismatch")
    if delivery.get("attachment_count") != 4 or delivery.get("inline_image_count") != 1:
        blockers.append("delivery MIME inventory mismatch")
    if delivery.get("recipient_plaintext_stored") is not False or delivery.get("raw_mime_stored") is not False:
        blockers.append("delivery privacy boundary violated")

    actual_blockers = set(payload.get("blockers") or [])
    missing = sorted(REQUIRED_BLOCKERS - actual_blockers)
    if missing:
        blockers.append("required package blockers missing: " + ", ".join(missing))
    if payload.get("executable_trade_intents") != []:
        blockers.append("package executable intents must be empty")
    rollback = payload.get("rollback") if isinstance(payload.get("rollback"), dict) else {}
    if rollback.get("automatic_reverse_orders") is not False or rollback.get("automatic_ledger_rewrite") is not False:
        blockers.append("rollback automation boundary violated")
    if rollback.get("post_stage_1_official_state_exists") is not False:
        blockers.append("nonexistent post-Stage-1 state must not be asserted")

    for key in ("portfolio_mutation", "ledger_write", "funding_authority", "execution_authority", "activation_authority", "production_delivery_authority"):
        if payload.get(key) is not False:
            blockers.append(f"package authority {key} must be false")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("--portfolio", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    args = parser.parse_args()
    payload = load(args.package)
    blockers = validate(payload, args.portfolio, args.ledger)
    print(json.dumps({
        "artifact_type": "etf_eu_sync_blocked_activation_package_validation",
        "valid": not blockers,
        "blockers": blockers,
        "package_id": payload.get("package_id"),
        "status": payload.get("status"),
        "activation_ready": payload.get("activation_ready"),
        "package_blocker_count": len(payload.get("blockers") or []),
    }, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
