from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing JSON artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _pdf_text(path: Path) -> str:
    if not path.exists():
        raise RuntimeError(f"Missing PDF artifact: {path}")
    return subprocess.run(["pdftotext", "-layout", str(path), "-"], check=True, text=True, capture_output=True).stdout


def _page_count(path: Path) -> int:
    raw = subprocess.run(["pdfinfo", str(path)], check=True, text=True, capture_output=True).stdout
    match = re.search(r"^Pages:\s+(\d+)\s*$", raw, flags=re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not determine page count for {path}")
    return int(match.group(1))


def _language_result(
    *,
    legacy_pdf: Path,
    v2_pdf: Path,
    report_date: str,
    language: str,
    validated_isin_first: bool,
) -> dict[str, Any]:
    legacy_text = _pdf_text(legacy_pdf)
    v2_text = _pdf_text(v2_pdf)
    legacy_pages = _page_count(legacy_pdf)
    v2_pages = _page_count(v2_pdf)
    investor = "Beleggersrapport" if language == "nl" else "Investor report"
    analyst = "Analistenrapport" if language == "nl" else "Analyst report"
    blockers: list[str] = []
    if report_date not in legacy_text or report_date not in v2_text:
        blockers.append("report date is not present in both outputs")
    if investor.casefold() not in v2_text.casefold() or analyst.casefold() not in v2_text.casefold():
        blockers.append("v2 investor/analyst hierarchy missing")
    if v2_pages <= legacy_pages:
        blockers.append(f"v2 does not add report depth: legacy_pages={legacy_pages}, v2_pages={v2_pages}")
    if not validated_isin_first:
        blockers.append("strict v2 validator did not confirm ISIN-first evidence")
    forbidden = [
        "candidate_requires_verification",
        "verified_ucits_trading_line",
        "valuation_grade=",
        "funding_authority=",
        "production_delivery_authority=",
    ]
    leaked = [token for token in forbidden if token.casefold() in v2_text.casefold()]
    if leaked:
        blockers.append("v2 internal-token leakage: " + ", ".join(leaked))
    return {
        "language": language,
        "legacy_pdf": str(legacy_pdf),
        "v2_pdf": str(v2_pdf),
        "legacy_page_count": legacy_pages,
        "v2_page_count": v2_pages,
        "additional_pages": v2_pages - legacy_pages,
        "report_date_consistent": report_date in legacy_text and report_date in v2_text,
        "investor_analyst_hierarchy_present": investor.casefold() in v2_text.casefold() and analyst.casefold() in v2_text.casefold(),
        "isin_first_visible": validated_isin_first,
        "isin_first_evidence_source": "strict_client_grade_validator",
        "pdf_isin_literal_count_diagnostic": v2_text.upper().count("ISIN"),
        "internal_token_leakage": leaked,
        "passed": not blockers,
        "blockers": blockers,
    }


def compare(args: argparse.Namespace) -> dict[str, Any]:
    state = _load_json(Path(args.v2_state))
    validation = _load_json(Path(args.v2_validation))
    pricing = _load_json(Path(args.pricing_artifact))
    macro = _load_json(Path(args.macro_artifact))
    history_rows = Path(args.valuation_history).read_text(encoding="utf-8").strip().splitlines()

    blockers: list[str] = []
    if state.get("state_valid") is not True:
        blockers.append("v2 normalized state invalid")
    if validation.get("client_grade_v2_passed") is not True:
        blockers.append("v2 strict client-grade validation failed")
    if (state.get("macro") or {}).get("fresh_for_report") is not True:
        blockers.append("v2 macro evidence is not fresh for report date")
    if pricing.get("min_threshold_met") is not True:
        blockers.append("fresh pricing threshold not met")
    if len([row for row in pricing.get("rows", []) if isinstance(row, dict) and row.get("close_price") is not None]) < 8:
        blockers.append("fewer than eight current pricing observations")
    if len(history_rows) < 3:
        blockers.append("valuation history was not refreshed with a current observation")
    if (macro.get("eu_adaptation") or {}).get("isin_first") is not True:
        blockers.append("macro adaptation does not preserve ISIN-first EU authority")

    dutch_validation = validation.get("dutch") if isinstance(validation.get("dutch"), dict) else {}
    english_validation = validation.get("english") if isinstance(validation.get("english"), dict) else {}
    dutch = _language_result(
        legacy_pdf=Path(args.legacy_dutch_pdf),
        v2_pdf=Path(args.v2_dutch_pdf),
        report_date=args.report_date,
        language="nl",
        validated_isin_first=dutch_validation.get("isin_first_visible") is True,
    )
    english = _language_result(
        legacy_pdf=Path(args.legacy_english_pdf),
        v2_pdf=Path(args.v2_english_pdf),
        report_date=args.report_date,
        language="en",
        validated_isin_first=english_validation.get("isin_first_visible") is True,
    )
    blockers.extend("NL: " + blocker for blocker in dutch["blockers"])
    blockers.extend("EN: " + blocker for blocker in english["blockers"])

    authority = state.get("authority") if isinstance(state.get("authority"), dict) else {}
    for field in ["valuation_grade", "funding_authority", "portfolio_mutation", "production_delivery_authority"]:
        if authority.get(field) is not False:
            blockers.append(f"authority field must remain false: {field}")

    result = {
        "schema_version": "etf_eu_production_v2_comparison_v2",
        "artifact_type": "etf_eu_production_v2_comparison",
        "generated_at_utc": _utc_now(),
        "run_id": args.run_id,
        "report_date": args.report_date,
        "report_suffix": args.report_suffix,
        "pricing_artifact": args.pricing_artifact,
        "macro_artifact": args.macro_artifact,
        "valuation_history": args.valuation_history,
        "same_current_inputs_used": True,
        "dutch": dutch,
        "english": english,
        "strict_v2_validation_passed": validation.get("client_grade_v2_passed") is True,
        "macro_fresh_for_report": (state.get("macro") or {}).get("fresh_for_report") is True,
        "pricing_threshold_passed": pricing.get("min_threshold_met") is True,
        "equity_surface": (state.get("equity_curve") or {}).get("surface") or ("chart" if (state.get("equity_curve") or {}).get("show_chart") else "cash_preservation_callout"),
        "portfolio_mutation": False,
        "transport_attempted": False,
        "production_delivery_performed": False,
        "promotion_recommended": not blockers,
        "blockers": blockers,
        "next_action": "PROMOTE_CLIENT_GRADE_V2_TO_ROUTINE_PRODUCTION" if not blockers else "REPAIR_CONCRETE_V2_COMPARISON_DEFECTS",
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare current Weekly ETF EU production and client-grade v2 shadow outputs.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--pricing-artifact", required=True)
    parser.add_argument("--macro-artifact", required=True)
    parser.add_argument("--valuation-history", required=True)
    parser.add_argument("--v2-state", required=True)
    parser.add_argument("--v2-validation", required=True)
    parser.add_argument("--legacy-dutch-pdf", required=True)
    parser.add_argument("--legacy-english-pdf", required=True)
    parser.add_argument("--v2-dutch-pdf", required=True)
    parser.add_argument("--v2-english-pdf", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    result = compare(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    if args.strict and result["promotion_recommended"] is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
