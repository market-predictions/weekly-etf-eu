from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_enriched_cockpit_render_v1"

TRUE_FIELDS = [
    "render_created",
    "deterministic_renderer_created",
    "english_markdown_rendered",
    "dutch_markdown_rendered",
    "english_html_rendered",
    "dutch_html_rendered",
    "candidate_universe_preserved",
    "candidate_evidence_map_rendered",
    "proxy_separation_map_rendered",
    "reader_action_map_rendered",
    "blocker_panel_rendered",
    "debug_surface_reduced",
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
    "source_universe_enrichment_manifest_path",
    "english_rendered_cockpit_markdown_path",
    "dutch_rendered_cockpit_markdown_path",
    "english_rendered_cockpit_html_path",
    "dutch_rendered_cockpit_html_path",
    "authorization_decision_artifact_path",
    "renderer_path",
    "render_validator_path",
    "render_tests_path",
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
]
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
FORBIDDEN_AUTHORITY_STATUSES = {
    "fundable",
    "promoted",
    "buy",
    "portfolio_holding",
    "delivery_authorized",
    "valuation_grade",
}


class EtfEuEnrichedCockpitRenderError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise EtfEuEnrichedCockpitRenderError("manifest root must be object")
    return data


def _require_path(payload: dict[str, Any], key: str) -> Path:
    raw = str(payload.get(key) or "").strip()
    if not raw:
        raise EtfEuEnrichedCockpitRenderError(f"{key} missing")
    path = Path(raw)
    if not path.exists():
        raise EtfEuEnrichedCockpitRenderError(f"{key} does not exist: {raw}")
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
            raise EtfEuEnrichedCockpitRenderError(f"{path} missing required term: {term}")

    if not any(term in lower for term in REQUIRED_POC_TERMS):
        raise EtfEuEnrichedCockpitRenderError(f"{path} missing proof-of-concept / POC wording")

    if "cockpit" not in lower:
        raise EtfEuEnrichedCockpitRenderError(f"{path} missing cockpit wording")

    if "review-only" not in lower:
        raise EtfEuEnrichedCockpitRenderError(f"{path} missing review-only wording")

    main = _main_body(text)
    for term in FORBIDDEN_MAIN_BODY_TERMS:
        if term in main:
            raise EtfEuEnrichedCockpitRenderError(f"{path} main body contains debug-like term: {term}")

    dangerous_phrases = [
        " is fundable",
        " status: fundable",
        "| fundable |",
        " status: promoted",
        "| promoted |",
        " buy signal",
        " portfolio_holding",
        " delivery_authorized=true",
        " valuation_grade=true",
    ]
    lower_main = main.lower()
    for phrase in dangerous_phrases:
        if phrase in lower_main:
            raise EtfEuEnrichedCockpitRenderError(f"{path} main body contains authority-creating phrase: {phrase}")


def _validate_statuses(payload: dict[str, Any], source_payload: dict[str, Any]) -> None:
    statuses = payload.get("visible_candidate_statuses")
    if not isinstance(statuses, dict) or not statuses:
        raise EtfEuEnrichedCockpitRenderError("visible_candidate_statuses must be a populated object")

    for key, status in statuses.items():
        if status not in ALLOWED_COCKPIT_STATUSES:
            raise EtfEuEnrichedCockpitRenderError(f"invalid cockpit status for {key}: {status}")
        if str(status).lower() in FORBIDDEN_AUTHORITY_STATUSES:
            raise EtfEuEnrichedCockpitRenderError(f"forbidden authority status for {key}: {status}")

    source_candidates = source_payload.get("visible_candidates")
    if not isinstance(source_candidates, list):
        raise EtfEuEnrichedCockpitRenderError("source visible_candidates must be a list")

    if payload.get("visible_candidate_count") != len(source_candidates):
        raise EtfEuEnrichedCockpitRenderError("render visible_candidate_count does not match source")

    source_statuses = [candidate.get("cockpit_status") for candidate in source_candidates]
    if sorted(statuses.values()) != sorted(source_statuses):
        raise EtfEuEnrichedCockpitRenderError("render candidate statuses do not match source statuses")


def validate_enriched_cockpit_render(path: Path) -> dict[str, str]:
    payload = _load_json(path)

    if payload.get("schema_version") != SCHEMA_VERSION:
        raise EtfEuEnrichedCockpitRenderError("bad schema_version")
    if payload.get("status") != "completed":
        raise EtfEuEnrichedCockpitRenderError("status must be completed")
    if payload.get("delivery_authorization_decision") != "remain_blocked":
        raise EtfEuEnrichedCockpitRenderError("delivery_authorization_decision must be remain_blocked")

    for field in TRUE_FIELDS:
        if payload.get(field) is not True:
            raise EtfEuEnrichedCockpitRenderError(f"{field} must be true")

    for field in FALSE_FIELDS:
        if payload.get(field) is not False:
            raise EtfEuEnrichedCockpitRenderError(f"{field} must be false")

    if not isinstance(payload.get("visible_candidate_count"), int) or payload["visible_candidate_count"] < 2:
        raise EtfEuEnrichedCockpitRenderError("visible_candidate_count must be >= 2")

    paths = {key: _require_path(payload, key) for key in PATH_FIELDS}
    source_payload = _load_json(paths["source_universe_enrichment_manifest_path"])

    _validate_statuses(payload, source_payload)
    _validate_report_text(paths["english_rendered_cockpit_markdown_path"])
    _validate_report_text(paths["dutch_rendered_cockpit_markdown_path"])

    for hash_key in [
        "source_manifest_hash",
        "english_markdown_hash",
        "dutch_markdown_hash",
        "english_html_hash",
        "dutch_html_hash",
    ]:
        value = str(payload.get(hash_key) or "")
        if len(value) != 64:
            raise EtfEuEnrichedCockpitRenderError(f"{hash_key} must be a sha256 hex digest")

    selected_next_package = str(payload.get("selected_next_package") or "").strip()
    if not selected_next_package:
        raise EtfEuEnrichedCockpitRenderError("selected_next_package missing")

    print(
        "ETF_EU_ENRICHED_COCKPIT_RENDER_OK | "
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
    validate_enriched_cockpit_render(Path(args.artifact))


if __name__ == "__main__":
    main()
