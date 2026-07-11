from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RUNNER = Path("runtime/send_etf_eu_current_package_delivery.py")
WORKFLOW = Path(".github/workflows/send-weekly-etf-eu-current-package.yml")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_adapter(adapter_path: Path) -> dict[str, Any]:
    _require(adapter_path.exists(), f"adapter missing: {adapter_path}")
    data = _load(adapter_path)
    _require(data.get("schema_version") == "etf_eu_current_package_transport_runner_adapter_v1", "adapter schema mismatch")
    _require(data.get("artifact_type") == "etf_eu_current_package_transport_runner_adapter", "adapter type mismatch")
    _require(data.get("current_package_chain_supported") is True, "current package chain not supported")
    _require(data.get("transport_runner_adapter_created") is True, "runner adapter not created")
    _require(data.get("dry_run_supported") is True, "dry_run not supported")
    _require(data.get("send_supported_with_guard") is True, "guarded send not supported")
    _require(data.get("send_mode_wired") is True, "send branch not wired")
    _require(data.get("delivery_authorized") is True, "delivery_authorized not true")
    _require(data.get("send_command_allowed") is True, "send_command_allowed not true")
    _require(data.get("run_queue_allowed") is True, "run_queue_allowed not true")
    _require(data.get("run_queue_created") is True, "run_queue_created not true")
    for key in [
        "workflow_dispatch_allowed",
        "transport_execution_allowed",
        "live_transport_executed",
        "send_executed",
        "transport_attempted",
        "transport_success",
        "receipt_confirmed",
        "recipient_plaintext_values_exposed",
        "secret_values_exposed",
        "raw_receipt_pdf_stored_in_github",
    ]:
        _require(data.get(key) is False, f"{key} must be false")

    _require(RUNNER.exists(), "current-package runner missing")
    _require(WORKFLOW.exists(), "current-package workflow missing")
    runner_text = RUNNER.read_text(encoding="utf-8")
    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    _require("--queue" in runner_text, "runner must accept queue input")
    _require("dry_run" in runner_text, "runner must support dry_run")
    _require("send" in runner_text, "runner must support send")
    _require("etf_eu_current_package_delivery_request_*.md" in workflow_text, "workflow missing current queue trigger")
    _require("runtime.send_etf_eu_current_package_delivery" in workflow_text, "workflow does not call current runner")
    _require("confirm_guarded_send" in workflow_text, "workflow missing guarded send confirmation")
    _require("MVP19" not in workflow_text, "current workflow must not be MVP19-only")
    return {"status": "valid", "adapter": str(adapter_path), "runner": str(RUNNER), "workflow": str(WORKFLOW)}


def validate_result(result_path: Path) -> dict[str, Any]:
    _require(result_path.exists(), f"result missing: {result_path}")
    data = _load(result_path)
    _require(data.get("schema_version") == "etf_eu_current_package_transport_result_v1", "result schema mismatch")
    mode = data.get("delivery_mode")
    _require(mode in {"dry_run", "send"}, f"invalid mode={mode}")
    _require(data.get("recipient_plaintext_values_exposed") is False, "recipient plaintext exposed")
    _require(data.get("secret_values_exposed") is False, "secret values exposed")
    _require(data.get("raw_receipt_pdf_stored_in_github") is False, "raw receipt material stored")
    _require(data.get("receipt_confirmed") is False, "receipt cannot be confirmed by transport result")
    if mode == "dry_run":
        _require(data.get("transport_attempted") is False, "dry_run attempted transport")
        _require(data.get("transport_success") is False, "dry_run claimed success")
    if data.get("transport_success") is True:
        _require(data.get("transport_attempted") is True, "success requires attempted transport")
        _require(bool(data.get("message_id_or_receipt_reference")), "success requires message reference")
    evidence = Path(str(data.get("delivery_evidence_path") or ""))
    _require(evidence.exists(), f"evidence missing: {evidence}")
    return {"status": "valid", "result": str(result_path), "evidence": str(evidence)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--result", default=None)
    args = parser.parse_args()
    output = validate_adapter(Path(args.adapter))
    if args.result:
        output["result_validation"] = validate_result(Path(args.result))
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
