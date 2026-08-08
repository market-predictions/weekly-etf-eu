from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

ALPHA_ROTATION_MARKER = Path("config/alpha_vantage_key_rotation_confirmed.json")
ALPHA_ROTATION_SCHEMA = "alpha_vantage_key_rotation_confirmation_v1"
ALPHA_SECRET_NAME = "ALPHA_VANTAGE_API_KEY"


def _load_valid_rotation_marker(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, "marker_absent"
    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False, "marker_unreadable_or_invalid_json"
    if not isinstance(payload, Mapping):
        return False, "marker_not_object"
    if payload.get("schema_version") != ALPHA_ROTATION_SCHEMA:
        return False, "marker_schema_mismatch"
    if payload.get("rotation_confirmed") is not True:
        return False, "marker_rotation_not_confirmed"
    if payload.get("secret_value_recorded") is not False:
        return False, "marker_secret_recording_contract_failed"
    if str(payload.get("repository_secret_name") or "").strip() != ALPHA_SECRET_NAME:
        return False, "marker_secret_name_mismatch"
    if not str(payload.get("confirmed_at_utc") or "").strip():
        return False, "marker_confirmation_time_missing"
    return True, "valid_rotation_confirmation"


def enforce_provider_secret_safety() -> dict[str, str | bool]:
    """Disable Alpha Vantage until a valid post-rotation record exists.

    Replacing the GitHub secret does not silently reactivate the provider. The
    repository-controlled marker must also be valid and must contain non-secret
    confirmation metadata only. An empty, malformed or stale marker fails closed.
    """
    alpha_present = bool(os.environ.get(ALPHA_SECRET_NAME, "").strip())
    rotation_confirmed, marker_status = _load_valid_rotation_marker(ALPHA_ROTATION_MARKER)
    if alpha_present and not rotation_confirmed:
        os.environ.pop(ALPHA_SECRET_NAME, None)
    return {
        "alpha_vantage_secret_was_present": alpha_present,
        "alpha_vantage_rotation_confirmed": rotation_confirmed,
        "alpha_vantage_live_enabled": alpha_present and rotation_confirmed,
        "rotation_marker": str(ALPHA_ROTATION_MARKER),
        "rotation_marker_status": marker_status,
        "rotation_marker_schema": ALPHA_ROTATION_SCHEMA,
    }
