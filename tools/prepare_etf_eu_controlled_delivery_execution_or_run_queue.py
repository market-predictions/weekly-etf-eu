from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VALID_MODES = {"decision_only", "run_queue", "transport_executed"}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Required JSON file does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _require_false(data: dict[str, Any], key: str, source: str) -> None:
    if data.get(key) is True:
        raise SystemExit(f"{source} must not have {key}=true")


def _require_true(data: dict[str, Any], key: str, source: str) -> None:
    if data.get(key) is not True:
        raise SystemExit(f"{source} must have {key}=true")


def _base_decision(args: argparse.Namespace, authorization: dict[str, Any], prep: dict[str, Any], package: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "etf_eu_controlled_delivery_decision_v1",
        "artifact_type": "etf_eu_controlled_delivery_decision",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "run_id": args.run_id,
        "report_date": args.report_date,
        "report_suffix": args.report_suffix,
        "source_of_truth_repo": "market-predictions/weekly-etf-eu",
        "reference_architecture_repo": "market-predictions/weekly-etf",
        "upstream_pattern_adapted": "weekly-etf controlled delivery and delivery-manifest concepts; adapted for EU package-bound authority without automatic transport",
        "mode": args.mode,
        "authorization_artifact": str(args.authorization),
        "delivery_prep_artifact": str(args.delivery_prep),
        "package_manifest": str(args.package_manifest),
        "routine_run_manifest": str(args.routine_manifest),
        "ready_for_controlled_delivery": True,
        "delivery_authorized": True,
        "send_command_allowed": True,
        "workflow_dispatch_allowed": False,
        "run_queue_allowed": False,
        "run_queue_created": False,
        "run_queue_artifact": None,
        "transport_execution_allowed": False,
        "send_executed": False,
        "transport_attempted": False,
        "transport_success": False,
        "receipt_confirmed": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "recipient_plaintext_values_exposed": False,
        "secret_values_exposed": False,
        "raw_receipt_pdf_stored_in_github": False,
        "delivery_evidence_artifact": None,
        "receipt_evidence_artifact": None,
        "warnings": [],
        "source_package_paths": {
            "dutch_primary_markdown": package.get("dutch_primary_markdown") or prep.get("dutch_primary_markdown"),
            "english_companion_markdown": package.get("english_companion_markdown") or prep.get("english_companion_markdown"),
            "dutch_primary_html": package.get("dutch_primary_html") or prep.get("dutch_primary_html"),
            "english_companion_html": package.get("english_companion_html") or prep.get("english_companion_html"),
            "dutch_primary_pdf": package.get("dutch_primary_pdf") or prep.get("dutch_primary_pdf"),
            "english_companion_pdf": package.get("english_companion_pdf") or prep.get("english_companion_pdf"),
        },
    }


def _write_queue(path: Path, decision: dict[str, Any]) -> None:
    content = f"""# ETF EU Controlled Delivery Request

Run id: `{decision['run_id']}`  
Report date: `{decision['report_date']}`

This is an EU-controlled run queue request. It contains artifact paths only.

```text
delivery_authorized=true
send_command_allowed=true
run_queue_created=true
workflow_dispatch_allowed=false
transport_execution_allowed=false
send_executed=false
transport_attempted=false
receipt_confirmed=false
```

Package manifest:

```text
{decision['package_manifest']}
```

Authorization artifact:

```text
{decision['authorization_artifact']}
```

Controlled delivery decision artifact:

```text
output/delivery_control/etf_eu_controlled_delivery_decision_20260710_000000.json
```

No plaintext recipients, SMTP secrets, or raw receipt files are stored here.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _update_routine(path: Path, decision: dict[str, Any]) -> None:
    routine = _read_json(path)
    routine.update({
        "controlled_delivery_decision_artifact": "output/delivery_control/etf_eu_controlled_delivery_decision_20260710_000000.json",
        "delivery_authorized": True,
        "send_command_allowed": True,
        "workflow_dispatch_allowed": decision["workflow_dispatch_allowed"],
        "run_queue_allowed": decision["run_queue_allowed"],
        "run_queue_created": decision["run_queue_created"],
        "transport_execution_allowed": decision["transport_execution_allowed"],
        "send_executed": decision["send_executed"],
        "transport_attempted": decision["transport_attempted"],
        "transport_success": decision["transport_success"],
        "receipt_confirmed": decision["receipt_confirmed"],
        "next_package": decision["next_package"],
        "routine_stage": decision["routine_stage"],
        "workflow_status": decision["routine_stage"],
        "generated_at_utc": decision["generated_at_utc"],
    })
    if decision.get("run_queue_artifact"):
        routine["run_queue_artifact"] = decision["run_queue_artifact"]
    path.write_text(json.dumps(routine, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build(args: argparse.Namespace) -> dict[str, Any]:
    if args.mode not in VALID_MODES:
        raise SystemExit(f"Invalid mode: {args.mode}")

    authorization = _read_json(args.authorization)
    prep = _read_json(args.delivery_prep)
    package = _read_json(args.package_manifest)

    _require_true(authorization, "ready_for_controlled_delivery", "authorization")
    _require_true(authorization, "delivery_authorized", "authorization")
    _require_true(authorization, "send_command_allowed", "authorization")
    _require_true(authorization, "guarded_confirmation_phrase_matched", "authorization")
    for key in [
        "workflow_dispatch_allowed",
        "run_queue_allowed",
        "transport_execution_allowed",
        "send_executed",
        "transport_attempted",
        "transport_success",
        "receipt_confirmed",
        "recipient_plaintext_values_exposed",
        "secret_values_exposed",
        "raw_receipt_pdf_stored_in_github",
        "valuation_grade",
        "funding_authority",
        "portfolio_mutation",
        "production_delivery_authority",
    ]:
        _require_false(authorization, key, "authorization")

    decision = _base_decision(args, authorization, prep, package)

    if args.mode == "decision_only":
        decision.update({
            "controlled_delivery_decision_status": "blocked_no_transport_selected",
            "routine_stage": "controlled_delivery_decision_blocked_no_transport_selected",
            "next_package": "ETF-EU-MVP28B_CONTROLLED_DELIVERY_TRANSPORT_SELECTION",
            "warnings": ["No explicit run queue or transport execution instruction was supplied; MVP28 chose decision_only."],
        })
    elif args.mode == "run_queue":
        queue_path = Path(args.run_queue_artifact)
        decision.update({
            "controlled_delivery_decision_status": "run_queue_artifact_created",
            "routine_stage": "controlled_delivery_run_queue_created",
            "run_queue_allowed": True,
            "run_queue_created": True,
            "run_queue_artifact": str(queue_path),
            "next_package": "ETF-EU-MVP29_DELIVERY_RUN_MONITOR_AND_RECEIPT_EVIDENCE",
        })
        _write_queue(queue_path, decision)
    else:
        raise SystemExit("transport_executed mode requires live transport evidence and is not implemented by this preparation script")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _update_routine(args.routine_manifest, decision)
    return decision


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare ETF EU controlled delivery decision or run queue.")
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="decision_only")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--delivery-prep", type=Path, required=True)
    parser.add_argument("--package-manifest", type=Path, required=True)
    parser.add_argument("--routine-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-queue-artifact", default="control/run_queue/etf_eu_controlled_delivery_request_20260710_000000.md")
    args = parser.parse_args()
    decision = build(args)
    print(
        "ETF_EU_CONTROLLED_DELIVERY_DECISION_OK | "
        f"mode={decision['mode']} | status={decision['controlled_delivery_decision_status']} | "
        f"next={decision['next_package']}"
    )


if __name__ == "__main__":
    main()
