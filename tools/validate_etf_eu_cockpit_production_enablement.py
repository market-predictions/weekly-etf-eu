from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from runtime.additive_etf_eu_cockpit_front_page import SUPPRESSED_SUMMARY_CLASS
from runtime.render_etf_eu_cockpit_front_page import FRONT_PAGE_MARKER


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"missing validation input: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _pages(path: Path) -> int:
    result = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True)
    match = re.search(r"^Pages:\s+(\d+)$", result.stdout, flags=re.MULTILINE)
    if match is None:
        raise RuntimeError(f"unable to read PDF page count: {path}")
    return int(match.group(1))


def _front(html_text: str) -> str:
    marker = html_text.find(FRONT_PAGE_MARKER)
    if marker < 0:
        return ""
    start = html_text.rfind("<section", 0, marker)
    end = html_text.find("</section>", marker)
    return html_text[start : end + len("</section>")] if start >= 0 and end >= 0 else ""


def validate(args: argparse.Namespace) -> dict[str, Any]:
    replay = _load(Path(args.replay))
    blockers: list[str] = []
    if replay.get("exact_current_state_used") is not True:
        blockers.append("replay did not use exact current state")
    if replay.get("non_delivery_replay") is not True:
        blockers.append("replay is not marked non-delivery")
    if replay.get("protected_inputs_unchanged") is not True:
        blockers.append("protected inputs changed")
    if replay.get("portfolio_mutation") is not False or replay.get("pricing_mutation") is not False:
        blockers.append("replay mutation boundary failed")
    if replay.get("external_transport") is not False:
        blockers.append("external transport boundary failed")

    disabled = replay.get("disabled_result") or {}
    if disabled.get("status") != "disabled" or not all((disabled.get("byte_identity") or {}).values()):
        blockers.append("disabled classic contract failed")
    if disabled.get("browser_audit_files_created") is not False:
        blockers.append("disabled mode created cockpit audit files")

    enabled = replay.get("enabled_result") or {}
    for key in ("front_page_count_nl", "front_page_count_en", "page_delta_nl", "page_delta_en"):
        if enabled.get(key) != 1:
            blockers.append(f"enabled contract mismatch: {key}")
    if enabled.get("attachment_contract_file_count") != 4:
        blockers.append("attachment contract changed")
    if enabled.get("primary_html_mode") != "email_safe_inline":
        blockers.append("primary HTML is not email-safe inline")
    if enabled.get("pdf_source_mode") != "browser_svg":
        blockers.append("PDF source is not browser SVG mode")

    paths = {
        key: Path(str(enabled.get(key) or ""))
        for key in (
            "dutch_primary_html", "english_companion_html", "dutch_primary_pdf", "english_companion_pdf",
            "dutch_browser_html", "english_browser_html",
        )
    }
    for key, path in paths.items():
        if not path.exists():
            blockers.append(f"enabled output missing: {key}")

    for language, primary_key, browser_key, pdf_key, investor, analyst in (
        ("nl", "dutch_primary_html", "dutch_browser_html", "dutch_primary_pdf", "Beleggersrapport", "Analistenrapport"),
        ("en", "english_companion_html", "english_browser_html", "english_companion_pdf", "Investor report", "Analyst report"),
    ):
        if not all(paths[key].exists() for key in (primary_key, browser_key, pdf_key)):
            continue
        primary = paths[primary_key].read_text(encoding="utf-8")
        browser = paths[browser_key].read_text(encoding="utf-8")
        primary_front = _front(primary)
        browser_front = _front(browser)
        if primary.count(FRONT_PAGE_MARKER) != 1 or browser.count(FRONT_PAGE_MARKER) != 1:
            blockers.append(f"{language}: front-page count mismatch")
        if 'data-render-mode="email"' not in primary_front or "style=" not in primary_front:
            blockers.append(f"{language}: primary HTML is not inline email mode")
        if "<style" in primary_front.lower():
            blockers.append(f"{language}: primary front page contains style block")
        if 'data-render-mode="browser"' not in browser_front or "<svg" not in browser_front:
            blockers.append(f"{language}: browser audit surface missing SVG mode")
        if "display:none!important" not in primary or primary.count(SUPPRESSED_SUMMARY_CLASS) != 1:
            blockers.append(f"{language}: investor summary suppression failed")
        front_index = primary.find(FRONT_PAGE_MARKER)
        investor_index = primary.find(investor, front_index + 1)
        analyst_index = primary.find(analyst, investor_index + 1)
        if not (front_index >= 0 and investor_index > front_index and analyst_index > investor_index):
            blockers.append(f"{language}: document order failed")
        if sum(f'<span class="badge">{number}</span>' in primary for number in range(1, 16)) != 15:
            blockers.append(f"{language}: classic section body changed")
        if _pages(paths[pdf_key]) != (enabled.get("enabled_pages") or {}).get(language):
            blockers.append(f"{language}: replay PDF page count mismatch")

    builder_text = Path(args.builder).read_text(encoding="utf-8")
    required_builder_tokens = [
        "apply_cockpit_to_package",
        "configured_feature_value",
        "cockpit_front_page_enabled",
        "cockpit_email_safe_surface_is_primary_html",
        "dutch_primary_browser_html",
        "english_companion_browser_html",
    ]
    for token in required_builder_tokens:
        if token not in builder_text:
            blockers.append(f"package builder missing integration token: {token}")

    workflow_text = Path(args.workflow).read_text(encoding="utf-8")
    expected_line = "MRKT_RPRTS_ETF_EU_COCKPIT_FRONT_PAGE: enabled"
    if expected_line not in workflow_text:
        blockers.append("routine workflow does not explicitly enable the cockpit")
    if "Generate and Validate Preview (NO EMAIL)" not in workflow_text:
        blockers.append("routine workflow non-delivery boundary missing")

    payload = {
        "schema_version": "etf_eu_cockpit_production_enablement_validation_v1",
        "artifact_type": "etf_eu_cockpit_production_enablement_validation",
        "passed": not blockers,
        "blockers": blockers,
        "source_replay": str(args.replay),
        "exact_current_state_used": replay.get("exact_current_state_used") is True,
        "non_delivery_replay": replay.get("non_delivery_replay") is True,
        "disabled_classic_contract_passed": disabled.get("status") == "disabled" and all((disabled.get("byte_identity") or {}).values()),
        "enabled_page_delta_nl": enabled.get("page_delta_nl"),
        "enabled_page_delta_en": enabled.get("page_delta_en"),
        "attachment_contract_file_count": enabled.get("attachment_contract_file_count"),
        "protected_inputs_unchanged": replay.get("protected_inputs_unchanged") is True,
        "production_workflow_feature_enabled": expected_line in workflow_text,
        "portfolio_mutation": False,
        "external_transport": False,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ETF EU cockpit production enablement evidence.")
    parser.add_argument("--replay", required=True)
    parser.add_argument("--builder", default="tools/build_etf_eu_routine_report_package_v2.py")
    parser.add_argument("--workflow", default=".github/workflows/run-weekly-etf-eu-routine-preview.yml")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    payload = validate(args)
    print(json.dumps(payload, indent=2, sort_keys=True))
    if payload["blockers"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
