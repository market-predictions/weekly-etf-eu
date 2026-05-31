from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

DEFAULT_SOURCE_POLICY = Path("config/ucits_pricing_source_policy.yml")
DEFAULT_OUTPUT_DIR = Path("output/pricing")
OFFICIAL_SOURCE_IDS = {"euronext_live", "deutsche_boerse_live"}


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def make_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def build_rows(policy: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in policy.get("trading_line_policies") or []:
        for source in line.get("source_order") or []:
            source_id = source.get("source_id")
            if source_id not in OFFICIAL_SOURCE_IDS:
                continue
            if source.get("valuation_grade_eligible") is not True:
                continue
            if not source.get("product_url") or not source.get("expected_currency"):
                continue
            rows.append({
                "registry_id": line.get("registry_id"),
                "isin": line.get("isin"),
                "exchange": line.get("exchange"),
                "exchange_ticker": line.get("exchange_ticker"),
                "trading_currency": line.get("trading_currency"),
                "provider_symbol": line.get("provider_symbol"),
                "source_id": source_id,
                "authority": source.get("authority"),
                "valuation_grade_eligible": source.get("valuation_grade_eligible"),
                "accept_as_valuation_grade": False,
                "status": source.get("status"),
                "product_url": source.get("product_url"),
                "product_code": source.get("product_code"),
                "mic_code": source.get("mic_code"),
                "expected_currency": source.get("expected_currency"),
                "expected_tokens": source.get("expected_tokens") or [],
                "discovery_status": "official_exchange_source_registered_not_priced",
                "portfolio_mutation": False,
                "production_delivery": False,
                "funding_authority": False,
                "valuation_authority": False,
            })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-policy", default=str(DEFAULT_SOURCE_POLICY))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    policy_path = Path(args.source_policy)
    output_dir = Path(args.output_dir)
    run_id = args.run_id or make_run_id()
    policy = load_yaml(policy_path)
    rows = build_rows(policy)
    artifact = {
        "schema_version": "ucits_official_exchange_source_snapshot_v1",
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_policy": str(policy_path),
        "portfolio_mutation": False,
        "production_delivery": False,
        "funding_authority": False,
        "valuation_authority": False,
        "rows": rows,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"ucits_official_exchange_source_snapshot_{run_id}.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(f"UCITS_OFFICIAL_EXCHANGE_SOURCE_SNAPSHOT_OK | artifact={path} | rows={len(rows)}")


if __name__ == "__main__":
    main()
