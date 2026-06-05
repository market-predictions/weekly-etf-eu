from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_run_bundle_manifest_v1"
DEFAULT_OUTPUT_ROOT = Path("output/runs")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_run_bundle_manifest(
    *,
    run_id: str,
    report_date: str,
    dutch_report_path: str,
    english_report_path: str,
    valuation_artifact_path: str,
    fundability_artifact_path: str,
    validation_evidence_path: str,
    delivery_manifest_path: str | None = None,
    created_at_utc: str | None = None,
) -> dict[str, Any]:
    delivery_manifest_path_or_null = delivery_manifest_path if delivery_manifest_path else None
    delivery_manifest_status = "available" if delivery_manifest_path_or_null else "not_available"

    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at_utc": created_at_utc or _utc_now(),
        "report_date": report_date,
        "dutch_report_path": dutch_report_path,
        "english_report_path": english_report_path,
        "valuation_artifact_path": valuation_artifact_path,
        "fundability_artifact_path": fundability_artifact_path,
        "validation_evidence_path": validation_evidence_path,
        "delivery_manifest_status": delivery_manifest_status,
        "delivery_manifest_path_or_null": delivery_manifest_path_or_null,
        "production_delivery": False,
        "email_delivery": False,
        "pdf_generation": False,
        "delivery_receipt": False,
    }


def write_run_bundle_manifest(
    output_root: Path,
    *,
    run_id: str,
    report_date: str,
    dutch_report_path: str,
    english_report_path: str,
    valuation_artifact_path: str,
    fundability_artifact_path: str,
    validation_evidence_path: str,
    delivery_manifest_path: str | None = None,
    created_at_utc: str | None = None,
) -> Path:
    output_dir = output_root / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = build_run_bundle_manifest(
        run_id=run_id,
        report_date=report_date,
        dutch_report_path=dutch_report_path,
        english_report_path=english_report_path,
        valuation_artifact_path=valuation_artifact_path,
        fundability_artifact_path=fundability_artifact_path,
        validation_evidence_path=validation_evidence_path,
        delivery_manifest_path=delivery_manifest_path,
        created_at_utc=created_at_utc,
    )
    path = output_dir / "etf_eu_run_bundle_manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--dutch-report-path", required=True)
    parser.add_argument("--english-report-path", required=True)
    parser.add_argument("--valuation-artifact-path", required=True)
    parser.add_argument("--fundability-artifact-path", required=True)
    parser.add_argument("--validation-evidence-path", required=True)
    parser.add_argument("--delivery-manifest-path", default=None)
    args = parser.parse_args()

    path = write_run_bundle_manifest(
        Path(args.output_root),
        run_id=args.run_id,
        report_date=args.report_date,
        dutch_report_path=args.dutch_report_path,
        english_report_path=args.english_report_path,
        valuation_artifact_path=args.valuation_artifact_path,
        fundability_artifact_path=args.fundability_artifact_path,
        validation_evidence_path=args.validation_evidence_path,
        delivery_manifest_path=args.delivery_manifest_path,
    )
    print(
        "ETF_EU_RUN_BUNDLE_MANIFEST_OK | "
        f"manifest={path} | production_delivery=false | email_delivery=false | "
        "pdf_generation=false | delivery_receipt=false"
    )


if __name__ == "__main__":
    main()
