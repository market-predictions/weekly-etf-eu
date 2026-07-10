from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_routine_run_manifest_v1"
ARTIFACT_TYPE = "etf_eu_routine_run_manifest"
SOURCE_OF_TRUTH_REPO = "market-predictions/weekly-etf-eu"
REFERENCE_ARCHITECTURE_REPO = "market-predictions/weekly-etf"
UPSTREAM_PATTERN = "weekly-etf routine workflow and run-manifest pattern; adapted for EU/UCITS authority boundaries"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _text(value: Any) -> str | None:
    raw = str(value or "").strip()
    return raw or None


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def _manifest_path(output_dir: Path, report_date: str, run_id: str) -> Path:
    return output_dir / "run_manifests" / f"etf_eu_routine_run_manifest_{report_date}_{run_id}.json"


def _reject_us_state(path_value: str | None, label: str) -> None:
    value = str(path_value or "")
    forbidden = {
        "portfolio_state_path": "output/etf_portfolio_state.json",
        "valuation_history_path": "output/etf_valuation_history.csv",
        "trade_ledger_path": "output/etf_trade_ledger.csv",
        "recommendation_scorecard_path": "output/etf_recommendation_scorecard.csv",
    }
    if label in forbidden and value == forbidden[label]:
        raise SystemExit(f"{label} must use EU-specific path, not U.S. authority path: {value}")


def build_manifest(args: argparse.Namespace) -> dict[str, Any]:
    for label, value in [
        ("portfolio_state_path", args.portfolio_state),
        ("valuation_history_path", args.valuation_history),
        ("trade_ledger_path", args.trade_ledger),
        ("recommendation_scorecard_path", args.recommendation_scorecard),
    ]:
        _reject_us_state(value, label)

    transport_attempted = _bool(args.transport_attempted)
    transport_success = _bool(args.transport_success)
    receipt_confirmed = _bool(args.receipt_confirmed)
    if transport_success and not transport_attempted:
        raise SystemExit("transport_success=true requires transport_attempted=true")
    if receipt_confirmed and not _text(args.delivery_closeout_manifest):
        raise SystemExit("receipt_confirmed=true requires delivery_closeout_manifest")

    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "run_id": args.run_id,
        "report_date": args.report_date,
        "report_suffix": args.report_suffix,
        "source_of_truth_repo": SOURCE_OF_TRUTH_REPO,
        "reference_architecture_repo": REFERENCE_ARCHITECTURE_REPO,
        "upstream_pattern_adapted": UPSTREAM_PATTERN,
        "routine_stage": args.routine_stage,
        "workflow_status": args.workflow_status,
        "workflow_conclusion": args.workflow_conclusion,
        "previous_delivery_closeout_manifest": _text(args.previous_delivery_closeout_manifest),
        "portfolio_state_path": _text(args.portfolio_state),
        "valuation_history_path": _text(args.valuation_history),
        "trade_ledger_path": _text(args.trade_ledger),
        "recommendation_scorecard_path": _text(args.recommendation_scorecard),
        "pricing_artifact_path": _text(args.pricing_artifact),
        "delivery_package_manifest": _text(args.delivery_package_manifest),
        "ready_artifact": _text(args.ready_artifact),
        "delivery_closeout_manifest": _text(args.delivery_closeout_manifest),
        "dutch_primary_markdown": _text(args.dutch_primary_markdown),
        "english_companion_markdown": _text(args.english_companion_markdown),
        "dutch_primary_html": _text(args.dutch_primary_html),
        "english_companion_html": _text(args.english_companion_html),
        "dutch_primary_pdf": _text(args.dutch_primary_pdf),
        "english_companion_pdf": _text(args.english_companion_pdf),
        "transport_attempted": transport_attempted,
        "transport_success": transport_success,
        "receipt_confirmed": receipt_confirmed,
        "valuation_grade": _bool(args.valuation_grade),
        "funding_authority": _bool(args.funding_authority),
        "portfolio_mutation": _bool(args.portfolio_mutation),
        "production_delivery_authority": _bool(args.production_delivery_authority),
        "fresh_generation_and_guarded_delivery_kept_separate": True,
        "routine_run_manifest_required": True,
        "next_package": args.next_package,
        "generated_at_utc": _utc_now(),
    }


def write_manifest(args: argparse.Namespace) -> Path:
    output_dir = Path(args.output_dir)
    manifest_path = Path(args.manifest_path) if args.manifest_path else _manifest_path(output_dir, args.report_date, args.run_id)
    payload = build_manifest(args)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    latest = manifest_path.parent / "latest_etf_eu_routine_run_manifest_path.txt"
    latest.write_text(str(manifest_path) + "\n", encoding="utf-8")
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Write an ETF EU routine weekly run manifest.")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--manifest-path", default=None)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--routine-stage", required=True)
    parser.add_argument("--workflow-status", default="planning_defined")
    parser.add_argument("--workflow-conclusion", default=None)
    parser.add_argument("--previous-delivery-closeout-manifest", default=None)
    parser.add_argument("--portfolio-state", default="output/etf_eu_portfolio_state.json")
    parser.add_argument("--valuation-history", default="output/etf_eu_valuation_history.csv")
    parser.add_argument("--trade-ledger", default="output/etf_eu_trade_ledger.csv")
    parser.add_argument("--recommendation-scorecard", default="output/etf_eu_recommendation_scorecard.csv")
    parser.add_argument("--pricing-artifact", default=None)
    parser.add_argument("--delivery-package-manifest", default=None)
    parser.add_argument("--ready-artifact", default=None)
    parser.add_argument("--delivery-closeout-manifest", default=None)
    parser.add_argument("--dutch-primary-markdown", default=None)
    parser.add_argument("--english-companion-markdown", default=None)
    parser.add_argument("--dutch-primary-html", default=None)
    parser.add_argument("--english-companion-html", default=None)
    parser.add_argument("--dutch-primary-pdf", default=None)
    parser.add_argument("--english-companion-pdf", default=None)
    parser.add_argument("--transport-attempted", default="false")
    parser.add_argument("--transport-success", default="false")
    parser.add_argument("--receipt-confirmed", default="false")
    parser.add_argument("--valuation-grade", default="false")
    parser.add_argument("--funding-authority", default="false")
    parser.add_argument("--portfolio-mutation", default="false")
    parser.add_argument("--production-delivery-authority", default="false")
    parser.add_argument("--next-package", default="ETF-EU-MVP23_FRESH_WEEKLY_EU_REPORT_GENERATION_DRY_RUN")
    args = parser.parse_args()

    path = write_manifest(args)
    print(
        "ETF_EU_ROUTINE_RUN_MANIFEST_OK | "
        f"run_id={args.run_id} | report_date={args.report_date} | stage={args.routine_stage} | manifest={path}"
    )


if __name__ == "__main__":
    main()
