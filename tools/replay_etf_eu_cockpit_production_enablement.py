from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from runtime.apply_etf_eu_cockpit_to_package import apply_cockpit_to_package
from runtime.inline_etf_eu_email_report_styles import MARKER_ATTRIBUTE


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"missing replay input: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _page_count(path: Path) -> int:
    result = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise RuntimeError(f"unable to read page count: {path}")


def _copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def replay(args: argparse.Namespace) -> dict[str, Any]:
    state_path = Path(args.state)
    state = _load(state_path)
    output_root = Path(args.output_root)
    disabled_root = output_root / "disabled"
    enabled_root = output_root / "enabled"

    classic = {
        "nl_html": Path(args.classic_nl_html),
        "nl_pdf": Path(args.classic_nl_pdf),
        "en_html": Path(args.classic_en_html),
        "en_pdf": Path(args.classic_en_pdf),
    }
    protected = [Path(value) for value in args.protected]
    protected_before = {str(path): _sha256(path) for path in protected}

    disabled = {
        "nl_html": disabled_root / classic["nl_html"].name,
        "nl_pdf": disabled_root / classic["nl_pdf"].name,
        "en_html": disabled_root / classic["en_html"].name,
        "en_pdf": disabled_root / classic["en_pdf"].name,
        "nl_browser": disabled_root / "unused_nl_browser.html",
        "en_browser": disabled_root / "unused_en_browser.html",
    }
    enabled = {
        "nl_html": enabled_root / classic["nl_html"].name,
        "nl_pdf": enabled_root / classic["nl_pdf"].name,
        "en_html": enabled_root / classic["en_html"].name,
        "en_pdf": enabled_root / classic["en_pdf"].name,
        "nl_browser": enabled_root / classic["nl_html"].name.replace(".html", "_browser.html"),
        "en_browser": enabled_root / classic["en_html"].name.replace(".html", "_browser.html"),
    }
    for key in ("nl_html", "nl_pdf", "en_html", "en_pdf"):
        _copy(classic[key], disabled[key])
        _copy(classic[key], enabled[key])

    disabled_result = apply_cockpit_to_package(
        state=state,
        dutch_html=disabled["nl_html"],
        english_html=disabled["en_html"],
        dutch_pdf=disabled["nl_pdf"],
        english_pdf=disabled["en_pdf"],
        dutch_browser_html=disabled["nl_browser"],
        english_browser_html=disabled["en_browser"],
        feature_value="disabled",
    )
    enabled_result = apply_cockpit_to_package(
        state=state,
        dutch_html=enabled["nl_html"],
        english_html=enabled["en_html"],
        dutch_pdf=enabled["nl_pdf"],
        english_pdf=enabled["en_pdf"],
        dutch_browser_html=enabled["nl_browser"],
        english_browser_html=enabled["en_browser"],
        feature_value="enabled",
    )

    if disabled_result.status != "disabled":
        raise RuntimeError(f"disabled replay failed: {disabled_result}")
    if not enabled_result.enabled or enabled_result.status != "enabled":
        raise RuntimeError(f"enabled replay failed: {enabled_result}")

    disabled_identity = {
        key: _sha256(disabled[key]) == _sha256(classic[key])
        for key in ("nl_html", "nl_pdf", "en_html", "en_pdf")
    }
    if not all(disabled_identity.values()):
        raise RuntimeError(f"disabled replay changed classic files: {disabled_identity}")

    marker = f'{MARKER_ATTRIBUTE}="true"'
    enabled_nl_text = enabled["nl_html"].read_text(encoding="utf-8")
    enabled_en_text = enabled["en_html"].read_text(encoding="utf-8")
    full_report_inlined = {
        "nl": marker in enabled_nl_text,
        "en": marker in enabled_en_text,
    }
    if not all(full_report_inlined.values()):
        raise RuntimeError(f"full-report email inlining missing: {full_report_inlined}")

    classic_pages = {"nl": _page_count(classic["nl_pdf"]), "en": _page_count(classic["en_pdf"])}
    enabled_pages = {"nl": _page_count(enabled["nl_pdf"]), "en": _page_count(enabled["en_pdf"])}
    if enabled_pages["nl"] != classic_pages["nl"] + 1 or enabled_pages["en"] != classic_pages["en"] + 1:
        raise RuntimeError(f"enabled page delta mismatch: classic={classic_pages} enabled={enabled_pages}")

    protected_after = {str(path): _sha256(path) for path in protected}
    protected_unchanged = protected_before == protected_after
    if not protected_unchanged:
        raise RuntimeError("protected replay inputs changed")

    payload = {
        "schema_version": "etf_eu_cockpit_production_enablement_replay_v1",
        "artifact_type": "etf_eu_cockpit_production_enablement_replay",
        "source_state": str(state_path),
        "source_run_id": state.get("run_id"),
        "report_date": state.get("report_date"),
        "exact_current_state_used": True,
        "non_delivery_replay": True,
        "disabled_result": {
            "status": disabled_result.status,
            "byte_identity": disabled_identity,
            "browser_audit_files_created": disabled["nl_browser"].exists() or disabled["en_browser"].exists(),
        },
        "enabled_result": {
            "status": enabled_result.status,
            "front_page_count_nl": enabled_result.dutch_front_page_count,
            "front_page_count_en": enabled_result.english_front_page_count,
            "summary_suppressed_nl": enabled_result.dutch_summary_suppressed,
            "summary_suppressed_en": enabled_result.english_summary_suppressed,
            "classic_pages": classic_pages,
            "enabled_pages": enabled_pages,
            "page_delta_nl": enabled_pages["nl"] - classic_pages["nl"],
            "page_delta_en": enabled_pages["en"] - classic_pages["en"],
            "primary_html_mode": "email_safe_inline_full_report",
            "full_report_email_inline_styled_nl": full_report_inlined["nl"],
            "full_report_email_inline_styled_en": full_report_inlined["en"],
            "pdf_source_mode": "browser_svg",
            "attachment_contract_file_count": 4,
            "dutch_primary_html": str(enabled["nl_html"]),
            "english_companion_html": str(enabled["en_html"]),
            "dutch_primary_pdf": str(enabled["nl_pdf"]),
            "english_companion_pdf": str(enabled["en_pdf"]),
            "dutch_browser_html": str(enabled["nl_browser"]),
            "english_browser_html": str(enabled["en_browser"]),
        },
        "protected_inputs": protected_before,
        "protected_inputs_unchanged": protected_unchanged,
        "portfolio_mutation": False,
        "pricing_mutation": False,
        "external_transport": False,
        "production_enablement_decision_recorded": False,
    }
    output = output_root / "etf_eu_cockpit_production_enablement_replay_20260719.json"
    output_root.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay ETF EU cockpit integration against the exact current accepted package.")
    parser.add_argument("--state", required=True)
    parser.add_argument("--classic-nl-html", required=True)
    parser.add_argument("--classic-nl-pdf", required=True)
    parser.add_argument("--classic-en-html", required=True)
    parser.add_argument("--classic-en-pdf", required=True)
    parser.add_argument("--output-root", default="output/cockpit_enablement_preview")
    parser.add_argument("--protected", action="append", default=[])
    args = parser.parse_args()
    payload = replay(args)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
