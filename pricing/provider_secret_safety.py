from __future__ import annotations

import os
from pathlib import Path

ALPHA_ROTATION_MARKER = Path("config/alpha_vantage_key_rotation_confirmed.json")


def enforce_provider_secret_safety() -> dict[str, str | bool]:
    """Disable a known-compromised Alpha Vantage secret until rotation is recorded.

    The marker is intentionally repository-controlled. Adding or replacing the GitHub
    secret alone does not silently reactivate the provider; the rotation must also be
    recorded as an explicit operational step.
    """
    alpha_present = bool(os.environ.get("ALPHA_VANTAGE_API_KEY", "").strip())
    rotation_confirmed = ALPHA_ROTATION_MARKER.exists()
    if alpha_present and not rotation_confirmed:
        os.environ.pop("ALPHA_VANTAGE_API_KEY", None)
    return {
        "alpha_vantage_secret_was_present": alpha_present,
        "alpha_vantage_rotation_confirmed": rotation_confirmed,
        "alpha_vantage_live_enabled": alpha_present and rotation_confirmed,
        "rotation_marker": str(ALPHA_ROTATION_MARKER),
    }
