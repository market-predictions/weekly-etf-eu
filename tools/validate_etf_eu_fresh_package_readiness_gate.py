from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_fresh_package_readiness_gate_v1"
ARTIFACT_TYPE = "etf_eu_fresh_package_readiness_gate"
SOURCE_OF_TRUTH_REPO = "market-predictions/weekly-etf-eu"
REFERENCE_ARCHITECTURE_REPO = "market-predictions/weekly-etf"
UPSTREAM_PATTERN = "weekly-etf package-readiness/pre-send validation concept; adapted for EU fresh package readiness without delivery authority"
NEXT_PASS = "ETF-EU-MVP26_GUARDED_FRESH_PACKAGE_DELIVERY_PREP"
NEXT_BLOCKED = "ETF-EU-MVP25B_FRESH_PACKAGE_READINESS_FIXES"

US_STATE_PATHS = {
    "output/etf_portfolio_state.json",
    "output/etf_valuation_history.csv",
    "output/etf_trade_ledger.csv",
    "output/etf_recommendation_scorecard.csv",
}

AUTHORITY_FALSE_KEYS = [
    "send_executed",
    "transport_attempted",
    "receipt_confirmed",
    "valuation_grade",
    "funding_authority",
    "portfolio_mutation",
    "production_delivery_authority",
]

STALE_REDELIVERY_TOKENS = [
    "controlled resend",
    "guarded resend",
    "herverzending",
    "resend_performed=true",
    "smtp_sendmail_returned_no_exception",
    "receipt_confirmed=true",
    "delivery_success_closed=true",
]

US_PROXY_SYMBOLS = ["SPY", "SMH", "GLD", "PPA", "PAVE", "URNM", "GSG"]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _path(value: object, label: str, blockers: list[str]) -> Path | None:
    raw = str(value or "").strip()
    if not raw:
        blockers.append(f"{label}_missing")
        return None
    path = Path(raw)
    if not path.exists():
        blockers.append(f"{label}_not_found:{path}")
        return None
    return path


def _check_false(payload: dict[str, Any], key: str, blockers: list[str], *, label: str = "manifest") -> None:
    if payload.get(key) is not False:
        blockers.append(f"{label}_{key}_must_be_false")


def _reject_us_state(value: object, label: str, blockers: list[str]) -> None:
    raw = str(value or "")
    if raw in US_STATE_PATHS:
        blockers.append(f"{label}_uses_us_state_authority:{raw}")
    if raw and not raw.startswith("output/etf_eu_"):
        blockers.append(f"{label}_must_be_eu_specific:{raw}")


def _read_text(path: Path | None) -> str:
    if not path:
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def _pdf_ok(path: Path | None, label: str, blockers: list[str]) -> None:
    if not path:
        return
    raw = path.read_bytes()
    if not raw.startswith(b"%PDF-"):
        blockers.append(f"{label}_missing_pdf_header")
    if b"%%EOF" not in raw[-256:]:
        blockers.append(f"{label}_missing_eof_marker")


def _stale_tokens(text: str) -> list[str]:
    lower = text.lower()
    return [token for token in STALE_REDELIVERY_TOKENS if token.lower() in lower]


def _investable_us_symbols(text: str) -> list[str]:
    offenders: list[str] = []
    lower = text.lower()
    if "not investable" in lower or "research proxy" in lower or "research reference" in lower:
        return offenders
    for symbol in US_PROXY_SYMBOLS:
        if re.search(rf"\b{re.escape(symbol)}\b", text):
            offenders.append(symbol)
    return offenders


def _validate_markdown(nl_md: Path | None, en_md: Path | None, blockers: list[str]) -> bool:
    local: list[str] = []
    nl = _read_text(nl_md)
    en = _read_text(en_md)
    if nl_md and "Nederlands" not in nl.splitlines()[0]:
        local.append("dutch_markdown_title_missing_nederlands")
    if en_md and "English Companion" not in en.splitlines()[0]:
        local.append("english_markdown_title_missing_companion")
    for label, text in [("dutch_markdown", nl), ("english_markdown", en)]:
        missing = [key for key in AUTHORITY_FALSE_KEYS if f"{key}=false" not in text]
        if missing:
            local.append(f"{label}_missing_authority_flags:{','.join(missing)}")
        stale = _stale_tokens(text)
        if stale:
            local.append(f"{label}_stale_delivery_wording:{','.join(stale)}")
        us = _investable_us_symbols(text)
        if us:
            local.append(f"{label}_us_symbols_look_investable:{','.join(us)}")
    blockers.extend(local)
    return not local


def _validate_html(nl_html: Path | None, en_html: Path | None, blockers: list[str]) -> bool:
    local: list[str] = []
    nl = _read_text(nl_html)
    en = _read_text(en_html)
    if nl_html and ("<html" not in nl.lower() or "Weekly ETF EU Review | Nederlands" not in nl):
        local.append("dutch_html_missing_expected_markers")
    if en_html and ("<html" not in en.lower() or "Weekly ETF EU Review | English Companion" not in en):
        local.append("english_html_missing_expected_markers")
    for label, text in [("dutch_html", nl), ("english_html", en)]:
        stale = _stale_tokens(text)
        if stale:
            local.append(f"{label}_stale_delivery_wording:{','.join(stale)}")
        for key in AUTHORITY_FALSE_KEYS:
            if f"{key}=false" not in text:
                local.append(f"{label}_missing_authority_flag:{key}")
    blockers.extend(local)
    return not local


def _validate_manifest(manifest: dict[str, Any], blockers: list[str]) -> bool:
    local: list[str] = []
    required = {
        "schema_version": "etf_eu_fresh_generation_package_v1",
        "artifact_type": "etf_eu_fresh_generation_package_manifest",
        "source_of_truth_repo": SOURCE_OF_TRUTH_REPO,
        "reference_architecture_repo": REFERENCE_ARCHITECTURE_REPO,
        "fresh_generation_status": "full_package_generated",
        "full_generation_status": "renderer_integrated",
        "markdown_generation_status": "generated",
        "html_generation_status": "generated",
        "pdf_generation_status": "generated",
    }
    for key, expected in required.items():
        if manifest.get(key) != expected:
            local.append(f"manifest_{key}_expected_{expected}_got_{manifest.get(key)}")
    for key in ["dutch_primary", "english_companion", "markdown_output_available", "html_output_available", "pdf_output_available"]:
        if manifest.get(key) is not True:
            local.append(f"manifest_{key}_must_be_true")
    if manifest.get("ready_for_controlled_delivery") is not False:
        local.append("manifest_ready_for_controlled_delivery_must_be_false_before_gate")
    for key in AUTHORITY_FALSE_KEYS:
        if manifest.get(key) is not False:
            local.append(f"manifest_{key}_must_be_false")
    for key in ["portfolio_state_path", "valuation_history_path", "trade_ledger_path", "recommendation_scorecard_path"]:
        raw = str(manifest.get(key) or "")
        if raw in US_STATE_PATHS or (raw and not raw.startswith("output/etf_eu_")):
            local.append(f"manifest_{key}_must_be_eu_specific:{raw}")
    blockers.extend(local)
    return not local


def _validate_routine_manifest(routine: dict[str, Any], manifest: dict[str, Any], blockers: list[str]) -> bool:
    local: list[str] = []
    expected = "output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json"
    if routine.get("delivery_package_manifest") != expected:
        local.append("routine_manifest_package_manifest_reference_mismatch")
    for key in [
        "dutch_primary_markdown",
        "english_companion_markdown",
        "dutch_primary_html",
        "english_companion_html",
        "dutch_primary_pdf",
        "english_companion_pdf",
    ]:
        if routine.get(key) != manifest.get(key):
            local.append(f"routine_manifest_{key}_reference_mismatch")
    if routine.get("transport_attempted") is not False:
        local.append("routine_transport_attempted_must_remain_false")
    if routine.get("transport_success") is not False:
        local.append("routine_transport_success_must_remain_false")
    if routine.get("receipt_confirmed") is not False:
        local.append("routine_receipt_confirmed_must_remain_false")
    blockers.extend(local)
    return not local


def evaluate(manifest_path: Path, ready_artifact_path: Path, routine_manifest_path: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    blockers: list[str] = []
    warnings: list[str] = []

    manifest = _read_json(manifest_path)
    ready = _read_json(ready_artifact_path)
    routine = _read_json(routine_manifest_path)

    nl_md = _path(manifest.get("dutch_primary_markdown"), "dutch_primary_markdown", blockers)
    en_md = _path(manifest.get("english_companion_markdown"), "english_companion_markdown", blockers)
    nl_html = _path(manifest.get("dutch_primary_html"), "dutch_primary_html", blockers)
    en_html = _path(manifest.get("english_companion_html"), "english_companion_html", blockers)
    nl_pdf = _path(manifest.get("dutch_primary_pdf"), "dutch_primary_pdf", blockers)
    en_pdf = _path(manifest.get("english_companion_pdf"), "english_companion_pdf", blockers)
    _path(manifest.get("ready_artifact"), "ready_artifact", blockers)
    _path(routine_manifest_path, "routine_manifest", blockers)

    markdown_gate = _validate_markdown(nl_md, en_md, blockers)
    html_gate = _validate_html(nl_html, en_html, blockers)
    _pdf_ok(nl_pdf, "dutch_primary_pdf", blockers)
    _pdf_ok(en_pdf, "english_companion_pdf", blockers)
    pdf_gate = not any("pdf" in blocker for blocker in blockers)
    manifest_gate = _validate_manifest(manifest, blockers)

    for key in AUTHORITY_FALSE_KEYS:
        _check_false(manifest, key, blockers)
        _check_false(ready, key, blockers, label="ready_artifact")
        _check_false(routine, key, blockers, label="routine_manifest")
    if ready.get("delivery_authorized", False) is not False:
        blockers.append("ready_artifact_delivery_authorized_must_be_false")

    for key in ["portfolio_state_path", "valuation_history_path", "trade_ledger_path", "recommendation_scorecard_path"]:
        _reject_us_state(manifest.get(key), key, blockers)

    routine_gate = _validate_routine_manifest(routine, manifest, blockers)
    authority_gate = not any("authority" in blocker or "must_be_false" in blocker or "delivery_authorized" in blocker for blocker in blockers)
    gate_passed = markdown_gate and html_gate and pdf_gate and manifest_gate and routine_gate and authority_gate and not blockers

    gate = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "generated_at_utc": _utc_now(),
        "run_id": manifest.get("run_id"),
        "report_date": manifest.get("report_date"),
        "report_suffix": manifest.get("report_suffix"),
        "source_of_truth_repo": SOURCE_OF_TRUTH_REPO,
        "reference_architecture_repo": REFERENCE_ARCHITECTURE_REPO,
        "upstream_pattern_adapted": UPSTREAM_PATTERN,
        "package_manifest": str(manifest_path),
        "ready_artifact": str(ready_artifact_path),
        "routine_run_manifest": str(routine_manifest_path),
        "dutch_primary_markdown": manifest.get("dutch_primary_markdown"),
        "english_companion_markdown": manifest.get("english_companion_markdown"),
        "dutch_primary_html": manifest.get("dutch_primary_html"),
        "english_companion_html": manifest.get("english_companion_html"),
        "dutch_primary_pdf": manifest.get("dutch_primary_pdf"),
        "english_companion_pdf": manifest.get("english_companion_pdf"),
        "markdown_gate_passed": markdown_gate,
        "html_gate_passed": html_gate,
        "pdf_gate_passed": pdf_gate,
        "manifest_gate_passed": manifest_gate,
        "authority_gate_passed": authority_gate,
        "routine_manifest_gate_passed": routine_gate,
        "readiness_gate_passed": gate_passed,
        "ready_for_controlled_delivery": gate_passed,
        "blockers": blockers,
        "warnings": warnings,
        "delivery_authorized": False,
        "send_executed": False,
        "transport_attempted": False,
        "receipt_confirmed": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "next_package": NEXT_PASS if gate_passed else NEXT_BLOCKED,
    }
    return gate, manifest, ready, routine


def _write_gate_and_updates(
    *,
    gate: dict[str, Any],
    manifest: dict[str, Any],
    ready: dict[str, Any],
    routine: dict[str, Any],
    manifest_path: Path,
    ready_artifact_path: Path,
    routine_manifest_path: Path,
    gate_path: Path,
    update_ready_artifact: bool,
    update_package_manifest: bool,
    update_routine_manifest: bool,
) -> None:
    _write_json(gate_path, gate)
    if not gate["readiness_gate_passed"]:
        return
    if update_ready_artifact:
        ready.update(
            {
                "package_readiness_gate": str(gate_path),
                "ready_for_controlled_delivery": True,
                "delivery_authorized": False,
                "reason": "MVP25 package-readiness gate passed. This permits later controlled-delivery preparation only; it is not send authorization.",
                "next_package": NEXT_PASS,
                "send_executed": False,
                "transport_attempted": False,
                "receipt_confirmed": False,
                "valuation_grade": False,
                "funding_authority": False,
                "portfolio_mutation": False,
                "production_delivery_authority": False,
            }
        )
        _write_json(ready_artifact_path, ready)
    if update_package_manifest:
        manifest.update(
            {
                "package_readiness_gate": str(gate_path),
                "readiness_gate_passed": True,
                "ready_for_controlled_delivery": True,
                "delivery_authorized": False,
                "next_package": NEXT_PASS,
            }
        )
        _write_json(manifest_path, manifest)
    if update_routine_manifest:
        routine.update(
            {
                "routine_stage": "fresh_package_readiness_gate_passed",
                "workflow_status": "fresh_package_readiness_gate_passed",
                "package_readiness_gate": str(gate_path),
                "ready_for_controlled_delivery": True,
                "transport_attempted": False,
                "transport_success": False,
                "receipt_confirmed": False,
                "next_package": NEXT_PASS,
            }
        )
        _write_json(routine_manifest_path, routine)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ETF EU fresh-package readiness and optionally write/update gate artifacts.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--ready-artifact", required=True)
    parser.add_argument("--routine-manifest", required=True)
    parser.add_argument("--write-gate", required=True)
    parser.add_argument("--update-ready-artifact", action="store_true")
    parser.add_argument("--update-package-manifest", action="store_true")
    parser.add_argument("--update-routine-manifest", action="store_true")
    args = parser.parse_args()

    gate, manifest, ready, routine = evaluate(Path(args.manifest), Path(args.ready_artifact), Path(args.routine_manifest))
    _write_gate_and_updates(
        gate=gate,
        manifest=manifest,
        ready=ready,
        routine=routine,
        manifest_path=Path(args.manifest),
        ready_artifact_path=Path(args.ready_artifact),
        routine_manifest_path=Path(args.routine_manifest),
        gate_path=Path(args.write_gate),
        update_ready_artifact=args.update_ready_artifact,
        update_package_manifest=args.update_package_manifest,
        update_routine_manifest=args.update_routine_manifest,
    )
    print(json.dumps(gate, indent=2, sort_keys=True))
    if not gate["readiness_gate_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
