from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_shadow_validation_evidence_v1"
DEFAULT_OUTPUT_DIR = Path("output/validation")
AUTHORITY_FLAGS = ["portfolio_mutation", "production_delivery", "funding_authority", "valuation_authority"]

VALIDATED_STEP_MARKERS = [
    "EU control files exist",
    "EU config files exist",
    "UCITS symbol registry validation passed",
    "UCITS investability contract validation passed",
    "UCITS pricing candidates built and validated",
    "UCITS pricing preflight built and validated",
    "UCITS valuation-pricing artifact built and validated",
    "Official exchange source snapshot built and validated",
    "Official exchange page evidence built and validated",
    "Generic UCITS close observations built and validated",
    "Euronext endpoint evidence built and validated as diagnostic only",
    "Euronext product-page evidence built and validated as diagnostic only",
    "Euronext dynamic quote response discovery built and validated as diagnostic only",
    "Euronext JS asset inspection built and validated as diagnostic only",
    "Twelve Data symbol discovery built and validated as diagnostic only",
    "EU cash-only state validated",
    "No U.S.-listed ETF appears as a funded EU holding",
    "EU candidate report skeleton rendered",
    "EU output and candidate-report contracts validated",
    "Inherited U.S. production sender is disabled",
    "No portfolio mutation, PDF generation or email delivery attempted",
]


def _suffix(report_date: str) -> str:
    y, m, d = report_date.split("-")
    return f"{y[2:]}{m}{d}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_record(path: Path, kind: str) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Required shadow-validation input artifact missing: {path}")
    return {
        "kind": kind,
        "path": str(path),
        "exists": True,
        "size_bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _walk_json_objects(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        found.append(value)
        for child in value.values():
            found.extend(_walk_json_objects(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_walk_json_objects(child))
    return found


def _assert_no_authority_flags(path: Path) -> dict[str, Any]:
    payload = _load_json(path)
    violations: list[str] = []
    for obj in _walk_json_objects(payload):
        for flag in AUTHORITY_FLAGS:
            if flag in obj and obj.get(flag) is not False:
                violations.append(f"{path}:{flag}={obj.get(flag)!r}")
        if obj.get("completed_session") is True:
            violations.append(f"{path}:completed_session=True")
        if obj.get("valuation_grade") is True:
            violations.append(f"{path}:valuation_grade=True")
        if obj.get("valuation_grade_row_count") not in (None, 0):
            violations.append(f"{path}:valuation_grade_row_count={obj.get('valuation_grade_row_count')!r}")
    if violations:
        raise RuntimeError("Shadow validation evidence safety check failed: " + "; ".join(violations))
    return {
        "path": str(path),
        "authority_flags_false_where_present": True,
        "completed_session_not_true_where_present": True,
        "valuation_grade_not_true_where_present": True,
    }


def _run_url() -> str | None:
    server = os.environ.get("GITHUB_SERVER_URL")
    repo = os.environ.get("GITHUB_REPOSITORY")
    run_id = os.environ.get("GITHUB_RUN_ID")
    if server and repo and run_id:
        return f"{server}/{repo}/actions/runs/{run_id}"
    return None


def build(run_id: str, report_date: str, output_dir: Path) -> Path:
    suffix = _suffix(report_date)
    pricing_dir = Path("output/pricing")
    artifact_inputs = [
        (pricing_dir / f"ucits_pricing_candidates_{run_id}.json", "pricing_candidates"),
        (pricing_dir / f"ucits_pricing_preflight_{run_id}.json", "pricing_preflight"),
        (pricing_dir / f"ucits_valuation_prices_{run_id}.json", "valuation_prices"),
        (pricing_dir / f"ucits_official_exchange_source_snapshot_{run_id}.json", "official_exchange_source_snapshot"),
        (pricing_dir / f"ucits_official_exchange_page_evidence_{run_id}.json", "official_exchange_page_evidence"),
        (pricing_dir / f"ucits_close_observations_{run_id}.json", "close_observations"),
        (pricing_dir / f"euronext_endpoint_evidence_{run_id}.json", "euronext_endpoint_evidence"),
        (pricing_dir / f"euronext_product_page_evidence_{run_id}.json", "euronext_product_page_evidence"),
        (pricing_dir / f"euronext_dynamic_quote_response_discovery_{run_id}.json", "euronext_dynamic_quote_response_discovery"),
        (pricing_dir / f"euronext_js_asset_inspection_{run_id}.json", "euronext_js_asset_inspection"),
        (pricing_dir / f"ucits_twelve_data_symbol_discovery_{run_id}.json", "twelve_data_symbol_discovery"),
        (Path("output") / f"weekly_etf_eu_review_{suffix}.md", "english_companion_report"),
        (Path("output") / f"weekly_etf_eu_review_nl_{suffix}.md", "dutch_primary_report"),
    ]
    artifact_records = [_artifact_record(path, kind) for path, kind in artifact_inputs]
    safety_checks = [
        _assert_no_authority_flags(path)
        for path, _kind in artifact_inputs
        if path.suffix == ".json"
    ]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "evidence_type": "non_production_shadow_validation",
        "validation_status": "passed",
        "run_id": run_id,
        "report_date": report_date,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": os.environ.get("GITHUB_REPOSITORY", "market-predictions/weekly-etf-eu"),
        "workflow": {
            "name": os.environ.get("GITHUB_WORKFLOW", "Weekly ETF EU UCITS bootstrap validation"),
            "run_id": os.environ.get("GITHUB_RUN_ID"),
            "run_number": os.environ.get("GITHUB_RUN_NUMBER"),
            "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
            "sha": os.environ.get("GITHUB_SHA"),
            "ref_name": os.environ.get("GITHUB_REF_NAME"),
            "actor": os.environ.get("GITHUB_ACTOR"),
            "run_url": _run_url(),
        },
        "validation_basis": "This artifact is written after all prior EU bootstrap validation workflow steps completed successfully.",
        "production_delivery": False,
        "portfolio_mutation": False,
        "funding_authority": False,
        "valuation_authority": False,
        "email_delivery": False,
        "pdf_render": False,
        "delivery_receipt": False,
        "not_delivery_receipt": True,
        "shadow_validation_only": True,
        "validated_step_markers": VALIDATED_STEP_MARKERS,
        "required_artifacts": artifact_records,
        "safety_checks": safety_checks,
        "next_verification_instruction": "Future chats can verify this run by fetching this JSON file from output/validation/ and checking schema_version, validation_status, false authority flags, required_artifacts and safety_checks.",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"etf_eu_shadow_validation_evidence_{run_id}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"ETF_EU_SHADOW_VALIDATION_EVIDENCE_OK | artifact={path} | required_artifacts={len(artifact_records)}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    build(args.run_id, args.report_date, Path(args.output_dir))


if __name__ == "__main__":
    main()
