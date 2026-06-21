from __future__ import annotations

import argparse
import json
from pathlib import Path

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_plan_20260618_000000.json")
MARKDOWN_PLAN = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_plan_20260618_000000.md")
ORIGINAL_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf")
LAYOUT_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_mvp_layout_20260618_000000.pdf")

REQUIRED_SECTIONS = [
    "## 1. Planning status",
    "## 2. Source artifacts inspected",
    "## 3. What WP15A proved",
    "## 4. What WP15C improved",
    "## 5. Remaining gap to premium client-grade",
    "## 6. Target premium cockpit structure",
    "## 7. Visual hierarchy requirements",
    "## 8. Dutch-first client reading flow",
    "## 9. Table and data presentation requirements",
    "## 10. Boundary/authority display requirements",
    "## 11. Research proxy separation requirements",
    "## 12. PDF renderer implications",
    "## 13. Validation requirements for the future implementation package",
    "## 14. Non-goals",
    "## 15. Recommended next package",
]

REQUIRED_PLAN_MARKERS = [
    "Page 1 — Executive cockpit cover",
    "Page 2 — Decision cockpit",
    "Page 3 — UCITS evidence cockpit",
    "Page 4 — Research proxy separation",
    "Page 5 — Action and validation checklist",
    "Decision framework",
    "Input/state contract",
    "Output contract",
    "Operational runbook",
    "delivery_authorization_decision=remain_blocked",
    "production_delivery=false",
    "portfolio_mutation=false",
    "candidate_promotion=false",
    "funding_authority=false",
    "valuation_grade=false",
    "selected_next_package=WP15F",
]


class PremiumSurfacePlanValidationError(RuntimeError):
    pass


def _require(path: Path, label: str) -> None:
    if not path.exists():
        raise PremiumSurfacePlanValidationError(f"missing {label}: {path}")


def _assert_true(data: dict, key: str) -> None:
    if data.get(key) is not True:
        raise PremiumSurfacePlanValidationError(f"expected true: {key}")


def _assert_false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        raise PremiumSurfacePlanValidationError(f"expected false: {key}")


def validate_premium_surface_plan(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise PremiumSurfacePlanValidationError(f"unexpected artifact path: {path}")

    _require(ARTIFACT, "JSON planning artifact")
    _require(MARKDOWN_PLAN, "markdown planning artifact")
    _require(ORIGINAL_PDF, "original WP15A PDF")
    _require(LAYOUT_PDF, "WP15C layout PDF")

    if not ORIGINAL_PDF.read_bytes().startswith(b"%PDF"):
        raise PremiumSurfacePlanValidationError("original PDF header missing")
    if not LAYOUT_PDF.read_bytes().startswith(b"%PDF"):
        raise PremiumSurfacePlanValidationError("layout PDF header missing")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise PremiumSurfacePlanValidationError("JSON planning artifact must be an object")

    expected_values = {
        "schema_version": "etf_eu_cockpit_pdf_premium_surface_plan_v1",
        "run_id": "20260618_000000",
        "status": "completed",
        "work_package": "WP15E",
        "source_work_package": "WP15D",
        "premium_surface_markdown_plan": str(MARKDOWN_PLAN),
        "premium_surface_json_plan": str(ARTIFACT),
        "original_pdf_mvp_path": str(ORIGINAL_PDF),
        "layout_pdf_path": str(LAYOUT_PDF),
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "WP15F",
    }
    for key, expected in expected_values.items():
        if data.get(key) != expected:
            raise PremiumSurfacePlanValidationError(f"unexpected {key}: {data.get(key)!r}")

    for key in ["premium_surface_planning_created", "original_pdf_mvp_preserved", "layout_pdf_preserved", "planning_only"]:
        _assert_true(data, key)

    for key in [
        "new_pdf_created",
        "renderer_changed",
        "pricing_evidence_changed",
        "recommendation_logic_changed",
        "live_data_fetch_performed",
        "production_delivery",
        "portfolio_mutation",
        "candidate_promotion",
        "funding_authority",
        "valuation_grade",
    ]:
        _assert_false(data, key)

    markdown = MARKDOWN_PLAN.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        if section not in markdown:
            raise PremiumSurfacePlanValidationError(f"markdown plan missing section: {section}")
    for marker in REQUIRED_PLAN_MARKERS:
        if marker not in markdown:
            raise PremiumSurfacePlanValidationError(f"markdown plan missing marker: {marker}")

    print(f"ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_PLAN_OK | artifact={ARTIFACT} | selected_next_package=WP15F")
    return {"status": "valid", "artifact": str(ARTIFACT), "selected_next_package": "WP15F"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_premium_surface_plan(Path(args.artifact))


if __name__ == "__main__":
    main()
