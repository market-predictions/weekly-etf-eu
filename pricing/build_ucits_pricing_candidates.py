from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("PyYAML is required for UCITS pricing candidate extraction") from exc

DEFAULT_REGISTRY = Path("config/ucits_symbol_registry.yml")
DEFAULT_OUTPUT_DIR = Path("output/pricing")
ELIGIBLE_STATUS = "verified_candidate_not_funded"
PENDING_VALUES = {"", "TBD", "pending_verification", None}


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _as_str(value: Any) -> str:
    return str(value or "").strip()


def _is_pending(value: Any) -> bool:
    return value in PENDING_VALUES or _as_str(value) in PENDING_VALUES


def _run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def build_candidates(registry_path: Path, run_id: str) -> dict[str, Any]:
    registry = _load_yaml(registry_path)
    candidates: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for fund in registry.get("funds") or []:
        registry_id = _as_str(fund.get("registry_id"))
        status = _as_str(fund.get("investability_status"))
        if status != ELIGIBLE_STATUS:
            skipped.append({
                "registry_id": registry_id,
                "reason": f"investability_status_not_{ELIGIBLE_STATUS}",
                "investability_status": status,
            })
            continue
        for line in fund.get("trading_lines") or []:
            required = ["exchange", "exchange_ticker", "trading_currency", "provider_symbol", "pricing_symbol_yahoo"]
            missing = [field for field in required if _is_pending(line.get(field))]
            if missing:
                skipped.append({
                    "registry_id": registry_id,
                    "reason": "trading_line_missing_required_fields",
                    "missing_fields": missing,
                    "exchange_ticker": line.get("exchange_ticker"),
                })
                continue
            candidates.append({
                "registry_id": registry_id,
                "isin": fund.get("isin"),
                "fund_name": fund.get("fund_name"),
                "provider": fund.get("provider"),
                "instrument_type": fund.get("instrument_type"),
                "investability_status": status,
                "fundable_status": fund.get("fundable_status"),
                "ucits_status": fund.get("ucits_status"),
                "priips_kid_status": fund.get("priips_kid_status"),
                "us_research_proxy": fund.get("us_research_proxy"),
                "exchange": line.get("exchange"),
                "exchange_ticker": line.get("exchange_ticker"),
                "trading_currency": line.get("trading_currency"),
                "provider_symbol": line.get("provider_symbol"),
                "pricing_symbol_yahoo": line.get("pricing_symbol_yahoo"),
                "line_verification_status": line.get("line_verification_status"),
                "pricing_status": line.get("pricing_status"),
                "portfolio_mutation": False,
                "production_delivery": False,
                "funding_authority": False,
            })
    return {
        "schema_version": "ucits_pricing_candidates_v1",
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_registry": str(registry_path),
        "eligible_investability_status": ELIGIBLE_STATUS,
        "portfolio_mutation": False,
        "production_delivery": False,
        "funding_authority": False,
        "candidates": candidates,
        "skipped": skipped,
    }


def write_candidates(registry_path: Path, output_dir: Path, run_id: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = build_candidates(registry_path, run_id)
    path = output_dir / f"ucits_pricing_candidates_{run_id}.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(f"UCITS_PRICING_CANDIDATES_OK | artifact={path} | candidates={len(artifact['candidates'])} | skipped={len(artifact['skipped'])}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()
    write_candidates(Path(args.registry), Path(args.output_dir), args.run_id or _run_id())


if __name__ == "__main__":
    main()
