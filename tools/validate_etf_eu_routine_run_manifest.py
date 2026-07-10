from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_routine_run_manifest_v1"
ARTIFACT_TYPE = "etf_eu_routine_run_manifest"
SOURCE_OF_TRUTH_REPO = "market-predictions/weekly-etf-eu"
REFERENCE_ARCHITECTURE_REPO = "market-predictions/weekly-etf"
LATEST_POINTER = Path("output/run_manifests/latest_etf_eu_routine_run_manifest_path.txt")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _optional_existing_path(value: object, label: str) -> None:
    if value is None or str(value).strip() == "":
        return
    path = Path(str(value))
    _require(path.exists(), f"{label} does not exist: {path}")


def _assert_eu_state_path(value: object, label: str) -> None:
    raw = str(value or "")
    forbidden = {
        "portfolio_state_path": "output/etf_portfolio_state.json",
        "valuation_history_path": "output/etf_valuation_history.csv",
        "trade_ledger_path": "output/etf_trade_ledger.csv",
        "recommendation_scorecard_path": "output/etf_recommendation_scorecard.csv",
    }
    _require(raw != forbidden.get(label), f"{label} uses U.S. state authority: {raw}")
    if raw:
        _require(raw.startswith("output/etf_eu_"), f"{label} must be EU-specific: {raw}")


def validate(manifest_path: Path) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    _require(manifest_path.exists(), f"manifest missing: {manifest_path}")
    data = _load(manifest_path)

    _require(data.get("schema_version") == SCHEMA_VERSION, "schema_version mismatch")
    _require(data.get("artifact_type") == ARTIFACT_TYPE, "artifact_type mismatch")
    _require(data.get("source_of_truth_repo") == SOURCE_OF_TRUTH_REPO, "source_of_truth_repo mismatch")
    _require(data.get("reference_architecture_repo") == REFERENCE_ARCHITECTURE_REPO, "reference_architecture_repo mismatch")
    _require(bool(data.get("upstream_pattern_adapted")), "upstream_pattern_adapted missing")

    _require(data.get("valuation_grade") is False, "valuation_grade must remain false")
    _require(data.get("funding_authority") is False, "funding_authority must remain false")
    _require(data.get("portfolio_mutation") is False, "portfolio_mutation must remain false")
    _require(data.get("production_delivery_authority") is False, "production_delivery_authority must remain false")

    attempted = data.get("transport_attempted")
    success = data.get("transport_success")
    receipt = data.get("receipt_confirmed")
    _require(isinstance(attempted, bool), "transport_attempted must be boolean")
    _require(isinstance(success, bool), "transport_success must be boolean")
    _require(isinstance(receipt, bool), "receipt_confirmed must be boolean")
    if success:
        _require(attempted is True, "transport_success requires transport_attempted")
    if receipt:
        _require(bool(data.get("delivery_closeout_manifest")), "receipt_confirmed requires delivery_closeout_manifest")

    for label in [
        "portfolio_state_path",
        "valuation_history_path",
        "trade_ledger_path",
        "recommendation_scorecard_path",
    ]:
        _assert_eu_state_path(data.get(label), label)

    for label in [
        "previous_delivery_closeout_manifest",
        "portfolio_state_path",
        "valuation_history_path",
        "trade_ledger_path",
        "recommendation_scorecard_path",
        "pricing_artifact_path",
        "delivery_package_manifest",
        "ready_artifact",
        "delivery_closeout_manifest",
        "dutch_primary_markdown",
        "english_companion_markdown",
        "dutch_primary_html",
        "english_companion_html",
        "dutch_primary_pdf",
        "english_companion_pdf",
    ]:
        _optional_existing_path(data.get(label), label)

    if data.get("dutch_primary_markdown"):
        _require("_nl_" in str(data.get("dutch_primary_markdown")) or str(data.get("dutch_primary_markdown")).endswith("_nl.md"), "Dutch primary markdown path must identify NL primary output")
    if data.get("english_companion_markdown"):
        _require("_nl_" not in str(data.get("english_companion_markdown")), "English companion markdown path must not be NL primary")

    if LATEST_POINTER.exists():
        pointed = LATEST_POINTER.read_text(encoding="utf-8").strip()
        _require(pointed == str(manifest_path), f"latest routine manifest pointer mismatch: {pointed}")

    return {
        "status": "valid",
        "manifest": str(manifest_path),
        "run_id": data.get("run_id"),
        "routine_stage": data.get("routine_stage"),
        "transport_attempted": attempted,
        "transport_success": success,
        "receipt_confirmed": receipt,
        "next_package": data.get("next_package"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate an ETF EU routine weekly run manifest.")
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    print(json.dumps(validate(Path(args.manifest)), indent=2))


if __name__ == "__main__":
    main()
