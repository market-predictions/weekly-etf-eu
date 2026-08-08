from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


CORE_FUNDED = {"VWCE", "EUNA", "SXR8"}
ALLOWED_ACTIVATED = {"L0CK"}


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


def normalize_ticker(value: Any) -> str:
    ticker = str(value or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


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
    for role in ("production_convergence_state", "pricing_artifact", "macro_policy_pack", "client_report_manifest"):
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

    portfolio = manifest.get("portfolio_snapshot") if isinstance(manifest.get("portfolio_snapshot"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    funded = {
        normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
        for row in positions
        if normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
    }
    if not CORE_FUNDED.issubset(funded):
        blockers.append(f"core funded tickers are incomplete: {sorted(funded)}")
    extras = funded - CORE_FUNDED
    if not extras.issubset(ALLOWED_ACTIVATED):
        blockers.append(f"unexpected activated funded tickers: {sorted(extras)}")
    if portfolio.get("position_count") != len(positions):
        blockers.append("portfolio position count does not match positions")
    if len(positions) not in {3, 4}:
        blockers.append("portfolio position count must be three or four")
    declared_funded = {
        normalize_ticker(value)
        for value in portfolio.get("funded_tickers") or []
        if normalize_ticker(value)
    }
    if declared_funded != funded:
        blockers.append("portfolio funded ticker summary does not match positions")
    if float(portfolio.get("cash_eur") or 0) <= 0:
        blockers.append("cash value missing")
    if not portfolio.get("pricing_close_dates"):
        blockers.append("pricing close dates missing")
    if not portfolio.get("official_portfolio_state_sha256") or not portfolio.get("official_trade_ledger_sha256"):
        blockers.append("protected-state hashes missing")

    activated_state = funded == CORE_FUNDED | ALLOWED_ACTIVATED
    if activated_state:
        if portfolio.get("model_portfolio_only") is not True:
            blockers.append("activated portfolio must remain model-only")
        if portfolio.get("real_broker_execution") is not False:
            blockers.append("activated portfolio must not imply broker execution")
        if not portfolio.get("activation_id"):
            blockers.append("activated portfolio provenance is missing")

    strategy = manifest.get("strategy_snapshot") if isinstance(manifest.get("strategy_snapshot"), dict) else {}
    if strategy.get("current_promoted_exposure_count") != 6:
        blockers.append("current promoted exposure count must be six")
    if strategy.get("mapped_promoted_exposure_count") != 6:
        blockers.append("mapped promoted exposure count must be six")
    if strategy.get("unmapped_promoted_exposure_count") != 0:
        blockers.append("unmapped promoted exposure count must be zero")
    if strategy.get("stage_1_review_candidate_count") != 2:
        blockers.append("Stage-1 review candidate count must be two")

    if activated_state:
        if strategy.get("stage_1_decision") != "partially_activated":
            blockers.append("activated Stage-1 decision must be partially_activated")
        if strategy.get("stage_1_activation_authorized") is not True:
            blockers.append("historical Stage-1 activation authority must be recorded")
        if set(strategy.get("activated_tickers") or []) != {"L0CK"}:
            blockers.append("activated Stage-1 ticker set must contain L0CK only")
        if set(strategy.get("remaining_monitored_tickers") or []) != {"VVSM"}:
            blockers.append("remaining monitored Stage-1 ticker must be VVSM")
        if strategy.get("model_portfolio_only") is not True:
            blockers.append("activated strategy snapshot must remain model-only")
        if strategy.get("real_broker_execution") is not False:
            blockers.append("activated strategy snapshot must not imply broker execution")
        if not strategy.get("activation_id"):
            blockers.append("activated strategy provenance is missing")
    else:
        if strategy.get("stage_1_decision") != "blocked":
            blockers.append("pre-activation Stage-1 decision must remain blocked")
        if strategy.get("stage_1_activation_authorized") is not False:
            blockers.append("pre-activation Stage-1 authority must be false")
        if strategy.get("activated_tickers") not in ([], None):
            blockers.append("pre-activation Stage-1 activated tickers must be empty")

    if strategy.get("executable_trade_intents") != []:
        blockers.append("executable trade intents must be empty")

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
    result = {
        "artifact_type": "etf_eu_converged_routine_manifest_validation",
        "valid": not blockers,
        "blockers": blockers,
        "run_id": manifest.get("run_id"),
        "report_date": manifest.get("report_date"),
        "report_suffix": manifest.get("report_suffix"),
        "attachment_count": len(manifest.get("files") or {}),
        "report_engine": manifest.get("report_engine"),
        "funded_position_count": len(manifest.get("portfolio_snapshot", {}).get("positions") or []),
        "stage_1_decision": manifest.get("strategy_snapshot", {}).get("stage_1_decision"),
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
