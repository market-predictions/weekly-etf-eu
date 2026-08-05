#!/usr/bin/env python3
"""Validate a Weekly ETF EU governance release-assurance record."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

REQUIRED_CHECKS = {
    "source_commit_bound",
    "artifact_files_present",
    "control_json_parseable",
    "artifact_formats_valid",
    "artifact_hashes_complete",
    "manifest_identity_consistent",
    "visual_review_passed",
    "delivery_queue_bound",
    "roles_separated",
}
REQUIRED_CLIENT_ARTIFACTS = {"nl_html", "nl_pdf", "en_html", "en_pdf"}


def fail(message: str) -> None:
    raise SystemExit(f"ETF_EU_RELEASE_ASSURANCE_INVALID: {message}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()

    try:
        payload: dict[str, Any] = json.loads(args.evidence.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail(f"unreadable evidence: {exc}")

    if payload.get("schema_version") != 1:
        fail("schema_version must equal 1")
    if payload.get("product") != "weekly_etf_eu":
        fail("unexpected product")
    if payload.get("decision") != "PASS":
        fail(f"decision is {payload.get('decision')!r}, expected 'PASS'")
    if payload.get("blockers"):
        fail("blockers must be empty")
    if payload.get("implementation_role") != "implementation_operations":
        fail("unexpected implementation role")
    if payload.get("assurance_role") != "governance_release_assurance":
        fail("unexpected assurance role")

    separation = payload.get("separation_of_duties")
    if not isinstance(separation, dict):
        fail("separation_of_duties missing")
    if separation.get("same_role") is not False:
        fail("implementation and assurance roles must be separate")
    if separation.get("implementation_may_self_certify") is not False:
        fail("implementation role may not self-certify")
    if separation.get("assurance_may_mutate_release_candidate") is not False:
        fail("assurance role may not mutate the candidate it certifies")

    identity = payload.get("identity")
    if not isinstance(identity, dict):
        fail("identity missing")
    if not re.fullmatch(r"[0-9a-f]{40}", str(identity.get("source_sha", ""))):
        fail("source_sha must be a lowercase 40-character Git SHA")
    if not identity.get("run_id") or not identity.get("report_date") or not identity.get("report_suffix"):
        fail("run identity is incomplete")

    checks = payload.get("checks")
    if not isinstance(checks, list):
        fail("checks must be a list")
    by_id: dict[str, dict[str, Any]] = {}
    for check in checks:
        if not isinstance(check, dict) or not check.get("id"):
            fail("malformed check")
        check_id = str(check["id"])
        if check_id in by_id:
            fail(f"duplicate check id: {check_id}")
        by_id[check_id] = check
    missing = sorted(REQUIRED_CHECKS - set(by_id))
    if missing:
        fail(f"missing required checks: {', '.join(missing)}")
    failed = sorted(
        check_id for check_id in REQUIRED_CHECKS if by_id[check_id].get("passed") is not True
    )
    if failed:
        fail(f"required checks failed: {', '.join(failed)}")

    hashes = payload.get("artifact_hashes")
    if not isinstance(hashes, dict):
        fail("artifact_hashes missing")
    missing_hashes = sorted(REQUIRED_CLIENT_ARTIFACTS - set(hashes))
    if missing_hashes:
        fail(f"missing client artifact hashes: {', '.join(missing_hashes)}")
    for key in REQUIRED_CLIENT_ARTIFACTS:
        entry = hashes.get(key)
        if not isinstance(entry, dict):
            fail(f"invalid artifact hash entry: {key}")
        if not entry.get("path"):
            fail(f"artifact path missing: {key}")
        if not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256", ""))):
            fail(f"invalid sha256: {key}")

    print(
        "ETF_EU_RELEASE_ASSURANCE_VALID | "
        f"run_id={identity['run_id']} | source_sha={identity['source_sha']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
