from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.send_etf_eu_report_runtime_html import validate_etf_eu_sender_preflight


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate(output_dir: Path, report_suffix: str | None = None) -> dict[str, object]:
    result = validate_etf_eu_sender_preflight(output_dir=output_dir, report_suffix=report_suffix)
    _require(result.get("schema_version") == "etf_eu_sender_preflight_v1", "wrong schema")
    _require(result.get("delivery_mode") == "preflight_no_send", "wrong delivery mode")
    _require(str(result.get("dutch_primary_report_path", "")).endswith(f"weekly_etf_eu_review_nl_{result['report_suffix']}.md"), "wrong Dutch primary path")
    _require(str(result.get("english_companion_report_path", "")).endswith(f"weekly_etf_eu_review_{result['report_suffix']}.md"), "wrong English companion path")
    _require(result.get("dutch_primary_exists") is True, "Dutch primary missing")
    _require(result.get("english_companion_exists") is True, "English companion missing")
    _require(result.get("us_report_name_assumption_detected") is False, "U.S. report-name assumption detected")
    _require(result.get("preflight_no_send_mode_supported") is True, "preflight no-send missing")
    for key in ["send_performed", "production_delivery", "email_delivery", "delivery_receipt", "delivery_success_claimed"]:
        _require(result.get(key) is False, f"expected false for {key}")
    print("ETF_EU_SENDER_ENTRYPOINT_OK | suffix=" + str(result["report_suffix"]))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--report-suffix", default=None)
    args = parser.parse_args()
    result = validate(Path(args.output_dir), args.report_suffix)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
