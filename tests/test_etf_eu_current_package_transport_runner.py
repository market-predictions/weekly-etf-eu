from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load(path: str) -> dict:
    return json.loads(read(path))


def test_current_package_transport_contract_and_runner_exist():
    assert (ROOT / "control/ETF_EU_CURRENT_PACKAGE_TRANSPORT_RUNNER_CONTRACT_V1.md").exists()
    runner = read("runtime/send_etf_eu_current_package_delivery.py")
    assert "--queue" in runner
    assert "dry_run" in runner
    assert "send" in runner
    assert "etf_eu_fresh_generation_package_v1" in runner
    assert "etf_eu_mvp19_fix2_ready_for_controlled_resend_v1" not in runner


def test_workflow_wires_current_package_runner():
    workflow = read(".github/workflows/send-weekly-etf-eu-current-package.yml")
    assert "control/run_queue/etf_eu_current_package_delivery_request_*.md" in workflow
    assert "runtime.send_etf_eu_current_package_delivery" in workflow
    assert "--mode dry_run" in workflow
    assert "--mode send" in workflow
    assert "confirm_guarded_send" in workflow


def test_adapter_records_no_execution():
    adapter = load("output/delivery_control/etf_eu_current_package_transport_runner_adapter_20260710_000000.json")
    assert adapter["current_package_chain_supported"] is True
    assert adapter["transport_runner_adapter_created"] is True
    assert adapter["dry_run_supported"] is True
    assert adapter["send_supported_with_guard"] is True
    assert adapter["send_mode_wired"] is True
    assert adapter["delivery_authorized"] is True
    assert adapter["send_command_allowed"] is True
    assert adapter["run_queue_allowed"] is True
    assert adapter["run_queue_created"] is True
    assert adapter["live_transport_executed"] is False
    assert adapter["transport_attempted"] is False
    assert adapter["receipt_confirmed"] is False


def test_queue_uses_current_package_chain():
    queue = read("control/run_queue/etf_eu_current_package_delivery_request_20260710_000000.md")
    assert "output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json" in queue
    assert "output/delivery_authorization/etf_eu_guarded_send_authorization_20260710_000000.json" in queue
    assert "MVP19" not in queue
