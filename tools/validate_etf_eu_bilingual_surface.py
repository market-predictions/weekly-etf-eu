from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = {
    "schema_version",
    "status",
    "english_source_report",
    "review_only",
    "derived_from_english_eu_source_artifact",
    "dutch_companion_independent_research_pass",
    "production_delivery",
    "portfolio_mutation",
    "funding_authority",
    "valuation_grade",
}


class EtfEuBilingualSurfaceError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise EtfEuBilingualSurfaceError("payload root must be object")
    return payload


def validate_bilingual_surface(path: Path) -> dict[str, str]:
    payload = _load(path)
    missing = sorted(REQUIRED_FIELDS - set(payload))
    if missing:
        raise EtfEuBilingualSurfaceError("missing fields: " + ", ".join(missing))
    if payload.get("schema_version") != "etf_eu_bilingual_surface_readiness_v1":
        raise EtfEuBilingualSurfaceError("bad schema_version")
    if payload.get("status") not in {"minimal_readiness", "implemented", "deferred"}:
        raise EtfEuBilingualSurfaceError("bad status")
    if payload.get("review_only") is not True:
        raise EtfEuBilingualSurfaceError("review_only flag invalid")
    if payload.get("derived_from_english_eu_source_artifact") is not True:
        raise EtfEuBilingualSurfaceError("derived flag invalid")
    if payload.get("dutch_companion_independent_research_pass") is not False:
        raise EtfEuBilingualSurfaceError("independent pass flag invalid")
    for key in ("production_delivery", "portfolio_mutation", "funding_authority", "valuation_grade"):
        if payload.get(key) is not False:
            raise EtfEuBilingualSurfaceError(f"{key} flag invalid")
    english_report = Path(str(payload.get("english_source_report")))
    if not english_report.exists():
        raise EtfEuBilingualSurfaceError("english_source_report missing")
    print(f"ETF_EU_BILINGUAL_SURFACE_OK | artifact={path}")
    return {"status": "valid", "artifact": str(path)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_bilingual_surface(Path(args.artifact))


if __name__ == "__main__":
    main()
