from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str, cwd: Path = ROOT, capture: bool = False) -> str:
    command = [sys.executable, *args]
    print("RUN", " ".join(str(item) for item in command), flush=True)
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        env=os.environ.copy(),
        text=True,
        check=True,
        capture_output=capture,
    )
    if capture:
        if completed.stdout:
            print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, end="", file=sys.stderr)
        return completed.stdout
    return ""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def first_matching(directory: Path, pattern: str) -> Path:
    matches = sorted(directory.glob(pattern))
    if not matches:
        raise RuntimeError(f"No file matched {pattern} in {directory}")
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--donor-dir", type=Path, required=True)
    parser.add_argument("--report-date", default="2026-08-03")
    parser.add_argument("--report-suffix", default="260803_01")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--donor-commit", required=True)
    args = parser.parse_args()

    donor = args.donor_dir.resolve()
    if not donor.exists():
        raise RuntimeError(f"Donor checkout missing: {donor}")

    os.environ["WP11_RUN_ID"] = args.run_id
    os.environ["REPORT_DATE"] = args.report_date
    os.environ["REQUESTED_CLOSE_DATE"] = args.report_date
    os.environ["ETF_PRICING_RUN_ID"] = args.run_id
    os.environ["MRKT_RPRTS_RUN_ID"] = args.run_id

    output = ROOT / "output"
    preview = output / "routine_preview"
    pricing_dir = output / "pricing"
    macro_dir = output / "macro"
    sync_dir = preview / "sync"
    source_dir = preview / "source_report"
    client_dir = preview / "client_report"
    fresh_dir = output / "fresh_generation"
    manifest_dir = output / "run_manifests"
    for path in (preview, pricing_dir, macro_dir, sync_dir, source_dir, client_dir, fresh_dir, manifest_dir):
        path.mkdir(parents=True, exist_ok=True)

    portfolio_path = output / "etf_eu_portfolio_state.json"
    ledger_path = output / "etf_eu_trade_ledger.csv"
    protected_before = {
        "portfolio": sha256(portfolio_path),
        "ledger": sha256(ledger_path),
    }
    (preview / "protected_state_before.json").write_text(
        json.dumps(protected_before, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    current_macro_source = macro_dir / f"etf_eu_current_macro_source_{args.run_id}.json"
    macro_artifact = macro_dir / f"etf_eu_macro_policy_{args.run_id}.json"
    run(
        "runtime/build_etf_eu_current_macro_source.py",
        "--donor",
        str(donor / "output/macro/latest.json"),
        "--report-date",
        args.report_date,
        "--output",
        str(current_macro_source),
    )
    run(
        "runtime/adapt_weekly_etf_macro_for_eu.py",
        "--source",
        str(current_macro_source),
        "--report-date",
        args.report_date,
        "--run-id",
        args.run_id,
        "--output",
        str(macro_artifact),
    )
    run("tools/validate_etf_eu_macro_adapter.py", str(macro_artifact))

    pricing_artifact = pricing_dir / f"ucits_close_price_validation_basket_results_{args.run_id}.json"
    pricing_qualification = pricing_dir / f"ucits_price_provider_qualification_{args.run_id}.json"
    run(
        "pricing/build_current_session_close_results.py",
        "--basket",
        "config/ucits_close_price_validation_basket.yml",
        "--report-date",
        args.report_date,
        "--run-id",
        args.run_id,
        "--output",
        str(pricing_artifact),
        "--qualification-output",
        str(pricing_qualification),
    )

    valuation_overlay = preview / f"etf_eu_routine_valuation_overlay_{args.run_id}.json"
    run(
        "runtime/build_etf_eu_routine_valuation_overlay.py",
        "--portfolio-state",
        str(portfolio_path),
        "--trade-ledger",
        str(ledger_path),
        "--pricing-artifact",
        str(pricing_artifact),
        "--report-date",
        args.report_date,
        "--run-id",
        args.run_id,
        "--output",
        str(valuation_overlay),
    )
    run(
        "runtime/update_etf_eu_valuation_history_from_overlay.py",
        "--history",
        str(output / "etf_eu_valuation_history.csv"),
        "--overlay",
        str(valuation_overlay),
        "--source-report",
        f"weekly_etf_eu_review_nl_{args.report_suffix}.html",
    )

    run(
        "runtime/build_shared_strategy_state.py",
        "--output",
        str(sync_dir / "etf_shared_strategy_state.json"),
        cwd=donor,
    )
    run(
        "runtime/build_shared_portfolio_target.py",
        "--shared-strategy-state",
        str(sync_dir / "etf_shared_strategy_state.json"),
        "--output",
        str(sync_dir / "etf_shared_portfolio_target.json"),
        cwd=donor,
    )
    run("tools/validate_shared_strategy_state.py", str(sync_dir / "etf_shared_strategy_state.json"), cwd=donor)
    run("tools/validate_shared_portfolio_target.py", str(sync_dir / "etf_shared_portfolio_target.json"), cwd=donor)

    for registry in (
        "config/ucits_symbol_registry_sync_additions.yml",
        "config/ucits_symbol_registry_sync_additions_wp09.yml",
        "config/ucits_symbol_registry_sync_additions_wp10.yml",
    ):
        run("tools/validate_etf_eu_sync_registry_additions.py", registry)
    merged_registry = sync_dir / "ucits_symbol_registry_sync_merged.yml"
    run("runtime/merge_etf_eu_sync_registries.py", "--output", str(merged_registry))
    sync_shadow = sync_dir / "etf_eu_strategy_sync_shadow.json"
    run(
        "runtime/build_etf_eu_strategy_sync_shadow.py",
        "--shared-strategy-state",
        str(sync_dir / "etf_shared_strategy_state.json"),
        "--shared-portfolio-target",
        str(sync_dir / "etf_shared_portfolio_target.json"),
        "--portfolio-state",
        str(valuation_overlay),
        "--registry",
        str(merged_registry),
        "--output",
        str(sync_shadow),
    )
    run("runtime/normalize_etf_eu_alignment_contract.py", str(sync_shadow))
    run("tools/validate_etf_eu_strategy_sync_shadow.py", str(sync_shadow))

    transition = sync_dir / "etf_eu_transition_evidence.json"
    run("pricing/build_etf_eu_transition_evidence.py", "--report-date", args.report_date, "--output", str(transition))
    run(
        "pricing/apply_etf_eu_transition_evidence_cache.py",
        str(transition),
        "--cache",
        "config/etf_eu_transition_evidence_cache_20260724.yml",
    )
    allocator_v2 = sync_dir / "etf_eu_target_allocator_shadow_v2.json"
    run(
        "runtime/build_etf_eu_target_allocator_shadow_v2.py",
        "--sync-shadow",
        str(sync_shadow),
        "--transition-evidence",
        str(transition),
        "--output",
        str(allocator_v2),
    )
    run("tools/validate_etf_eu_target_allocator_shadow_v2.py", str(allocator_v2))
    overlap = sync_dir / "etf_eu_incumbent_overlap_review.json"
    run("runtime/build_etf_eu_incumbent_overlap_review.py", "--output", str(overlap))
    run("tools/validate_etf_eu_incumbent_overlap_review.py", str(overlap))
    allocator = sync_dir / "etf_eu_target_allocator_shadow.json"
    run(
        "runtime/build_etf_eu_target_allocator_shadow_v3_policy_gate.py",
        "--base-allocator",
        str(allocator_v2),
        "--sync-shadow",
        str(sync_shadow),
        "--transition-evidence",
        str(transition),
        "--overlap-review",
        str(overlap),
        "--policy",
        "config/etf_eu_transition_policy_v1.yml",
        "--output",
        str(allocator),
    )
    run("tools/validate_etf_eu_target_allocator_shadow_v3.py", str(allocator))

    run("runtime/render_etf_eu_sister_report_shadow.py", "--sync-shadow", str(sync_shadow), "--output-dir", str(source_dir))
    source_manifest = first_matching(source_dir, "etf_eu_sister_report_shadow_manifest_*.json")
    run("runtime/add_etf_eu_portfolio_alignment_surface.py", str(source_manifest), "--sync-shadow", str(sync_shadow))
    run("runtime/add_etf_eu_target_allocator_surface.py", str(source_manifest), "--allocator", str(allocator))
    run("runtime/add_etf_eu_incumbent_overlap_surface.py", str(source_manifest), "--review", str(overlap))
    run("runtime/polish_etf_eu_sister_report_client_surface.py", str(source_manifest))
    run("runtime/finalize_etf_eu_sister_report_nl_language.py", str(source_manifest))
    run("runtime/reconcile_etf_eu_report_with_policy_allocator.py", str(source_manifest), "--allocator", str(allocator), "--sync-shadow", str(sync_shadow))
    run("runtime/reconcile_etf_eu_promoted_candidate_visibility.py", str(source_manifest), "--allocator", str(allocator), "--sync-shadow", str(sync_shadow))
    run("runtime/finalize_etf_eu_promoted_candidate_contract.py", str(source_manifest), "--allocator", str(allocator), "--sync-shadow", str(sync_shadow))
    run("runtime/finalize_etf_eu_policy_reconciliation_surface.py", str(source_manifest))
    run("runtime/compact_etf_eu_policy_transition_surface.py", str(source_manifest))
    run("runtime/fix_etf_eu_sister_report_layout.py", str(source_manifest))
    run("runtime/finalize_etf_eu_policy_report_pagination.py", str(source_manifest))
    run("runtime/finalize_etf_eu_report_output_contract.py", str(source_manifest), "--allocator", str(allocator), "--sync-shadow", str(sync_shadow))
    run("runtime/finalize_etf_eu_wp10_source_language.py", str(source_manifest))
    run("runtime/fix_etf_eu_sister_report_layout.py", str(source_manifest))
    run("runtime/finalize_etf_eu_policy_report_pagination.py", str(source_manifest))
    run("tools/run_etf_eu_allocator_report_validation_bundle.py", str(source_manifest), "--output", str(source_dir / "source_report_validation_bundle.json"))

    state_path = preview / f"etf_eu_production_convergence_state_{args.run_id}.json"
    run(
        "runtime/build_etf_eu_production_convergence_state.py",
        "--sync-shadow",
        str(sync_shadow),
        "--allocator",
        str(allocator),
        "--wp09-receipt",
        "control/evidence/etf_eu_wp09_fresh_cutover_evidence_30501245612_1.json",
        "--portfolio-state",
        str(portfolio_path),
        "--trade-ledger",
        str(ledger_path),
        "--donor-commit",
        args.donor_commit,
        "--run-id",
        args.run_id,
        "--output",
        str(state_path),
    )
    run("runtime/apply_etf_eu_routine_valuation_to_convergence_state.py", str(state_path), "--overlay", str(valuation_overlay), "--report-date", args.report_date)
    state_validation = preview / f"etf_eu_production_convergence_state_validation_{args.run_id}.json"
    validation_text = run("tools/validate_etf_eu_production_convergence_state.py", str(state_path), capture=True)
    state_validation.write_text(validation_text, encoding="utf-8")

    run("runtime/prepare_etf_eu_wp10_client_executive_surface.py", str(source_manifest), "--state", str(state_path))
    run("runtime/apply_etf_eu_routine_valuation_to_client_report.py", str(source_manifest), "--state", str(state_path))
    run("runtime/add_etf_eu_current_close_monitor.py", str(source_manifest), "--pricing", str(pricing_artifact), "--report-date", args.report_date)
    run("runtime/promote_etf_eu_sister_report_to_production_candidate.py", str(source_manifest), "--state", str(state_path), "--output-dir", str(client_dir))
    client_manifest = first_matching(client_dir, "etf_eu_production_converged_report_manifest_*.json")
    run(
        "tools/validate_etf_eu_production_converged_report.py",
        str(client_manifest),
        "--state",
        str(state_path),
        "--output",
        str(preview / f"etf_eu_production_converged_report_validation_{args.run_id}.json"),
    )

    run(
        "tools/build_etf_eu_converged_routine_package.py",
        "--client-manifest",
        str(client_manifest),
        "--state",
        str(state_path),
        "--pricing",
        str(pricing_artifact),
        "--macro",
        str(macro_artifact),
        "--output-dir",
        str(fresh_dir),
        "--manifest-dir",
        str(manifest_dir),
        "--run-id",
        args.run_id,
        "--report-date",
        args.report_date,
        "--suffix",
        args.report_suffix,
        "--source-sha",
        args.source_sha,
        "--donor-commit",
        args.donor_commit,
    )
    routine_manifest = manifest_dir / f"etf_eu_routine_run_manifest_{args.report_date}_{args.run_id}.json"
    run(
        "tools/validate_etf_eu_converged_routine_manifest.py",
        str(routine_manifest),
        "--output",
        str(preview / f"etf_eu_converged_routine_manifest_validation_{args.run_id}.json"),
    )
    page_dir = preview / f"pdf_pages_{args.run_id}"
    run("tools/render_etf_eu_routine_pdf_review_pages.py", "--manifest", str(routine_manifest), "--output-dir", str(page_dir))

    protected_after = {"portfolio": sha256(portfolio_path), "ledger": sha256(ledger_path)}
    (preview / "protected_state_after.json").write_text(
        json.dumps(protected_after, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if protected_after != protected_before:
        raise RuntimeError(f"Protected state changed: before={protected_before} after={protected_after}")
    state = load_json(state_path)
    manifest = load_json(routine_manifest)
    if state.get("stage_1_decision", {}).get("executable_trade_intents") != []:
        raise RuntimeError("Expanded report unexpectedly contains executable trade intents")
    if manifest.get("delivery_authority") is not False:
        raise RuntimeError("Expanded report unexpectedly escalated delivery authority")

    pricing = load_json(pricing_artifact)
    summary = {
        "schema_version": "etf_eu_aug3_expanded_report_run_summary_v1",
        "run_id": args.run_id,
        "report_date": args.report_date,
        "report_suffix": args.report_suffix,
        "source_sha": args.source_sha,
        "donor_commit": args.donor_commit,
        "pricing_artifact": str(pricing_artifact),
        "pricing_qualification": str(pricing_qualification),
        "valuation_overlay": str(valuation_overlay),
        "macro_artifact": str(macro_artifact),
        "state": str(state_path),
        "routine_manifest": str(routine_manifest),
        "priced_line_count": pricing.get("priced_line_count"),
        "line_count": pricing.get("line_count"),
        "funded_position_count": state.get("position_count") or len(state.get("positions", [])),
        "protected_state_unchanged": True,
        "portfolio_mutation": False,
        "delivery_authority": False,
    }
    summary_path = preview / f"etf_eu_aug3_expanded_report_run_summary_{args.run_id}.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "ETF_EU_AUG3_EXPANDED_REPORT_OK"
        f" | run_id={args.run_id}"
        f" | priced={summary['priced_line_count']}/{summary['line_count']}"
        f" | manifest={routine_manifest}"
        f" | protected_state_unchanged=true"
        f" | delivery=false"
    )


if __name__ == "__main__":
    main()
