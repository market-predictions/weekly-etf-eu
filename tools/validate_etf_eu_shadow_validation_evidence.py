from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_shadow_validation_evidence_v1"
DEFAULT_OUTPUT_DIR = Path("output/validation")
AUTHORITY_FLAGS = ["production_delivery", "portfolio_mutation", "funding_authority", "valuation_authority", "email_delivery", "pdf_render", "delivery_receipt"]
REQUIRED_TOP_LEVEL_TRUE = ["not_delivery_receipt", "shadow_validation_only"]
REQUIRED_ARTIFACT_KINDS = {
    "pricing_candidates",
    "pricing_preflight",
    "valuation_prices",
    "official_exchange_source_snapshot",
    "official_exchange_page_evidence",
    "close_observations",
    "euronext_endpoint_evidence",
    "euronext_product_page_evidence",
    "euronext_dynamic_quote_response_discovery",
    "euronext_js_asset_inspection",
    "twelve_data_symbol_discovery",
    "english_companion_report",
    "dutch_primary_report",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_file(output_dir: Path) -> Path:
    files = sorted(output_dir.glob("etf_eu_shadow_validation_evidence_*.json"))
    if not files:
        raise RuntimeError(f"No ETF EU shadow validation evidence artifacts found in {output_dir}")
    return files[-1]


def text(value: Any) -> str:
    return str(value or "").strip()


def validate(path: Path) -> None:
    payload = load_json(path)
    errors: list[str] = []
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version_must_be_etf_eu_shadow_validation_evidence_v1")
    if payload.get("evidence_type") != "non_production_shadow_validation":
        errors.append("evidence_type_must_be_non_production_shadow_validation")
    if payload.get("validation_status") != "passed":
        errors.append("validation_status_must_be_passed")
    if not text(payload.get("run_id")):
        errors.append("run_id_required")
    if not text(payload.get("report_date")):
        errors.append("report_date_required")
    for flag in AUTHORITY_FLAGS:
        if payload.get(flag) is not False:
            errors.append(f"{flag}_must_be_false")
    for field in REQUIRED_TOP_LEVEL_TRUE:
        if payload.get(field) is not True:
            errors.append(f"{field}_must_be_true")
    workflow = payload.get("workflow") or {}
    if not isinstance(workflow, dict):
        errors.append("workflow_must_be_object")
    elif not text(workflow.get("name")):
        errors.append("workflow_name_required")

    artifacts = payload.get("required_artifacts") or []
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("required_artifacts_must_be_non_empty_list")
    else:
        kinds = {text(item.get("kind")) for item in artifacts if isinstance(item, dict)}
        missing = REQUIRED_ARTIFACT_KINDS - kinds
        if missing:
            errors.append("missing_required_artifact_kinds:" + ",".join(sorted(missing)))
        for idx, item in enumerate(artifacts):
            label = f"required_artifact:{idx}"
            if not isinstance(item, dict):
                errors.append(f"{label}:must_be_object")
                continue
            if item.get("exists") is not True:
                errors.append(f"{label}:exists_must_be_true")
            if not text(item.get("path")):
                errors.append(f"{label}:path_required")
            if not text(item.get("sha256")) or len(text(item.get("sha256"))) != 64:
                errors.append(f"{label}:valid_sha256_required")
            try:
                if int(item.get("size_bytes", 0)) <= 0:
                    errors.append(f"{label}:size_bytes_must_be_positive")
            except (TypeError, ValueError):
                errors.append(f"{label}:size_bytes_must_be_integer")

    checks = payload.get("safety_checks") or []
    if not isinstance(checks, list) or not checks:
        errors.append("safety_checks_must_be_non_empty_list")
    else:
        for idx, check in enumerate(checks):
            label = f"safety_check:{idx}"
            if not isinstance(check, dict):
                errors.append(f"{label}:must_be_object")
                continue
            for field in [
                "authority_flags_false_where_present",
                "completed_session_not_true_where_present",
                "valuation_grade_not_true_where_present",
            ]:
                if check.get(field) is not True:
                    errors.append(f"{label}:{field}_must_be_true")

    markers = payload.get("validated_step_markers") or []
    if not isinstance(markers, list) or len(markers) < 10:
        errors.append("validated_step_markers_must_have_sufficient_detail")

    if errors:
        raise RuntimeError("ETF EU shadow validation evidence failed: " + "; ".join(errors))
    print(f"ETF_EU_SHADOW_VALIDATION_EVIDENCE_VALIDATION_OK | artifact={path} | artifacts={len(artifacts)} | safety_checks={len(checks)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", default=None)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    artifact = Path(args.artifact) if args.artifact else latest_file(Path(args.output_dir))
    validate(artifact)


if __name__ == "__main__":
    main()
