from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_client_poc_surface_v1"
TRUE_FIELDS = [
    "client_surface_created",
    "debug_surface_reduced",
    "technical_evidence_moved_to_appendix",
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
    "english_source_report_path",
    "dutch_source_report_path",
    "english_poc_markdown_path",
    "dutch_poc_markdown_path",
    "english_poc_html_path",
    "dutch_poc_html_path",
    "authorization_decision_artifact_path",
]
REQUIRED_TERMS = ["UCITS", "IE00B5BMR087", "CSPX.L", "SXR8.DE", "SPY"]
FORBIDDEN_MAIN_BODY_TERMS = [
    "ETF_EU_",
    "tests/test_",
    "tools/validate_",
    "selected_next_package",
    "schema_version",
    "artifact=",
]


class EtfEuClientPocSurfaceError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise EtfEuClientPocSurfaceError("manifest root must be object")
    return data


def _require_path(payload: dict[str, Any], key: str) -> Path:
    raw = str(payload.get(key) or "").strip()
    if not raw:
        raise EtfEuClientPocSurfaceError(f"{key} missing")
    path = Path(raw)
    if not path.exists():
        raise EtfEuClientPocSurfaceError(f"{key} does not exist: {raw}")
    return path


def _main_body(text: str) -> str:
    markers = ["## Appendix", "## Bijlage"]
    indexes = [text.find(marker) for marker in markers if text.find(marker) != -1]
    if not indexes:
        return text
    return text[: min(indexes)]


def _validate_report_text(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for term in REQUIRED_TERMS:
        if term not in text:
            raise EtfEuClientPocSurfaceError(f"{path} missing required term: {term}")
    lower = text.lower()
    if "review-only" not in lower and "proof of concept" not in lower and "proof-of-concept" not in lower:
        raise EtfEuClientPocSurfaceError(f"{path} missing review-only or proof-of-concept wording")
    main = _main_body(text)
    for term in FORBIDDEN_MAIN_BODY_TERMS:
        if term in main:
            raise EtfEuClientPocSurfaceError(f"main body contains debug-like term: {term}")


def validate_client_poc_surface(path: Path) -> dict[str, str]:
    payload = _load_json(path)
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise EtfEuClientPocSurfaceError("bad schema_version")
    if payload.get("status") != "completed":
        raise EtfEuClientPocSurfaceError("status must be completed")
    if payload.get("delivery_authorization_decision") != "remain_blocked":
        raise EtfEuClientPocSurfaceError("delivery_authorization_decision must be remain_blocked")
    for field in TRUE_FIELDS:
        if payload.get(field) is not True:
            raise EtfEuClientPocSurfaceError(f"{field} must be true")
    for field in FALSE_FIELDS:
        if payload.get(field) is not False:
            raise EtfEuClientPocSurfaceError(f"{field} must be false")
    paths = {key: _require_path(payload, key) for key in PATH_FIELDS}
    _validate_report_text(paths["english_poc_markdown_path"])
    _validate_report_text(paths["dutch_poc_markdown_path"])
    if not str(payload.get("selected_next_package") or "").strip():
        raise EtfEuClientPocSurfaceError("selected_next_package missing")
    print(f"ETF_EU_CLIENT_POC_SURFACE_OK | artifact={path} | selected_next_package={payload['selected_next_package']}")
    return {"status": "valid", "artifact": str(path), "selected_next_package": str(payload["selected_next_package"])}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_client_poc_surface(Path(args.artifact))


if __name__ == "__main__":
    main()
