from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _require_tools() -> None:
    missing = [name for name in ("pdfinfo", "pdftoppm") if not shutil.which(name)]
    if missing:
        raise RuntimeError("Missing required Poppler tools: " + ", ".join(missing))


def _page_count(pdf: Path) -> int:
    completed = subprocess.run(["pdfinfo", str(pdf)], check=True, text=True, capture_output=True)
    match = re.search(r"^Pages:\s+(\d+)\s*$", completed.stdout, flags=re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not determine page count for {pdf}")
    return int(match.group(1))


def render_review_pages(*, pdf: Path, output_dir: Path, dpi: int = 160) -> dict[str, object]:
    _require_tools()
    if not pdf.exists():
        raise FileNotFoundError(pdf)
    pages = _page_count(pdf)
    middle = max(1, (pages + 1) // 2)
    requested = [("first", 1), ("middle", middle), ("last", pages)]
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered: dict[str, str] = {}
    for label, page in requested:
        destination_prefix = output_dir / f"{label}_{page:03d}"
        subprocess.run(
            [
                "pdftoppm",
                "-f",
                str(page),
                "-l",
                str(page),
                "-r",
                str(dpi),
                "-png",
                "-singlefile",
                str(pdf),
                str(destination_prefix),
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        png = destination_prefix.with_suffix(".png")
        if not png.exists() or png.stat().st_size <= 0:
            raise RuntimeError(f"Rendered page was not created: {png}")
        rendered[label] = str(png)
    return {
        "generated_at_utc": _utc_now(),
        "pdf": str(pdf),
        "page_count": pages,
        "dpi": dpi,
        "rendered_pages": rendered,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Render first, middle and last PDF pages for review.")
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--dpi", type=int, default=160)
    parser.add_argument("--write-index")
    args = parser.parse_args()

    result = render_review_pages(pdf=Path(args.pdf), output_dir=Path(args.output_dir), dpi=args.dpi)
    if args.write_index:
        index = Path(args.write_index)
        index.parent.mkdir(parents=True, exist_ok=True)
        index.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
