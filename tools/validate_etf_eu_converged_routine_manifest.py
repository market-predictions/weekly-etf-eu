from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate(manifest: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if manifest.get("schema_version") != "etf_eu_routine_run_manifest_v3_converged":
        blockers.append("unexpected manifest schema")
    if manifest.get("report_engine") != "production_convergence_v1":
        blockers.append("unexpected report engine")
    if manifest.get("report_section_count") != 19:
        blockers.append("report section count must be 19")
    if manifest.get("languages") != ["nl", "en"]:
        blockers.append("language contract must be Dutch primary plus English companion")
    if manifest.get("expected_attachment_count") != 4:
        blockers.append("expected attachment count must be four")
    if not manifest.get("run_id") or not manifest.get("report_date") or not manifest.get("report_suffix"):
        blockers.append("run identity is incomplete")
    if not manifest.get("source_commit_sha") or not manifest.get("donor_commit_sha"):
        blockers.append("source SHA or donor commit missing")

    files = manifest.get("files") if isinstance(manifest.get("files"), dict) else {}
    if set(files) != {"nl_html", "nl_pdf", "en_html", "en_pdf"}:
        blockers.append("exact four-file package contract is incomplete")
    seen_paths: set[str] = set()
    for role, record in files.items():
        if not isinstance(record, dict):
            blockers.append(f"invalid file record: {role}")
            continue
        path = Path(str(record.get("path") or ""))
        if not path.is_file() or path.stat().st_size <= 0:
            blockers.append(f"missing or empty package file: {role}")
            continue
        if str(path) in seen_paths:
            blockers.append(f"duplicate package file path: {path}")
        seen_paths.add(str(path))
        if record.get("sha256") != sha256_file(path):
            blockers.append(f"file hash mismatch: {role}")
        if int(record.get("size_bytes") or 0) != path.stat().st_size:
            blockers.append(f"file size mismatch: {role}")

    state_artifacts = manifest.get("state_artifacts") if isinstance(manifest.get("state_artifacts"), dict) else {}
    required_state_artifacts = (
        "production_convergence_state",
        "portfolio_policy_validation",
        "pricing_artifact",
        "macro_policy_pack",
        "client_report_manifest",
    )
    for role in required_state_artifacts:
        record = state_artifacts.get(role)
        if not isinstance(record, dict):
            blockers.append(f"state artifact missing: {role}")
            continue
        path = Path(str(record.get("path") or ""))
        if not path.is_file():
            blockers.append(f"state artifact file missing: {role}")
            continue
        if record.get("sha256") != sha256_file(path):
            blockers.append(f"state artifact hash mismatch: {role}")

    policy_record = state_artifacts.get("portfolio_policy_validation") if isinstance(state_artifacts.get("portfolio_policy_validation"), dict) else {}
    policy_path = Path(str(policy_record.get("path") or ""))
    policy_validation: dict[str, Any] = {}
    if policy_path.is_file():
        try:
            policy_validation = load(policy_path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, RuntimeError):
            blockers.append("portfolio policy validation is not parseable")
    if policy_validation:
        if policy_validation.get("schema_version") != "etf_eu_portfolio_policy_validation_v2":
            blockers.append("unexpected portfolio policy validation schema")
        if policy_validation.get("verdict") != "PASS" or policy_validation.get("valid") is not True:
            blockers.append("portfolio policy validation did not PASS")
        if policy_validation.get("blockers"):
            blockers.append("portfolio policy validation contains blockers")
        if policy_record.get("policy_id") != policy_validation.get("policy_id"):
            blockers.append("portfolio policy identity mismatch")
        if policy_record.get("policy_sha256") != policy_validation.get("policy_sha256"):
            blockers.append("portfolio policy hash mismatch")
        state_record = state_artifacts.get("production_convergence_state") if isinstance(state_artifacts.get("production_convergence_state"), dict) else {}
        if policy_validation.get("state_sha256") != state_record.get("sha256"):
            blockers.append("portfolio policy verdict is not bound to convergence state")

    portfolio = manifest.get("portfolio_snapshot") if isinstance(manifest.get("portfolio_snapshot"), dict) else {}
    funded_tickers = sorted(str(value) for value in portfolio.get("funded_tickers") or [])
    policy_funded = sorted(str(value) for value in policy_validation.get("portfolio", {}).get("funded_tickers") or []) if policy_validation else []
    if policy_funded and funded_tickers != policy_funded:
        blockers.append("manifest funded ticker roster differs from policy validation")
    if int(portfolio.get("position_count") or 0) != len(funded_tickers):
        blockers.append("portfolio position count differs from funded ticker roster")
    if policy_funded and int(portfolio.get("position_count") or 0) != int(policy_validation.get("portfolio", {}).get("position_count") or 0):
        blockers.append("portfolio position count differs from policy validation")
    if float(portfolio.get("cash_eur") or 0) <= 0:
        blockers.append("cash value missing")
    if portfolio.get("portfolio_policy_verdict") != "PASS":
        blockers.append("portfolio snapshot is not policy-approved")
    if portfolio.get("portfolio_policy_id") != policy_validation.get("policy_id") if policy_validation else True:
        blockers.append("portfolio snapshot policy identity mismatch")
    if not portfolio.get("pricing_close_dates"):
        blockers.append("pricing close dates missing")
    if not portfolio.get("official_portfolio_state_sha256") or not portfolio.get("official_trade_ledger_sha256"):
        blockers.append("protected-state hashes missing")
    if portfolio.get("model_portfolio_only") is not True or portfolio.get("real_broker_execution") is not False:
        blockers.append("model-only portfolio boundary invalid")

    strategy = manifest.get("strategy_snapshot") if isinstance(manifest.get("strategy_snapshot"), dict) else {}
    if strategy.get("current_promoted_exposure_count") != 6:
        blockers.append("current promoted exposure count must be six")
    if strategy.get("mapped_promoted_exposure_count") != 6:
        blockers.append("mapped promoted exposure count must be six")
    if strategy.get("unmapped_promoted_exposure_count") != 0:
        blockers.append("unmapped promoted exposure count must be zero")
    if strategy.get("stage_1_review_candidate_count") != 2:
        blockers.append("Stage-1 review candidate count must be two")
    stage_value = strategy.get("stage_1_decision")
    if stage_value not in {"blocked", "partially_activated"}:
        blockers.append("unsupported Stage-1 decision state")
    if stage_value == "blocked":
        if strategy.get("stage_1_activation_authorized") is not False:
            blockers.append("blocked Stage-1 state cannot have activation authority")
        if strategy.get("activated_tickers") not in ([], None):
            blockers.append("blocked Stage-1 state cannot contain activated tickers")
    if stage_value == "partially_activated":
        if strategy.get("stage_1_activation_authorized") is not True:
            blockers.append("partially activated state must record activation authority")
        if sorted(strategy.get("activated_tickers") or []) != ["L0CK"]:
            blockers.append("partially activated state must bind L0CK activation")
        if sorted(strategy.get("remaining_monitored_tickers") or []) != ["VVSM"]:
            blockers.append("partially activated state must retain VVSM as monitored")
    if strategy.get("executable_trade_intents") != []:
        blockers.append("executable trade intents must be empty")
    if strategy.get("model_portfolio_only") is not True or strategy.get("real_broker_execution") is not False:
        blockers.append("strategy model-only boundary invalid")

    if manifest.get("package_status") != "generated_pending_machine_and_visual_review":
        blockers.append("initial package status is unexpected")
    if manifest.get("ready_for_controlled_delivery") is not False:
        blockers.append("package cannot be delivery-ready before review")
    for key in ("delivery_authority", "smtp_transport_success", "independent_receipt_confirmed", "portfolio_mutation", "ledger_write", "execution_authority"):
        if manifest.get(key) is not False:
            blockers.append(f"manifest {key} must be false")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = load(args.manifest)
    blockers = validate(manifest)
    policy_record = (manifest.get("state_artifacts") or {}).get("portfolio_policy_validation") or {}
    result = {
        "artifact_type": "etf_eu_converged_routine_manifest_validation",
        "valid": not blockers,
        "blockers": blockers,
        "run_id": manifest.get("run_id"),
        "report_date": manifest.get("report_date"),
        "report_suffix": manifest.get("report_suffix"),
        "attachment_count": len(manifest.get("files") or {}),
        "report_engine": manifest.get("report_engine"),
        "portfolio_policy_id": policy_record.get("policy_id"),
        "portfolio_policy_verdict": policy_record.get("verdict"),
    }
    text = json.dumps(result, indent=2, ensure_ascii=False)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
