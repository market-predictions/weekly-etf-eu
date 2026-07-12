from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing input: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def prepare(args: argparse.Namespace) -> dict[str, Path]:
    package_path = Path(args.package_manifest)
    ready_path = Path(args.ready_artifact)
    routine_path = Path(args.routine_manifest)
    package = _load(package_path)
    ready = _load(ready_path)
    routine = _load(routine_path)

    if package.get("run_id") != args.run_id or routine.get("run_id") != args.run_id:
        raise SystemExit("run id mismatch")
    if package.get("report_date") != args.report_date or package.get("report_suffix") != args.report_suffix:
        raise SystemExit("report identity mismatch")
    if package.get("ready_for_controlled_delivery") is not True or ready.get("ready_for_controlled_delivery") is not True:
        raise SystemExit("package is not ready for controlled delivery")
    for payload in (package, ready, routine):
        if payload.get("valuation_grade") is not False:
            raise SystemExit("valuation grade must remain false")
        if payload.get("funding_authority") is not False:
            raise SystemExit("funding authority must remain false")
        if payload.get("portfolio_mutation") is not False:
            raise SystemExit("portfolio mutation must remain false")
        if payload.get("production_delivery_authority") is not False:
            raise SystemExit("production delivery authority must remain false")

    generated = _utc_now()
    prep_path = Path("output/delivery_prep") / f"etf_eu_guarded_fresh_package_delivery_prep_{args.run_id}.json"
    authorization_path = Path("output/delivery_authorization") / f"etf_eu_guarded_send_authorization_{args.run_id}.json"
    decision_path = Path("output/delivery_control") / f"etf_eu_controlled_delivery_decision_{args.run_id}.json"
    selection_path = Path("output/delivery_control") / f"etf_eu_controlled_delivery_transport_selection_{args.run_id}.json"
    queue_path = Path("control/run_queue") / f"etf_eu_routine_delivery_request_{args.run_id}.md"

    common = {
        "generated_at_utc": generated,
        "run_id": args.run_id,
        "report_date": args.report_date,
        "report_suffix": args.report_suffix,
        "source_of_truth_repo": "market-predictions/weekly-etf-eu",
        "reference_architecture_repo": "market-predictions/weekly-etf",
        "package_manifest": str(package_path),
        "ready_artifact": str(ready_path),
        "routine_run_manifest": str(routine_path),
        "recipient_plaintext_values_exposed": False,
        "secret_values_exposed": False,
        "raw_receipt_pdf_stored_in_github": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
    }
    prep = dict(common)
    prep.update({
        "schema_version": "etf_eu_routine_delivery_prep_v1",
        "artifact_type": "etf_eu_routine_delivery_prep",
        "ready_for_controlled_delivery": True,
        "delivery_authorized": False,
        "send_command_allowed": False,
        "next_action": "AUTHORIZE_ROUTINE_GUARDED_DELIVERY",
    })
    authorization = dict(common)
    authorization.update({
        "schema_version": "etf_eu_guarded_send_authorization_v1",
        "artifact_type": "etf_eu_guarded_send_authorization",
        "ready_for_controlled_delivery": True,
        "delivery_authorized": True,
        "send_command_allowed": True,
        "authorization_basis": "explicit user request to generate a fresh routine Weekly ETF EU report",
        "next_action": "EXECUTE_ROUTINE_GUARDED_DELIVERY",
    })
    decision = dict(common)
    decision.update({
        "schema_version": "etf_eu_routine_controlled_delivery_decision_v1",
        "artifact_type": "etf_eu_routine_controlled_delivery_decision",
        "controlled_delivery_decision_status": "routine_guarded_delivery_selected",
        "delivery_authorized": True,
        "send_command_allowed": True,
        "transport_attempted": False,
        "receipt_confirmed": False,
    })
    selection = dict(common)
    selection.update({
        "schema_version": "etf_eu_routine_transport_selection_v1",
        "artifact_type": "etf_eu_routine_transport_selection",
        "transport_selection_status": "current_package_smtp_runner_selected",
        "selected_transport_mode": "guarded_send",
        "delivery_authorized": True,
        "send_command_allowed": True,
        "transport_attempted": False,
        "receipt_confirmed": False,
    })
    _write(prep_path, prep)
    _write(authorization_path, authorization)
    _write(decision_path, decision)
    _write(selection_path, selection)

    queue_text = "\n".join([
        "# ETF EU routine current-package delivery request",
        "schema_version=etf_eu_current_package_delivery_queue_v1",
        "artifact_type=etf_eu_current_package_delivery_queue",
        f"run_id={args.run_id}",
        f"report_date={args.report_date}",
        f"report_suffix={args.report_suffix}",
        f"package_manifest={package_path}",
        f"authorization_artifact={authorization_path}",
        f"controlled_delivery_decision_artifact={decision_path}",
        f"transport_selection_artifact={selection_path}",
        f"routine_run_manifest={routine_path}",
        "delivery_authorized=true",
        "send_command_allowed=true",
        "recipient_plaintext_values_exposed=false",
        "secret_values_exposed=false",
        "raw_receipt_pdf_stored_in_github=false",
        "",
    ])
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(queue_text, encoding="utf-8")

    routine.update({
        "routine_stage": "routine_guarded_delivery_authorized",
        "workflow_status": "routine_guarded_delivery_authorized",
        "delivery_prep_artifact": str(prep_path),
        "delivery_authorization_artifact": str(authorization_path),
        "controlled_delivery_decision_artifact": str(decision_path),
        "controlled_delivery_transport_selection_artifact": str(selection_path),
        "run_queue_artifact": str(queue_path),
        "delivery_authorized": True,
        "send_command_allowed": True,
        "transport_attempted": False,
        "transport_success": False,
        "receipt_confirmed": False,
        "next_action": "EXECUTE_ROUTINE_GUARDED_DELIVERY",
    })
    _write(routine_path, routine)
    return {
        "delivery_prep": prep_path,
        "authorization": authorization_path,
        "decision": decision_path,
        "selection": selection_path,
        "queue": queue_path,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--package-manifest", required=True)
    parser.add_argument("--ready-artifact", required=True)
    parser.add_argument("--routine-manifest", required=True)
    args = parser.parse_args()
    outputs = prepare(args)
    print("ETF_EU_ROUTINE_DELIVERY_CONTROL_OK | " + " | ".join(f"{k}={v}" for k, v in outputs.items()))


if __name__ == "__main__":
    main()
