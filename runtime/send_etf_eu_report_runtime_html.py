from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

EU_EN_REPORT_RE = re.compile(r"^weekly_etf_eu_review_(\d{6})\.md$")
EU_NL_REPORT_RE = re.compile(r"^weekly_etf_eu_review_nl_(\d{6})\.md$")
US_REPORT_RE = re.compile(r"^weekly_analysis(?:_pro)?_.*\.md$")


def _suffix_for(path: Path) -> str | None:
    for pattern in (EU_EN_REPORT_RE, EU_NL_REPORT_RE):
        match = pattern.match(path.name)
        if match:
            return match.group(1)
    return None


def _discover(output_dir: Path) -> tuple[dict[str, Path], dict[str, Path], list[str], list[str]]:
    english: dict[str, Path] = {}
    dutch: dict[str, Path] = {}
    ignored: list[str] = []
    us_named: list[str] = []
    for path in sorted(output_dir.glob("*.md")):
        if not path.is_file():
            continue
        en_match = EU_EN_REPORT_RE.match(path.name)
        nl_match = EU_NL_REPORT_RE.match(path.name)
        if en_match:
            english[en_match.group(1)] = path
        elif nl_match:
            dutch[nl_match.group(1)] = path
        elif path.name.startswith("weekly_etf_eu_review"):
            ignored.append(path.name)
        elif US_REPORT_RE.match(path.name):
            us_named.append(path.name)
    return english, dutch, ignored, us_named


def _select_suffix(english: dict[str, Path], dutch: dict[str, Path], report_suffix: str | None) -> str:
    if report_suffix:
        if report_suffix not in dutch:
            raise RuntimeError(f"ETF EU sender preflight failed: missing Dutch primary report for suffix {report_suffix}")
        if report_suffix not in english:
            raise RuntimeError(f"ETF EU sender preflight failed: missing English companion report for suffix {report_suffix}")
        return report_suffix
    complete_suffixes = sorted(set(english) & set(dutch))
    if not complete_suffixes:
        raise RuntimeError("ETF EU sender preflight failed: no complete canonical Dutch/English report pair found")
    return complete_suffixes[-1]


def validate_etf_eu_sender_preflight(
    *,
    output_dir: Path,
    report_suffix: str | None = None,
    delivery_mode: str = "preflight_no_send",
) -> dict[str, object]:
    if delivery_mode != "preflight_no_send":
        raise RuntimeError("ETF EU sender preflight only supports delivery_mode=preflight_no_send")
    output_dir = Path(output_dir)
    if not output_dir.exists():
        raise RuntimeError(f"ETF EU sender preflight failed: output_dir does not exist: {output_dir}")

    english, dutch, ignored, us_named = _discover(output_dir)
    selected_suffix = _select_suffix(english, dutch, report_suffix)
    dutch_path = dutch[selected_suffix]
    english_path = english[selected_suffix]

    return {
        "schema_version": "etf_eu_sender_preflight_v1",
        "delivery_mode": "preflight_no_send",
        "report_suffix": selected_suffix,
        "dutch_primary_report_path": str(dutch_path),
        "english_companion_report_path": str(english_path),
        "dutch_primary_exists": dutch_path.exists(),
        "english_companion_exists": english_path.exists(),
        "non_canonical_artifacts_ignored": bool(ignored),
        "non_canonical_artifacts_ignored_count": len(ignored),
        "ignored_non_canonical_artifacts": ignored,
        "us_report_name_assumption_detected": False,
        "us_named_artifacts_ignored": us_named,
        "preflight_no_send_mode_supported": True,
        "send_performed": False,
        "production_delivery": False,
        "email_delivery": False,
        "delivery_receipt": False,
        "delivery_success_claimed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--report-suffix", default=None)
    args = parser.parse_args()
    result = validate_etf_eu_sender_preflight(output_dir=Path(args.output_dir), report_suffix=args.report_suffix)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
