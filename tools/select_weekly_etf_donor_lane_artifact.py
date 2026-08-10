from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


def _date(value: str) -> date:
    return date.fromisoformat(value[:10])


def select(root: Path, report_date: str) -> Path:
    target = _date(report_date)
    candidates: list[tuple[date, Path]] = []
    for path in (root / "output" / "lane_reviews").glob("etf_lane_assessment_*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            observed = _date(str(payload.get("report_date") or ""))
        except Exception:
            continue
        if observed <= target:
            candidates.append((observed, path))
    if not candidates:
        raise RuntimeError(f"No donor lane artifact available on/before {report_date}")
    candidates.sort(key=lambda item: (item[0], item[1].name))
    return candidates[-1][1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--donor-root", type=Path, required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--write-path", type=Path)
    args = parser.parse_args()
    selected = select(args.donor_root, args.report_date)
    if args.write_path:
        args.write_path.parent.mkdir(parents=True, exist_ok=True)
        args.write_path.write_text(str(selected) + "\n", encoding="utf-8")
    print(selected)


if __name__ == "__main__":
    main()
