from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_premium_cockpit_surface_v1"

TRUE_FIELDS = [
    "cockpit_surface_created",
    "premium_starting_page_created",
    "hero_block_created",
    "status_cards_created",
    "reader_action_map_created",
    "blocker_panel_created",
    "technical_appendix_preserved",
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
    "source_client_surface_manifest_path",
    "english_cockpit_markdown_path",
    "dutch_cockpit_markdown_path",
    "english_cockpit_html_path",
    "dutch_cockpit_html_path",
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


class EtfEuPremiumCockpitSurfaceError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise EtfEuPremiumCockpitSurfaceError("manifest root must be object")
    return data


def _require_path(payload: dict[str, Any], key: str) -> Path:
    raw = str(payload.get(key) or "").strip()
    if not raw:
        raise EtfEuPremiumCockpitSurfaceError(f"{key} missing")
    path = Path(raw)
    if not path.exists():
        raise EtfEuPremiumCockpitSurfaceError(f"{key} does not exist: {raw}")
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
            raise EtfEuPremiumCockpitSurfaceError(f"{path} missing required term: {term}")

    if not any(term in lower for term in REQUIRED_POC_TERMS):
        raise EtfEuPremiumCockpitSurfaceError(f"{path} missing proof-of-concept / POC wording")

    if "cockpit" not in lower:
        raise EtfEuPremiumCockpitSurfaceError(f"{path} missing cockpit wording")

    main = _main_body(text)
    for term in FORBIDDEN_MAIN_BODY_TERMS:
        if term in main:
            raise EtfEuPremiumCockpitSurfaceError(f"{path} main body contains debug-like term: {term}")


def validate_premium_cockpit_surface(path: Path) -> dict[str, str]:
    payload = _load_json(path)

    if payload.get("schema_version") != SCHEMA_VERSION:
        raise EtfEuPremiumCockpitSurfaceError("bad schema_version")
    if payload.get("status") != "completed":
        raise EtfEuPremiumCockpitSurfaceError("status must be completed")
    if payload.get("delivery_authorization_decision") != "remain_blocked":
        raise EtfEuPremiumCockpitSurfaceError("delivery_authorization_decision must be remain_blocked")

    for field in TRUE_FIELDS:
        if payload.get(field) is not True:
            raise EtfEuPremiumCockpitSurfaceError(f"{field} must be true")

    for field in FALSE_FIELDS:
        if payload.get(field) is not False:
            raise EtfEuPremiumCockpitSurfaceError(f"{field} must be false")

    paths = {key: _require_path(payload, key) for key in PATH_FIELDS}

    _validate_report_text(paths["english_cockpit_markdown_path"])
    _validate_report_text(paths["dutch_cockpit_markdown_path"])

    selected_next_package = str(payload.get("selected_next_package") or "").strip()
    if not selected_next_package:
        raise EtfEuPremiumCockpitSurfaceError("selected_next_package missing")

    print(
        "ETF_EU_PREMIUM_COCKPIT_SURFACE_OK | "
        f"artifact={path} | selected_next_package={selected_next_package}"
    )
    return {"status": "valid", "artifact": str(path), "selected_next_package": selected_next_package}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_premium_cockpit_surface(Path(args.artifact))


if __name__ == "__main__":
    main()
