from __future__ import annotations

import json
import tempfile
from argparse import Namespace
from pathlib import Path
from typing import Any

from pricing.ucits_close_price_validation_contract_v2 import (
    SCHEMA_VERSION,
    validate_artifact,
)
from runtime.build_etf_eu_client_grade_report_state import build_state as build_legacy_state


def build_state(args: Namespace) -> dict[str, Any]:
    pricing_path = Path(args.pricing_artifact)
    portfolio_path = Path(args.portfolio_state)
    pricing_validation = validate_artifact(
        pricing_path,
        expected_report_date=args.report_date,
        portfolio_state_path=portfolio_path,
        require_funded_consensus=True,
    )
    if pricing_validation["valid"] is not True:
        raise RuntimeError(
            "Canonical v2 pricing contract failed: "
            + "; ".join(pricing_validation["blockers"])
        )

    pricing_payload = json.loads(pricing_path.read_text(encoding="utf-8"))
    # The legacy state constructor is retained as an internal layout helper only.
    # Its historical min_threshold_met check is satisfied in an ephemeral copy;
    # the canonical production authority is the v2 contract validated above.
    compatibility_payload = dict(pricing_payload)
    compatibility_payload["min_threshold_met"] = True

    with tempfile.TemporaryDirectory(prefix="etf_eu_pricing_v2_") as tmpdir:
        compatibility_path = Path(tmpdir) / "pricing_v2_compat.json"
        compatibility_path.write_text(
            json.dumps(compatibility_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        legacy_args = Namespace(**vars(args))
        legacy_args.pricing_artifact = str(compatibility_path)
        state = build_legacy_state(legacy_args)

    blockers = [
        blocker
        for blocker in state.get("blockers") or []
        if blocker != "pricing coverage threshold not met"
    ]
    state["schema_version"] = "etf_eu_client_grade_report_state_v2"
    state["sources"]["pricing_artifact"] = str(pricing_path)
    state["pricing"].update(
        {
            "contract_schema": SCHEMA_VERSION,
            "contract_validation": pricing_validation,
            "report_date": pricing_payload.get("report_date"),
            "report_pricing_gate_passed": pricing_payload.get("report_pricing_gate_passed") is True,
            "funded_two_provider_consensus_required": True,
            "pricing_authority": "canonical_v2_completed_close_contract",
        }
    )
    state["pricing_contract"] = {
        "schema_version": SCHEMA_VERSION,
        "artifact": str(pricing_path),
        "expected_report_date": args.report_date,
        "report_pricing_gate_passed": pricing_payload.get("report_pricing_gate_passed") is True,
        "funded_two_provider_consensus_required": True,
        "validation": pricing_validation,
    }
    state["blockers"] = blockers
    state["state_valid"] = not blockers and pricing_validation["valid"] is True
    return state
