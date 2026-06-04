from __future__ import annotations

import argparse
import json
from pathlib import Path

from pricing.build_ucits_valuation_prices import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_REGISTRY,
    DEFAULT_SOURCE_POLICY,
    _latest_file,
    _run_id,
    build_valuation_artifact,
)
from pricing.enrich_ucits_valuation_agreement import enrich_valuation_artifact


def write_valuation_artifact_with_agreement(
    registry_path: Path,
    source_policy_path: Path,
    candidate_artifact_path: Path,
    output_dir: Path,
    run_id: str,
    preflight_artifact_path: Path | None = None,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    base_artifact = build_valuation_artifact(
        registry_path,
        source_policy_path,
        candidate_artifact_path,
        output_dir,
        run_id,
        preflight_artifact_path,
    )
    artifact = enrich_valuation_artifact(base_artifact)
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
