from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_cockpit_pricing_integration_v1"
TRUE_FIELDS = [
    "pricing_integration_created",
    "pricing_integrated_cockpit_surface_created",
    "pricing_line_evidence_rendered",
    "candidate_pricing_evidence_preserved",
    "pricing_line_status_map_preserved",
    "unsafe_pricing_symbol_guard_rendered",
    "proxy_ambiguity_guard_rendered",
    "valuation_grade_guard_rendered",
    "funding_authority_guard_rendered",
    "candidate_promotion_guard_rendered",
    "ucits_identity_preserved",
    "proxy_separation_preserved",
    "pricing_evidence_preserved",
    "debug_surface_reduced",
]
FALSE_FIELDS = ["production_delivery", "portfolio_mutation", "candidate_promotion", "funding_authority", "valuation_grade"]
PATH_FIELDS = [
    "source_enriched_cockpit_render_manifest_path",
    "source_universe_enrichment_manifest_path",
    "source_pricing_line_expansion_manifest_path",
    "source_pricing_line_expansion_notes_path",
    "authorization_decision_artifact_path",
    "english_pricing_integrated_cockpit_markdown_path",
    "dutch_pricing_integrated_cockpit_markdown_path",
    "english_pricing_integrated_cockpit_html_path",
    "dutch_pricing_integrated_cockpit_html_path",
    "renderer_path",
    "validator_path",
    "tests_path",
]
REQUIRED_TERMS = [
    "UCITS",
    "IE00B5BMR087",
    "IE00BMC38736",
    "CSPX.L",
    "SXR8.DE",
    "SPY",
    "SMH",
    "GLD",
    "PAVE",
    "source_evidence_available",
    "usable_for_review_only",
    "pricing_symbol_ambiguous",
    "policy_blocked",
    "identity_incomplete",
    "review-only",
    "delivery_authorization_decision=remain_blocked",
    "production_delivery=false",
    "portfolio_mutation=false",
    "candidate_promotion=false",
    "funding_authority=false",
    "valuation_grade=false",
]
FORBIDDEN_MAIN_BODY_TERMS = ["tests/test_", "tools/validate_", "schema_version", "selected_next_package", "artifact="]


class EtfEuCockpitPricingIntegrationError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise EtfEuCockpitPricingIntegrationError("manifest root must be object")
    return data


def _require_path(payload: dict[str, Any], key: str) -> Path:
    raw = str(payload.get(key) or "").strip()
    if not raw:
        raise EtfEuCockpitPricingIntegrationError(f"{key} missing")
    path = Path(raw)
    if not path.exists():
        raise EtfEuCockpitPricingIntegrationError(f"{key} does not exist: {raw}")
    return path


def _main_body(text: str) -> str:
    markers = ["## Appendix", "## Bijlage"]
    indexes = [text.find(marker) for marker in markers if text.find(marker) != -1]
    if not indexes:
        return text
    return text[: min(indexes)]


def _validate_markdown(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    main = _main_body(text)
    for term in REQUIRED_TERMS:
        if term not in text:
            raise EtfEuCockpitPricingIntegrationError(f"{path} missing required term: {term}")
    for term in FORBIDDEN_MAIN_BODY_TERMS:
        if term in main:
            raise EtfEuCockpitPricingIntegrationError(f"{path} main body contains debug-like term: {term}")
    lower = main.lower()
    forbidden_positive_phrases = [
        "smh is safe ucits pricing evidence",
        "gld is an eu holding",
        "pave is an eu holding",
        "spy is an eu holding",
        "delivery_authorization_decision=authorized",
        "production_delivery=true",
        "portfolio_mutation=true",
        "candidate_promotion=true",
        "funding_authority=true",
        "valuation_grade=true",
    ]
    for phrase in forbidden_positive_phrases:
        if phrase in lower:
            raise EtfEuCockpitPricingIntegrationError(f"{path} contains forbidden authority phrase: {phrase}")


def _validate_pricing_source(path: Path) -> None:
    pricing = _load_json(path)
    for candidate in pricing.get("candidate_pricing_evidence", []):
        for field in ["safe_for_valuation_grade", "safe_for_funding_decision", "safe_for_candidate_promotion"]:
            if candidate.get(field) is not False:
                raise EtfEuCockpitPricingIntegrationError(f"{candidate.get('candidate_id')} {field} must be false")
    by_id = {candidate.get("candidate_id"): candidate for candidate in pricing.get("candidate_pricing_evidence", [])}
    smh = by_id.get("IE00BMC38736")
    if not smh or smh.get("safe_for_cockpit_pricing_evidence") is not False:
        raise EtfEuCockpitPricingIntegrationError("SMH candidate must not be safe for cockpit pricing evidence")


def validate_cockpit_pricing_integration(path: Path) -> dict[str, str]:
    payload = _load_json(path)
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise EtfEuCockpitPricingIntegrationError("bad schema_version")
    if payload.get("status") != "completed":
        raise EtfEuCockpitPricingIntegrationError("status must be completed")
    if payload.get("delivery_authorization_decision") != "remain_blocked":
        raise EtfEuCockpitPricingIntegrationError("delivery_authorization_decision must be remain_blocked")
    for field in TRUE_FIELDS:
        if payload.get(field) is not True:
            raise EtfEuCockpitPricingIntegrationError(f"{field} must be true")
    for field in FALSE_FIELDS:
        if payload.get(field) is not False:
            raise EtfEuCockpitPricingIntegrationError(f"{field} must be false")
    if payload.get("visible_candidate_count") != 4:
        raise EtfEuCockpitPricingIntegrationError("visible_candidate_count must be 4")
    expected_summary = {"source_evidence_available": 1, "pricing_symbol_ambiguous": 1, "policy_blocked": 1, "identity_incomplete": 1}
    if payload.get("pricing_line_status_summary") != expected_summary:
        raise EtfEuCockpitPricingIntegrationError("pricing_line_status_summary not preserved")
    unsafe = json.dumps(payload.get("unsafe_pricing_symbols", []))
    for symbol in ["SMH", "GLD", "PAVE"]:
        if symbol not in unsafe:
            raise EtfEuCockpitPricingIntegrationError(f"unsafe_pricing_symbols missing {symbol}")
    paths = {key: _require_path(payload, key) for key in PATH_FIELDS}
    _validate_pricing_source(paths["source_pricing_line_expansion_manifest_path"])
    _validate_markdown(paths["english_pricing_integrated_cockpit_markdown_path"])
    _validate_markdown(paths["dutch_pricing_integrated_cockpit_markdown_path"])
    selected_next_package = str(payload.get("selected_next_package") or "").strip()
    if not selected_next_package:
        raise EtfEuCockpitPricingIntegrationError("selected_next_package missing")
    print(
        "ETF_EU_COCKPIT_PRICING_INTEGRATION_OK | "
        f"artifact={path} | visible_candidate_count={payload['visible_candidate_count']} | "
        f"selected_next_package={selected_next_package}"
    )
    return {"status": "valid", "artifact": str(path), "selected_next_package": selected_next_package, "visible_candidate_count": str(payload["visible_candidate_count"])}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_cockpit_pricing_integration(Path(args.artifact))


if __name__ == "__main__":
    main()
