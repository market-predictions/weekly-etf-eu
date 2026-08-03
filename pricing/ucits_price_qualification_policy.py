from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _text(value: Any) -> str:
    return str(value or "").strip()


def _symbol_match(row: dict[str, Any]) -> bool | None:
    returned = _text(row.get("returned_symbol")).upper()
    requested = _text(row.get("provider_symbol")).upper()
    if not returned:
        return None
    return returned == requested


def _is_identity_anchor(row: dict[str, Any]) -> bool:
    return (
        row.get("pricing_status") == "priced"
        and _symbol_match(row) is True
        and row.get("venue_match") is True
        and row.get("currency_match") is True
    )


def apply_identity_anchor_policy(path: Path) -> dict[str, Any]:
    """Require one exact-line metadata anchor inside every accepted price consensus.

    A provider with a successful close but no returned symbol, venue or currency can
    corroborate a close. It cannot independently establish trading-line identity.
    """
    payload = json.loads(path.read_text(encoding="utf-8"))
    lines = [row for row in payload.get("lines", []) if isinstance(row, dict)]
    for line in lines:
        agreeing = set(line.get("agreeing_providers") or [])
        anchors: list[str] = []
        corroborators: list[str] = []
        for provider_row in line.get("provider_results", []) or []:
            if not isinstance(provider_row, dict):
                continue
            provider_row["symbol_match"] = _symbol_match(provider_row)
            provider_row["identity_anchor"] = _is_identity_anchor(provider_row)
            provider = _text(provider_row.get("provider"))
            if provider not in agreeing:
                continue
            if provider_row["identity_anchor"]:
                anchors.append(provider)
            elif provider_row.get("pricing_status") == "priced":
                corroborators.append(provider)
        line["identity_anchor_providers"] = anchors
        line["identity_anchor_provider_count"] = len(anchors)
        line["corroborating_providers"] = corroborators
        line["identity_assurance_status"] = (
            "metadata_anchored_exact_line" if anchors else "unanchored_price_consensus"
        )
        if line.get("qualification_status") == "qualified_development_consensus" and not anchors:
            line["qualification_status"] = "price_consensus_identity_unanchored"

    funded = [line for line in lines if line.get("funded")]
    payload["qualified_line_count"] = sum(
        line.get("qualification_status") == "qualified_development_consensus" for line in lines
    )
    payload["funded_consensus_count"] = sum(
        line.get("qualification_status") == "qualified_development_consensus" for line in funded
    )
    payload["funded_identity_anchor_count"] = sum(
        int(line.get("identity_anchor_provider_count") or 0) >= 1 for line in funded
    )
    payload["report_pricing_gate_passed"] = bool(funded) and all(
        line.get("qualification_status") == "qualified_development_consensus" for line in funded
    )
    payload["identity_policy"] = {
        "same_date_provider_count_required": 2,
        "metadata_identity_anchor_required": 1,
        "anchor_requirements": [
            "returned_symbol_matches_requested_provider_symbol",
            "returned_venue_matches_expected_mic",
            "returned_currency_matches_expected_currency",
        ],
        "providers_without_returned_metadata": "corroboration_only",
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload
