from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PACKAGE_SCHEMA = "etf_eu_corrected_resend_package_v1"
PREPARATION_SCHEMA = "etf_eu_corrected_resend_preparation_v1"
RUN_MANIFEST_SCHEMA = "etf_eu_corrected_resend_manifest_v1"
SOURCE_RUNTIME_RUN_ID = "20260712_182002"
UPSTREAM_PATTERN = (
    "weekly-etf explicit report-path delivery, pre-send rendered-output validation, "
    "redacted recipient manifest, transport-versus-receipt separation and final "
    "run-manifest closeout; adapted for the approved EU correction package"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"missing required artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _approved_sources(repair_run_id: str, report_suffix: str) -> dict[str, Path]:
    root = Path("output/repair_preview") / repair_run_id
    return {
        "dutch_primary_html": root / f"weekly_etf_eu_review_nl_{report_suffix}.html",
        "dutch_primary_pdf": root / f"weekly_etf_eu_review_nl_{report_suffix}.pdf",
        "english_companion_html": root / f"weekly_etf_eu_review_{report_suffix}.html",
        "english_companion_pdf": root / f"weekly_etf_eu_review_{report_suffix}.pdf",
    }


def _delivery_names(report_suffix: str) -> dict[str, str]:
    return {
        "dutch_primary_html": f"weekly_etf_eu_review_nl_{report_suffix}_gecorrigeerd.html",
        "dutch_primary_pdf": f"weekly_etf_eu_review_nl_{report_suffix}_gecorrigeerd.pdf",
        "english_companion_html": f"weekly_etf_eu_review_{report_suffix}_corrected.html",
        "english_companion_pdf": f"weekly_etf_eu_review_{report_suffix}_corrected.pdf",
    }


def prepare(
    *,
    correction_control_id: str,
    source_run_id: str,
    repair_run_id: str,
    report_date: str,
    report_suffix: str,
    output_dir: Path,
) -> dict[str, Any]:
    combined_path = Path("output/quality") / f"etf_eu_routine_pdf_client_grade_{repair_run_id}.json"
    nl_path = Path("output/quality") / f"etf_eu_routine_pdf_client_grade_{repair_run_id}_nl.json"
    en_path = Path("output/quality") / f"etf_eu_routine_pdf_client_grade_{repair_run_id}_en.json"
    visual_path = Path("output/quality") / f"etf_eu_routine_pdf_visual_review_{repair_run_id}.json"
    original_result_path = Path("output/delivery") / f"etf_eu_current_package_transport_result_{SOURCE_RUNTIME_RUN_ID}.json"
    original_evidence_path = Path("output/delivery") / f"etf_eu_current_package_delivery_evidence_{SOURCE_RUNTIME_RUN_ID}.json"

    combined = _load_json(combined_path)
    nl = _load_json(nl_path)
    en = _load_json(en_path)
    visual = _load_json(visual_path)
    original_result = _load_json(original_result_path)
    _load_json(original_evidence_path)

    _require(combined.get("source_run_id") == source_run_id, "combined machine gate source_run_id mismatch")
    _require(combined.get("repair_run_id") == repair_run_id, "combined machine gate repair_run_id mismatch")
    _require(combined.get("dutch_pdf_client_grade_passed") is True, "Dutch combined machine gate did not pass")
    _require(combined.get("english_pdf_client_grade_passed") is True, "English combined machine gate did not pass")
    _require(combined.get("pdf_client_grade_passed") is True, "combined machine gate did not pass")
    _require(not combined.get("blockers"), "combined machine gate contains blockers")
    _require(nl.get("machine_validation_passed") is True, "Dutch machine validation did not pass")
    _require(en.get("machine_validation_passed") is True, "English machine validation did not pass")
    _require(visual.get("source_run_id") == source_run_id, "visual review source_run_id mismatch")
    _require(visual.get("repair_run_id") == repair_run_id, "visual review repair_run_id mismatch")
    _require(visual.get("visual_review_passed") is True, "visual review did not pass")
    _require(not visual.get("blockers"), "visual review contains blockers")
    _require(original_result.get("transport_success") is True, "original transport success evidence missing")
    _require(original_result.get("report_date") == report_date, "original report date mismatch")
    _require(str(original_result.get("report_suffix")) == report_suffix, "original report suffix mismatch")

    sources = _approved_sources(repair_run_id, report_suffix)
    for label, path in sources.items():
        _require(path.exists(), f"approved corrected source missing: {label}={path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    names = _delivery_names(report_suffix)
    deliveries = {label: output_dir / name for label, name in names.items()}
    source_sha: dict[str, str] = {}
    delivery_sha: dict[str, str] = {}
    source_bytes: dict[str, int] = {}
    delivery_bytes: dict[str, int] = {}

    for label, source in sources.items():
        destination = deliveries[label]
        shutil.copyfile(source, destination)
        source_sha[label] = _sha256(source)
        delivery_sha[label] = _sha256(destination)
        source_bytes[label] = source.stat().st_size
        delivery_bytes[label] = destination.stat().st_size
        _require(source_sha[label] == delivery_sha[label], f"byte identity failed for {label}")
        _require(source_bytes[label] == delivery_bytes[label], f"byte size identity failed for {label}")

    generated_at = _utc_now()
    package: dict[str, Any] = {
        "schema_version": PACKAGE_SCHEMA,
        "artifact_type": "etf_eu_corrected_resend_package",
        "generated_at_utc": generated_at,
        "correction_control_id": correction_control_id,
        "source_run_id": source_run_id,
        "source_runtime_run_id": SOURCE_RUNTIME_RUN_ID,
        "repair_run_id": repair_run_id,
        "report_date": report_date,
        "report_suffix": report_suffix,
        "source_of_truth_repo": "market-predictions/weekly-etf-eu",
        "reference_architecture_repo": "market-predictions/weekly-etf",
        "upstream_pattern_adapted": UPSTREAM_PATTERN,
        "correction_reason": "The original transport succeeded, but its plain-text PDF attachments were materially incomplete.",
        "original_transport_result": str(original_result_path),
        "original_delivery_evidence": str(original_evidence_path),
        "original_client_output_valid": False,
        "combined_machine_gate_artifact": str(combined_path),
        "dutch_machine_gate_artifact": str(nl_path),
        "english_machine_gate_artifact": str(en_path),
        "visual_review_artifact": str(visual_path),
        "dutch_machine_gate_passed": True,
        "english_machine_gate_passed": True,
        "combined_machine_gate_passed": True,
        "visual_review_passed": True,
        "approved_source_files": {key: str(value) for key, value in sources.items()},
        "corrected_delivery_files": {key: str(value) for key, value in deliveries.items()},
        "source_sha256": source_sha,
        "delivery_sha256": delivery_sha,
        "source_bytes": source_bytes,
        "delivery_bytes": delivery_bytes,
        "byte_identity_passed": True,
        "corrected_client_output_valid": True,
        "recipient_plaintext_values_exposed": False,
        "secret_values_exposed": False,
        "raw_receipt_pdf_stored_in_github": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "corrected_resend_prepared": True,
        "corrected_resend_executed": False,
        "next_action": "RUN_CORRECTED_RESEND_VALIDATE_ONLY",
        "blockers": [],
        "warnings": [],
    }
    manifest_path = Path("output/delivery_control") / f"etf_eu_corrected_resend_package_{correction_control_id}.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    preparation = {
        "schema_version": PREPARATION_SCHEMA,
        "artifact_type": "etf_eu_corrected_resend_preparation",
        "generated_at_utc": generated_at,
        "correction_control_id": correction_control_id,
        "source_run_id": source_run_id,
        "repair_run_id": repair_run_id,
        "report_date": report_date,
        "report_suffix": report_suffix,
        "corrected_package_manifest": str(manifest_path),
        "corrected_resend_prepared": True,
        "corrected_resend_executed": False,
        "transport_attempted": False,
        "transport_success": False,
        "receipt_confirmed": False,
        "recipient_plaintext_values_exposed": False,
        "secret_values_exposed": False,
        "next_action": "RUN_CORRECTED_RESEND_VALIDATE_ONLY",
        "blockers": [],
    }
    preparation_path = Path("output/delivery_authorization") / f"etf_eu_corrected_resend_preparation_{correction_control_id}.json"
    preparation_path.parent.mkdir(parents=True, exist_ok=True)
    preparation_path.write_text(json.dumps(preparation, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    run_manifest = {
        "schema_version": RUN_MANIFEST_SCHEMA,
        "artifact_type": "etf_eu_corrected_resend_manifest",
        "generated_at_utc": generated_at,
        "correction_control_id": correction_control_id,
        "source_run_id": source_run_id,
        "source_runtime_run_id": SOURCE_RUNTIME_RUN_ID,
        "repair_run_id": repair_run_id,
        "report_date": report_date,
        "report_suffix": report_suffix,
        "status": "corrected_resend_prepared",
        "corrected_package_manifest": str(manifest_path),
        "corrected_queue": f"control/run_queue/etf_eu_corrected_resend_request_{correction_control_id}.md",
        "corrected_client_output_valid": True,
        "corrected_resend_executed": False,
        "transport_attempted": False,
        "transport_success": False,
        "receipt_confirmed": False,
        "next_action": "EXPLICITLY_DISPATCH_CORRECTED_RESEND",
    }
    run_manifest_path = Path("output/run_manifests") / f"etf_eu_corrected_resend_manifest_{correction_control_id}.json"
    run_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    run_manifest_path.write_text(json.dumps(run_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        "ETF_EU_CORRECTED_RESEND_PACKAGE_OK | "
        f"control_id={correction_control_id} | manifest={manifest_path} | files={len(deliveries)}"
    )
    return package


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare the immutable Weekly ETF EU corrected-resend package.")
    parser.add_argument("--correction-control-id", required=True)
    parser.add_argument("--source-run-id", required=True)
    parser.add_argument("--repair-run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    prepare(
        correction_control_id=args.correction_control_id,
        source_run_id=args.source_run_id,
        repair_run_id=args.repair_run_id,
        report_date=args.report_date,
        report_suffix=args.report_suffix,
        output_dir=Path(args.output_dir),
    )


if __name__ == "__main__":
    main()
