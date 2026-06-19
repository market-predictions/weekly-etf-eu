from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_pricing_line_expansion_v1"

TRUE_FIELDS = [
    "pricing_line_expansion_created",
    "candidate_pricing_evidence_map_created",
    "pricing_line_status_map_created",
    "proxy_ambiguity_guard_created",
    "valuation_grade_guard_created",
    "funding_authority_guard_created",
    "candidate_promotion_guard_created",
    "ucits_identity_preserved",
    "proxy_separation_preserved",
    "pricing_evidence_preserved",
]

FALSE_FIELDS = [
    "production_delivery",
    "portfolio_mutation",
    "candidate_promotion",
    "funding_authority",
    "valuation_grade",
]

PATH_FIELDS = [
    "source_enriched_cockpit_render_manifest_path",
    "source_universe_enrichment_manifest_path",
    "source_symbol_registry_path",
    "source_proxy_map_path",
    "authorization_decision_artifact_path",
    "notes_path",
]

ALLOWED_PRICING_LINE_STATUSES = {
    "source_evidence_available",
    "pricing_symbol_pending",
    "pricing_symbol_ambiguous",
    "identity_incomplete",
    "policy_blocked",
    "not_applicable",
}
ALLOWED_PRICING_EVIDENCE_STATUSES = {
    "usable_for_review_only",
    "not_usable_until_exchange_line_verified",
    "not_usable_until_isin_verified",
    "not_usable_until_policy_decision",
    "not_valuation_grade",
}
US_PROXIES = {"SPY", "SMH", "GLD", "PAVE"}


class EtfEuPricingLineExpansionError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise EtfEuPricingLineExpansionError("manifest root must be object")
    return data


def _require_path(payload: dict[str, Any], key: str) -> Path:
    raw = str(payload.get(key) or "").strip()
    if not raw:
        raise EtfEuPricingLineExpansionError(f"{key} missing")
    path = Path(raw)
    if not path.exists():
        raise EtfEuPricingLineExpansionError(f"{key} does not exist: {raw}")
    return path


def _candidate_by_id(candidates: list[dict[str, Any]], candidate_id: str) -> dict[str, Any]:
    for candidate in candidates:
        if candidate.get("candidate_id") == candidate_id or candidate.get("isin") == candidate_id:
            return candidate
    raise EtfEuPricingLineExpansionError(f"candidate not found: {candidate_id}")


def _trading_symbols(candidate: dict[str, Any]) -> set[str]:
    symbols: set[str] = set()
    for line in candidate.get("trading_lines", []):
        for key in ["pricing_symbol_yahoo", "exchange_ticker"]:
            value = str(line.get(key) or "").strip()
            if value:
                symbols.add(value)
    return symbols


def _proxy_symbols(candidate: dict[str, Any]) -> set[str]:
    return {str(proxy.get("us_proxy") or "").strip() for proxy in candidate.get("research_proxies", []) if proxy.get("us_proxy")}


def _validate_candidate_common(candidate: dict[str, Any]) -> None:
    for key in [
        "candidate_id",
        "isin",
        "fund_name",
        "provider",
        "cockpit_status",
        "pricing_line_status",
        "pricing_evidence_status",
        "trading_lines",
        "research_proxies",
        "safe_for_cockpit_pricing_evidence",
        "safe_for_valuation_grade",
        "safe_for_funding_decision",
        "safe_for_candidate_promotion",
        "evidence_gaps",
        "reader_meaning",
        "next_pricing_action",
    ]:
        if key not in candidate:
            raise EtfEuPricingLineExpansionError(f"candidate missing {key}: {candidate}")

    if candidate["pricing_line_status"] not in ALLOWED_PRICING_LINE_STATUSES:
        raise EtfEuPricingLineExpansionError(f"invalid pricing_line_status: {candidate['pricing_line_status']}")
    if candidate["pricing_evidence_status"] not in ALLOWED_PRICING_EVIDENCE_STATUSES:
        raise EtfEuPricingLineExpansionError(f"invalid pricing_evidence_status: {candidate['pricing_evidence_status']}")

    for key in ["safe_for_valuation_grade", "safe_for_funding_decision", "safe_for_candidate_promotion"]:
        if candidate.get(key) is not False:
            raise EtfEuPricingLineExpansionError(f"{candidate['candidate_id']} {key} must be false")

    for line in candidate.get("trading_lines", []):
        if line.get("safe_for_valuation_grade") is not False:
            raise EtfEuPricingLineExpansionError(f"{candidate['candidate_id']} trading line valuation grade must be false")

    for proxy in candidate.get("research_proxies", []):
        if proxy.get("us_proxy") in US_PROXIES and proxy.get("proxy_must_not_be_pricing_line") is not True:
            raise EtfEuPricingLineExpansionError(f"proxy must be blocked as pricing line: {proxy}")


def _validate_candidate_expectations(candidates: list[dict[str, Any]]) -> None:
    cspx = _candidate_by_id(candidates, "IE00B5BMR087")
    if cspx.get("pricing_line_status") != "source_evidence_available":
        raise EtfEuPricingLineExpansionError("IE00B5BMR087 must have source_evidence_available")
    if cspx.get("pricing_evidence_status") != "usable_for_review_only":
        raise EtfEuPricingLineExpansionError("IE00B5BMR087 must be usable_for_review_only")
    if cspx.get("safe_for_cockpit_pricing_evidence") is not True:
        raise EtfEuPricingLineExpansionError("IE00B5BMR087 must be safe for cockpit pricing evidence")
    if not {"CSPX.L", "SXR8.DE"} <= _trading_symbols(cspx):
        raise EtfEuPricingLineExpansionError("IE00B5BMR087 must contain CSPX.L and SXR8.DE")
    if "SPY" not in _proxy_symbols(cspx):
        raise EtfEuPricingLineExpansionError("IE00B5BMR087 must preserve SPY proxy")

    smh = _candidate_by_id(candidates, "IE00BMC38736")
    if smh.get("cockpit_status") != "pricing_incomplete":
        raise EtfEuPricingLineExpansionError("IE00BMC38736 must remain pricing_incomplete")
    if smh.get("pricing_line_status") not in {"pricing_symbol_ambiguous", "pricing_symbol_pending"}:
        raise EtfEuPricingLineExpansionError("IE00BMC38736 must be ambiguous or pending")
    if smh.get("safe_for_cockpit_pricing_evidence") is not False:
        raise EtfEuPricingLineExpansionError("IE00BMC38736 must not be safe for cockpit pricing evidence")
    if "SMH" not in _proxy_symbols(smh):
        raise EtfEuPricingLineExpansionError("IE00BMC38736 must preserve SMH proxy")
    if "exchange-specific" not in smh.get("next_pricing_action", ""):
        raise EtfEuPricingLineExpansionError("IE00BMC38736 next action must mention exchange-specific verification")

    gold = _candidate_by_id(candidates, "TBD-3-iShares Physical Gold ETC")
    if gold.get("cockpit_status") != "blocked_until_verified":
        raise EtfEuPricingLineExpansionError("gold/ETC must remain blocked_until_verified")
    if gold.get("pricing_line_status") not in {"policy_blocked", "pricing_symbol_pending"}:
        raise EtfEuPricingLineExpansionError("gold/ETC must be policy blocked or pricing pending")
    if gold.get("safe_for_cockpit_pricing_evidence") is not False:
        raise EtfEuPricingLineExpansionError("gold/ETC must not be safe for cockpit pricing evidence")
    if "GLD" not in _proxy_symbols(gold):
        raise EtfEuPricingLineExpansionError("gold/ETC must preserve GLD proxy")
    if "ETC policy" not in gold.get("next_pricing_action", ""):
        raise EtfEuPricingLineExpansionError("gold/ETC next action must mention ETC policy")

    infr = _candidate_by_id(candidates, "TBD-4-iShares Global Infrastructure UCITS ETF")
    if infr.get("cockpit_status") != "identity_incomplete":
        raise EtfEuPricingLineExpansionError("infrastructure must remain identity_incomplete")
    if infr.get("pricing_line_status") not in {"identity_incomplete", "pricing_symbol_pending"}:
        raise EtfEuPricingLineExpansionError("infrastructure must remain identity incomplete or pricing pending")
    if infr.get("safe_for_cockpit_pricing_evidence") is not False:
        raise EtfEuPricingLineExpansionError("infrastructure must not be safe for cockpit pricing evidence")
    if "PAVE" not in _proxy_symbols(infr):
        raise EtfEuPricingLineExpansionError("infrastructure must preserve PAVE proxy")
    action = infr.get("next_pricing_action", "")
    if "ISIN" not in action or "issuer" not in action:
        raise EtfEuPricingLineExpansionError("infrastructure next action must mention ISIN and issuer verification")


def validate_pricing_line_expansion(path: Path) -> dict[str, str]:
    payload = _load_json(path)

    if payload.get("schema_version") != SCHEMA_VERSION:
        raise EtfEuPricingLineExpansionError("bad schema_version")
    if payload.get("status") != "completed":
        raise EtfEuPricingLineExpansionError("status must be completed")
    if payload.get("delivery_authorization_decision") != "remain_blocked":
        raise EtfEuPricingLineExpansionError("delivery_authorization_decision must be remain_blocked")

    for field in TRUE_FIELDS:
        if payload.get(field) is not True:
            raise EtfEuPricingLineExpansionError(f"{field} must be true")
    for field in FALSE_FIELDS:
        if payload.get(field) is not False:
            raise EtfEuPricingLineExpansionError(f"{field} must be false")

    paths = {key: _require_path(payload, key) for key in PATH_FIELDS}
    if "review-only" not in paths["notes_path"].read_text(encoding="utf-8"):
        raise EtfEuPricingLineExpansionError("notes file must contain review-only boundary")

    candidates = payload.get("candidate_pricing_evidence")
    if not isinstance(candidates, list) or len(candidates) != 4:
        raise EtfEuPricingLineExpansionError("candidate_pricing_evidence must contain exactly 4 entries")
    if payload.get("visible_candidate_count") != 4:
        raise EtfEuPricingLineExpansionError("visible_candidate_count must be 4")

    for candidate in candidates:
        _validate_candidate_common(candidate)
    _validate_candidate_expectations(candidates)

    unsafe = json.dumps(payload.get("unsafe_pricing_symbols", []))
    for symbol in ["SMH", "GLD", "PAVE"]:
        if symbol not in unsafe:
            raise EtfEuPricingLineExpansionError(f"unsafe_pricing_symbols missing {symbol}")

    selected_next_package = str(payload.get("selected_next_package") or "").strip()
    if not selected_next_package:
        raise EtfEuPricingLineExpansionError("selected_next_package missing")

    print(
        "ETF_EU_PRICING_LINE_EXPANSION_OK | "
        f"artifact={path} | visible_candidate_count={payload['visible_candidate_count']} | "
        f"selected_next_package={selected_next_package}"
    )
    return {
        "status": "valid",
        "artifact": str(path),
        "selected_next_package": selected_next_package,
        "visible_candidate_count": str(payload["visible_candidate_count"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_pricing_line_expansion(Path(args.artifact))


if __name__ == "__main__":
    main()
