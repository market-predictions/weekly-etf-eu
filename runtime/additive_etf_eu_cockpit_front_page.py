from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from weasyprint import HTML

from runtime.etf_eu_cockpit_email_safe_surface import render_email_safe_front_page
from runtime.render_etf_eu_cockpit_front_page import FRONT_PAGE_MARKER, STYLE_ID, CockpitFragment, render_browser_fragment

FEATURE_FLAG = "MRKT_RPRTS_ETF_EU_COCKPIT_FRONT_PAGE"
VALID_VALUES = frozenset({"disabled", "enabled"})
SUPPRESSED_SUMMARY_CLASS = "cockpit-summary-suppressed"


@dataclass(frozen=True)
class InjectionResult:
    html: str
    status: str
    diagnostic: str
    feature_value: str
    front_page_count: int
    investor_summary_suppressed: bool


def parse_feature_value(raw: str | None = None) -> str:
    value = os.environ.get(FEATURE_FLAG, "disabled") if raw is None else raw
    normalized = str(value).strip().lower()
    if normalized not in VALID_VALUES:
        raise ValueError(f"{FEATURE_FLAG} must be disabled or enabled")
    return normalized


def _pct(value: float, language: str, decimals: int, *, signed: bool = False) -> str:
    sign = "+" if signed and value > 0 else ""
    text = f"{sign}{value:.{decimals}f}%"
    return text.replace(".", ",") if language == "nl" else text


def _front_page_precision(fragment_html: str, state: dict, language: str) -> str:
    portfolio = state.get("portfolio") or {}
    starting = float(portfolio.get("starting_capital_eur") or 100000.0)
    nav = float(portfolio.get("nav_eur") or starting)
    since = float(portfolio.get("since_inception_return_pct") or ((nav / starting - 1.0) * 100.0 if starting else 0.0))
    points = [row for row in (state.get("equity_curve") or {}).get("points") or [] if isinstance(row, dict) and row.get("nav_eur")]
    peak = 0.0
    drawdown = 0.0
    for row in points:
        value = float(row["nav_eur"])
        peak = max(peak, value)
        if peak:
            drawdown = min(drawdown, (value / peak - 1.0) * 100.0)

    old_since = _pct(since, language, 1, signed=True)
    new_since = _pct(since, language, 2, signed=True) if abs(since) < 1 else old_since
    old_drawdown = _pct(drawdown, language, 1)
    new_drawdown = _pct(drawdown, language, 2) if abs(drawdown) < 1 else old_drawdown
    fragment_html = fragment_html.replace(old_since, new_since)
    fragment_html = fragment_html.replace(old_drawdown, new_drawdown)
    history_label = f"{len(points)} waarderingspunten" if language == "nl" else f"{len(points)} valuation points"
    fragment_html = fragment_html.replace(">sinds start<", f">{history_label}<", 1)
    fragment_html = fragment_html.replace(">since inception<", f">{history_label}<", 1)
    return fragment_html


def _suppress_first_investor_summary(html_text: str) -> tuple[str, bool]:
    marker = '<div class="summary-strip">'
    if marker not in html_text:
        return html_text, False
    replacement = (
        f'<div class="summary-strip {SUPPRESSED_SUMMARY_CLASS}" '
        'aria-hidden="true" style="display:none!important">'
    )
    return html_text.replace(marker, replacement, 1), True


def _inject_style(html_text: str, css: str) -> str:
    if not css or f'id="{STYLE_ID}"' in html_text:
        return html_text
    head_close = re.search(r"</head\s*>", html_text, flags=re.IGNORECASE)
    if head_close is None:
        return css + html_text
    return html_text[: head_close.start()] + css + html_text[head_close.start() :]


def _inject_after_body(html_text: str, fragment_html: str) -> str:
    body = re.search(r"<body\b[^>]*>", html_text, flags=re.IGNORECASE)
    if body is None:
        raise RuntimeError("classic HTML is missing an opening body element")
    return html_text[: body.end()] + fragment_html + html_text[body.end() :]


def inject(classic_html: str, *, state: dict, language: str, feature_value: str | None = None, render_mode: str = "browser") -> InjectionResult:
    try:
        mode = parse_feature_value(feature_value)
    except Exception as exc:
        return InjectionResult(classic_html, "fallback", f"invalid_feature_value:{type(exc).__name__}", str(feature_value), classic_html.count(FRONT_PAGE_MARKER), False)
    if mode == "disabled":
        return InjectionResult(classic_html, "disabled", "feature_disabled", mode, classic_html.count(FRONT_PAGE_MARKER), False)
    if FRONT_PAGE_MARKER in classic_html:
        count = classic_html.count(FRONT_PAGE_MARKER)
        return InjectionResult(
            classic_html,
            "enabled" if count == 1 else "fallback",
            "already_injected" if count == 1 else "multiple_existing_front_pages",
            mode,
            count,
            SUPPRESSED_SUMMARY_CLASS in classic_html and "display:none!important" in classic_html,
        )
    try:
        if render_mode == "email":
            fragment = CockpitFragment(css="", html=render_email_safe_front_page(state, language), language=language)
        elif render_mode == "browser":
            fragment = render_browser_fragment(state, language)
        else:
            raise ValueError("render_mode must be browser or email")
        fragment = CockpitFragment(css=fragment.css, html=_front_page_precision(fragment.html, state, language), language=language)
        updated, suppressed = _suppress_first_investor_summary(classic_html)
        updated = _inject_style(updated, fragment.css)
        updated = _inject_after_body(updated, fragment.html)
        count = updated.count(FRONT_PAGE_MARKER)
        if count != 1:
            raise RuntimeError("front-page count is not exactly one after injection")
        return InjectionResult(updated, "enabled", "front_page_injected", mode, count, suppressed)
    except Exception as exc:
        return InjectionResult(classic_html, "fallback", f"render_or_injection_failure:{type(exc).__name__}:{exc}", mode, classic_html.count(FRONT_PAGE_MARKER), False)


def render_preview(*, state_path: Path, classic_html_path: Path, output_html_path: Path, language: str, feature_value: str, render_mode: str, output_pdf_path: Path | None = None, classic_pdf_path: Path | None = None) -> InjectionResult:
    state = json.loads(state_path.read_text(encoding="utf-8"))
    classic = classic_html_path.read_text(encoding="utf-8")
    result = inject(classic, state=state, language=language, feature_value=feature_value, render_mode=render_mode)
    output_html_path.parent.mkdir(parents=True, exist_ok=True)
    output_html_path.write_text(result.html, encoding="utf-8")
    if output_pdf_path is not None:
        output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
        if result.status == "disabled" and classic_pdf_path is not None:
            shutil.copyfile(classic_pdf_path, output_pdf_path)
        else:
            HTML(string=result.html, base_url=str(classic_html_path.parent.resolve())).write_pdf(str(output_pdf_path))
        if not output_pdf_path.exists() or output_pdf_path.stat().st_size <= 0:
            raise RuntimeError("preview PDF was not created")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Render an isolated additive Weekly ETF EU cockpit preview.")
    parser.add_argument("--state", required=True)
    parser.add_argument("--classic-html", required=True)
    parser.add_argument("--classic-pdf")
    parser.add_argument("--output-html", required=True)
    parser.add_argument("--output-pdf")
    parser.add_argument("--language", choices=["nl", "en"], required=True)
    parser.add_argument("--feature", choices=["disabled", "enabled"], required=True)
    parser.add_argument("--render-mode", choices=["browser", "email"], default="browser")
    args = parser.parse_args()
    result = render_preview(
        state_path=Path(args.state),
        classic_html_path=Path(args.classic_html),
        classic_pdf_path=Path(args.classic_pdf) if args.classic_pdf else None,
        output_html_path=Path(args.output_html),
        output_pdf_path=Path(args.output_pdf) if args.output_pdf else None,
        language=args.language,
        feature_value=args.feature,
        render_mode=args.render_mode,
    )
    print(
        "ETF_EU_COCKPIT_PREVIEW_OK"
        f" | status={result.status} | language={args.language} | render_mode={args.render_mode}"
        f" | front_pages={result.front_page_count} | summary_suppressed={result.investor_summary_suppressed}"
    )
    if args.feature == "enabled" and result.status != "enabled":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
