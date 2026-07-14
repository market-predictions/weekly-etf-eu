from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def _load(path: Path) -> dict:
    if not path.exists():
        raise RuntimeError(f"missing page review index: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Write pending ETF EU visual-review evidence.")
    parser.add_argument("--source-run-id", required=True)
    parser.add_argument("--sanitization-run-id", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--preview-dir", required=True)
    parser.add_argument("--dutch-index", required=True)
    parser.add_argument("--english-index", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    preview = Path(args.preview_dir)
    dutch = _load(Path(args.dutch_index))
    english = _load(Path(args.english_index))
    payload = {
        "schema_version": "etf_eu_routine_pdf_visual_review_v1",
        "artifact_type": "etf_eu_routine_pdf_visual_review",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_run_id": args.source_run_id,
        "repair_run_id": args.sanitization_run_id,
        "sanitization_run_id": args.sanitization_run_id,
        "dutch_pdf": str(preview / f"weekly_etf_eu_review_nl_{args.report_suffix}.pdf"),
        "english_pdf": str(preview / f"weekly_etf_eu_review_{args.report_suffix}.pdf"),
        "dutch_page_count": dutch["page_count"],
        "english_page_count": english["page_count"],
        "dutch_pages_reviewed": [],
        "english_pages_reviewed": [],
        "first_page_reviewed": False,
        "middle_page_reviewed": False,
        "last_page_reviewed": False,
        "no_right_edge_clipping": False,
        "no_bottom_clipping": False,
        "no_overlapping_text": False,
        "tables_readable": False,
        "headings_readable": False,
        "unicode_correct": False,
        "all_sections_visible": False,
        "duplicate_title_absent": False,
        "client_surface_language_clean": False,
        "visual_review_passed": False,
        "review_notes": ["Rendered first, middle and last pages are ready for explicit visual inspection."],
        "blockers": ["manual visual inspection required"],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
