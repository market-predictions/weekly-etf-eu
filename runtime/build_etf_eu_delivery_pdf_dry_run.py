from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_delivery_pdf_dry_run_v1"
DEFAULT_RUN_ID = "20260618_000000"
DEFAULT_REPORT = Path("output/weekly_etf_eu_review_260618_draft.md")
DEFAULT_PRICING = Path("output/pricing/etf_eu_ucits_closing_price_smoke_20260618_000000.json")
DEFAULT_PORTING = Path("output/porting/etf_eu_wp14g_donor_comparison_20260618_000000.json")
DEFAULT_BILINGUAL = Path("output/bilingual/etf_eu_bilingual_surface_readiness_20260618_000000.json")

FALSE_FLAGS = {
    "production_delivery": False,
    "recipient_activation": False,
    "send_attempted": False,
    "mail_transport_enabled": False,
    "smtp_configured": False,
    "secrets_present": False,
    "real_recipients": False,
    "real_receipt": False,
    "proof_claimed": False,
    "portfolio_mutation": False,
    "candidate_promotion": False,
    "funding_authority": False,
    "valuation_grade": False,
}


def _exists(path: Path) -> bool:
    return path.exists() and path.is_file()


def build_delivery_pdf_dry_run_manifest(
    *,
    report_path: Path = DEFAULT_REPORT,
    pricing_artifact_path: Path = DEFAULT_PRICING,
    porting_artifact_path: Path = DEFAULT_PORTING,
    bilingual_surface_artifact_path: Path = DEFAULT_BILINGUAL,
    run_id: str = DEFAULT_RUN_ID,
) -> dict[str, Any]:
    validators_run = [
        "tools/validate_etf_eu_ucits_closing_price_smoke.py",
        "tools/validate_etf_eu_draft_report_surface.py",
        "tools/validate_etf_eu_report_quality.py",
        "tools/validate_etf_eu_bilingual_surface.py",
        "tools/validate_etf_eu_delivery_pdf_dry_run.py",
    ]
    tests_expected = [
        "tests/test_etf_eu_delivery_pdf_dry_run.py",
        "tests/test_etf_eu_report_quality.py",
        "tests/test_etf_eu_bilingual_surface.py",
        "tests/test_etf_eu_draft_report_surface.py",
        "tests/test_etf_eu_ucits_closing_price_smoke.py",
        "tests/test_etf_eu_ucits_symbol_registry_identity.py",
        "tests/test_etf_eu_wp14c_ucits_identity_audit.py",
        "tests/test_etf_eu_wp14b_roadmap_lane_implementation_plan.py",
        "tests/test_etf_eu_wp14a_roadmap_lane_selection.py",
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "status": "completed",
        "created_at_utc": datetime(2026, 6, 18, 0, 0, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
        "report_path": str(report_path),
        "pricing_artifact_path": str(pricing_artifact_path),
        "porting_artifact_path": str(porting_artifact_path),
        "bilingual_surface_artifact_path": str(bilingual_surface_artifact_path),
        "dry_run_only": True,
        **FALSE_FLAGS,
        "pdf_generation_status": "not_generated_dry_run_manifest_only",
        "html_generation_status": "not_generated",
        "source_files_exist": {
            "report_path": _exists(report_path),
            "pricing_artifact_path": _exists(pricing_artifact_path),
            "porting_artifact_path": _exists(porting_artifact_path),
            "bilingual_surface_artifact_path": _exists(bilingual_surface_artifact_path),
        },
        "validators_run": validators_run,
        "tests_expected": tests_expected,
        "selected_next_package": "WP14I",
        "selected_next_package_title": "ETF EU mature bilingual draft/report rendering integration, no delivery",
    }


def write_delivery_pdf_dry_run_manifest(output_path: Path, **kwargs: Any) -> Path:
    manifest = build_delivery_pdf_dry_run_manifest(**kwargs)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--pricing-artifact", default=str(DEFAULT_PRICING))
    parser.add_argument("--porting-artifact", default=str(DEFAULT_PORTING))
    parser.add_argument("--bilingual-artifact", default=str(DEFAULT_BILINGUAL))
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    args = parser.parse_args()
    output = write_delivery_pdf_dry_run_manifest(
        Path(args.output),
        report_path=Path(args.report),
        pricing_artifact_path=Path(args.pricing_artifact),
        porting_artifact_path=Path(args.porting_artifact),
        bilingual_surface_artifact_path=Path(args.bilingual_artifact),
        run_id=args.run_id,
    )
    print(f"ETF_EU_DELIVERY_PDF_DRY_RUN_BUILT | output={output}")


if __name__ == "__main__":
    main()
