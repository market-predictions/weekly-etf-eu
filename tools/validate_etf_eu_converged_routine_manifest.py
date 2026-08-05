from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


CURRENT_AUTHORITY_KEYS = (
    "portfolio_mutation",
    "ledger_write",
    "funding_authority",
    "activation_authority",
    "execution_authority",
    "production_delivery_authority",
)
ALLOWED_STAGE_VALUES = {"blocked", "partially_activated", "activated"}


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


def stage_contract(state: dict[str, Any]) -> dict[str, Any]:
    stage = state.get("stage_1_decision") if isinstance(state.get("stage_1_decision"), dict) else {}
    value = str(stage.get("value") or "").strip()
    activated = sorted(
        {normalize_ticker(item) for item in stage.get("activated_tickers") or [] if normalize_ticker(item)}
    )
    monitored = sorted(
        {
            normalize_ticker(item)
            for item in stage.get("remaining_monitored_tickers") or []
            if normalize_ticker(item)
        }
    )
    return {
        "value": value,
        "activated_tickers": activated,
        "remaining_monitored_tickers": monitored,
        "activation_recorded": value in {"partially_activated", "activated"} and bool(activated),
        "executable_trade_intents": stage.get("executable_trade_intents"),
    }


def official_positions(state: dict[str, Any]) -> list[dict[str, Any]]:
    portfolio = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    if not positions:
        raise RuntimeError("Convergence state has no official portfolio positions")
    return positions


def position_identities(rows: list[dict[str, Any]]) -> set[tuple[str, str]]:
    return {
        (
            normalize_ticker(row.get("ticker") or row.get("exchange_ticker")),
            str(row.get("isin") or row.get("instrument_isin") or "").strip().upper(),
        )
        for row in rows
    }


def validate(manifest: dict[str, Any], state: dict[str, Any], state_path: Path) -> list[str]:
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
    if state.get("run_id") and manifest.get("run_id") != state.get("run_id"):
        blockers.append("manifest run id differs from convergence state")
    if manifest.get("report_date") != state.get("report_date"):
        blockers.append("manifest report date differs from convergence state")

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
        if role == "production_convergence_state":
            if path.resolve() != state_path.resolve():
                blockers.append("manifest convergence-state path differs from validation input")
            if record.get("sha256") != sha256_file(state_path):
                blockers.append("manifest convergence-state hash differs from validation input")

    state_positions = official_positions(state)
    state_portfolio = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    manifest_portfolio = manifest.get("portfolio_snapshot") if isinstance(manifest.get("portfolio_snapshot"), dict) else {}
    if manifest_portfolio.get("position_count") != len(state_positions):
        blockers.append("portfolio position count differs from convergence state")
    if position_identities([row for row in manifest_portfolio.get("positions") or [] if isinstance(row, dict)]) != position_identities(state_positions):
        blockers.append("portfolio position identity roster differs from convergence state")
    for field in ("nav_eur", "cash_eur", "invested_market_value_eur"):
        if manifest_portfolio.get(field) != state_portfolio.get(field):
            blockers.append(f"portfolio {field} differs from convergence state")
    if float(manifest_portfolio.get("cash_eur") or 0) < 0:
        blockers.append("cash value cannot be negative")
    if not manifest_portfolio.get("pricing_close_dates"):
        blockers.append("pricing close dates missing")
    if not manifest_portfolio.get("official_portfolio_state_sha256") or not manifest_portfolio.get("official_trade_ledger_sha256"):
        blockers.append("protected-state hashes missing")

    strategy = manifest.get("strategy_snapshot") if isinstance(manifest.get("strategy_snapshot"), dict) else {}
    expected_stage = stage_contract(state)
    if expected_stage["value"] not in ALLOWED_STAGE_VALUES:
        blockers.append(f"unsupported convergence-state Stage-1 decision: {expected_stage['value'] or 'missing'}")
    if strategy.get("current_promoted_exposure_count") != len(state.get("promoted_exposures") or []):
        blockers.append("current promoted exposure count differs from convergence state")
    state_strategy = state.get("strategy") if isinstance(state.get("strategy"), dict) else {}
    for field in ("mapped_promoted_exposure_count", "unmapped_promoted_exposure_count"):
        if strategy.get(field) != state_strategy.get(field):
            blockers.append(f"strategy {field} differs from convergence state")
    if strategy.get("stage_1_review_candidate_count") != len(state.get("stage_1_review_candidates") or []):
        blockers.append("Stage-1 review candidate count differs from convergence state")
    if strategy.get("stage_1_decision") != expected_stage["value"]:
        blockers.append("Stage-1 decision differs from convergence state")
    if sorted(strategy.get("activated_tickers") or []) != expected_stage["activated_tickers"]:
        blockers.append("activated ticker roster differs from convergence state")
    if sorted(strategy.get("remaining_monitored_tickers") or []) != expected_stage["remaining_monitored_tickers"]:
        blockers.append("monitored ticker roster differs from convergence state")
    if strategy.get("stage_1_activation_recorded") is not expected_stage["activation_recorded"]:
        blockers.append("activation provenance differs from convergence state")
    if strategy.get("current_activation_authority") is not False:
        blockers.append("current Stage-1 activation authority must be false")
    if strategy.get("executable_trade_intents") != [] or expected_stage["executable_trade_intents"] != []:
        blockers.append("executable trade intents must be empty")

    state_authority = state.get("authority") if isinstance(state.get("authority"), dict) else {}
    for key in CURRENT_AUTHORITY_KEYS:
        if state_authority.get(key) is not False:
            blockers.append(f"convergence-state current authority {key} must be false")
        if manifest.get(key) is not False:
            blockers.append(f"manifest current authority {key} must be false")

    if manifest.get("package_status") != "generated_pending_machine_and_visual_review":
        blockers.append("initial package status is unexpected")
    if manifest.get("ready_for_controlled_delivery") is not False:
        blockers.append("package cannot be delivery-ready before review")
    for key in ("delivery_authority", "smtp_transport_success", "independent_receipt_confirmed"):
        if manifest.get(key) is not False:
            blockers.append(f"manifest {key} must be false")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = load(args.manifest)
    state = load(args.state)
    blockers = validate(manifest, state, args.state)
    stage = stage_contract(state)
    result = {
        "artifact_type": "etf_eu_converged_routine_manifest_validation_v2",
        "valid": not blockers,
        "blockers": blockers,
        "run_id": manifest.get("run_id"),
        "report_date": manifest.get("report_date"),
        "report_suffix": manifest.get("report_suffix"),
        "attachment_count": len(manifest.get("files") or {}),
        "report_engine": manifest.get("report_engine"),
        "position_count": len(official_positions(state)),
        "stage_1_decision": stage["value"],
        "activated_tickers": stage["activated_tickers"],
        "remaining_monitored_tickers": stage["remaining_monitored_tickers"],
        "current_activation_authority": False,
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
