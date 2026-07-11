from pathlib import Path


def test_current_package_wiring_files_exist() -> None:
    paths = [
        "control/ETF_EU_DELIVERY_WORKFLOW_WIRING_CONTRACT_V1.md",
        "tools/prepare_etf_eu_current_package_delivery_queue.py",
        "tools/validate_etf_eu_current_package_delivery_queue.py",
        "tools/validate_etf_eu_delivery_workflow_wiring.py",
        ".github/workflows/send-weekly-etf-eu-current-package.yml",
        "control/run_queue/etf_eu_current_package_delivery_request_20260710_000000.md",
        "output/delivery_control/etf_eu_delivery_workflow_wiring_20260710_000000.json",
    ]
    for item in paths:
        assert Path(item).exists(), item


def test_queue_references_current_package_chain() -> None:
    text = Path("control/run_queue/etf_eu_current_package_delivery_request_20260710_000000.md").read_text(encoding="utf-8")
    assert "etf_eu_current_package_delivery_queue_v1" in text
    assert "etf_eu_fresh_generation_package_manifest_20260710_000000.json" in text
    assert "etf_eu_guarded_send_authorization_20260710_000000.json" in text
    assert "etf_eu_controlled_delivery_decision_20260710_000000.json" in text
    assert "etf_eu_controlled_delivery_transport_selection_20260710_000000.json" in text
    assert "20260709" not in text
    assert "MVP19" not in text


def test_workflow_has_current_package_queue_trigger() -> None:
    workflow = Path(".github/workflows/send-weekly-etf-eu-current-package.yml").read_text(encoding="utf-8")
    assert "etf_eu_current_package_delivery_request_*.md" in workflow
    assert "validate_only" in workflow
    assert "dry_run" in workflow
    assert "ETF_EU_CURRENT_PACKAGE_QUEUE_OK" in workflow
    assert "20260709_000000" not in workflow


def test_wiring_artifact_keeps_delivery_unexecuted() -> None:
    text = Path("output/delivery_control/etf_eu_delivery_workflow_wiring_20260710_000000.json").read_text(encoding="utf-8")
    assert '"current_package_chain_supported": true' in text
    assert '"run_queue_created": true' in text
    assert '"transport_attempted": false' in text
    assert '"send_executed": false' in text
    assert '"receipt_confirmed": false' in text
