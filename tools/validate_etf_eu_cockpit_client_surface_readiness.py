from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_cockpit_client_surface_readiness_v1"
READY = "ready_for_client_surface_review"
TRUE_FIELDS = [
    "readiness_gate_created",
    "client_surface_readiness_assessed",
    "pricing_evidence_clarity_assessed",
    "authority_boundary_clarity_assessed",
    "proxy_separation_clarity_assessed",
    "candidate_status_clarity_assessed",
    "dutch_english_surface_parity_assessed",
    "debug_surface_hygiene_assessed",
    "no_delivery_guard_preserved",
    "no_portfolio_mutation_guard_preserved",
    "no_candidate_promotion_guard_preserved",
    "no_funding_authority_guard_preserved",
    "no_valuation_grade_guard_preserved",
]
FALSE_FIELDS = ["production_delivery", "portfolio_mutation", "candidate_promotion", "funding_authority", "valuation_grade"]
PATH_FIELDS = [
    "source_pricing_integration_manifest_path",
    "source_pricing_line_expansion_manifest_path",
    "source_english_pricing_integrated_cockpit_markdown_path",
    "source_dutch_pricing_integrated_cockpit_markdown_path",
    "source_english_pricing_integrated_cockpit_html_path",
    "source_dutch_pricing_integrated_cockpit_html_path",
    "authorization_decision_artifact_path",
    "readiness_notes_path",
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
FORBIDDEN_AUTHORITY_PHRASES = [
    "delivery authorization granted",
    "production delivery authorized",
    "buy signal",
    "fund decision",
    "valuation-grade evidence",
    "smh is safe ucits pricing evidence",
    "spy is an eu holding",
    "smh is an eu holding",
    "gld is an eu holding",
    "pave is an eu holding",
    "gld is an eu pricing line",
    "pave is an eu pricing line",
]


class EtfEuClientSurfaceReadinessError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise EtfEuClientSurfaceReadinessError("artifact root must be object")
    return data


def _require_path(payload: dict[str, Any], key: str) -> Path:
    raw = str(payload.get(key) or "").strip()
    if not raw:
        raise EtfEuClientSurfaceReadinessError(f"{key} missing")
    path = Path(raw)
    if not path.exists():
        raise EtfEuClientSurfaceReadinessError(f"{key} does not exist: {raw}")
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
            raise EtfEuClientSurfaceReadinessError(f"{path} missing required term: {term}")
    for term in FORBIDDEN_MAIN_BODY_TERMS:
        if term in main:
            raise EtfEuClientSurfaceReadinessError(f"{path} main body contains debug-like term: {term}")
    lower = main.lower()
    for phrase in FORBIDDEN_AUTHORITY_PHRASES:
        if phrase in lower:
            raise EtfEuClientSurfaceReadinessError(f"{path} contains forbidden phrase: {phrase}")


def _validate_dimensions(payload: dict[str, Any]) -> None:
    dimensions = payload.get("readiness_dimensions")
    if not isinstance(dimensions, dict):
        raise EtfEuClientSurfaceReadinessError("readiness_dimensions must be object")
    expected = {
        "client_surface_clarity",
        "pricing_evidence_clarity",
        "authority_boundary_clarity",
        "proxy_separation_clarity",
        "candidate_status_clarity",
        "dutch_english_surface_parity",
        "debug_surface_hygiene",
        "no_delivery_guard",
        "no_portfolio_mutation_guard",
        "no_candidate_promotion_guard",
        "no_funding_authority_guard",
        "no_valuation_grade_guard",
    }
    if set(dimensions) != expected:
        raise EtfEuClientSurfaceReadinessError("readiness_dimensions keys mismatch")
    for name, dimension in dimensions.items():
        if dimension.get("status") != READY:
            raise EtfEuClientSurfaceReadinessError(f"{name} not ready")
        evidence = dimension.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise EtfEuClientSurfaceReadinessError(f"{name} missing evidence")


def validate_client_surface_readiness(path: Path) -> dict[str, str]:
    payload = _load_json(path)
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise EtfEuClientSurfaceReadinessError("bad schema_version")
    if payload.get("status") != "completed":
        raise EtfEuClientSurfaceReadinessError("status must be completed")
    if payload.get("overall_readiness_status") != READY:
        raise EtfEuClientSurfaceReadinessError("overall_readiness_status must be ready_for_client_surface_review")
    if payload.get("delivery_authorization_decision") != "remain_blocked":
        raise EtfEuClientSurfaceReadinessError("delivery_authorization_decision must remain blocked")
    if payload.get("visible_candidate_count") != 4:
        raise EtfEuClientSurfaceReadinessError("visible_candidate_count must be 4")
    for field in TRUE_FIELDS:
        if payload.get(field) is not True:
            raise EtfEuClientSurfaceReadinessError(f"{field} must be true")
    for field in FALSE_FIELDS:
        if payload.get(field) is not False:
            raise EtfEuClientSurfaceReadinessError(f"{field} must be false")
    _validate_dimensions(payload)
    paths = {key: _require_path(payload, key) for key in PATH_FIELDS}
    _validate_markdown(paths["source_english_pricing_integrated_cockpit_markdown_path"])
    _validate_markdown(paths["source_dutch_pricing_integrated_cockpit_markdown_path"])
    notes = paths["readiness_notes_path"].read_text(encoding="utf-8")
    for term in ["proof-of-concept", "not a production-delivery artifact", "CSPX.L", "SXR8.DE", "SMH", "Gold/ETC", "Infrastructure", "research proxies only"]:
        if term not in notes:
            raise EtfEuClientSurfaceReadinessError(f"notes missing term: {term}")
    selected_next_package = str(payload.get("selected_next_package") or "").strip()
    if not selected_next_package:
        raise EtfEuClientSurfaceReadinessError("selected_next_package missing")
    print(
        "ETF_EU_COCKPIT_CLIENT_SURFACE_READINESS_OK | "
        f"artifact={path} | overall_readiness_status={payload['overall_readiness_status']} | "
        f"selected_next_package={selected_next_package}"
    )
    return {"status": "valid", "artifact": str(path), "overall_readiness_status": payload["overall_readiness_status"], "selected_next_package": selected_next_package}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_client_surface_readiness(Path(args.artifact))


if __name__ == "__main__":
    main()
