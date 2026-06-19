from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_cockpit_universe_enrichment_v1"

TRUE_FIELDS = [
    "universe_enrichment_created",
    "enriched_cockpit_surface_created",
    "candidate_universe_expanded",
    "candidate_evidence_map_created",
    "proxy_separation_map_created",
    "reader_action_map_created",
    "blocker_panel_created",
    "debug_surface_reduced",
    "ucits_identity_preserved",
    "proxy_separation_preserved",
    "pricing_evidence_preserved",
]

FALSE_FIELDS = [
    "delivery_authorized",
    "production_delivery",
    "portfolio_mutation",
    "candidate_promotion",
    "funding_authority",
    "valuation_grade",
]

PATH_FIELDS = [
    "source_premium_cockpit_manifest_path",
    "source_symbol_registry_path",
    "source_proxy_map_path",
    "english_enriched_cockpit_markdown_path",
    "dutch_enriched_cockpit_markdown_path",
    "english_enriched_cockpit_html_path",
    "dutch_enriched_cockpit_html_path",
    "authorization_decision_artifact_path",
]

REQUIRED_TERMS = ["UCITS", "IE00B5BMR087", "CSPX.L", "SXR8.DE", "SPY"]
REQUIRED_POC_TERMS = ["proof of concept", "proof-of-concept", "poc"]
FORBIDDEN_MAIN_BODY_TERMS = [
    "tests/test_",
    "tools/validate_",
    "schema_version",
    "selected_next_package",
    "artifact=",
]
ALLOWED_COCKPIT_STATUSES = {
    "visible_review_candidate",
    "identity_incomplete",
    "pricing_incomplete",
    "proxy_only_mapping",
    "blocked_until_verified",
}
FORBIDDEN_CANDIDATE_STATUSES = {
    "fundable",
    "promoted",
    "buy",
    "portfolio_holding",
    "delivery_authorized",
    "valuation_grade",
}


class EtfEuCockpitUniverseEnrichmentError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise EtfEuCockpitUniverseEnrichmentError("manifest root must be object")
    return data


def _require_path(payload: dict[str, Any], key: str) -> Path:
    raw = str(payload.get(key) or "").strip()
    if not raw:
        raise EtfEuCockpitUniverseEnrichmentError(f"{key} missing")
    path = Path(raw)
    if not path.exists():
        raise EtfEuCockpitUniverseEnrichmentError(f"{key} does not exist: {raw}")
    return path


def _main_body(text: str) -> str:
    markers = ["## Appendix", "## Bijlage"]
    indexes = [text.find(marker) for marker in markers if text.find(marker) != -1]
    if not indexes:
        return text
    return text[: min(indexes)]


def _validate_report_text(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    lower = text.lower()

    for term in REQUIRED_TERMS:
        if term not in text:
            raise EtfEuCockpitUniverseEnrichmentError(f"{path} missing required term: {term}")

    if not any(term in lower for term in REQUIRED_POC_TERMS):
        raise EtfEuCockpitUniverseEnrichmentError(f"{path} missing proof-of-concept / POC wording")

    if "cockpit" not in lower:
        raise EtfEuCockpitUniverseEnrichmentError(f"{path} missing cockpit wording")

    if "review-only" not in lower:
        raise EtfEuCockpitUniverseEnrichmentError(f"{path} missing review-only wording")

    main = _main_body(text)
    for term in FORBIDDEN_MAIN_BODY_TERMS:
        if term in main:
            raise EtfEuCockpitUniverseEnrichmentError(f"{path} main body contains debug-like term: {term}")


def _validate_visible_candidates(payload: dict[str, Any]) -> None:
    count = payload.get("visible_candidate_count")
    if not isinstance(count, int) or count < 1:
        raise EtfEuCockpitUniverseEnrichmentError("visible_candidate_count must be >= 1")

    candidates = payload.get("visible_candidates")
    if not isinstance(candidates, list) or len(candidates) != count:
        raise EtfEuCockpitUniverseEnrichmentError("visible_candidates must be a list matching visible_candidate_count")

    if count < 2:
        raise EtfEuCockpitUniverseEnrichmentError("candidate_universe_expanded requires at least two visible candidates")

    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise EtfEuCockpitUniverseEnrichmentError("visible candidate must be object")
        status = str(candidate.get("cockpit_status") or "").strip()
        if status not in ALLOWED_COCKPIT_STATUSES:
            raise EtfEuCockpitUniverseEnrichmentError(f"invalid cockpit_status: {status}")
        lowered_values = {str(value).strip().lower() for value in candidate.values() if not isinstance(value, (dict, list))}
        if lowered_values & FORBIDDEN_CANDIDATE_STATUSES:
            raise EtfEuCockpitUniverseEnrichmentError(f"forbidden candidate authority status found: {lowered_values & FORBIDDEN_CANDIDATE_STATUSES}")
        for required in ["isin", "fund_name", "trading_lines", "research_proxies", "evidence_status", "evidence_gaps", "reader_meaning"]:
            if required not in candidate:
                raise EtfEuCockpitUniverseEnrichmentError(f"visible candidate missing {required}")

    combined = json.dumps(candidates)
    for term in ["IE00B5BMR087", "CSPX.L", "SXR8.DE", "SPY"]:
        if term not in combined:
            raise EtfEuCockpitUniverseEnrichmentError(f"visible_candidates missing required term: {term}")


def validate_cockpit_universe_enrichment(path: Path) -> dict[str, str]:
    payload = _load_json(path)

    if payload.get("schema_version") != SCHEMA_VERSION:
        raise EtfEuCockpitUniverseEnrichmentError("bad schema_version")
    if payload.get("status") != "completed":
        raise EtfEuCockpitUniverseEnrichmentError("status must be completed")
    if payload.get("delivery_authorization_decision") != "remain_blocked":
        raise EtfEuCockpitUniverseEnrichmentError("delivery_authorization_decision must be remain_blocked")

    for field in TRUE_FIELDS:
        if payload.get(field) is not True:
            raise EtfEuCockpitUniverseEnrichmentError(f"{field} must be true")

    for field in FALSE_FIELDS:
        if payload.get(field) is not False:
            raise EtfEuCockpitUniverseEnrichmentError(f"{field} must be false")

    paths = {key: _require_path(payload, key) for key in PATH_FIELDS}
    _validate_report_text(paths["english_enriched_cockpit_markdown_path"])
    _validate_report_text(paths["dutch_enriched_cockpit_markdown_path"])
    _validate_visible_candidates(payload)

    selected_next_package = str(payload.get("selected_next_package") or "").strip()
    if not selected_next_package:
        raise EtfEuCockpitUniverseEnrichmentError("selected_next_package missing")

    print(
        "ETF_EU_COCKPIT_UNIVERSE_ENRICHMENT_OK | "
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
    validate_cockpit_universe_enrichment(Path(args.artifact))


if __name__ == "__main__":
    main()
