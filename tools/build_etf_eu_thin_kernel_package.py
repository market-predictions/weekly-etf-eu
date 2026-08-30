from __future__ import annotations

import argparse
import hashlib
import json
from argparse import Namespace
from pathlib import Path
from typing import Any

from runtime.apply_etf_eu_current_reunderwriting import (
    apply_cash_reunderwriting_to_contract_state,
    apply_current_reunderwriting,
)
from runtime.apply_etf_eu_donor_parity_contract import apply_contract, write_recommendation_scorecard
from runtime.build_etf_eu_client_grade_report_state_v2 import build_state
from runtime.build_etf_eu_donor_discovery_bridge import write_bridge
from runtime.current.render import render_to_paths
from runtime.current.review_state import (
    build_review_state,
    dump_review_state,
    write_accountability_observation,
)
from weasyprint import HTML


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Required artifact not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected object in {path}")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact(path: Path) -> dict[str, Any]:
    return {"path": str(path), "sha256": _sha256(path), "size_bytes": path.stat().st_size}


def build(args: argparse.Namespace) -> dict[str, Path]:
    current_dir = Path(args.output_dir)
    history_dir = Path(args.history_dir) / args.report_date / args.run_id
    evidence_dir = Path(args.evidence_dir) / args.run_id
    current_dir.mkdir(parents=True, exist_ok=True)
    history_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)

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
    normalized = build_state(state_args)
    if normalized.get("state_valid") is not True:
        raise RuntimeError(f"Normalized current state invalid: {normalized.get('blockers')}")

    macro = _load(Path(args.macro_pack))
    donor_lane = _load(Path(args.donor_lane_artifact))
    reunderwriting_path = evidence_dir / "current_reunderwriting.json"
    normalized = apply_current_reunderwriting(
        normalized,
        donor_lane=donor_lane,
        macro_pack=macro,
        report_date=args.report_date,
        run_id=args.run_id,
        output_path=reunderwriting_path,
    )
    normalized = apply_contract(normalized, macro_pack=macro)
    normalized = apply_cash_reunderwriting_to_contract_state(normalized)

    bridge_path = evidence_dir / "donor_discovery_bridge.json"
    bridge = write_bridge(
        Path(args.donor_lane_artifact),
        Path(args.proxy_map),
        Path(args.pricing_artifact),
        Path(args.portfolio_state),
        bridge_path,
    )
    normalized["donor_discovery_bridge"] = bridge
    normalized["discovery_parity"] = {
        "contract": "control/ETF_EU_DISCOVERY_FUNDABILITY_CONTRACT_V1.md",
        "donor_lane_artifact": args.donor_lane_artifact,
        "bridge_artifact": str(bridge_path),
        "funding_authority": False,
    }
    write_recommendation_scorecard(normalized, Path(args.recommendation_scorecard), args.report_date, args.run_id)

    review_state_path = current_dir / "review_state.json"
    review_state = build_review_state(
        normalized,
        comparator_config_path=Path(args.comparator_config),
        accountability_history_path=Path(args.accountability_history),
        report_date=args.report_date,
        run_id=args.run_id,
        pricing_artifact=args.pricing_artifact,
        donor_lane_artifact=args.donor_lane_artifact,
        macro_pack=args.macro_pack,
    )
    if review_state.get("state_valid") is not True:
        raise RuntimeError(f"Frozen review state invalid: {review_state.get('blockers')}")
    dump_review_state(review_state, review_state_path)

    nl_md = current_dir / "report_nl.md"
    en_md = current_dir / "report_en.md"
    nl_html = current_dir / "report_nl.html"
    en_html = current_dir / "report_en.html"
    nl_pdf = current_dir / "report_nl.pdf"
    en_pdf = current_dir / "report_en.pdf"
    render_to_paths(review_state, language="nl", markdown_path=nl_md, html_path=nl_html)
    render_to_paths(review_state, language="en", markdown_path=en_md, html_path=en_html)
    HTML(filename=str(nl_html), base_url=str(nl_html.parent.resolve())).write_pdf(str(nl_pdf))
    HTML(filename=str(en_html), base_url=str(en_html.parent.resolve())).write_pdf(str(en_pdf))

    # The accountability observation is the only persistent state updated by this
    # architecture run. It records measurement, never a portfolio/trade mutation.
    write_accountability_observation(review_state, Path(args.accountability_history))

    artifacts = {
        "review_state": _artifact(review_state_path),
        "nl_md": _artifact(nl_md),
        "en_md": _artifact(en_md),
        "nl_html": _artifact(nl_html),
        "en_html": _artifact(en_html),
        "nl_pdf": _artifact(nl_pdf),
        "en_pdf": _artifact(en_pdf),
    }
    manifest = {
        "schema_version": "etf_eu_thin_kernel_manifest_v1",
        "run_id": args.run_id,
        "report_date": args.report_date,
        "report_suffix": args.report_suffix,
        "semantic_source": str(review_state_path),
        "semantic_state_frozen": True,
        "post_freeze_semantic_mutation": False,
        "current_kernel": "runtime/current",
        "candidate_builder": "tools/build_etf_eu_thin_kernel_package.py",
        "production_renderer": "runtime/current/render.py",
        "artifacts": artifacts,
        "evidence": {
            "pricing": args.pricing_artifact,
            "macro": args.macro_pack,
            "donor_lane": args.donor_lane_artifact,
            "current_reunderwriting": str(reunderwriting_path),
            "donor_discovery_bridge": str(bridge_path),
            "accountability_history": args.accountability_history,
            "primary_comparator": args.comparator_config,
            "previous_routine_manifest": args.previous_routine_manifest,
            "previous_delivery_closeout_manifest": args.previous_delivery_closeout_manifest,
        },
        "authority": {
            "portfolio_mutation": False,
            "trade_ledger_write": False,
            "real_broker_execution": False,
            "delivery_authority": False,
            "smtp_send": False,
            "funding_authority": False,
        },
    }
    manifest_path = current_dir / "manifest.json"
    _write(manifest_path, manifest)

    # Keep a run-specific immutable copy while output/current remains the single
    # obvious latest candidate namespace.
    for path in (review_state_path, nl_md, en_md, nl_html, en_html, nl_pdf, en_pdf, manifest_path):
        destination = history_dir / path.name
        destination.write_bytes(path.read_bytes())

    evidence_manifest = {
        "schema_version": "etf_eu_thin_kernel_evidence_v1",
        "run_id": args.run_id,
        "report_date": args.report_date,
        "review_state_sha256": _sha256(review_state_path),
        "pricing_artifact": args.pricing_artifact,
        "reunderwriting": str(reunderwriting_path),
        "donor_bridge": str(bridge_path),
        "portfolio_mutated": False,
        "trade_ledger_written": False,
        "delivery_authority": False,
    }
    evidence_manifest_path = evidence_dir / "manifest.json"
    _write(evidence_manifest_path, evidence_manifest)

    return {
        "review_state": review_state_path,
        "nl_md": nl_md,
        "en_md": en_md,
        "nl_html": nl_html,
        "en_html": en_html,
        "nl_pdf": nl_pdf,
        "en_pdf": en_pdf,
        "manifest": manifest_path,
        "evidence_manifest": evidence_manifest_path,
        "reunderwriting": reunderwriting_path,
        "donor_bridge": bridge_path,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Weekly ETF EU Thin Current Kernel candidate package")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--pricing-artifact", required=True)
    parser.add_argument("--macro-pack", required=True)
    parser.add_argument("--donor-lane-artifact", required=True)
    parser.add_argument("--previous-routine-manifest", required=True)
    parser.add_argument("--previous-delivery-closeout-manifest", required=True)
    parser.add_argument("--registry", default="config/ucits_symbol_registry.yml")
    parser.add_argument("--proxy-map", default="config/ucits_benchmark_proxy_map.yml")
    parser.add_argument("--portfolio-state", default="output/etf_eu_portfolio_state.json")
    parser.add_argument("--valuation-history", default="output/etf_eu_valuation_history.csv")
    parser.add_argument("--recommendation-scorecard", default="output/etf_eu_recommendation_scorecard.csv")
    parser.add_argument("--accountability-history", default="output/etf_eu_accountability_history.csv")
    parser.add_argument("--comparator-config", default="config/etf_eu_primary_comparator.yml")
    parser.add_argument("--output-dir", default="output/current")
    parser.add_argument("--evidence-dir", default="output/evidence")
    parser.add_argument("--history-dir", default="output/history")
    args = parser.parse_args()
    outputs = build(args)
    print("ETF_EU_THIN_KERNEL_PACKAGE_OK | " + " | ".join(f"{key}={value}" for key, value in outputs.items()))


if __name__ == "__main__":
    main()
