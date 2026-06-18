from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_bilingual_report_surface_v1"
FALSE_FIELDS = [
    "production_delivery",
    "recipient_activation",
    "send_attempted",
    "portfolio_mutation",
    "candidate_promotion",
    "funding_authority",
    "valuation_grade",
]
REQUIRED_ARTIFACT_FIELDS = {
    "schema_version",
    "run_id",
    "status",
    "english_report_path",
    "dutch_report_path",
    "derived_from_english_eu_source_artifact",
    "dutch_companion_independent_research_pass",
    "meaning_parity_checked",
    "review_only",
    "selected_next_package",
    "selected_next_package_title",
    *FALSE_FIELDS,
}


class EtfEuMatureBilingualReportError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise EtfEuMatureBilingualReportError("artifact root must be object")
    return payload


def _require_text(text: str, snippets: list[str], label: str) -> None:
    missing = [snippet for snippet in snippets if snippet not in text]
    if missing:
        raise EtfEuMatureBilingualReportError(f"{label} missing: " + ", ".join(missing))


def validate_mature_bilingual_report(artifact_path: Path) -> dict[str, str]:
    artifact = _load(artifact_path)
    missing = sorted(REQUIRED_ARTIFACT_FIELDS - set(artifact))
    if missing:
        raise EtfEuMatureBilingualReportError("missing artifact fields: " + ", ".join(missing))
    if artifact.get("schema_version") != SCHEMA_VERSION:
        raise EtfEuMatureBilingualReportError("bad schema_version")
    if artifact.get("status") != "completed":
        raise EtfEuMatureBilingualReportError("status must be completed")
    if artifact.get("review_only") is not True:
        raise EtfEuMatureBilingualReportError("review_only must be true")
    if artifact.get("derived_from_english_eu_source_artifact") is not True:
        raise EtfEuMatureBilingualReportError("derived_from_english_eu_source_artifact must be true")
    if artifact.get("dutch_companion_independent_research_pass") is not False:
        raise EtfEuMatureBilingualReportError("Dutch companion independent pass must be false")
    if artifact.get("meaning_parity_checked") is not True:
        raise EtfEuMatureBilingualReportError("meaning_parity_checked must be true")
    for field in FALSE_FIELDS:
        if artifact.get(field) is not False:
            raise EtfEuMatureBilingualReportError(f"{field} must be false")
    en_path = Path(str(artifact.get("english_report_path") or ""))
    nl_path = Path(str(artifact.get("dutch_report_path") or ""))
    if not en_path.exists():
        raise EtfEuMatureBilingualReportError("English mature report missing")
    if not nl_path.exists():
        raise EtfEuMatureBilingualReportError("Dutch mature report missing")
    en = en_path.read_text(encoding="utf-8")
    nl = nl_path.read_text(encoding="utf-8")
    _require_text(
        en,
        [
            "ETF EU mature draft status",
            "review_only=true",
            "production_delivery=false",
            "portfolio_mutation=false",
            "funding_authority=false",
            "valuation_grade=false",
            "UCITS pricing evidence",
            "UCITS identity table",
            "Research proxy separation",
            "Source/freshness disclosure",
            "EU decision cockpit",
            "CSPX.L",
            "SXR8.DE",
            "U.S. ETFs remain research proxies only",
            "WP14J",
        ],
        "English report",
    )
    _require_text(
        nl,
        [
            "review-only",
            "geen productielevering",
            "geen ontvangers geactiveerd",
            "geen portefeuillemutatie",
            "geen financieringsautoriteit",
            "geen waarderingsautoriteit",
            "UCITS",
            "CSPX.L",
            "SXR8.DE",
            "Amerikaanse ETF's zijn alleen researchproxy's",
            "WP14J",
        ],
        "Dutch report",
    )
    if "production_delivery=true" in en or "valuation_grade=true" in en:
        raise EtfEuMatureBilingualReportError("English report contains promoted authority flag")
    print(f"ETF_EU_MATURE_BILINGUAL_REPORT_OK | artifact={artifact_path} | selected_next_package={artifact['selected_next_package']}")
    return {"status": "valid", "artifact": str(artifact_path), "selected_next_package": str(artifact["selected_next_package"])}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_mature_bilingual_report(Path(args.artifact))


if __name__ == "__main__":
    main()
