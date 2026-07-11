from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


QUEUE_SCHEMA_VERSION = "etf_eu_current_package_delivery_queue_v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"required input missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _validate_inputs(package: dict[str, Any], authorization: dict[str, Any], selection: dict[str, Any]) -> None:
    _require(package.get("schema_version") == "etf_eu_fresh_generation_package_v1", "fresh package manifest schema mismatch")
    _require(package.get("ready_for_controlled_delivery") is True, "fresh package is not ready for controlled delivery")
    _require(package.get("dutch_primary") is True, "Dutch primary package flag missing")
    _require(package.get("english_companion") is True, "English companion package flag missing")
    _require(package.get("pdf_output_available") is True, "PDF output is not available")
    _require(package.get("html_output_available") is True, "HTML output is not available")
    _require(package.get("valuation_grade") is False, "package must not claim valuation grade")
    _require(package.get("funding_authority") is False, "package must not claim funding authority")
    _require(package.get("portfolio_mutation") is False, "package must not mutate portfolio")

    _require(authorization.get("schema_version") == "etf_eu_guarded_send_authorization_v1", "authorization schema mismatch")
    _require(authorization.get("delivery_authorized") is True, "delivery is not authorized")
    _require(authorization.get("send_command_allowed") is True, "send command is not allowed")
    _require(authorization.get("guarded_confirmation_phrase_matched") is True, "guarded phrase is not matched")
    _require(authorization.get("recipient_plaintext_values_exposed") is False, "recipient plaintext exposure flag is not false")
    _require(authorization.get("secret_values_exposed") is False, "secret exposure flag is not false")

    _require(selection.get("schema_version") == "etf_eu_controlled_delivery_transport_selection_v1", "transport selection schema mismatch")
    _require(selection.get("transport_selection_status") == "blocked_missing_eu_delivery_workflow_wiring", "unexpected transport selection status")
    _require(selection.get("delivery_authorized") is True, "selection does not preserve authorization")
    _require(selection.get("send_command_allowed") is True, "selection does not preserve send command allowance")


def build_queue(*, run_id: str, report_date: str, report_suffix: str, package_manifest: Path, authorization: Path, controlled_delivery_decision: Path, transport_selection: Path, routine_manifest: Path) -> str:
    package = _read_json(package_manifest)
    authorization_data = _read_json(authorization)
    selection = _read_json(transport_selection)
    _read_json(controlled_delivery_decision)
    _read_json(routine_manifest)
    _validate_inputs(package, authorization_data, selection)

    lines = [
        "# ETF EU Current Package Delivery Request",
        "",
        f"schema_version={QUEUE_SCHEMA_VERSION}",
        "artifact_type=etf_eu_current_package_delivery_queue",
        f"generated_at_utc={_utc_now()}",
        f"run_id={run_id}",
        f"report_date={report_date}",
        f"report_suffix={report_suffix}",
        f"package_manifest={package_manifest}",
        f"authorization_artifact={authorization}",
        f"controlled_delivery_decision_artifact={controlled_delivery_decision}",
        f"transport_selection_artifact={transport_selection}",
        f"routine_run_manifest={routine_manifest}",
        f"dutch_primary_html={package.get('dutch_primary_html')}",
        f"english_companion_html={package.get('english_companion_html')}",
        f"dutch_primary_pdf={package.get('dutch_primary_pdf')}",
        f"english_companion_pdf={package.get('english_companion_pdf')}",
        "recipient_policy=runtime_secret_or_config_only",
        "recipient_plaintext_values_exposed=false",
        "secret_values_exposed=false",
        "raw_receipt_pdf_stored_in_github=false",
        "delivery_authorized=true",
        "send_command_allowed=true",
        "workflow_dispatch_allowed=false",
        "transport_execution_allowed=false",
        "send_executed=false",
        "transport_attempted=false",
        "receipt_confirmed=false",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create current-package ETF EU delivery queue artifact.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--package-manifest", required=True)
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--controlled-delivery-decision", required=True)
    parser.add_argument("--transport-selection", required=True)
    parser.add_argument("--routine-manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    content = build_queue(
        run_id=args.run_id,
        report_date=args.report_date,
        report_suffix=args.report_suffix,
        package_manifest=Path(args.package_manifest),
        authorization=Path(args.authorization),
        controlled_delivery_decision=Path(args.controlled_delivery_decision),
        transport_selection=Path(args.transport_selection),
        routine_manifest=Path(args.routine_manifest),
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    print(f"ETF_EU_CURRENT_PACKAGE_QUEUE_OK | queue={out}")


if __name__ == "__main__":
    main()
