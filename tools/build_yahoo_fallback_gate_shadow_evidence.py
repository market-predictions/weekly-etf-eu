from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "yahoo_fallback_gate_shadow_evidence_v1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path, kind: str) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Required artifact missing: {path}")
    return {"kind": kind, "path": str(path), "exists": True, "size_bytes": path.stat().st_size, "sha256": sha256(path)}


def run_url() -> str | None:
    server = os.environ.get("GITHUB_SERVER_URL")
    repo = os.environ.get("GITHUB_REPOSITORY")
    run_id = os.environ.get("GITHUB_RUN_ID")
    return f"{server}/{repo}/actions/runs/{run_id}" if server and repo and run_id else None


def build(run_id: str, output_dir: Path) -> Path:
    pricing_dir = Path("output/pricing")
    artifacts = [
        record(pricing_dir / f"yahoo_ucits_close_diagnostics_{run_id}.json", "yahoo_ucits_close_diagnostics"),
        record(pricing_dir / f"yahoo_fallback_gate_evaluation_{run_id}.json", "yahoo_fallback_gate_evaluation"),
        record(pricing_dir / f"yahoo_completed_session_gate_{run_id}.json", "yahoo_completed_session_gate"),
        record(pricing_dir / f"ucits_twelve_data_symbol_discovery_{run_id}.json", "twelve_data_symbol_discovery"),
        record(pricing_dir / f"yahoo_cross_source_gate_{run_id}.json", "yahoo_cross_source_gate"),
    ]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "validation_status": "passed",
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": os.environ.get("GITHUB_REPOSITORY", "market-predictions/weekly-etf-eu"),
        "workflow": {
            "name": os.environ.get("GITHUB_WORKFLOW", "Yahoo fallback gate validation"),
            "run_id": os.environ.get("GITHUB_RUN_ID"),
            "run_number": os.environ.get("GITHUB_RUN_NUMBER"),
            "sha": os.environ.get("GITHUB_SHA"),
            "run_url": run_url(),
        },
        "contract": "control/YAHOO_VERIFIED_FALLBACK_CONTRACT_V1.md",
        "session_policy": "config/ucits_exchange_session_policy.yml",
        "required_artifacts": artifacts,
        "all_rows_blocked_until_contract_gates_pass": True,
        "completed_session_gate_evidence_present": True,
        "cross_source_gate_evidence_present": True,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"yahoo_fallback_gate_shadow_evidence_{run_id}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"YAHOO_FALLBACK_GATE_SHADOW_EVIDENCE_OK | artifact={path}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-dir", default="output/validation")
    args = parser.parse_args()
    build(args.run_id, Path(args.output_dir))


if __name__ == "__main__":
    main()
