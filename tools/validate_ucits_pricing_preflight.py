from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT_DIR = Path("output/pricing")
ALLOWED_STATUSES = {
    "priced_non_authoritative",
    "unpriced_dependency_missing",
    "unpriced_no_history",
    "unpriced_provider_error",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_preflight_file(output_dir: Path) -> Path:
    files = sorted(output_dir.glob("ucits_pricing_preflight_*.json"))
    if not files:
        raise RuntimeError(f"No UCITS pricing preflight artifacts found in {output_dir}")
    return files[-1]


def validate(path: Path, *, require_one_priced: bool = False) -> None:
    payload = _load_json(path)
    errors: list[str] = []
    if payload.get("schema_version") != "ucits_pricing_preflight_v1":
        errors.append("schema_version_must_be_ucits_pricing_preflight_v1")
    if payload.get("pricing_authority") != "non_authoritative_connectivity_preflight":
        errors.append("pricing_authority_must_be_non_authoritative_connectivity_preflight")
    for field in ["portfolio_mutation", "production_delivery", "funding_authority"]:
        if payload.get(field) is not False:
            errors.append(f"top_level_{field}_must_be_false")
    results = payload.get("results") or []
    if not isinstance(results, list) or not results:
        errors.append("at_least_one_preflight_result_required")
    priced = 0
    for idx, row in enumerate(results):
        label = f"result:{idx}:{row.get('registry_id') or 'unknown'}"
        for field in ["registry_id", "isin", "fund_name", "exchange", "exchange_ticker", "trading_currency", "provider_symbol", "pricing_symbol_yahoo"]:
            if not str(row.get(field) or "").strip():
                errors.append(f"{label}:missing_{field}")
        for field in ["portfolio_mutation", "production_delivery", "funding_authority"]:
            if row.get(field) is not False:
                errors.append(f"{label}:{field}_must_be_false")
        preflight = row.get("preflight_result") or {}
        status = preflight.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{label}:unexpected_preflight_status:{status}")
        if status == "priced_non_authoritative":
            priced += 1
            if preflight.get("close") is None:
                errors.append(f"{label}:priced_result_missing_close")
            if not preflight.get("observed_date"):
                errors.append(f"{label}:priced_result_missing_observed_date")
    if require_one_priced and priced < 1:
        errors.append("require_one_priced_requested_but_no_symbol_priced")
    if errors:
        raise RuntimeError("UCITS pricing preflight validation failed: " + "; ".join(errors))
    print(f"UCITS_PRICING_PREFLIGHT_VALIDATION_OK | artifact={path} | results={len(results)} | priced_non_authoritative={priced}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", default=None)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--require-one-priced", action="store_true")
    args = parser.parse_args()
    artifact = Path(args.artifact) if args.artifact else _latest_preflight_file(Path(args.output_dir))
    validate(artifact, require_one_priced=args.require_one_priced)


if __name__ == "__main__":
    main()
