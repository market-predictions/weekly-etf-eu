from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.validate_etf_eu_routine_run_manifest import validate as validate_routine_manifest

SCHEMA_VERSION = "etf_eu_fresh_generation_dry_run_v1"
ARTIFACT_TYPE = "etf_eu_fresh_generation_package_manifest"
SOURCE_OF_TRUTH_REPO = "market-predictions/weekly-etf-eu"
REFERENCE_ARCHITECTURE_REPO = "market-predictions/weekly-etf"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _path(value: object, label: str) -> Path:
    raw = str(value or "").strip()
    _require(bool(raw), f"{label} missing")
    path = Path(raw)
    _require(path.exists(), f"{label} does not exist: {path}")
    return path


def _assert_false(data: dict[str, Any], key: str) -> None:
    _require(data.get(key) is False, f"{key} must be false")


def _reject_us_state(value: object, label: str) -> None:
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
    _require(manifest_path.exists(), f"fresh-generation manifest missing: {manifest_path}")
    data = _load(manifest_path)

    _require(data.get("schema_version") == SCHEMA_VERSION, "schema_version mismatch")
    _require(data.get("artifact_type") == ARTIFACT_TYPE, "artifact_type mismatch")
    _require(data.get("source_of_truth_repo") == SOURCE_OF_TRUTH_REPO, "source_of_truth_repo mismatch")
    _require(data.get("reference_architecture_repo") == REFERENCE_ARCHITECTURE_REPO, "reference_architecture_repo mismatch")
    _require(bool(data.get("upstream_pattern_adapted")), "upstream_pattern_adapted missing")
    _require(bool(data.get("fresh_generation_status")), "fresh_generation_status missing")

    _require(data.get("dutch_primary") is True, "dutch_primary must be true")
    _require(data.get("english_companion") is True, "english_companion must be true")
    _require(data.get("ready_for_controlled_delivery") is False, "ready_for_controlled_delivery must remain false in MVP23")
    _require(data.get("pdf_generation_status") == "not_implemented_in_mvp23", "pdf_generation_status must remain explicit")

    for key in [
        "send_executed",
        "transport_attempted",
        "receipt_confirmed",
        "valuation_grade",
        "funding_authority",
        "portfolio_mutation",
        "production_delivery_authority",
        "main_surface_us_holdings_exposure",
        "nan_price_in_client_surface",
        "stale_delivery_wording_present",
    ]:
        _assert_false(data, key)

    for label in [
        "portfolio_state_path",
        "valuation_history_path",
        "trade_ledger_path",
        "recommendation_scorecard_path",
    ]:
        _reject_us_state(data.get(label), label)
        _path(data.get(label), label)

    generated_paths = [
        "dutch_primary_markdown",
        "english_companion_markdown",
        "dutch_primary_html",
        "english_companion_html",
        "ready_artifact",
    ]
    for label in generated_paths:
        _path(data.get(label), label)

    _require(data.get("dutch_primary_pdf") in {None, ""}, "Dutch PDF must not be claimed in MVP23 scaffold")
    _require(data.get("english_companion_pdf") in {None, ""}, "English PDF must not be claimed in MVP23 scaffold")
    _require("_nl_" in str(data.get("dutch_primary_markdown")), "Dutch primary path must identify NL output")
    _require("_nl_" not in str(data.get("english_companion_markdown")), "English companion path must not be NL primary")

    routine_path = Path("output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json")
    routine = validate_routine_manifest(routine_path)
    _require(routine.get("transport_attempted") is False, "routine manifest must remain no-send")
    _require(routine.get("transport_success") is False, "routine manifest must remain no-transport")
    _require(routine.get("receipt_confirmed") is False, "routine manifest must not confirm receipt")

    return {
        "status": "valid",
        "manifest": str(manifest_path),
        "fresh_generation_status": data.get("fresh_generation_status"),
        "ready_for_controlled_delivery": data.get("ready_for_controlled_delivery"),
        "routine_manifest": routine.get("manifest"),
        "next_package": data.get("next_package"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ETF EU fresh-generation no-send dry-run manifest.")
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    print(json.dumps(validate(Path(args.manifest)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
