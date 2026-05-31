from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT_DIR = Path("output/pricing")
ALLOWED_SOURCE_IDS = {"euronext_live", "deutsche_boerse_live"}
ALLOWED_ADAPTERS = {"euronext_live", "deutsche_boerse_live"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_file(output_dir: Path) -> Path:
    files = sorted(output_dir.glob("ucits_close_observations_*.json"))
    if not files:
        raise RuntimeError(f"No UCITS close observation artifacts found in {output_dir}")
    return files[-1]


def text(value: Any) -> str:
    return str(value or "").strip()


def validate(path: Path) -> None:
    payload = load_json(path)
    errors: list[str] = []
    if payload.get("schema_version") != "ucits_close_observations_v1":
        errors.append("schema_version_must_be_ucits_close_observations_v1")
    for field in ["portfolio_mutation", "production_delivery", "funding_authority", "valuation_authority"]:
        if payload.get(field) is not False:
            errors.append(f"top_level_{field}_must_be_false")

    rows = payload.get("rows") or []
    if not isinstance(rows, list) or not rows:
        errors.append("at_least_one_close_observation_row_required")

    for idx, row in enumerate(rows):
        label = f"row:{idx}:{row.get('registry_id') or 'unknown'}"
        for field in [
            "registry_id",
            "isin",
            "exchange",
            "exchange_ticker",
            "trading_currency",
            "source_id",
            "adapter_name",
            "observation_status",
            "confidence",
            "parser_status",
        ]:
            if not text(row.get(field)):
                errors.append(f"{label}:missing_{field}")
        if row.get("source_id") not in ALLOWED_SOURCE_IDS:
            errors.append(f"{label}:unexpected_source_id:{row.get('source_id')}")
        if row.get("adapter_name") not in ALLOWED_ADAPTERS:
            errors.append(f"{label}:unexpected_adapter_name:{row.get('adapter_name')}")
        if row.get("candidate_close") is not None:
            errors.append(f"{label}:candidate_close_must_remain_null_in_scaffold_phase")
        if row.get("candidate_date") is not None:
            errors.append(f"{label}:candidate_date_must_remain_null_in_scaffold_phase")
        if row.get("completed_session") is not False:
            errors.append(f"{label}:completed_session_must_be_false_in_scaffold_phase")
        if not isinstance(row.get("blockers"), list) or not row.get("blockers"):
            errors.append(f"{label}:blockers_required")
        if not isinstance(row.get("source_lineage"), dict):
            errors.append(f"{label}:source_lineage_must_be_object")
        for field in ["portfolio_mutation", "production_delivery", "funding_authority", "valuation_authority"]:
            if row.get(field) is not False:
                errors.append(f"{label}:{field}_must_be_false")

    if errors:
        raise RuntimeError("UCITS close observation validation failed: " + "; ".join(errors))
    print(f"UCITS_CLOSE_OBSERVATIONS_VALIDATION_OK | artifact={path} | rows={len(rows)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", default=None)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    artifact = Path(args.artifact) if args.artifact else latest_file(Path(args.output_dir))
    validate(artifact)


if __name__ == "__main__":
    main()
