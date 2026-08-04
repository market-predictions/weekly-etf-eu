from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from runtime import finalize_etf_eu_sister_report_nl_language as legacy


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def sanitize_manifest(manifest_path: Path) -> None:
    manifest = load_object(manifest_path)
    nl = manifest.get("languages", {}).get("nl", {})
    html_path = Path(str(nl.get("html") or ""))
    if not html_path.exists():
        raise RuntimeError(f"Dutch source HTML missing: {html_path}")
    text = html_path.read_text(encoding="utf-8")
    replacements = (
        (
            r"promoted exposures are not represented(?: in the current portfolio)?",
            "gepromoveerde blootstellingen zijn niet allemaal als afzonderlijke portefeuillepositie opgenomen",
        ),
        (
            r"promoted exposure is not represented(?: in the current portfolio)?",
            "de gepromoveerde blootstelling is niet als afzonderlijke portefeuillepositie opgenomen",
        ),
        (
            r"promoted exposures are not yet implemented",
            "gepromoveerde blootstellingen zijn nog niet allemaal als afzonderlijke modelpositie opgenomen",
        ),
        (
            r"promoted exposure is not yet implemented",
            "de gepromoveerde blootstelling is nog niet als afzonderlijke modelpositie opgenomen",
        ),
    )
    updated = text
    for pattern, replacement in replacements:
        updated = re.sub(pattern, replacement, updated, flags=re.IGNORECASE)
    if updated != text:
        html_path.write_text(updated, encoding="utf-8")
    print(f"ETF_EU_NL_ACTIVATED_WARNING_SANITIZED | changed={str(updated != text).lower()} | html={html_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    sanitize_manifest(args.manifest)
    legacy.apply(args.manifest)
    print(args.manifest)


if __name__ == "__main__":
    main()
