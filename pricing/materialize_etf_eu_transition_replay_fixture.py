from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected YAML object: {path}")
    return payload


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def materialize(fixture: Path, provenance_path: Path, universe_path: Path, output: Path) -> None:
    provenance = load_json(provenance_path)
    universe = load_yaml(universe_path)
    if provenance.get("schema_version") != "etf_eu_transition_replay_fixture_provenance_v1":
        raise RuntimeError("Unsupported replay fixture provenance schema")
    compressed = fixture.read_bytes()
    if sha256(compressed) != provenance.get("fixture_gzip_sha256"):
        raise RuntimeError("Replay fixture gzip hash mismatch")
    raw = gzip.decompress(compressed)
    if sha256(raw) != provenance.get("materialized_panel_sha256"):
        raise RuntimeError("Replay fixture materialized hash mismatch")
    panel = json.loads(raw.decode("utf-8"))
    if not isinstance(panel, dict) or panel.get("schema_version") != "etf_eu_transition_replay_panel_v1":
        raise RuntimeError("Replay fixture panel schema mismatch")
    if panel.get("valid") is not True:
        raise RuntimeError("Replay fixture panel is not valid")
    if str(panel.get("report_date")) != str(universe.get("report_date")):
        raise RuntimeError("Replay fixture report date differs from current replay universe")
    if panel.get("symbols") != universe.get("symbols"):
        raise RuntimeError("Replay fixture symbols differ from current replay universe")
    if int(panel.get("common_trading_day_count") or 0) < int(universe.get("minimum_common_trading_days") or 60):
        raise RuntimeError("Replay fixture has insufficient common trading history")
    if int(panel.get("common_trading_day_count") or 0) != int(provenance.get("common_trading_day_count") or 0):
        raise RuntimeError("Replay fixture day count differs from provenance")
    if panel.get("common_start_date") != provenance.get("common_start_date") or panel.get("common_end_date") != provenance.get("common_end_date"):
        raise RuntimeError("Replay fixture date range differs from provenance")
    for key in ("valuation_grade", "funding_authority", "portfolio_mutation", "execution_authority", "optimization_authority"):
        if panel.get(key) is not False:
            raise RuntimeError(f"Replay fixture authority escalated: {key}")

    panel["deterministic_replay_fixture"] = {
        "applied": True,
        "source_workflow_run_id": provenance.get("source_workflow_run_id"),
        "source_artifact_id": provenance.get("source_artifact_id"),
        "materialized_panel_sha256": provenance.get("materialized_panel_sha256"),
        "live_network_required": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "execution_authority": False,
        "optimization_authority": False,
        "production_delivery_authority": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(panel, indent=2) + "\n", encoding="utf-8")
    print(
        "ETF_EU_TRANSITION_REPLAY_FIXTURE_OK"
        f" | report_date={panel['report_date']}"
        f" | days={panel['common_trading_day_count']}"
        f" | source_run={provenance.get('source_workflow_run_id')}"
        f" | output={output}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize deterministic ETF EU transition replay fixture")
    parser.add_argument("--fixture", type=Path, default=Path("config/replay/etf_eu_transition_replay_panel_20260727.json.gz"))
    parser.add_argument("--provenance", type=Path, default=Path("config/replay/etf_eu_transition_replay_panel_20260727.provenance.json"))
    parser.add_argument("--universe", type=Path, default=Path("config/etf_eu_transition_replay_universe.yml"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    materialize(args.fixture, args.provenance, args.universe, args.output)


if __name__ == "__main__":
    main()
