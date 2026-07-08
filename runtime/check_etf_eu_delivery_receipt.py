from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_receipt_check(*, run_id: str, evidence_path: str, delay_minutes: int, mvp15_static: bool) -> dict[str, Any]:
    status = "not_attempted" if mvp15_static else "receipt_not_found_after_delay"
    return {
        "schema_version": "etf_eu_delivery_receipt_check_v1",
        "artifact_type": "etf_eu_delivery_receipt_check",
        "generated_at_utc": _utc_now(),
        "run_id": run_id,
        "evidence_path": evidence_path,
        "delay_minutes": delay_minutes,
        "check_target": "recipient_mailbox_or_receipt_source",
        "receipt_status": status,
        "receipt_confirmed": False,
        "delivery_success_claimed": False,
        "transport_success_not_inbox_receipt": True,
        "mvp15_static": mvp15_static,
        "secret_values_exposed": False,
        "recipient_plaintext_values_exposed": False,
    }


def write_receipt_check(output_dir: Path, *, run_id: str, evidence_path: str, delay_minutes: int, mvp15_static: bool) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_receipt_check(
        run_id=run_id,
        evidence_path=evidence_path,
        delay_minutes=delay_minutes,
        mvp15_static=mvp15_static,
    )
    path = output_dir / f"etf_eu_receipt_check_{run_id}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output/delivery")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--evidence-path", required=True)
    parser.add_argument("--delay-minutes", type=int, default=10)
    parser.add_argument("--mvp15-static", action="store_true")
    args = parser.parse_args()
    path = write_receipt_check(
        Path(args.output_dir),
        run_id=args.run_id,
        evidence_path=args.evidence_path,
        delay_minutes=args.delay_minutes,
        mvp15_static=args.mvp15_static,
    )
    print(f"ETF_EU_RECEIPT_CHECK_ARTIFACT_OK | receipt={path}")


if __name__ == "__main__":
    main()
