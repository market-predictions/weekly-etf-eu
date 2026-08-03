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


def _render_with_pdftoppm(pdf_path: Path, language_dir: Path, prefix: Path, dpi: int) -> list[Path] | None:
    renderer = shutil.which("pdftoppm")
    if renderer is None:
        return None
    subprocess.run(
        [renderer, "-png", "-r", str(dpi), str(pdf_path), str(prefix)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return sorted(language_dir.glob(f"{prefix.name}-*.png"))


def _render_with_pymupdf(pdf_path: Path, language_dir: Path, prefix: Path, dpi: int) -> list[Path]:
    try:
        import pymupdf
    except ImportError as exc:
        raise RuntimeError("Neither pdftoppm nor PyMuPDF is available for PDF page rendering") from exc

    scale = dpi / 72.0
    matrix = pymupdf.Matrix(scale, scale)
    rendered: list[Path] = []
    with pymupdf.open(pdf_path) as document:
        for index, page in enumerate(document, start=1):
            page_path = language_dir / f"{prefix.name}-{index:02d}.png"
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            pixmap.save(page_path)
            rendered.append(page_path)
    return rendered


def render_pdf(
    pdf_path: Path,
    output_dir: Path,
    language: str,
    dpi: int,
    min_text_characters_per_page: int,
) -> dict[str, Any]:
    reader = PdfReader(str(pdf_path))
    expected_pages = len(reader.pages)
    if expected_pages <= 0:
        raise RuntimeError(f"PDF contains no pages: {pdf_path}")

    extracted_text_counts = []
    for page in reader.pages:
        normalized = " ".join((page.extract_text() or "").split())
        extracted_text_counts.append(len(normalized))
    low_content_pages = [
        index
        for index, count in enumerate(extracted_text_counts, start=1)
        if count < min_text_characters_per_page
    ]
    if low_content_pages:
        raise RuntimeError(
            f"Low-content PDF page detected for {language}: pages={low_content_pages} "
            f"threshold={min_text_characters_per_page} counts={extracted_text_counts}"
        )

    language_dir = output_dir / language
    language_dir.mkdir(parents=True, exist_ok=True)
    prefix = language_dir / f"weekly_etf_eu_review_{language}"
    rendered = _render_with_pdftoppm(pdf_path, language_dir, prefix, dpi)
    renderer_name = "pdftoppm"
    if rendered is None:
        rendered = _render_with_pymupdf(pdf_path, language_dir, prefix, dpi)
        renderer_name = "pymupdf"

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
                "extracted_text_character_count": extracted_text_counts[index - 1],
            }
        )
    return {
        "language": language,
        "source_pdf": str(pdf_path),
        "source_pdf_sha256": sha256_file(pdf_path),
        "page_count": expected_pages,
        "minimum_text_characters_per_page": min_text_characters_per_page,
        "minimum_observed_text_characters": min(extracted_text_counts),
        "low_content_page_count": 0,
        "dpi": dpi,
        "renderer": renderer_name,
        "pages": pages,
    }


def build_review(
    manifest_path: Path,
    output_dir: Path,
    dpi: int,
    min_text_characters_per_page: int,
) -> Path:
    manifest = load_manifest(manifest_path)
    pdfs = resolve_pdf_files(manifest)
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered = [
        render_pdf(path, output_dir, language, dpi, min_text_characters_per_page)
        for language, path in pdfs.items()
    ]
    payload = {
        "schema_version": "etf_eu_routine_pdf_review_pages_v1",
        "artifact_type": "etf_eu_routine_pdf_review_pages",
        "generated_at_utc": utc_now(),
        "routine_manifest": str(manifest_path),
        "routine_run_id": manifest.get("run_id"),
        "report_date": manifest.get("report_date"),
        "language_count": len(rendered),
        "total_page_count": sum(item["page_count"] for item in rendered),
        "low_content_page_count": sum(item["low_content_page_count"] for item in rendered),
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
        f" | low_content_pages={payload['low_content_page_count']}"
    )
    return review_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=144)
    parser.add_argument("--min-text-characters-per-page", type=int, default=400)
    args = parser.parse_args()
    if args.dpi < 72 or args.dpi > 300:
        raise SystemExit("--dpi must be between 72 and 300")
    if args.min_text_characters_per_page < 0:
        raise SystemExit("--min-text-characters-per-page must be non-negative")
    build_review(
        args.manifest,
        args.output_dir,
        args.dpi,
        args.min_text_characters_per_page,
    )


if __name__ == "__main__":
    main()
