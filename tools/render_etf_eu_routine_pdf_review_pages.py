from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pypdf import PdfReader


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "etf_eu_routine_run_manifest_v3_converged":
        raise RuntimeError("Unexpected routine manifest schema")
    return payload


def resolve_pdf_files(manifest: dict[str, Any]) -> dict[str, Path]:
    files = manifest.get("files") if isinstance(manifest.get("files"), dict) else {}
    resolved: dict[str, Path] = {}
    for language, key in (("nl", "nl_pdf"), ("en", "en_pdf")):
        item = files.get(key) if isinstance(files.get(key), dict) else {}
        path = Path(str(item.get("path") or ""))
        if not path.is_file() or path.stat().st_size <= 0:
            raise RuntimeError(f"Routine PDF missing or empty for {language}: {path}")
        expected_sha = str(item.get("sha256") or "")
        actual_sha = sha256_file(path)
        if expected_sha and actual_sha != expected_sha:
            raise RuntimeError(f"Routine PDF digest mismatch for {language}")
        resolved[language] = path
    return resolved


def render_pdf(pdf_path: Path, output_dir: Path, language: str, dpi: int) -> dict[str, Any]:
    renderer = shutil.which("pdftoppm")
    if renderer is None:
        raise RuntimeError("pdftoppm is required to render PDF review pages")

    reader = PdfReader(str(pdf_path))
    expected_pages = len(reader.pages)
    if expected_pages <= 0:
        raise RuntimeError(f"PDF contains no pages: {pdf_path}")

    language_dir = output_dir / language
    language_dir.mkdir(parents=True, exist_ok=True)
    prefix = language_dir / f"weekly_etf_eu_review_{language}"
    subprocess.run(
        [renderer, "-png", "-r", str(dpi), str(pdf_path), str(prefix)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    rendered = sorted(language_dir.glob(f"{prefix.name}-*.png"))
    if len(rendered) != expected_pages:
        raise RuntimeError(
            f"Rendered page count mismatch for {language}: expected={expected_pages} actual={len(rendered)}"
        )
    pages = []
    for index, page_path in enumerate(rendered, start=1):
        if page_path.stat().st_size <= 0:
            raise RuntimeError(f"Rendered page is empty: {page_path}")
        pages.append(
            {
                "page_number": index,
                "path": str(page_path),
                "sha256": sha256_file(page_path),
                "size_bytes": page_path.stat().st_size,
            }
        )
    return {
        "language": language,
        "source_pdf": str(pdf_path),
        "source_pdf_sha256": sha256_file(pdf_path),
        "page_count": expected_pages,
        "dpi": dpi,
        "renderer": "pdftoppm",
        "pages": pages,
    }


def build_review(manifest_path: Path, output_dir: Path, dpi: int) -> Path:
    manifest = load_manifest(manifest_path)
    pdfs = resolve_pdf_files(manifest)
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered = [render_pdf(path, output_dir, language, dpi) for language, path in pdfs.items()]
    payload = {
        "schema_version": "etf_eu_routine_pdf_review_pages_v1",
        "artifact_type": "etf_eu_routine_pdf_review_pages",
        "generated_at_utc": utc_now(),
        "routine_manifest": str(manifest_path),
        "routine_run_id": manifest.get("run_id"),
        "report_date": manifest.get("report_date"),
        "language_count": len(rendered),
        "total_page_count": sum(item["page_count"] for item in rendered),
        "renderings": rendered,
        "visual_review_status": "rendered_pending_human_review",
        "portfolio_mutation": False,
        "delivery_authority": False,
    }
    review_path = output_dir / "etf_eu_routine_pdf_review_pages_manifest.json"
    review_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "ETF_EU_ROUTINE_PDF_REVIEW_PAGES_OK"
        f" | manifest={review_path}"
        f" | languages={payload['language_count']}"
        f" | pages={payload['total_page_count']}"
    )
    return review_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=144)
    args = parser.parse_args()
    if args.dpi < 72 or args.dpi > 300:
        raise SystemExit("--dpi must be between 72 and 300")
    build_review(args.manifest, args.output_dir, args.dpi)


if __name__ == "__main__":
    main()
