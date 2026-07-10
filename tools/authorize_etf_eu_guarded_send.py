from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_guarded_send_authorization_v1"
ARTIFACT_TYPE = "etf_eu_guarded_send_authorization"
SOURCE_OF_TRUTH_REPO = "market-predictions/weekly-etf-eu"
REFERENCE_ARCHITECTURE_REPO = "market-predictions/weekly-etf"
UPSTREAM_PATTERN = "weekly-etf guarded send authorization concept; adapted for EU explicit phrase-gated send authority without transport execution"
REQUIRED_PHRASE = "AUTHORIZE ETF-EU GUARDED SEND 20260710_000000"
AUTHORIZED_NEXT_PACKAGE = "ETF-EU-MVP28_CONTROLLED_SEND_EXECUTION_OR_RUN_QUEUE"
BLOCKED_NEXT_PACKAGE = "ETF-EU-MVP27B_EXPLICIT_SEND_AUTHORIZATION_RETRY"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Required input does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _require_false(data: dict[str, Any], key: str, *, label: str) -> None:
    if data.get(key) is not False:
        raise SystemExit(f"{label}.{key} must be false before authorization; got {data.get(key)!r}")


def _verify_preconditions(prep: dict[str, Any], routine: dict[str, Any]) -> None:
    if prep.get("ready_for_controlled_delivery") is not True:
        raise SystemExit("delivery prep must have ready_for_controlled_delivery=true")
    for key in [
        "delivery_authorized",
        "send_executed",
        "transport_attempted",
        "transport_success",
        "receipt_confirmed",
        "valuation_grade",
        "funding_authority",
        "portfolio_mutation",
        "production_delivery_authority",
        "recipient_plaintext_values_exposed",
        "secret_values_exposed",
        "raw_receipt_pdf_stored_in_github",
    ]:
        _require_false(prep, key, label="delivery_prep")
    for key in ["delivery_authorized", "transport_attempted", "transport_success", "receipt_confirmed", "valuation_grade", "funding_authority", "portfolio_mutation", "production_delivery_authority"]:
        _require_false(routine, key, label="routine_manifest")


def _path_from(data: dict[str, Any], key: str) -> str:
    value = str(data.get(key) or "").strip()
    if not value:
        raise SystemExit(f"delivery prep missing required path: {key}")
    if not Path(value).exists():
        raise SystemExit(f"delivery prep path does not exist for {key}: {value}")
    return value


def _authorization_status(phrase: str) -> tuple[bool, str, list[str], list[str]]:
    supplied = phrase.strip()
    if supplied == REQUIRED_PHRASE:
        return True, "authorized_for_future_guarded_send", [], ["Authorization permits a later controlled-send package only; MVP27 does not execute transport."]
    blockers = ["missing_exact_guarded_confirmation_phrase"]
    warnings = [
        "Exact guarded confirmation phrase was not supplied as standalone authorization.",
        "Instruction/example text containing the phrase is not sufficient authorization.",
    ]
    return False, "blocked_missing_guarded_confirmation_phrase", blockers, warnings


def build_authorization(args: argparse.Namespace) -> dict[str, Any]:
    delivery_prep_path = Path(args.delivery_prep)
    routine_path = Path(args.routine_manifest)
    prep = _load_json(delivery_prep_path)
    routine = _load_json(routine_path)
    _verify_preconditions(prep, routine)

    phrase = args.authorization_phrase or ""
    phrase_present = bool(phrase.strip())
    phrase_matched, status, blockers, warnings = _authorization_status(phrase)
    next_package = AUTHORIZED_NEXT_PACKAGE if phrase_matched else BLOCKED_NEXT_PACKAGE

    authorization = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "generated_at_utc": _utc_now(),
        "run_id": args.run_id,
        "report_date": args.report_date,
        "report_suffix": args.report_suffix,
        "source_of_truth_repo": SOURCE_OF_TRUTH_REPO,
        "reference_architecture_repo": REFERENCE_ARCHITECTURE_REPO,
        "upstream_pattern_adapted": UPSTREAM_PATTERN,
        "delivery_prep_artifact": str(delivery_prep_path),
        "package_manifest": _path_from(prep, "package_manifest"),
        "ready_artifact": _path_from(prep, "ready_artifact"),
        "package_readiness_gate": _path_from(prep, "package_readiness_gate"),
        "routine_run_manifest": str(routine_path),
        "ready_for_controlled_delivery": True,
        "delivery_authorized": phrase_matched,
        "authorization_status": status,
        "authorization_source": args.authorization_source,
        "required_guarded_confirmation_phrase": REQUIRED_PHRASE,
        "guarded_confirmation_phrase_present": phrase_present,
        "guarded_confirmation_phrase_matched": phrase_matched,
        "explicit_user_authorization_required": True,
        "explicit_user_authorization_present": phrase_matched,
        "send_command_allowed": phrase_matched,
        "workflow_dispatch_allowed": False,
        "run_queue_allowed": False,
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
        "next_package": next_package,
        "blockers": blockers,
        "warnings": warnings,
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(authorization, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    routine.update(
        {
            "delivery_authorization_artifact": str(output),
            "delivery_authorized": phrase_matched,
            "send_command_allowed": phrase_matched,
            "workflow_dispatch_allowed": False,
            "run_queue_allowed": False,
            "transport_execution_allowed": False,
            "transport_attempted": False,
            "transport_success": False,
            "receipt_confirmed": False,
            "routine_stage": "explicit_guarded_send_authorization_created" if phrase_matched else "explicit_guarded_send_authorization_blocked",
            "workflow_status": "explicit_guarded_send_authorization_created" if phrase_matched else "explicit_guarded_send_authorization_blocked",
            "next_package": next_package,
        }
    )
    routine_path.write_text(json.dumps(routine, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return authorization


def main() -> None:
    parser = argparse.ArgumentParser(description="Create ETF EU explicit guarded-send authorization artifact without executing transport.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--delivery-prep", required=True)
    parser.add_argument("--routine-manifest", required=True)
    parser.add_argument("--authorization-phrase", default="")
    parser.add_argument("--authorization-source", default="user_message_or_explicit_cli_argument")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    authorization = build_authorization(args)
    print(
        "ETF_EU_GUARDED_SEND_AUTHORIZATION_OK | "
        f"status={authorization['authorization_status']} | "
        f"delivery_authorized={authorization['delivery_authorized']} | "
        f"send_executed={authorization['send_executed']} | "
        f"transport_attempted={authorization['transport_attempted']} | "
        f"next_package={authorization['next_package']} | output={args.output}"
    )


if __name__ == "__main__":
    main()
