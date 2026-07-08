from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ALLOWED_DELIVERY_STATUSES = {
    "not_attempted",
    "attempt_pending",
    "transport_succeeded_unconfirmed",
    "transport_failed",
    "receipt_confirmed",
    "receipt_not_found_after_delay",
    "smtp_sendmail_returned_no_exception",
    "smtp_sendmail_failed",
    "evidence_invalid",
}
SUCCESS_CAVEAT = "not an end-recipient inbox receipt"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _language_codes(languages: list[dict[str, object]]) -> set[str]:
    return {str(item.get("language")) for item in languages if isinstance(item, dict)}


def _validate_language_evidence(languages: list[dict[str, object]], *, pdf_generation: bool) -> None:
    _require(_language_codes(languages) == {"nl", "en"}, "ETF EU delivery evidence requires exactly nl and en languages")
    for item in languages:
        language = str(item.get("language"))
        _require(language in {"nl", "en"}, f"unsupported language: {language}")
        _require(item.get("recipient_redacted") is True, f"{language}: recipient must be redacted")
        recipient_hash = str(item.get("recipient_hash") or "")
        _require(bool(recipient_hash), f"{language}: recipient_hash missing")
        _require("@" not in recipient_hash, f"{language}: recipient_hash must not contain plaintext recipient")
        _require(bool(item.get("report_path")), f"{language}: report_path missing")
        _require(bool(item.get("source_manifest_path")), f"{language}: source_manifest_path missing")
        _require(bool(item.get("source_manifest_type")), f"{language}: source_manifest_type missing")
        _require(bool(item.get("timestamp_utc")), f"{language}: timestamp_utc missing")
        _require(bool(item.get("mode")), f"{language}: mode missing")
        _require(bool(item.get("report")), f"{language}: report missing")
        _require("html_body" in item, f"{language}: html_body missing")
        attachments = item.get("attachments") or []
        pdf_attachments = item.get("pdf_attachments") or []
        _require(isinstance(attachments, list), f"{language}: attachments must be a list")
        _require(isinstance(pdf_attachments, list), f"{language}: pdf_attachments must be a list")
        _require(item.get("attachment_count") == len(attachments), f"{language}: attachment_count mismatch")
        if pdf_generation:
            _require(item.get("pdf_attached") == "yes", f"{language}: pdf attachment evidence required")
            _require(bool(pdf_attachments), f"{language}: pdf_attachments required")
        else:
            _require(item.get("pdf_attached") in {"no", "yes"}, f"{language}: pdf_attached must be yes/no")


def build_etf_eu_delivery_evidence(
    *,
    run_id: str,
    report_date: str,
    report_suffix: str,
    sender_entrypoint_path: Path,
    dutch_primary_report_path: Path,
    english_companion_report_path: Path,
    controlled_send_preflight_manifest: Path,
    base_delivery_manifest: Path,
    delivery_status: str,
    delivery_status_meaning: str,
    languages: list[dict[str, object]],
    source: dict[str, object],
    generated_at_utc: str | None = None,
) -> dict[str, object]:
    _require(delivery_status in ALLOWED_DELIVERY_STATUSES, f"unsupported delivery_status={delivery_status}")
    _require(bool(delivery_status_meaning), "delivery_status_meaning required")
    if delivery_status in {"smtp_sendmail_returned_no_exception", "transport_succeeded_unconfirmed"}:
        _require(SUCCESS_CAVEAT in delivery_status_meaning, "transport-layer evidence must include inbox-receipt caveat")
    _validate_language_evidence(languages, pdf_generation=False)
    delivery_success = delivery_status == "smtp_sendmail_returned_no_exception"
    email_delivery = delivery_success
    production_delivery = delivery_success
    delivery_receipt = delivery_status == "receipt_confirmed"
    if delivery_status in {"not_attempted", "attempt_pending", "transport_failed", "receipt_not_found_after_delay", "transport_succeeded_unconfirmed"}:
        delivery_success = False
        email_delivery = False
        production_delivery = False
        delivery_receipt = False
    return {
        "schema_version": "etf_eu_delivery_evidence_v1",
        "artifact_type": "etf_eu_controlled_send_delivery_evidence",
        "generated_at_utc": generated_at_utc or _utc_now(),
        "run_id": run_id,
        "report_date": report_date,
        "report_suffix": report_suffix,
        "delivery_status": delivery_status,
        "delivery_status_meaning": delivery_status_meaning,
        "recipient_data_policy": "redacted_hash_only",
        "sender_entrypoint_path": str(sender_entrypoint_path),
        "dutch_primary_report_path": str(dutch_primary_report_path),
        "english_companion_report_path": str(english_companion_report_path),
        "controlled_send_preflight_manifest": str(controlled_send_preflight_manifest),
        "base_delivery_manifest": str(base_delivery_manifest),
        "language_count": len(languages),
        "languages": languages,
        "source": source,
        "secret_values_exposed": False,
        "recipient_plaintext_values_exposed": False,
        "production_delivery": production_delivery,
        "email_delivery": email_delivery,
        "pdf_generation": False,
        "delivery_receipt": delivery_receipt,
        "delivery_success": delivery_success,
        "delivery_error": None if delivery_status in {"not_attempted", "attempt_pending"} else source.get("delivery_error"),
        "receipt_status": "receipt_confirmed" if delivery_receipt else delivery_status,
    }


def write_etf_eu_delivery_evidence(
    output_dir: Path,
    *,
    run_id: str,
    report_date: str,
    report_suffix: str,
    sender_entrypoint_path: Path,
    dutch_primary_report_path: Path,
    english_companion_report_path: Path,
    controlled_send_preflight_manifest: Path,
    base_delivery_manifest: Path,
    delivery_status: str,
    delivery_status_meaning: str,
    languages: list[dict[str, object]],
    source: dict[str, object],
    generated_at_utc: str | None = None,
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence = build_etf_eu_delivery_evidence(
        run_id=run_id,
        report_date=report_date,
        report_suffix=report_suffix,
        sender_entrypoint_path=sender_entrypoint_path,
        dutch_primary_report_path=dutch_primary_report_path,
        english_companion_report_path=english_companion_report_path,
        controlled_send_preflight_manifest=controlled_send_preflight_manifest,
        base_delivery_manifest=base_delivery_manifest,
        delivery_status=delivery_status,
        delivery_status_meaning=delivery_status_meaning,
        languages=languages,
        source=source,
        generated_at_utc=generated_at_utc,
    )
    path = output_dir / f"etf_eu_delivery_evidence_{run_id}.json"
    path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _fixture_languages(*, report_suffix: str, run_id: str, mode: str, source_manifest_type: str) -> list[dict[str, object]]:
    timestamp = _utc_now()
    return [
        {
            "language": "nl",
            "report_path": f"output/weekly_etf_eu_review_nl_{report_suffix}.md",
            "source_manifest_path": f"output/delivery/etf_eu_delivery_manifest_{run_id}.json",
            "source_manifest_type": source_manifest_type,
            "timestamp_utc": timestamp,
            "mode": mode,
            "report": "Dutch primary client report",
            "recipient_hash": "sha256:redacted-nl-fixture",
            "recipient_redacted": True,
            "html_body": False,
            "pdf_attached": "no",
            "attachments": [],
            "attachment_count": 0,
            "pdf_attachments": [],
        },
        {
            "language": "en",
            "report_path": f"output/weekly_etf_eu_review_{report_suffix}.md",
            "source_manifest_path": f"output/delivery/etf_eu_delivery_manifest_{run_id}.json",
            "source_manifest_type": source_manifest_type,
            "timestamp_utc": timestamp,
            "mode": mode,
            "report": "English companion report",
            "recipient_hash": "sha256:redacted-en-fixture",
            "recipient_redacted": True,
            "html_body": False,
            "pdf_attached": "no",
            "attachments": [],
            "attachment_count": 0,
            "pdf_attachments": [],
        },
    ]


def _write_mvp15_static(args: argparse.Namespace) -> Path:
    stage = args.stage
    status = "attempt_pending" if stage == "pre" else "not_attempted"
    meaning = (
        "MVP15 pre-transport evidence placeholder; no outbound delivery executed"
        if stage == "pre"
        else "MVP15 post-transport evidence placeholder; no outbound delivery executed"
    )
    return write_etf_eu_delivery_evidence(
        Path(args.output_dir),
        run_id=args.run_id,
        report_date=args.report_date,
        report_suffix=args.report_suffix,
        sender_entrypoint_path=Path("runtime/send_etf_eu_report_runtime_html.py"),
        dutch_primary_report_path=Path(f"output/weekly_etf_eu_review_nl_{args.report_suffix}.md"),
        english_companion_report_path=Path(f"output/weekly_etf_eu_review_{args.report_suffix}.md"),
        controlled_send_preflight_manifest=Path(f"output/delivery/etf_eu_delivery_manifest_{args.run_id}.json"),
        base_delivery_manifest=Path(f"output/delivery/etf_eu_delivery_manifest_{args.run_id}.json"),
        delivery_status=status,
        delivery_status_meaning=meaning,
        languages=_fixture_languages(run_id=args.run_id, report_suffix=args.report_suffix, mode=f"mvp15_static_{stage}", source_manifest_type="mvp15_static_guarded_evidence"),
        source={"writer": "runtime/write_etf_eu_delivery_evidence.py", "basis": f"mvp15_static_{stage}", "transport_executed": False},
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output/delivery")
    parser.add_argument("--fixture", action="store_true")
    parser.add_argument("--mvp15-static", action="store_true")
    parser.add_argument("--stage", choices=["pre", "post"], default="pre")
    parser.add_argument("--run-id", default="20260708_000000")
    parser.add_argument("--report-date", default="2026-07-08")
    parser.add_argument("--report-suffix", default="260708")
    args = parser.parse_args()
    if args.mvp15_static:
        path = _write_mvp15_static(args)
        print(f"ETF_EU_MVP15_STATIC_DELIVERY_EVIDENCE_OK | stage={args.stage} | evidence={path}")
        return
    if not args.fixture:
        raise SystemExit("Use --fixture or --mvp15-static. Real transport evidence is not created by this writer package.")
    languages = _fixture_languages(
        run_id="20260708_000000",
        report_suffix="260708",
        mode="fixture_no_send",
        source_manifest_type="mvp09_fixture_no_send_evidence",
    )
    for row in languages:
        row["source_manifest_path"] = "output/delivery/etf_eu_sender_preflight_20260708_000000.json"
    path = write_etf_eu_delivery_evidence(
        Path(args.output_dir),
        run_id="20260708_000000",
        report_date="2026-07-08",
        report_suffix="260708",
        sender_entrypoint_path=Path("runtime/send_etf_eu_report_runtime_html.py"),
        dutch_primary_report_path=Path("output/weekly_etf_eu_review_nl_260708.md"),
        english_companion_report_path=Path("output/weekly_etf_eu_review_260708.md"),
        controlled_send_preflight_manifest=Path("output/delivery/etf_eu_controlled_send_preflight_manifest_20260708_000000.json"),
        base_delivery_manifest=Path("output/delivery/etf_eu_delivery_manifest_20260708_142840.json"),
        delivery_status="not_attempted",
        delivery_status_meaning="controlled-send evidence writer implemented but no outbound delivery executed",
        languages=languages,
        source={"writer": "runtime/write_etf_eu_delivery_evidence.py", "basis": "mvp09_fixture_no_send_evidence"},
        generated_at_utc="2026-07-08T00:00:00Z",
    )
    print(f"ETF_EU_DELIVERY_EVIDENCE_FIXTURE_OK | evidence={path}")


if __name__ == "__main__":
    main()
