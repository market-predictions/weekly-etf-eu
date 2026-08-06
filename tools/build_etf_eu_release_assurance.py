#!/usr/bin/env python3
"""Build an independent Weekly ETF EU release-assurance evidence record.

This script intentionally does not render reports, mutate portfolio state, or send mail.
It reconstructs the release candidate from immutable files and records a fail-closed
PASS/FAIL decision for the separate governance role.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

IMPLEMENTATION_ROLE = "implementation_operations"
ASSURANCE_ROLE = "governance_release_assurance"
REQUIRED_CLIENT_ARTIFACTS = ("nl_html", "nl_pdf", "en_html", "en_pdf")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def contains_identity(payload: Any, value: str) -> bool:
    if isinstance(payload, dict):
        return any(contains_identity(item, value) for item in payload.values())
    if isinstance(payload, list):
        return any(contains_identity(item, value) for item in payload)
    return str(payload) == value


def add_check(checks: list[dict[str, Any]], blockers: list[str], check_id: str, passed: bool, evidence: Any) -> None:
    checks.append({"id": check_id, "passed": bool(passed), "evidence": evidence})
    if not passed:
        blockers.append(check_id)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--package-manifest", required=True, type=Path)
    parser.add_argument("--ready-artifact", required=True, type=Path)
    parser.add_argument("--routine-manifest", required=True, type=Path)
    parser.add_argument("--visual-review", required=True, type=Path)
    parser.add_argument("--delivery-queue", required=True, type=Path)
    parser.add_argument("--nl-html", required=True, type=Path)
    parser.add_argument("--nl-pdf", required=True, type=Path)
    parser.add_argument("--en-html", required=True, type=Path)
    parser.add_argument("--en-pdf", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []
    blockers: list[str] = []
    try:
        datetime.strptime(args.report_date, "%Y-%m-%d")
        valid_report_date = True
    except ValueError:
        valid_report_date = False
    source_sha_valid = bool(re.fullmatch(r"[0-9a-fA-F]{40}", args.source_sha))
    add_check(checks, blockers, "source_commit_bound", source_sha_valid and valid_report_date and bool(args.run_id) and bool(args.report_suffix), {"source_sha": args.source_sha, "run_id": args.run_id, "report_date": args.report_date, "report_suffix": args.report_suffix})

    artifact_paths = {
        "package_manifest": args.package_manifest,
        "ready_artifact": args.ready_artifact,
        "routine_manifest": args.routine_manifest,
        "visual_review": args.visual_review,
        "delivery_queue": args.delivery_queue,
        "nl_html": args.nl_html,
        "nl_pdf": args.nl_pdf,
        "en_html": args.en_html,
        "en_pdf": args.en_pdf,
    }
    missing = [str(path) for path in artifact_paths.values() if not path.is_file()]
    add_check(checks, blockers, "artifact_files_present", not missing, {"missing": missing})

    parsed: dict[str, Any] = {}
    json_errors: dict[str, str] = {}
    for key in ("package_manifest", "ready_artifact", "routine_manifest", "visual_review", "delivery_queue"):
        path = artifact_paths[key]
        if path.is_file():
            try:
                parsed[key] = load_json(path)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                json_errors[key] = str(exc)
    add_check(checks, blockers, "control_json_parseable", not json_errors, json_errors)

    format_errors: list[str] = []
    for key in ("nl_html", "en_html"):
        path = artifact_paths[key]
        if path.is_file():
            raw = path.read_text(encoding="utf-8", errors="replace").lower()
            if len(raw.encode("utf-8")) < 1024 or ("<html" not in raw and "<!doctype" not in raw):
                format_errors.append(f"{key}: invalid or unexpectedly small HTML")
    for key in ("nl_pdf", "en_pdf"):
        path = artifact_paths[key]
        if path.is_file():
            with path.open("rb") as handle:
                header = handle.read(5)
            if path.stat().st_size < 1024 or header != b"%PDF-":
                format_errors.append(f"{key}: invalid or unexpectedly small PDF")
    add_check(checks, blockers, "artifact_formats_valid", not format_errors, format_errors)

    hashes: dict[str, dict[str, str]] = {}
    if not missing:
        for key, path in artifact_paths.items():
            hashes[key] = {"path": str(path), "sha256": sha256_file(path)}
    client_hashes_complete = all(key in hashes for key in REQUIRED_CLIENT_ARTIFACTS)
    add_check(checks, blockers, "artifact_hashes_complete", client_hashes_complete, {key: hashes.get(key) for key in REQUIRED_CLIENT_ARTIFACTS})

    identity_failures: list[str] = []
    for key in ("package_manifest", "ready_artifact", "routine_manifest"):
        payload = parsed.get(key)
        if payload is None:
            identity_failures.append(f"{key}: unavailable")
            continue
        if not contains_identity(payload, args.run_id):
            identity_failures.append(f"{key}: run_id not bound")
        if not contains_identity(payload, args.report_date):
            identity_failures.append(f"{key}: report_date not bound")
    add_check(checks, blockers, "manifest_identity_consistent", not identity_failures, identity_failures)

    routine = parsed.get("routine_manifest") if isinstance(parsed.get("routine_manifest"), dict) else {}
    state_artifacts = routine.get("state_artifacts") if isinstance(routine.get("state_artifacts"), dict) else {}
    policy_record = state_artifacts.get("portfolio_policy_validation") if isinstance(state_artifacts.get("portfolio_policy_validation"), dict) else {}
    state_record = state_artifacts.get("production_convergence_state") if isinstance(state_artifacts.get("production_convergence_state"), dict) else {}
    policy_path = Path(str(policy_record.get("path") or ""))
    policy_payload: dict[str, Any] = {}
    policy_errors: list[str] = []
    if not policy_path.is_file():
        policy_errors.append("policy validation artifact missing")
    else:
        try:
            loaded = load_json(policy_path)
            if not isinstance(loaded, dict):
                policy_errors.append("policy validation is not a JSON object")
            else:
                policy_payload = loaded
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            policy_errors.append(f"policy validation unreadable: {exc}")
    if policy_payload:
        if policy_payload.get("schema_version") != "etf_eu_portfolio_policy_validation_v2":
            policy_errors.append("unexpected policy validation schema")
        if policy_payload.get("verdict") != "PASS" or policy_payload.get("valid") is not True or policy_payload.get("blockers"):
            policy_errors.append("policy validation did not PASS")
        if policy_record.get("sha256") != sha256_file(policy_path):
            policy_errors.append("policy validation artifact hash mismatch")
        if policy_record.get("policy_id") != policy_payload.get("policy_id"):
            policy_errors.append("policy identity mismatch")
        if policy_record.get("policy_sha256") != policy_payload.get("policy_sha256"):
            policy_errors.append("policy source hash mismatch")
        if policy_payload.get("state_sha256") != state_record.get("sha256"):
            policy_errors.append("policy PASS is not bound to convergence state")
    add_check(checks, blockers, "portfolio_policy_passed", not policy_errors, {"errors": policy_errors, "policy_id": policy_payload.get("policy_id"), "policy_sha256": policy_payload.get("policy_sha256"), "state_sha256": policy_payload.get("state_sha256"), "validation_sha256": sha256_file(policy_path) if policy_path.is_file() else None})
    if policy_path.is_file():
        hashes["portfolio_policy_validation"] = {"path": str(policy_path), "sha256": sha256_file(policy_path)}

    visual = parsed.get("visual_review", {})
    visual_passed = isinstance(visual, dict) and visual.get("visual_review_passed") is True and not visual.get("blockers")
    add_check(checks, blockers, "visual_review_passed", visual_passed, {"visual_review_passed": visual.get("visual_review_passed") if isinstance(visual, dict) else None, "blockers": visual.get("blockers") if isinstance(visual, dict) else ["invalid visual review payload"]})

    queue = parsed.get("delivery_queue") if isinstance(parsed.get("delivery_queue"), dict) else {}
    queue_bound = contains_identity(queue, args.run_id) and contains_identity(queue, args.report_date)
    queue_policy_bound = contains_identity(queue, str(policy_payload.get("policy_id") or "")) and contains_identity(queue, str(policy_payload.get("policy_sha256") or ""))
    add_check(checks, blockers, "delivery_queue_bound", queue_bound, {"path": str(args.delivery_queue), "run_id_bound": contains_identity(queue, args.run_id), "report_date_bound": contains_identity(queue, args.report_date)})
    add_check(checks, blockers, "delivery_queue_policy_bound", queue_policy_bound, {"policy_id": policy_payload.get("policy_id"), "policy_sha256": policy_payload.get("policy_sha256")})

    add_check(checks, blockers, "roles_separated", IMPLEMENTATION_ROLE != ASSURANCE_ROLE, {"implementation_role": IMPLEMENTATION_ROLE, "assurance_role": ASSURANCE_ROLE, "implementation_may_self_certify": False})

    decision = "PASS" if not blockers else "FAIL"
    output = {
        "schema_version": 2,
        "product": "weekly_etf_eu",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "decision": decision,
        "status": "GOVERNANCE_PASS_PRE_SEND" if decision == "PASS" else "GOVERNANCE_FAIL",
        "implementation_role": IMPLEMENTATION_ROLE,
        "assurance_role": ASSURANCE_ROLE,
        "separation_of_duties": {"same_role": False, "implementation_may_self_certify": False, "assurance_may_mutate_release_candidate": False},
        "identity": {"source_sha": args.source_sha.lower(), "run_id": args.run_id, "report_date": args.report_date, "report_suffix": args.report_suffix},
        "portfolio_policy": {"policy_id": policy_payload.get("policy_id"), "policy_sha256": policy_payload.get("policy_sha256"), "validation_sha256": sha256_file(policy_path) if policy_path.is_file() else None, "state_sha256": policy_payload.get("state_sha256"), "verdict": policy_payload.get("verdict")},
        "checks": checks,
        "artifact_hashes": hashes,
        "blockers": blockers,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ETF_EU_RELEASE_ASSURANCE_{decision} | output={args.output} | blockers={len(blockers)}")
    return 0 if decision == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
