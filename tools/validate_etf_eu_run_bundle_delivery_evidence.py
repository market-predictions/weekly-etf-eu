from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_delivery_evidence import validate as validate_delivery_evidence


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate(fixture_path: Path) -> dict[str, Any]:
    fixture_path = Path(fixture_path)
    _require(fixture_path.exists(), f"missing run-bundle delivery evidence fixture: {fixture_path}")
    fixture = _load(fixture_path)
    _require(fixture.get("schema_version") == "etf_eu_run_bundle_delivery_evidence_fixture_v1", "schema mismatch")
    evidence_path = Path(str(fixture.get("delivery_evidence_path") or ""))
    _require(evidence_path.exists(), f"delivery evidence path missing: {evidence_path}")
    evidence = validate_delivery_evidence(evidence_path)
    _require(fixture.get("delivery_evidence_status") == evidence["delivery_status"], "delivery evidence status mismatch")
    _require(fixture.get("controlled_send_preflight_manifest") == "output/delivery/etf_eu_controlled_send_preflight_manifest_20260708_000000.json", "preflight manifest path mismatch")
    if fixture.get("delivery_evidence_status") == "not_attempted":
        _require(fixture.get("delivery_success") is False, "not_attempted fixture must not claim success")
    for key in ["production_delivery", "email_delivery", "delivery_receipt", "workflow_guard_removed", "delivery_mode_send_unlocked"]:
        _require(fixture.get(key) is False, f"expected false for {key}")
    _require(fixture.get("workflow_guard_present") is True, "workflow guard must be present")
    return {
        "status": "valid",
        "fixture": str(fixture_path),
        "delivery_evidence_path": str(evidence_path),
        "delivery_evidence_status": fixture.get("delivery_evidence_status"),
        "delivery_success": fixture.get("delivery_success"),
        "workflow_guard_present": fixture.get("workflow_guard_present"),
        "workflow_guard_removed": fixture.get("workflow_guard_removed"),
        "delivery_mode_send_unlocked": fixture.get("delivery_mode_send_unlocked"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", required=True)
    args = parser.parse_args()
    print(json.dumps(validate(Path(args.fixture)), indent=2))


if __name__ == "__main__":
    main()
