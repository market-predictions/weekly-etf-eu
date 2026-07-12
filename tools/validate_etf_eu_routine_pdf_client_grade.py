from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from tools.validate_etf_eu_routine_pdf_client_grade_base import validate_pdf as validate_base


ISIN_RE = re.compile(r"\b[A-Z]{2}[A-Z0-9]{9}\d\b")


def validate_pdf(
    *,
    pdf: Path,
    html: Path,
    markdown: Path,
    language: str,
    repair_run_id: str,
    source_run_id: str,
) -> dict[str, Any]:
    result = validate_base(
        pdf=pdf,
        html=html,
        markdown=markdown,
        language=language,
        repair_run_id=repair_run_id,
        source_run_id=source_run_id,
    )
    represented_rows = len(ISIN_RE.findall(markdown.read_text(encoding="utf-8").upper()))
    blockers = list(result.get("blockers", []))
    if represented_rows < 8:
        blockers.append(f"Expected at least 8 represented pricing lines, found {represented_rows}")
    result.update(
        {
            "schema_version": "etf_eu_routine_pdf_client_grade_v2",
            "pricing_line_count_detected": represented_rows,
            "pricing_line_count_source": "source_markdown_isin_rows",
            "blockers": blockers,
            "machine_validation_passed": not blockers,
        }
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Weekly ETF EU client-grade HTML/PDF output.")
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--html", required=True)
    parser.add_argument("--markdown", required=True)
    parser.add_argument("--language", required=True, choices=["nl", "en"])
    parser.add_argument("--repair-run-id", required=True)
    parser.add_argument("--source-run-id", required=True)
    parser.add_argument("--write-result", required=True)
    args = parser.parse_args()
    result = validate_pdf(
        pdf=Path(args.pdf),
        html=Path(args.html),
        markdown=Path(args.markdown),
        language=args.language,
        repair_run_id=args.repair_run_id,
        source_run_id=args.source_run_id,
    )
    output = Path(args.write_result)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["machine_validation_passed"] is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
