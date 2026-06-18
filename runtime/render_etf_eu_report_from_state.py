from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

DEFAULT_REGISTRY = Path("config/ucits_symbol_registry.yml")
DEFAULT_PRICING = Path("output/pricing/etf_eu_ucits_closing_price_smoke_20260618_000000.json")
DEFAULT_DRAFT = Path("output/weekly_etf_eu_review_260618_draft.md")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"JSON root must be object: {path}")
    return payload


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"YAML root must be object: {path}")
    return payload


def build_etf_eu_report_state(
    *,
    registry_path: Path = DEFAULT_REGISTRY,
    pricing_artifact_path: Path = DEFAULT_PRICING,
    draft_report_path: Path = DEFAULT_DRAFT,
) -> dict[str, Any]:
    registry = _load_yaml(registry_path)
    pricing = _load_json(pricing_artifact_path)
    draft_text = draft_report_path.read_text(encoding="utf-8")
    prices = pricing.get("prices") if isinstance(pricing.get("prices"), list) else []
    funds = registry.get("funds") if isinstance(registry.get("funds"), list) else []
    return {
        "schema_version": "etf_eu_report_state_bridge_v1",
        "source_files": {
            "ucits_registry": str(registry_path),
            "pricing_artifact": str(pricing_artifact_path),
            "draft_report": str(draft_report_path),
        },
        "status": "review_only",
        "authority": {
            "production_delivery": False,
            "portfolio_mutation": False,
            "funding_authority": False,
            "valuation_grade": False,
            "candidate_promotion": False,
        },
        "summary": {
            "ucits_funds_seen": len(funds),
            "pricing_rows": len(prices),
            "pricing_symbols": [row.get("pricing_symbol") for row in prices if isinstance(row, dict)],
            "draft_report_chars": len(draft_text),
        },
        "report_context": {
            "identity_model": registry.get("canonical_identity"),
            "registry_status": registry.get("registry_status"),
            "pricing_source_policy": pricing.get("source_policy", {}),
            "selected_next_package": "WP14G",
            "porting_rule": "port_behavior_not_us_assumptions",
        },
    }


def write_report_state(output_path: Path, **kwargs: Any) -> Path:
    state = build_etf_eu_report_state(**kwargs)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--pricing-artifact", default=str(DEFAULT_PRICING))
    parser.add_argument("--draft-report", default=str(DEFAULT_DRAFT))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = write_report_state(
        Path(args.output),
        registry_path=Path(args.registry),
        pricing_artifact_path=Path(args.pricing_artifact),
        draft_report_path=Path(args.draft_report),
    )
    print(f"ETF_EU_REPORT_STATE_BRIDGE_OK | output={output}")


if __name__ == "__main__":
    main()
