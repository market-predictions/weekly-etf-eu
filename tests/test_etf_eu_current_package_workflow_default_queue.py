from __future__ import annotations

import re
from pathlib import Path


WORKFLOW = Path(".github/workflows/send-weekly-etf-eu-current-package.yml")


def _default_queue_path(workflow_text: str) -> Path:
    match = re.search(
        r"queue_path:\n(?:.*\n){0,4}?\s+default:\s+\"([^\"]+)\"",
        workflow_text,
    )
    assert match is not None, "workflow_dispatch queue_path default not found"
    return Path(match.group(1))


def _parse_queue(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def test_guarded_send_default_points_to_existing_locked_prepared_queue() -> None:
    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    queue_path = _default_queue_path(workflow_text)

    assert queue_path.as_posix().startswith("control/prepared_delivery/")
    assert queue_path.exists(), f"prepared default queue missing: {queue_path}"

    queue = _parse_queue(queue_path)
    assert queue["run_id"] == "20260717_141500"
    assert queue["report_suffix"] == "260717_06"
    assert queue["accepted_package_lock"] == (
        "output/delivery_control/etf_eu_accepted_package_lock_20260717_141500.json"
    )
    assert Path(queue["accepted_package_lock"]).exists()
    assert queue["delivery_authorized"] == "true"
    assert queue["send_command_allowed"] == "true"


def test_guarded_send_rejects_legacy_or_unlocked_queue_paths_before_transport() -> None:
    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    assert "ETF_EU_SEND_REQUIRES_PREPARED_DELIVERY_QUEUE" in workflow_text
    assert "ETF_EU_PREPARED_QUEUE_LOCK_REFERENCE_MISSING" in workflow_text
    assert "grep -q '^accepted_package_lock='" in workflow_text
