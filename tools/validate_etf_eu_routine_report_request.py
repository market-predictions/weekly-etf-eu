from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path


REQUIRED = {
    "schema_version",
    "artifact_type",
    "run_id",
    "report_date",
    "report_suffix",
    "previous_routine_manifest",
    "previous_delivery_closeout_manifest",
    "execution_mode",
    "delivery_authority",
    "recipient_plaintext_values_exposed",
    "secret_values_exposed",
    "raw_receipt_pdf_stored_in_github",
}
FORBIDDEN_KEYS = {
    "send_confirmation",
    "second_send_confirmation",
    "smtp_recipient",
    "recipient_email",
}
FORBIDDEN = [
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"SMTP_PASS", re.IGNORECASE),
    re.compile(r"MRKT_RPRTS_SMTP", re.IGNORECASE),
]


def parse(path: Path) -> dict[str, str]:
    if not path.exists():
        raise AssertionError(f"request missing: {path}")
    raw = path.read_text(encoding="utf-8")
    for pattern in FORBIDDEN:
        if pattern.search(raw):
            raise AssertionError(f"request contains forbidden pattern: {pattern.pattern}")
    data: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    missing = REQUIRED - set(data)
    if missing:
        raise AssertionError(f"request missing keys: {sorted(missing)}")
    forbidden_present = FORBIDDEN_KEYS & set(data)
    if forbidden_present:
        raise AssertionError(
            "candidate request contains delivery-only keys: "
            f"{sorted(forbidden_present)}"
        )
    return data


def validate(path: Path) -> dict[str, str]:
    data = parse(path)
    if data["schema_version"] != "etf_eu_routine_report_request_v2":
        raise AssertionError("request schema mismatch; current routine requires v2 candidate-only requests")
    if data["artifact_type"] != "etf_eu_routine_report_request":
        raise AssertionError("request type mismatch")
    if data["execution_mode"] != "generate_validate_candidate":
        raise AssertionError("unsupported execution mode; routine generation is candidate-only")
    if data["delivery_authority"] != "false":
        raise AssertionError("candidate request cannot grant delivery authority")
    for key in [
        "recipient_plaintext_values_exposed",
        "secret_values_exposed",
        "raw_receipt_pdf_stored_in_github",
    ]:
        if data[key] != "false":
            raise AssertionError(f"{key} must be false")
    run_id = data["run_id"]
    report_date = data["report_date"]
    report_suffix = data["report_suffix"]
    if not re.fullmatch(r"\d{8}_\d{6}", run_id):
        raise AssertionError("run_id format mismatch")
    parsed_date = date.fromisoformat(report_date)
    if report_suffix != parsed_date.strftime("%y%m%d"):
        raise AssertionError("report_suffix does not match report_date")
    if run_id[:8] != parsed_date.strftime("%Y%m%d"):
        raise AssertionError("run_id date does not match report_date")
    for key in ["previous_routine_manifest", "previous_delivery_closeout_manifest"]:
        ref = Path(data[key])
        if not ref.exists():
            raise AssertionError(f"referenced historical artifact missing: {ref}")
    if "20260710_000000" == run_id or report_suffix == "260710":
        raise AssertionError("previous run identity cannot be reused")
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    data = validate(Path(args.request))
    print(
        "ETF_EU_ROUTINE_REPORT_REQUEST_OK"
        f" | run_id={data['run_id']}"
        f" | report_date={data['report_date']}"
        " | mode=generate_validate_candidate"
        " | delivery_authority=false"
    )


if __name__ == "__main__":
    main()
