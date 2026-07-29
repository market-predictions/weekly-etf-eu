from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime import build_etf_eu_stage_2_readiness as base


REQUIRED_FALSE_AUTHORITY_FLAGS = (
    "portfolio_mutation",
    "funding_authority",
    "execution_authority",
    "production_delivery_authority",
)


def normalize_sync_authority(sync: dict[str, Any]) -> dict[str, Any]:
    if sync.get("schema_version") != "etf_eu_strategy_sync_shadow_v2":
        raise RuntimeError("Unsupported synchronization contract")
    authority = sync.get("authority") if isinstance(sync.get("authority"), dict) else {}
    if authority.get("shadow_only") is not True:
        raise RuntimeError("Synchronization artifact is not shadow-only")
    for key in REQUIRED_FALSE_AUTHORITY_FLAGS:
        if authority.get(key) is not False:
            raise RuntimeError(f"Synchronization authority {key} must be false")
    normalized = dict(sync)
    normalized["portfolio_mutation"] = False
    normalized["funding_authority"] = False
    normalized["execution_authority"] = False
    normalized["production_delivery_authority"] = False
    return normalized


def validate_euna_authority(euna: dict[str, Any]) -> None:
    if euna.get("schema_version") != "etf_eu_euna_risk_budget_review_v1":
        raise RuntimeError("Unsupported EUNA review contract")
    for key in (
        "portfolio_mutation",
        "funding_authority",
        "execution_authority",
        "activation_authority",
        "production_delivery_authority",
    ):
        if euna.get(key) is not False:
            raise RuntimeError(f"EUNA authority {key} must be false")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build ETF EU Stage-2 readiness with explicit authority-contract normalization")
    parser.add_argument("--allocator", type=Path, required=True)
    parser.add_argument("--sync-shadow", type=Path, required=True)
    parser.add_argument("--product-evidence", type=Path, required=True)
    parser.add_argument("--euna-review", type=Path, required=True)
    parser.add_argument("--donor-pin", type=Path, default=Path("config/weekly_etf_donor_contract_pin.json"))
    parser.add_argument("--policy", type=Path, default=Path("config/etf_eu_stage_2_transition_policy_v1.yml"))
    parser.add_argument("--stage-1-operational-state", type=Path)
    parser.add_argument("--activation-authorization", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    allocator = base.load_json(args.allocator)
    sync = normalize_sync_authority(base.load_json(args.sync_shadow))
    product_evidence = base.load_yaml(args.product_evidence)
    euna = base.load_json(args.euna_review)
    validate_euna_authority(euna)
    donor_pin = base.load_json(args.donor_pin)
    policy = base.load_yaml(args.policy)
    stage_1_state = base.load_json(args.stage_1_operational_state) if args.stage_1_operational_state else None
    authorization = base.load_json(args.activation_authorization) if args.activation_authorization else None

    payload = base.build(
        allocator,
        sync,
        product_evidence,
        euna,
        donor_pin,
        policy,
        stage_1_state,
        authorization,
    )
    payload["input_authority_contract"] = {
        "allocator": "nested_authority_verified_by_base_builder",
        "strategy_sync": "nested_authority_verified_and_normalized_to_top_level_false",
        "euna_review": "top_level_authority_verified_false",
        "authority_escalation": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
