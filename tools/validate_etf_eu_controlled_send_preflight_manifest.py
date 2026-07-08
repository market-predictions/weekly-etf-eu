from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_delivery_manifest import validate_manifest

DEFAULT_MANIFEST = Path("output/delivery/etf_eu_controlled_send_preflight_manifest_20260708_000000.json")
DEFAULT_SENDER_PREFLIGHT = Path("output/delivery/etf_eu_sender_preflight_20260708_000000.json")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate(
    manifest_path: Path = DEFAULT_MANIFEST,
    sender_preflight_path: Path = DEFAULT_SENDER_PREFLIGHT,
) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    sender_preflight_path = Path(sender_preflight_path)
    _require(manifest_path.exists(), f"missing controlled-send preflight manifest: {manifest_path}")
    _require(sender_preflight_path.exists(), f"missing sender preflight evidence: {sender_preflight_path}")

    validate_manifest(manifest_path)
    payload = _load(manifest_path)
    sender = _load(sender_preflight_path)

    _require(payload["status"] == "ready_for_future_delivery", "manifest status must be ready_for_future_delivery")
    _require(payload["delivery_enabled"] is False, "delivery_enabled must remain false")
    _require(payload["receipt"]["receipt_status"] == "pending", "receipt status must be pending")
    receipt_path = Path(payload["receipt"]["receipt_path"])
    _require(str(receipt_path), "receipt path must be reserved")
    _require(not receipt_path.exists(), "reserved receipt file must not exist")

    authority = payload["authority"]
    for key in ["email_delivery", "production_delivery", "delivery_receipt", "pdf_generation"]:
        _require(authority[key] is False, f"authority.{key} must remain false")

    blockers = payload.get("blockers")
    _require(isinstance(blockers, list) and blockers, "blockers must be present")
    blocker_text = " ".join(str(item).lower() for item in blockers)
    for token in ["guard", "outbound", "success", "mvp08"]:
        _require(token in blocker_text, f"blockers missing token: {token}")

    _require(sender.get("schema_version") == "etf_eu_sender_preflight_v1", "sender preflight schema mismatch")
    _require(sender.get("delivery_mode") == "preflight_no_send", "sender preflight mode mismatch")
    _require(sender.get("send_performed") is False, "sender preflight must not perform send")
    _require(sender.get("delivery_success_claimed") is False, "sender preflight must not claim success")
    _require(sender.get("production_delivery") is False, "sender preflight production_delivery must be false")
    _require(sender.get("email_delivery") is False, "sender preflight email_delivery must be false")
    _require(sender.get("delivery_receipt") is False, "sender preflight delivery_receipt must be false")

    return {
        "status": "valid",
        "manifest": str(manifest_path),
        "sender_preflight": str(sender_preflight_path),
        "manifest_status": payload["status"],
        "delivery_enabled": payload["delivery_enabled"],
        "receipt_status": payload["receipt"]["receipt_status"],
        "receipt_file_created": receipt_path.exists(),
        "send_performed": sender["send_performed"],
        "delivery_success_claimed": sender["delivery_success_claimed"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--sender-preflight", default=str(DEFAULT_SENDER_PREFLIGHT))
    args = parser.parse_args()
    result = validate(Path(args.manifest), Path(args.sender_preflight))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
