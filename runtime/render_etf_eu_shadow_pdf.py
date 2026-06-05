from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_shadow_pdf_manifest_v1"
DEFAULT_OUTPUT_DIR = Path("output/pdf")
STATIC_CREATED_AT_UTC = "1970-01-01T00:00:00Z"


def _suffix(report_date: str) -> str:
    y, m, d = report_date.split("-")
    return f"{y[2:]}{m}{d}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _markdown_preview(markdown: str, *, max_lines: int = 40) -> list[str]:
    lines: list[str] = []
    for raw in markdown.splitlines():
        clean = raw.strip()
        if not clean:
            continue
        clean = clean.replace("#", "").replace("*", "").replace("`", "")
        clean = " ".join(clean.split())
        if clean:
            lines.append(clean[:105])
        if len(lines) >= max_lines:
            break
    return lines or ["Weekly ETF EU shadow PDF artifact"]


def _minimal_pdf_bytes(title: str, markdown: str) -> bytes:
    lines = [title, "Shadow-only PDF rendering artifact", *_markdown_preview(markdown)]
    text_ops = ["BT", "/F1 10 Tf", "50 800 Td", "14 TL"]
    for line in lines:
        safe = _pdf_escape(line.encode("latin-1", errors="replace").decode("latin-1"))
        text_ops.append(f"({safe}) Tj")
        text_ops.append("T*")
    text_ops.append("ET")
    stream = "\n".join(text_ops).encode("latin-1")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    output = bytearray(b"%PDF-1.4\n% ETF EU shadow PDF artifact\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(output)


def render_markdown_to_shadow_pdf(markdown_path: Path, pdf_path: Path, *, title: str) -> Path:
    if not markdown_path.exists():
        raise FileNotFoundError(f"Markdown report not found: {markdown_path}")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    markdown = markdown_path.read_text(encoding="utf-8")
    pdf_path.write_bytes(_minimal_pdf_bytes(title, markdown))
    return pdf_path


def build_shadow_pdf_manifest(
    *,
    run_id: str,
    report_date: str,
    dutch_report_path: Path | None = None,
    english_report_path: Path | None = None,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> Path:
    suffix = _suffix(report_date)
    dutch_report = dutch_report_path or Path("output") / f"weekly_etf_eu_review_nl_{suffix}.md"
    english_report = english_report_path or Path("output") / f"weekly_etf_eu_review_{suffix}.md"
    dutch_pdf = output_dir / f"weekly_etf_eu_review_nl_{suffix}.pdf"
    english_pdf = output_dir / f"weekly_etf_eu_review_{suffix}.pdf"

    render_markdown_to_shadow_pdf(dutch_report, dutch_pdf, title=f"Weekly ETF EU Review NL {report_date}")
    render_markdown_to_shadow_pdf(english_report, english_pdf, title=f"Weekly ETF EU Review EN {report_date}")

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "shadow_pdf_manifest",
        "status": "shadow_only",
        "run_id": run_id,
        "report_date": report_date,
        "created_at_utc": STATIC_CREATED_AT_UTC,
        "dutch_report_path": str(dutch_report),
        "english_report_path": str(english_report),
        "dutch_pdf_path": str(dutch_pdf),
        "english_pdf_path": str(english_pdf),
        "pdf_generation": "shadow_only",
        "production_delivery": False,
        "email_delivery": False,
        "delivery_receipt": False,
        "portfolio_mutation": False,
        "funding_authority": False,
        "valuation_grade": False,
        "candidate_promotion": False,
        "workflow_integrated": False,
        "not_delivery_receipt": True,
        "shadow_artifacts_only": True,
        "artifacts": [
            {
                "kind": "dutch_primary_shadow_pdf",
                "path": str(dutch_pdf),
                "source_markdown_path": str(dutch_report),
                "exists": dutch_pdf.exists(),
                "size_bytes": dutch_pdf.stat().st_size if dutch_pdf.exists() else 0,
                "sha256": _sha256(dutch_pdf) if dutch_pdf.exists() else "",
            },
            {
                "kind": "english_companion_shadow_pdf",
                "path": str(english_pdf),
                "source_markdown_path": str(english_report),
                "exists": english_pdf.exists(),
                "size_bytes": english_pdf.stat().st_size if english_pdf.exists() else 0,
                "sha256": _sha256(english_pdf) if english_pdf.exists() else "",
            },
        ],
        "authority_note": "PDF rendering is shadow-only and does not create production delivery, email delivery, or a delivery receipt.",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / f"etf_eu_shadow_pdf_manifest_{run_id}.json"
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(
        "ETF_EU_SHADOW_PDF_RENDER_OK"
        f" | manifest={manifest_path}"
        f" | dutch_pdf={dutch_pdf}"
        f" | english_pdf={english_pdf}"
        " | pdf_generation=shadow_only | production_delivery=false | email_delivery=false | delivery_receipt=false"
    )
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--dutch-report", default=None)
    parser.add_argument("--english-report", default=None)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    build_shadow_pdf_manifest(
        run_id=args.run_id,
        report_date=args.report_date,
        dutch_report_path=Path(args.dutch_report) if args.dutch_report else None,
        english_report_path=Path(args.english_report) if args.english_report else None,
        output_dir=Path(args.output_dir),
    )


if __name__ == "__main__":
    main()
