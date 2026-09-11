from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
from typing import Any

import weasyprint
from pypdf import PdfReader
from weasyprint import HTML

from runtime.current.render import render_html, render_markdown

WEASYPRINT_VERSION = "68.0"
REQUIRED_ARTIFACT_KEYS = ("nl_md", "en_md", "nl_html", "en_html", "nl_pdf", "en_pdf")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _pdf_identifier(html_text: str) -> bytes:
    return hashlib.sha256(html_text.encode("utf-8")).digest()


def _pdf_bytes(html_text: str) -> bytes:
    _require(
        weasyprint.__version__ == WEASYPRINT_VERSION,
        f"canonical PDF renderer version mismatch: expected {WEASYPRINT_VERSION}, got {weasyprint.__version__}",
    )
    return HTML(
        string=html_text,
        base_url=str(Path("output/current").resolve()),
    ).write_pdf(pdf_identifier=_pdf_identifier(html_text))


def _pdf_projection_fingerprint(pdf_bytes: bytes, *, expected_identifier: bytes) -> tuple[Any, ...]:
    eof = pdf_bytes.rfind(b"%%EOF")
    _require(eof >= 0 and not pdf_bytes[eof + len(b"%%EOF") :].strip(), "approved PDF has trailing data")
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes), strict=True)
    except Exception as exc:
        raise AssertionError("approved PDF is not parseable") from exc
    document_id = reader.trailer.get("/ID")
    _require(document_id is not None and len(document_id) >= 1, "approved PDF deterministic source identifier missing")
    first_id = document_id[0]
    raw_id = getattr(first_id, "original_bytes", None)
    _require(raw_id == expected_identifier, "approved PDF is not bound to the expected HTML projection")
    pages: list[tuple[Any, ...]] = []
    for page in reader.pages:
        box = page.mediabox
        pages.append(
            (
                round(float(box.left), 6),
                round(float(box.bottom), 6),
                round(float(box.right), 6),
                round(float(box.top), 6),
                page.extract_text() or "",
            )
        )
    metadata = reader.metadata or {}
    return (
        len(reader.pages),
        str(metadata.get("/Producer") or ""),
        tuple(pages),
    )


def expected_projection_bytes(review_state_bytes: bytes) -> dict[str, bytes]:
    try:
        review_state = json.loads(review_state_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AssertionError("invalid frozen review_state JSON for projection validation") from exc
    _require(isinstance(review_state, dict), "frozen review_state must be a JSON object")

    nl_md = render_markdown(review_state, "nl")
    en_md = render_markdown(review_state, "en")
    nl_html = render_html(review_state, "nl")
    en_html = render_html(review_state, "en")
    return {
        "nl_md": nl_md.encode("utf-8"),
        "en_md": en_md.encode("utf-8"),
        "nl_html": nl_html.encode("utf-8"),
        "en_html": en_html.encode("utf-8"),
        "nl_pdf": _pdf_bytes(nl_html),
        "en_pdf": _pdf_bytes(en_html),
    }


def validate_projection_bytes(
    review_state_bytes: bytes,
    approved_artifacts: dict[str, bytes],
) -> None:
    _require(
        set(REQUIRED_ARTIFACT_KEYS) <= set(approved_artifacts),
        "six approved client artifacts required for pure-projection validation",
    )
    expected = expected_projection_bytes(review_state_bytes)
    for key in ("nl_md", "en_md", "nl_html", "en_html"):
        _require(
            approved_artifacts[key] == expected[key],
            f"approved client artifact is not a pure projection of frozen review_state: {key}",
        )
    for language in ("nl", "en"):
        html_key = f"{language}_html"
        pdf_key = f"{language}_pdf"
        html_text = expected[html_key].decode("utf-8")
        expected_fingerprint = _pdf_projection_fingerprint(
            expected[pdf_key], expected_identifier=_pdf_identifier(html_text)
        )
        approved_fingerprint = _pdf_projection_fingerprint(
            approved_artifacts[pdf_key], expected_identifier=_pdf_identifier(html_text)
        )
        _require(
            approved_fingerprint == expected_fingerprint,
            f"approved client artifact is not a pure projection of frozen review_state: {pdf_key}",
        )
