from __future__ import annotations

import argparse
import json
from pathlib import Path

WORKFLOW_PATH = Path(".github/workflows/send-weekly-etf-eu-current-package.yml")
QUEUE_TRIGGER = "control/run_queue/etf_eu_current_package_delivery_request_*.md"


def _read_json(path: Path) -> dict:
    if not path.exists():
        raise RuntimeError(f"missing JSON artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate(artifact_path: Path) -> dict[str, object]:
    artifact = _read_json(artifact_path)
    if artifact.get("schema_version") != "etf_eu_delivery_workflow_wiring_v1":
        raise RuntimeError("workflow wiring schema mismatch")
    if artifact.get("artifact_type") != "etf_eu_delivery_workflow_wiring":
        raise RuntimeError("workflow wiring artifact type mismatch")
    if artifact.get("current_package_chain_supported") is not True:
        raise RuntimeError("current package chain is not supported")
    if artifact.get("legacy_mvp19_fix2_only") is not False:
        raise RuntimeError("workflow must not be legacy MVP19/FIX2 only")
    if artifact.get("validate_only_supported") is not True:
        raise RuntimeError("validate_only support missing")
    if artifact.get("dry_run_supported") is not True:
        raise RuntimeError("dry_run support missing")
    if artifact.get("run_queue_created") is not True:
        raise RuntimeError("run queue was not created")
    if artifact.get("run_queue_allowed") is not True:
        raise RuntimeError("run_queue_allowed must be true")
    for key in ["transport_attempted", "send_executed", "transport_success", "receipt_confirmed", "recipient_plaintext_values_exposed", "secret_values_exposed", "raw_receipt_pdf_stored_in_github"]:
        if artifact.get(key) is not False:
            raise RuntimeError(f"{key} must be false")

    workflow = Path(str(artifact.get("workflow_file") or WORKFLOW_PATH))
    if not workflow.exists():
        raise RuntimeError(f"workflow file missing: {workflow}")
    text = workflow.read_text(encoding="utf-8")
    for needle in [QUEUE_TRIGGER, "validate_only", "dry_run", "ETF_EU_CURRENT_PACKAGE_QUEUE_OK"]:
        if needle not in text:
            raise RuntimeError(f"workflow missing current-package marker: {needle}")
    if "20260709_000000" in text or "MVP19-FIX2" in text:
        raise RuntimeError("current-package workflow must not hardcode legacy MVP19/FIX2 inputs")

    queue = Path(str(artifact.get("queue_artifact") or ""))
    if not queue.exists():
        raise RuntimeError(f"queue artifact missing: {queue}")
    if "etf_eu_current_package_delivery_queue_v1" not in queue.read_text(encoding="utf-8"):
        raise RuntimeError("queue artifact schema marker missing")

    return {"status": "valid", "artifact": str(artifact_path), "workflow": str(workflow), "queue": str(queue)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ETF EU current-package workflow wiring.")
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()
    print(json.dumps(validate(Path(args.artifact)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
