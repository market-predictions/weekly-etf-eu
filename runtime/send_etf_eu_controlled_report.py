from __future__ import annotations

import argparse
import hashlib
import json
import os
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any

REQUIRED_ENV = [
    "ETF_EU_SMTP_HOST",
    "ETF_EU_SMTP_PORT",
    "ETF_EU_SMTP_USERNAME",
    "ETF_EU_SMTP_PASSWORD",
    "ETF_EU_MAIL_FROM",
    "ETF_EU_RECIPIENT_NL",
    "ETF_EU_RECIPIENT_EN",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _read_config() -> dict[str, str]:
    missing = [name for name in REQUIRED_ENV if not os.environ.get(name)]
    _require(not missing, "missing required ETF EU mail runtime configuration: " + ",".join(missing))
    return {name: os.environ[name] for name in REQUIRED_ENV}


def _report_paths(report_suffix: str) -> dict[str, Path]:
    paths = {
        "nl": Path(f"output/weekly_etf_eu_review_nl_{report_suffix}.md"),
        "en": Path(f"output/weekly_etf_eu_review_{report_suffix}.md"),
    }
    for language, path in paths.items():
        _require(path.exists(), f"missing {language} report path: {path}")
    return paths


def _build_message(*, language: str, report_date: str, sender: str, recipient: str, report_path: Path) -> EmailMessage:
    text = report_path.read_text(encoding="utf-8")
    subject_lang = "NL" if language == "nl" else "EN"
    msg = EmailMessage()
    msg["Subject"] = f"Weekly ETF EU UCITS Review {subject_lang} — {report_date}"
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(text)
    msg.add_attachment(text.encode("utf-8"), maintype="text", subtype="markdown", filename=report_path.name)
    return msg


def _send_messages(*, cfg: dict[str, str], messages: list[EmailMessage]) -> None:
    host = cfg["ETF_EU_SMTP_HOST"]
    port = int(cfg["ETF_EU_SMTP_PORT"])
    username = cfg["ETF_EU_SMTP_USERNAME"]
    password = cfg["ETF_EU_SMTP_PASSWORD"]
    if port == 465:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host, port, context=context, timeout=60) as smtp:
            smtp.login(username, password)
            for msg in messages:
                smtp.send_message(msg)
        return
    with smtplib.SMTP(host, port, timeout=60) as smtp:
        smtp.ehlo()
        smtp.starttls(context=ssl.create_default_context())
        smtp.ehlo()
        smtp.login(username, password)
        for msg in messages:
            smtp.send_message(msg)


def build_result(
    *,
    run_id: str,
    report_date: str,
    report_suffix: str,
    cfg: dict[str, str],
    reports: dict[str, Path],
    transport_status: str,
    error: str | None,
) -> dict[str, Any]:
    languages = [
        {
            "language": "nl",
            "report_path": str(reports["nl"]),
            "recipient_redacted": True,
            "recipient_hash": _sha256(cfg["ETF_EU_RECIPIENT_NL"]),
        },
        {
            "language": "en",
            "report_path": str(reports["en"]),
            "recipient_redacted": True,
            "recipient_hash": _sha256(cfg["ETF_EU_RECIPIENT_EN"]),
        },
    ]
    return {
        "schema_version": "etf_eu_controlled_transport_result_v1",
        "artifact_type": "etf_eu_controlled_transport_result",
        "generated_at_utc": _utc_now(),
        "run_id": run_id,
        "report_date": report_date,
        "report_suffix": report_suffix,
        "sender_entrypoint_path": "runtime/send_etf_eu_controlled_report.py",
        "real_sender_entrypoint_called": True,
        "transport_attempted": True,
        "transport_status": transport_status,
        "transport_success_unconfirmed": transport_status == "transport_succeeded_unconfirmed",
        "transport_success_not_inbox_receipt": True,
        "receipt_confirmed": False,
        "completion_claimed": False,
        "recipient_data_policy": "redacted_hash_only",
        "languages": languages,
        "secret_values_exposed": False,
        "recipient_plaintext_values_exposed": False,
        "portfolio_mutation": False,
        "funding_authority": False,
        "valuation_grade": False,
        "delivery_error": error,
    }


def write_result(output_dir: Path, payload: dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"etf_eu_transport_result_{payload['run_id']}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm-controlled-send", action="store_true")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--output-dir", default="output/delivery")
    args = parser.parse_args()
    _require(args.confirm_controlled_send, "controlled sender requires explicit --confirm-controlled-send")
    cfg = _read_config()
    reports = _report_paths(args.report_suffix)
    sender = cfg["ETF_EU_MAIL_FROM"]
    messages = [
        _build_message(language="nl", report_date=args.report_date, sender=sender, recipient=cfg["ETF_EU_RECIPIENT_NL"], report_path=reports["nl"]),
        _build_message(language="en", report_date=args.report_date, sender=sender, recipient=cfg["ETF_EU_RECIPIENT_EN"], report_path=reports["en"]),
    ]
    try:
        _send_messages(cfg=cfg, messages=messages)
    except Exception as exc:
        payload = build_result(
            run_id=args.run_id,
            report_date=args.report_date,
            report_suffix=args.report_suffix,
            cfg=cfg,
            reports=reports,
            transport_status="transport_failed",
            error=type(exc).__name__,
        )
        path = write_result(Path(args.output_dir), payload)
        print(f"ETF_EU_CONTROLLED_TRANSPORT_RESULT | status=transport_failed | result={path}")
        raise
    payload = build_result(
        run_id=args.run_id,
        report_date=args.report_date,
        report_suffix=args.report_suffix,
        cfg=cfg,
        reports=reports,
        transport_status="transport_succeeded_unconfirmed",
        error=None,
    )
    path = write_result(Path(args.output_dir), payload)
    print(f"ETF_EU_CONTROLLED_TRANSPORT_RESULT | status=transport_succeeded_unconfirmed | result={path}")


if __name__ == "__main__":
    main()
