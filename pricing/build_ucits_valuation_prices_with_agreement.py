from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from pricing.build_ucits_valuation_prices import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_REGISTRY,
    DEFAULT_SOURCE_POLICY,
    _latest_file,
    _run_id,
    build_valuation_artifact,
)
from pricing.enrich_ucits_valuation_agreement import enrich_valuation_artifact


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _write_shadow_policy(source_policy_path: Path, output_dir: Path, run_id: str) -> Path:
    """Create a conservative policy copy accepted by the legacy builder.

    The live source policy can record a temporary Yahoo fallback posture, but the
    legacy valuation builder intentionally accepts only non-authoritative Yahoo
    evidence. This shadow copy lets the wrapper build an evidence-only artifact
    without weakening valuation authority.
    """

    policy = deepcopy(_load_yaml(source_policy_path))
    policy["pricing_authority_mode"] = "valuation_grade_pending"
    rules = policy.setdefault("rules", {})
    rules["yfinance_default_authority"] = "non_authoritative_connectivity_only"
    rules["twelve_data_default_accept_as_valuation_grade"] = False
    rules["portfolio_mutation_from_pricing"] = False
    rules["production_delivery_from_pricing"] = False
    rules["funding_authority_from_pricing"] = False

    for source in policy.get("source_authority_hierarchy") or []:
        if source.get("source_id") == "yahoo_yfinance":
            source["authority"] = "non_authoritative_connectivity_only"
            source["valuation_grade_eligible"] = False
            source["notes"] = "Shadow wrapper override: Yahoo evidence is non-authoritative for agreement-gate valuation artifacts."

    for line in policy.get("trading_line_policies") or []:
        for source in line.get("source_order") or []:
            if source.get("source_id") == "yahoo_yfinance":
                source["authority"] = "non_authoritative_connectivity_only"
                source["valuation_grade_eligible"] = False
                source["accept_as_valuation_grade"] = False
                source["status"] = "shadow_non_authoritative_connectivity_only"

    output_dir.mkdir(parents=True, exist_ok=True)
    shadow_path = output_dir / f"ucits_pricing_source_policy_shadow_{run_id}.yml"
    shadow_path.write_text(yaml.safe_dump(policy, sort_keys=False), encoding="utf-8")
    return shadow_path


def write_valuation_artifact_with_agreement(
    registry_path: Path,
    source_policy_path: Path,
    candidate_artifact_path: Path,
    output_dir: Path,
    run_id: str,
    preflight_artifact_path: Path | None = None,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    shadow_policy_path = _write_shadow_policy(source_policy_path, output_dir, run_id)
    base_artifact = build_valuation_artifact(
        registry_path,
        shadow_policy_path,
        candidate_artifact_path,
        output_dir,
        run_id,
        preflight_artifact_path,
    )
    artifact = enrich_valuation_artifact(base_artifact)
    artifact["source_policy_original"] = str(source_policy_path)
    artifact["source_policy_shadow"] = str(shadow_policy_path)
    artifact["pricing_authority_mode_original"] = _load_yaml(source_policy_path).get("pricing_authority_mode")
    artifact["agreement_wrapper_policy_mode"] = "shadow_non_authoritative_yahoo_no_promotion"
    artifact["valuation_grade_row_count"] = 0
    artifact["portfolio_mutation"] = False
    artifact["production_delivery"] = False
    artifact["funding_authority"] = False
    path = output_dir / f"ucits_valuation_prices_{run_id}.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    gate_grade = sum(
        1 for row in artifact["rows"] if (row.get("agreement_gate_evidence") or {}).get("status") == "valuation_grade"
    )
    print(
        "UCITS_VALUATION_PRICES_WITH_AGREEMENT_OK"
        f" | artifact={path}"
        f" | rows={len(artifact['rows'])}"
        f" | agreement_gate_valuation_grade_evidence={gate_grade}"
        f" | valuation_grade_rows={artifact['valuation_grade_row_count']}"
        " | portfolio_mutation=false | delivery=false"
    )
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--source-policy", default=str(DEFAULT_SOURCE_POLICY))
    parser.add_argument("--candidate-artifact", default=None)
    parser.add_argument("--preflight-artifact", default=None)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    run_id = args.run_id or _run_id()
    candidate_artifact = Path(args.candidate_artifact) if args.candidate_artifact else _latest_file(output_dir, "ucits_pricing_candidates_*.json")
    preflight_artifact = Path(args.preflight_artifact) if args.preflight_artifact else None
    write_valuation_artifact_with_agreement(
        Path(args.registry),
        Path(args.source_policy),
        candidate_artifact,
        output_dir,
        run_id,
        preflight_artifact,
    )


if __name__ == "__main__":
    main()
