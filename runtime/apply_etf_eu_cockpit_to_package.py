from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from weasyprint import HTML

from runtime.additive_etf_eu_cockpit_front_page import FEATURE_FLAG, inject, parse_feature_value


@dataclass(frozen=True)
class PackageCockpitResult:
    status: str
    feature_value: str
    enabled: bool
    diagnostic: str
    dutch_front_page_count: int
    english_front_page_count: int
    dutch_summary_suppressed: bool
    english_summary_suppressed: bool
    dutch_browser_html: Path | None
    english_browser_html: Path | None


def _render_pdf_bytes(html_text: str, *, base_url: Path) -> bytes:
    return HTML(string=html_text, base_url=str(base_url.resolve())).write_pdf()


def _write_atomic(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        handle.write(payload)
        temp_path = Path(handle.name)
    os.replace(temp_path, path)


def _write_text_atomic(path: Path, text: str) -> None:
    _write_atomic(path, text.encode("utf-8"))


def apply_cockpit_to_package(
    *,
    state: dict[str, Any],
    dutch_html: Path,
    english_html: Path,
    dutch_pdf: Path,
    english_pdf: Path,
    dutch_browser_html: Path,
    english_browser_html: Path,
    feature_value: str | None = None,
) -> PackageCockpitResult:
    """Apply one bilingual cockpit mutation without changing the attachment contract.

    The primary HTML files become the inline/table client versions used by the
    mail body and HTML attachments. PDFs are rendered from the richer browser
    versions, which are retained as internal audit files. Disabled or failed
    integration leaves the existing package byte-identical.
    """

    try:
        feature = parse_feature_value(feature_value)
    except Exception as exc:
        return PackageCockpitResult(
            status="fallback",
            feature_value=str(feature_value),
            enabled=False,
            diagnostic=f"invalid_feature_value:{type(exc).__name__}",
            dutch_front_page_count=0,
            english_front_page_count=0,
            dutch_summary_suppressed=False,
            english_summary_suppressed=False,
            dutch_browser_html=None,
            english_browser_html=None,
        )

    if feature == "disabled":
        return PackageCockpitResult(
            status="disabled",
            feature_value=feature,
            enabled=False,
            diagnostic="feature_disabled",
            dutch_front_page_count=0,
            english_front_page_count=0,
            dutch_summary_suppressed=False,
            english_summary_suppressed=False,
            dutch_browser_html=None,
            english_browser_html=None,
        )

    classic_nl = dutch_html.read_text(encoding="utf-8")
    classic_en = english_html.read_text(encoding="utf-8")
    browser_nl = inject(classic_nl, state=state, language="nl", feature_value=feature, render_mode="browser")
    browser_en = inject(classic_en, state=state, language="en", feature_value=feature, render_mode="browser")
    email_nl = inject(classic_nl, state=state, language="nl", feature_value=feature, render_mode="email")
    email_en = inject(classic_en, state=state, language="en", feature_value=feature, render_mode="email")
    results = (browser_nl, browser_en, email_nl, email_en)
    if any(result.status != "enabled" or result.front_page_count != 1 for result in results):
        diagnostic = ";".join(result.diagnostic for result in results)
        return PackageCockpitResult(
            status="fallback",
            feature_value=feature,
            enabled=False,
            diagnostic=f"bilingual_integration_failed:{diagnostic}",
            dutch_front_page_count=browser_nl.front_page_count,
            english_front_page_count=browser_en.front_page_count,
            dutch_summary_suppressed=browser_nl.investor_summary_suppressed,
            english_summary_suppressed=browser_en.investor_summary_suppressed,
            dutch_browser_html=None,
            english_browser_html=None,
        )

    if not all(result.investor_summary_suppressed for result in results):
        return PackageCockpitResult(
            status="fallback",
            feature_value=feature,
            enabled=False,
            diagnostic="bilingual_investor_summary_suppression_failed",
            dutch_front_page_count=browser_nl.front_page_count,
            english_front_page_count=browser_en.front_page_count,
            dutch_summary_suppressed=browser_nl.investor_summary_suppressed,
            english_summary_suppressed=browser_en.investor_summary_suppressed,
            dutch_browser_html=None,
            english_browser_html=None,
        )

    try:
        nl_pdf_bytes = _render_pdf_bytes(browser_nl.html, base_url=dutch_html.parent)
        en_pdf_bytes = _render_pdf_bytes(browser_en.html, base_url=english_html.parent)
        if not nl_pdf_bytes or not en_pdf_bytes:
            raise RuntimeError("cockpit PDF render returned empty bytes")
    except Exception as exc:
        return PackageCockpitResult(
            status="fallback",
            feature_value=feature,
            enabled=False,
            diagnostic=f"pdf_render_failed:{type(exc).__name__}:{exc}",
            dutch_front_page_count=browser_nl.front_page_count,
            english_front_page_count=browser_en.front_page_count,
            dutch_summary_suppressed=True,
            english_summary_suppressed=True,
            dutch_browser_html=None,
            english_browser_html=None,
        )

    # Commit only after both languages and both render modes have succeeded.
    _write_text_atomic(dutch_html, email_nl.html)
    _write_text_atomic(english_html, email_en.html)
    _write_atomic(dutch_pdf, nl_pdf_bytes)
    _write_atomic(english_pdf, en_pdf_bytes)
    _write_text_atomic(dutch_browser_html, browser_nl.html)
    _write_text_atomic(english_browser_html, browser_en.html)

    return PackageCockpitResult(
        status="enabled",
        feature_value=feature,
        enabled=True,
        diagnostic="bilingual_cockpit_package_applied",
        dutch_front_page_count=1,
        english_front_page_count=1,
        dutch_summary_suppressed=True,
        english_summary_suppressed=True,
        dutch_browser_html=dutch_browser_html,
        english_browser_html=english_browser_html,
    )


def configured_feature_value() -> str:
    return os.environ.get(FEATURE_FLAG, "disabled")
