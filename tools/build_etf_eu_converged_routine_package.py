from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
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


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def copy_file(source: Path, target: Path) -> dict[str, Any]:
    if not source.is_file() or source.stat().st_size <= 0:
        raise RuntimeError(f"Source package file missing or empty: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return {
        "path": str(target),
        "sha256": sha256_file(target),
        "size_bytes": target.stat().st_size,
    }


def normalize_ticker(value: Any) -> str:
    ticker = str(value or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def build(
    client_manifest_path: Path,
    state_path: Path,
    pricing_path: Path,
    macro_path: Path,
    output_dir: Path,
    manifest_dir: Path,
    run_id: str,
    report_date: str,
    suffix: str,
    source_sha: str,
    donor_commit: str,
) -> Path:
    client = load(client_manifest_path)
    state = load(state_path)
    pricing = load(pricing_path)
    macro = load(macro_path)
    if client.get("schema_version") != "etf_eu_production_converged_report_manifest_v1":
        raise RuntimeError("Unexpected client report manifest schema")
    if state.get("schema_version") != "etf_eu_production_convergence_state_v1":
        raise RuntimeError("Unexpected convergence state schema")
    if state.get("report_date") != report_date:
        raise RuntimeError("Convergence state report date differs from routine request")

    stage = state.get("stage_1_decision") if isinstance(state.get("stage_1_decision"), dict) else {}
    executable_intents = stage.get("executable_trade_intents")
    if executable_intents != []:
        raise RuntimeError("Convergence state contains executable trade intents")

    output_dir.mkdir(parents=True, exist_ok=True)
    languages = client.get("languages") if isinstance(client.get("languages"), dict) else {}
    source_nl = languages.get("nl") if isinstance(languages.get("nl"), dict) else {}
    source_en = languages.get("en") if isinstance(languages.get("en"), dict) else {}
    files = {
        "nl_html": copy_file(Path(str(source_nl.get("html") or "")), output_dir / f"weekly_etf_eu_review_nl_{suffix}.html"),
        "nl_pdf": copy_file(Path(str(source_nl.get("pdf") or "")), output_dir / f"weekly_etf_eu_review_nl_{suffix}.pdf"),
        "en_html": copy_file(Path(str(source_en.get("html") or "")), output_dir / f"weekly_etf_eu_review_{suffix}.html"),
        "en_pdf": copy_file(Path(str(source_en.get("pdf") or "")), output_dir / f"weekly_etf_eu_review_{suffix}.pdf"),
    }

    portfolio = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    funded_tickers = sorted(
        {
            normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
            for row in positions
            if normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
        }
    )
    activation = portfolio.get("last_model_capital_activation") or state.get("model_capital_activation") or {}
    activated_tickers = sorted(
        {normalize_ticker(value) for value in stage.get("activated_tickers") or [] if normalize_ticker(value)}
    )
    monitored_tickers = sorted(
        {
            normalize_ticker(value)
            for value in stage.get("remaining_monitored_tickers") or []
            if normalize_ticker(value)
        }
    )

    manifest = {
        "schema_version": "etf_eu_routine_run_manifest_v3_converged",
        "artifact_type": "etf_eu_routine_run_manifest",
        "generated_at_utc": utc_now(),
        "run_id": run_id,
        "report_date": report_date,
        "report_suffix": suffix,
        "source_repository": "market-predictions/weekly-etf-eu",
        "source_commit_sha": source_sha,
        "donor_repository": "market-predictions/weekly-etf",
        "donor_commit_sha": donor_commit,
        "donor_report_date": state.get("donor", {}).get("report_date") or state.get("donor", {}).get("source_report_date"),
        "report_engine": "production_convergence_v1",
        "client_renderer_mode": client.get("client_renderer_mode"),
        "report_section_count": 19,
        "languages": ["nl", "en"],
        "dutch_primary": True,
        "english_companion": True,
        "expected_attachment_count": 4,
        "files": files,
        "state_artifacts": {
            "production_convergence_state": {
                "path": str(state_path),
                "sha256": sha256_file(state_path),
            },
            "pricing_artifact": {
                "path": str(pricing_path),
                "sha256": sha256_file(pricing_path),
                "line_count": pricing.get("line_count"),
                "priced_line_count": pricing.get("priced_line_count"),
                "failed_line_count": pricing.get("failed_line_count"),
            },
            "macro_policy_pack": {
                "path": str(macro_path),
                "sha256": sha256_file(macro_path),
                "report_date": macro.get("report_date"),
            },
            "client_report_manifest": {
                "path": str(client_manifest_path),
                "sha256": sha256_file(client_manifest_path),
            },
        },
        "portfolio_snapshot": {
            "starting_capital_eur": portfolio.get("starting_capital_eur"),
            "nav_eur": portfolio.get("nav_eur"),
            "cash_eur": portfolio.get("cash_eur"),
            "invested_market_value_eur": portfolio.get("invested_market_value_eur"),
            "position_count": portfolio.get("position_count"),
            "funded_tickers": funded_tickers,
            "positions": positions,
            "valuation_role": portfolio.get("valuation_role"),
            "pricing_close_dates": portfolio.get("pricing_close_dates"),
            "official_portfolio_state_sha256": portfolio.get("portfolio_state_sha256"),
            "official_trade_ledger_sha256": portfolio.get("trade_ledger_sha256"),
            "model_portfolio_only": portfolio.get("model_portfolio_only"),
            "real_broker_execution": portfolio.get("real_broker_execution"),
            "activation_id": activation.get("activation_id") if isinstance(activation, dict) else None,
        },
        "strategy_snapshot": {
            "current_promoted_exposure_count": len(state.get("promoted_exposures") or []),
            "mapped_promoted_exposure_count": state.get("strategy", {}).get("mapped_promoted_exposure_count"),
            "unmapped_promoted_exposure_count": state.get("strategy", {}).get("unmapped_promoted_exposure_count"),
            "stage_1_review_candidate_count": len(state.get("stage_1_review_candidates") or []),
            "stage_1_decision": stage.get("value"),
            "stage_1_activation_authorized": stage.get("stage_1_activation_authorized"),
            "activated_tickers": activated_tickers,
            "remaining_monitored_tickers": monitored_tickers,
            "executable_trade_intents": executable_intents,
            "model_portfolio_only": portfolio.get("model_portfolio_only"),
            "real_broker_execution": portfolio.get("real_broker_execution"),
            "activation_id": activation.get("activation_id") if isinstance(activation, dict) else None,
        },
        "package_status": "generated_pending_machine_and_visual_review",
        "ready_for_controlled_delivery": False,
        "delivery_authority": False,
        "smtp_transport_success": False,
        "independent_receipt_confirmed": False,
        "portfolio_mutation": False,
        "ledger_write": False,
        "execution_authority": False,
    }
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / f"etf_eu_routine_run_manifest_{report_date}_{run_id}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(manifest_path)
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-manifest", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--pricing", type=Path, required=True)
    parser.add_argument("--macro", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("output/fresh_generation"))
    parser.add_argument("--manifest-dir", type=Path, default=Path("output/run_manifests"))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--suffix", required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--donor-commit", required=True)
    args = parser.parse_args()
    build(
        client_manifest_path=args.client_manifest,
        state_path=args.state,
        pricing_path=args.pricing,
        macro_path=args.macro,
        output_dir=args.output_dir,
        manifest_dir=args.manifest_dir,
        run_id=args.run_id,
        report_date=args.report_date,
        suffix=args.suffix,
        source_sha=args.source_sha,
        donor_commit=args.donor_commit,
    )


if __name__ == "__main__":
    main()
