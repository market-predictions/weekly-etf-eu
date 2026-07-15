from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime.equity_curve_eu_contract import validate_equity_curve_contract


SECTIONS = {
    "nl": [
        "Besliscockpit", "Portefeuille en kapitaal", "Regime- en beleidsdashboard",
        "Structurele UCITS-kansenradar", "Belangrijkste risico’s en invalidaties",
        "Portefeuilleontwikkeling", "Conclusie", "Allocatiekaart", "Tweede-orde-effecten",
        "UCITS-kandidaten en prijsbewijs", "Verificatiefunnel", "Review huidige posities",
        "Vervanging, rotatie en vermijdingsradar", "Input voor de volgende run", "Disclaimer",
    ],
    "en": [
        "Decision cockpit", "Portfolio and capital", "Regime and policy dashboard",
        "Structural UCITS opportunity radar", "Key risks and invalidations",
        "Portfolio development", "Conclusion", "Allocation map", "Second-order effects",
        "UCITS candidates and pricing evidence", "Verification funnel", "Current-position review",
        "Replacement, rotation and avoidance radar", "Input for the next run", "Disclaimer",
    ],
}

FORBIDDEN = [
    "valuation_grade=", "funding_authority=", "portfolio_mutation=",
    "production_delivery_authority=", "candidate_requires_verification",
    "verified_ucits_trading_line", "priced_non_authoritative", "fetch_failed", "```", "|---|",
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _text(path: Path) -> str:
    if not path.exists():
        raise RuntimeError(f"Missing artifact: {path}")
    return path.read_text(encoding="utf-8")


def _pdf_text(path: Path) -> str:
    return subprocess.run(["pdftotext", "-layout", str(path), "-"], check=True, text=True, capture_output=True).stdout


def _pages(path: Path) -> int:
    raw = subprocess.run(["pdfinfo", str(path)], check=True, text=True, capture_output=True).stdout
    match = re.search(r"^Pages:\s+(\d+)\s*$", raw, flags=re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not read page count: {path}")
    return int(match.group(1))


def validate_language(state: dict[str, Any], *, language: str, html_path: Path, pdf_path: Path) -> dict[str, Any]:
    html_text = _text(html_path)
    pdf_text = _pdf_text(pdf_path)
    combined = html_text + "\n" + pdf_text
    lower = combined.casefold()
    missing = [item for item in SECTIONS[language] if item.casefold() not in lower]
    forbidden = [item for item in FORBIDDEN if item.casefold() in lower]
    page_count = _pages(pdf_path)
    blockers: list[str] = []
    if missing:
        blockers.append("missing sections: " + ", ".join(missing))
    if forbidden:
        blockers.append("forbidden tokens: " + ", ".join(forbidden))
    if page_count < 6 or page_count > 14:
        blockers.append(f"page count outside 6-14: {page_count}")
    investor = "Beleggersrapport" if language == "nl" else "Investor report"
    analyst = "Analistenrapport" if language == "nl" else "Analyst report"
    if investor.casefold() not in lower or analyst.casefold() not in lower:
        blockers.append("investor/analyst hierarchy missing")
    if combined.upper().count("ISIN") < 8:
        blockers.append("ISIN-first evidence not visible enough")
    research = "alleen onderzoek" if language == "nl" else "research only"
    if research.casefold() not in lower:
        blockers.append("research references not labelled")
    if state.get("macro", {}).get("fresh_for_report") is not True:
        disclosure = "Macro-refresh vereist" if language == "nl" else "Macro refresh required"
        if disclosure.casefold() not in lower:
            blockers.append("stale macro disclosure missing")
    blockers.extend(validate_equity_curve_contract(state, html_text))
    return {
        "language": language,
        "page_count": page_count,
        "missing_sections": missing,
        "forbidden_tokens": forbidden,
        "passed": not blockers,
        "blockers": blockers,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True)
    parser.add_argument("--dutch-html", required=True)
    parser.add_argument("--dutch-pdf", required=True)
    parser.add_argument("--english-html", required=True)
    parser.add_argument("--english-pdf", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    state = json.loads(_text(Path(args.state)))
    blockers: list[str] = []
    if state.get("state_valid") is not True:
        blockers.append("normalized state invalid")
    authority = state.get("authority") or {}
    if authority.get("canonical_identity") != "isin_first" or authority.get("us_etfs_research_only") is not True:
        blockers.append("EU identity boundary failed")
    for key in ["valuation_grade", "funding_authority", "portfolio_mutation", "production_delivery_authority"]:
        if authority.get(key) is not False:
            blockers.append(f"authority field must remain false: {key}")

    nl = validate_language(state, language="nl", html_path=Path(args.dutch_html), pdf_path=Path(args.dutch_pdf))
    en = validate_language(state, language="en", html_path=Path(args.english_html), pdf_path=Path(args.english_pdf))
    blockers.extend("NL: " + item for item in nl["blockers"])
    blockers.extend("EN: " + item for item in en["blockers"])

    result = {
        "schema_version": "etf_eu_client_grade_report_v2_validation_v1",
        "generated_at_utc": _now(),
        "run_id": state.get("run_id"),
        "source_run_id": state.get("source_run_id"),
        "report_date": state.get("report_date"),
        "dutch": nl,
        "english": en,
        "client_grade_v2_passed": not blockers,
        "strict_mode": args.strict,
        "blockers": blockers,
        "warnings": state.get("warnings") or [],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    if args.strict and result["client_grade_v2_passed"] is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
