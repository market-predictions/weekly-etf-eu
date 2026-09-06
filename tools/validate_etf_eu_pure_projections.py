from __future__ import annotations

import json
from pathlib import Path

import weasyprint
from weasyprint import HTML

from runtime.current.render import render_html, render_markdown

WEASYPRINT_VERSION = "68.0"
REQUIRED_ARTIFACT_KEYS = ("nl_md", "en_md", "nl_html", "en_html", "nl_pdf", "en_pdf")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _pdf_bytes(html_text: str) -> bytes:
    _require(
        weasyprint.__version__ == WEASYPRINT_VERSION,
        f"canonical PDF renderer version mismatch: expected {WEASYPRINT_VERSION}, got {weasyprint.__version__}",
    )
    return HTML(
        string=html_text,
        base_url=str(Path("output/current").resolve()),
    ).write_pdf()


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
    for key in REQUIRED_ARTIFACT_KEYS:
        _require(
            approved_artifacts[key] == expected[key],
            f"approved client artifact is not a pure projection of frozen review_state: {key}",
        )
