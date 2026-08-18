from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any

CONFIG_ALIASES = {
    "host": ("ETF_EU_TRANSPORT_HOST", "ETF_EU_SMTP_HOST"),
    "port": ("ETF_EU_TRANSPORT_PORT", "ETF_EU_SMTP_PORT"),
    "username": ("ETF_EU_TRANSPORT_USER", "ETF_EU_SMTP_USERNAME"),
    "password": ("ETF_EU_TRANSPORT_AUTH", "ETF_EU_SMTP_PASSWORD"),
    "sender": ("ETF_EU_FROM_ADDRESS", "ETF_EU_MAIL_FROM"),
    "recipient_nl": ("ETF_EU_TO_NL", "ETF_EU_RECIPIENT_NL"),
    "recipient_en": ("ETF_EU_TO_EN", "ETF_EU_RECIPIENT_EN"),
}

EQUITY_CURVE_SVG_PATTERN = re.compile(
    r'(<svg\b[^>]*class=["\'][^"\']*\bequity-curve-svg\b[^"\']*["\'][^>]*>.*?</svg>)',
    re.IGNORECASE | re.DOTALL,
)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _env_value(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def _read_config() -> dict[str, str]:
    cfg: dict[str, str] = {}
    missing: list[str] = []
    for key, names in CONFIG_ALIASES.items():
        value = _env_value(*names)
        if not value:
            missing.append("/".join(names))
        else:
            cfg[key] = value
    _require(not missing, "missing required ETF EU transport runtime configuration: " + ",".join(missing))
    return cfg


def _report_paths(report_suffix: str, *, nl_md: str | None = None, en_md: str | None = None) -> dict[str, Path]:
    return {
        "nl_md": Path(nl_md) if nl_md else Path(f"output/weekly_etf_eu_review_nl_{report_suffix}.md"),
        "en_md": Path(en_md) if en_md else Path(f"output/weekly_etf_eu_review_{report_suffix}.md"),
    }


def _package_paths(manifest_path: Path | None) -> dict[str, Path]:
    if manifest_path is None:
        return {}
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    _require(payload.get("schema_version") == "etf_eu_delivery_package_manifest_v1", "invalid package manifest schema")
    _require(payload.get("pdf_output_available") is True, "package manifest has no PDF output")
    _require(payload.get("dutch_primary") is True, "Dutch primary PDF required")
    _require(payload.get("english_companion") is True, "English companion PDF required")
    _require(payload.get("source_is_independently_assured") is True, "package source is not independently assured")
    _require(payload.get("artifact_hashes_verified") is True, "package artifact hashes were not verified")
    paths = {
        "nl_pdf": Path(str(payload.get("dutch_primary_pdf"))),
        "en_pdf": Path(str(payload.get("english_companion_pdf"))),
        "nl_html": Path(str(payload.get("dutch_primary_html"))),
        "en_html": Path(str(payload.get("english_companion_html"))),
    }
    for path in paths.values():
        _require(path.exists(), f"missing package asset: {path}")
    return paths


def _materialize_email_equity_curve(html_body: str, *, language: str) -> tuple[str, bytes | None, str | None]:
    """Replace the canonical inline equity SVG with a mail-safe related PNG.

    The canonical HTML remains untouched on disk. If it declares an equity-curve
    surface, message construction fails closed unless exactly one curve SVG can
    be converted and referenced by exactly one CID URL.
    """
    has_curve_marker = "equity-curve-block" in html_body or "equity-curve-svg" in html_body
    matches = list(EQUITY_CURVE_SVG_PATTERN.finditer(html_body))
    if not has_curve_marker:
        _require(not matches, "equity curve SVG found without canonical curve marker")
        return html_body, None, None

    _require(len(matches) == 1, f"expected exactly one equity curve SVG, found {len(matches)}")
    match = matches[0]
    svg_text = match.group(1)
    try:
        import cairosvg

        png_bytes = cairosvg.svg2png(
            bytestring=svg_text.encode("utf-8"),
            output_width=920,
            output_height=390,
        )
    except Exception as exc:
        raise RuntimeError("failed to materialize mail-safe equity curve PNG") from exc

    _require(png_bytes.startswith(PNG_SIGNATURE), "mail-safe equity curve conversion did not produce PNG")
    cid = f"etf-eu-equity-curve-{language}@weekly-etf-eu"
    alt = "Portefeuillecurve (EUR)" if language == "nl" else "Portfolio equity curve (EUR)"
    replacement = (
        f'<img class="equity-curve-email-img" src="cid:{cid}" alt="{alt}" '
        'width="920" style="display:block;width:100%;max-width:920px;height:auto;border:0;" />'
    )
    email_html = html_body[: match.start()] + replacement + html_body[match.end() :]
    _require("equity-curve-svg" not in email_html, "inline equity SVG remained in email HTML")
    _require(email_html.count(f"cid:{cid}") == 1, "email equity curve CID reference must occur exactly once")
    return email_html, png_bytes, cid


def _build_message(
    *,
    language: str,
    report_date: str,
    sender: str,
    recipient: str,
    markdown_path: Path,
    pdf_path: Path | None,
    html_path: Path | None,
    require_pdf_package: bool,
) -> EmailMessage:
    _require(markdown_path.exists(), f"missing markdown source: {markdown_path}")
    if require_pdf_package:
        _require(pdf_path is not None and pdf_path.exists(), f"PDF package required for {language}")
    text = markdown_path.read_text(encoding="utf-8")
    subject_lang = "NL" if language == "nl" else "EN"
    msg = EmailMessage()
    msg["Subject"] = f"Weekly ETF EU UCITS Review {subject_lang} — {report_date}"
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(text)
    if html_path is not None and html_path.exists():
        email_html, curve_png, curve_cid = _materialize_email_equity_curve(
            html_path.read_text(encoding="utf-8"),
            language=language,
        )
        msg.add_alternative(email_html, subtype="html")
        if curve_png is not None:
            _require(curve_cid is not None, "equity curve PNG missing CID")
            html_part = msg.get_payload()[-1]
            html_part.add_related(
                curve_png,
                maintype="image",
                subtype="png",
                cid=f"<{curve_cid}>",
                filename=f"weekly_etf_eu_equity_curve_{language}.png",
                disposition="inline",
            )
    if pdf_path is not None and pdf_path.exists():
        msg.add_attachment(pdf_path.read_bytes(), maintype="application", subtype="pdf", filename=pdf_path.name)
    elif not require_pdf_package:
        msg.add_attachment(text.encode("utf-8"), maintype="text", subtype="markdown", filename=markdown_path.name)
    return msg


def _send_messages(*, cfg: dict[str, str], messages: list[EmailMessage]) -> None:
    host = cfg["host"]
    port = int(cfg["port"])
    username = cfg["username"]
    password = cfg["password"]
    if port == 465:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host, port, context=context, timeout=60) as transport:
            transport.login(username, password)
            for msg in messages:
                transport.send_message(msg)
        return
    with smtplib.SMTP(host, port, timeout=60) as transport:
        transport.ehlo()
        transport.starttls(context=ssl.create_default_context())
        transport.ehlo()
        transport.login(username, password)
        for msg in messages:
            transport.send_message(msg)


def build_result(
    *,
    run_id: str,
    report_date: str,
    report_suffix: str,
    cfg: dict[str, str],
    reports: dict[str, Path],
    package: dict[str, Path],
    transport_status: str,
    error: str | None,
    require_pdf_package: bool,
) -> dict[str, Any]:
    languages = [
        {
            "language": "nl",
            "report_path": str(reports["nl_md"]),
            "pdf_path": str(package.get("nl_pdf", "")),
            "recipient_redacted": True,
            "recipient_hash": _sha256(cfg["recipient_nl"]),
        },
        {
            "language": "en",
            "report_path": str(reports["en_md"]),
            "pdf_path": str(package.get("en_pdf", "")),
            "recipient_redacted": True,
            "recipient_hash": _sha256(cfg["recipient_en"]),
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
        "require_pdf_package": require_pdf_package,
        "pdf_package_used": bool(package),
        "email_equity_curve_transport": "cid_png_when_present",
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
    parser.add_argument("--nl-md")
    parser.add_argument("--en-md")
    parser.add_argument("--output-dir", default="output/delivery")
    parser.add_argument("--require-pdf-package", action="store_true")
    parser.add_argument("--delivery-package-manifest", default=None)
    args = parser.parse_args()
    _require(args.confirm_controlled_send, "controlled sender requires explicit --confirm-controlled-send")
    cfg = _read_config()
    reports = _report_paths(args.report_suffix, nl_md=args.nl_md, en_md=args.en_md)
    package = _package_paths(Path(args.delivery_package_manifest) if args.delivery_package_manifest else None)
    if args.require_pdf_package:
        _require(bool(package), "--require-pdf-package requires --delivery-package-manifest")
    sender = cfg["sender"]
    messages = [
        _build_message(
            language="nl",
            report_date=args.report_date,
            sender=sender,
            recipient=cfg["recipient_nl"],
            markdown_path=reports["nl_md"],
            pdf_path=package.get("nl_pdf"),
            html_path=package.get("nl_html"),
            require_pdf_package=args.require_pdf_package,
        ),
        _build_message(
            language="en",
            report_date=args.report_date,
            sender=sender,
            recipient=cfg["recipient_en"],
            markdown_path=reports["en_md"],
            pdf_path=package.get("en_pdf"),
            html_path=package.get("en_html"),
            require_pdf_package=args.require_pdf_package,
        ),
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
            package=package,
            transport_status="transport_failed",
            error=type(exc).__name__,
            require_pdf_package=args.require_pdf_package,
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
        package=package,
        transport_status="transport_succeeded_unconfirmed",
        error=None,
        require_pdf_package=args.require_pdf_package,
    )
    path = write_result(Path(args.output_dir), payload)
    print(f"ETF_EU_CONTROLLED_TRANSPORT_RESULT | status=transport_succeeded_unconfirmed | result={path}")


if __name__ == "__main__":
    main()
