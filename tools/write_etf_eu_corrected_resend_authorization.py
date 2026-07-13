from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_authorization(
    *,
    output: Path,
    runtime_run_id: str,
    correction_control_id: str,
    github_run_id: str,
    github_commit_sha: str,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "etf_eu_corrected_resend_authorization_v1",
        "artifact_type": "etf_eu_corrected_resend_authorization",
        "generated_at_utc": _utc_now(),
        "runtime_run_id": runtime_run_id,
        "correction_control_id": correction_control_id,
        "workflow_dispatch": True,
        "github_run_id": github_run_id,
        "github_commit_sha": github_commit_sha,
        "corrected_resend_authorized": True,
        "send_command_allowed": True,
        "send_confirmation_received": True,
        "recipient_plaintext_values_exposed": False,
        "secret_values_exposed": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ETF_EU_CORRECTED_RESEND_AUTHORIZATION_OK | output={output}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Write the runtime corrected-resend authorization artifact.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--runtime-run-id", required=True)
    parser.add_argument("--correction-control-id", required=True)
    parser.add_argument("--github-run-id", required=True)
    parser.add_argument("--github-commit-sha", required=True)
    args = parser.parse_args()
    write_authorization(
        output=Path(args.output),
        runtime_run_id=args.runtime_run_id,
        correction_control_id=args.correction_control_id,
        github_run_id=args.github_run_id,
        github_commit_sha=args.github_commit_sha,
    )


if __name__ == "__main__":
    main()
