from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT_DIR = Path("output/delivery")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_blocked_design_manifest(
    *,
    run_id: str,
    report_date: str,
    dutch_report_path: str,
    english_report_path: str,
    valuation_artifact_path: str,
    fundability_artifact_path: str,
    validation_evidence_paths: list[str] | None = None,
    created_at_utc: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "etf_eu_delivery_manifest_v1",
        "run_id": run_id,
        "created_at_utc": created_at_utc or _utc_now(),
        "report_date": report_date,
        "status": "blocked_design_only",
        "delivery_enabled": False,
        "gates": {
            "main_workflow_green": True,
            "dutch_first_report_contract_green": True,
            "fundability_rules_clear": True,
            "delivery_manifest_exists": True,
            "receipt_path_exists": False,
        },
        "artifacts": {
            "dutch_report_path": dutch_report_path,
            "english_report_path": english_report_path,
            "valuation_artifact_path": valuation_artifact_path,
            "fundability_artifact_path": fundability_artifact_path,
            "validation_evidence_paths": validation_evidence_paths or [],
        },
        "receipt": {
            "receipt_required": True,
            "receipt_path": "",
            "receipt_status": "not_created",
        },
        "authority": {
            "funding_authority": False,
            "portfolio_mutation": False,
            "valuation_grade_promotion": False,
            "candidate_promotion_to_fundable": False,
            "pdf_generation": False,
            "email_delivery": False,
            "delivery_receipt": False,
            "production_delivery": False,
        },
        "blockers": [
            "delivery implementation not enabled",
            "receipt path not created",
            "email delivery not authorized",
            "PDF generation not authorized",
        ],
    }


def write_blocked_design_manifest(
    output_dir: Path,
    *,
    run_id: str,
    report_date: str,
    dutch_report_path: str,
    english_report_path: str,
    valuation_artifact_path: str,
    fundability_artifact_path: str,
    validation_evidence_paths: list[str] | None = None,
    created_at_utc: str | None = None,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = build_blocked_design_manifest(
        run_id=run_id,
        report_date=report_date,
        dutch_report_path=dutch_report_path,
        english_report_path=english_report_path,
        valuation_artifact_path=valuation_artifact_path,
        fundability_artifact_path=fundability_artifact_path,
        validation_evidence_paths=validation_evidence_paths,
        created_at_utc=created_at_utc,
    )
    path = output_dir / f"etf_eu_delivery_manifest_{run_id}.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--dutch-report-path", required=True)
    parser.add_argument("--english-report-path", required=True)
    parser.add_argument("--valuation-artifact-path", required=True)
    parser.add_argument("--fundability-artifact-path", required=True)
    parser.add_argument("--validation-evidence-path", action="append", default=[])
    args = parser.parse_args()
    path = write_blocked_design_manifest(
        Path(args.output_dir),
        run_id=args.run_id,
        report_date=args.report_date,
        dutch_report_path=args.dutch_report_path,
        english_report_path=args.english_report_path,
        valuation_artifact_path=args.valuation_artifact_path,
        fundability_artifact_path=args.fundability_artifact_path,
        validation_evidence_paths=list(args.validation_evidence_path),
    )
    print(f"ETF_EU_DELIVERY_MANIFEST_DESIGN_ONLY_OK | manifest={path} | delivery_enabled=false | receipt_status=not_created")


if __name__ == "__main__":
    main()
