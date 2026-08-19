from __future__ import annotations

import base64
import re
from pathlib import Path
from typing import Any

from runtime.equity_curve_png_contract import render_equity_curve_png


class StandaloneHtmlEquityError(RuntimeError):
    pass


EQUITY_SVG_BLOCK_RE = re.compile(
    r'<div\b[^>]*class=["\'][^"\']*\bequity-curve-block\b[^"\']*["\'][^>]*>\s*'
    r'<svg\b[^>]*class=["\'][^"\']*\bequity-curve-svg\b[^"\']*["\'][^>]*>.*?</svg>\s*'
    r'</div>',
    flags=re.IGNORECASE | re.DOTALL,
)
EQUITY_SVG_ELEMENT_RE = re.compile(
    r'<svg\b[^>]*class=["\'][^"\']*\bequity-curve-svg\b[^"\']*["\'][^>]*>',
    flags=re.IGNORECASE,
)
EQUITY_DATA_URI_RE = re.compile(
    r'<img\b(?=[^>]*\bclass=["\'][^"\']*\bequity-curve-image\b[^"\']*["\'])'
    r'(?=[^>]*\bsrc=["\']data:image/png;base64,[A-Za-z0-9+/=]+["\'])[^>]*>',
    flags=re.IGNORECASE,
)


def _points_from_state(state: dict[str, Any]) -> list[tuple[str, float]]:
    curve = state.get("equity_curve") if isinstance(state.get("equity_curve"), dict) else {}
    points: list[tuple[str, float]] = []
    for row in curve.get("points") or []:
        if not isinstance(row, dict):
            continue
        try:
            points.append((str(row.get("date")), float(row.get("nav_eur"))))
        except (TypeError, ValueError):
            continue
    return points


def _png_data_uri(path: Path) -> str:
    payload = path.read_bytes()
    if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
        raise StandaloneHtmlEquityError(f"Equity-curve asset is not PNG: {path}")
    return "data:image/png;base64," + base64.b64encode(payload).decode("ascii")


def materialize_standalone_equity_html(
    rendered_html: str,
    state: dict[str, Any],
    *,
    language: str,
    chart_path: Path,
) -> str:
    """Replace the renderer's inline equity SVG with the donor-standard embedded PNG."""
    curve = state.get("equity_curve") if isinstance(state.get("equity_curve"), dict) else {}
    show_chart = curve.get("show_chart") is True
    svg_matches = list(EQUITY_SVG_BLOCK_RE.finditer(rendered_html))

    if not show_chart:
        if svg_matches:
            raise StandaloneHtmlEquityError("Equity curve SVG present while state says no chart should be shown")
        return rendered_html

    points = _points_from_state(state)
    if len(points) < 2:
        raise StandaloneHtmlEquityError("Equity curve is required but fewer than two valid points are available")
    if len(svg_matches) != 1:
        raise StandaloneHtmlEquityError(
            f"Expected exactly one renderer equity SVG block before donor materialization; found {len(svg_matches)}"
        )

    render_equity_curve_png(points, chart_path, language=language)
    image_src = _png_data_uri(chart_path)
    alt = "Portefeuillecurve (EUR)" if language.lower().startswith("nl") else "Equity Curve (EUR)"
    replacement = (
        '<div class="equity-curve-block">'
        f'<img class="equity-curve-image" src="{image_src}" alt="{alt}" width="920" '
        'style="display:block;width:100%;max-width:920px;height:auto;border:0;" />'
        '</div>'
    )
    standalone = EQUITY_SVG_BLOCK_RE.sub(replacement, rendered_html, count=1)
    if EQUITY_SVG_ELEMENT_RE.search(standalone):
        raise StandaloneHtmlEquityError("Inline equity SVG remained after donor PNG materialization")
    if len(EQUITY_DATA_URI_RE.findall(standalone)) != 1:
        raise StandaloneHtmlEquityError("Standalone HTML must contain exactly one embedded equity-curve PNG")
    if standalone.count("data:image/png;base64,") != 1:
        raise StandaloneHtmlEquityError("Standalone HTML equity PNG data URI must occur exactly once")
    return standalone


def validate_standalone_html_equity(rendered_html: str, state: dict[str, Any]) -> None:
    curve = state.get("equity_curve") if isinstance(state.get("equity_curve"), dict) else {}
    show_chart = curve.get("show_chart") is True
    data_uri_count = rendered_html.count("data:image/png;base64,")
    has_equity_svg = EQUITY_SVG_ELEMENT_RE.search(rendered_html) is not None
    if show_chart and data_uri_count != 1:
        raise StandaloneHtmlEquityError(
            f"Expected one embedded equity PNG for visible curve; found {data_uri_count}"
        )
    if show_chart and has_equity_svg:
        raise StandaloneHtmlEquityError("Standalone HTML still contains inline equity SVG")
    if not show_chart and data_uri_count:
        raise StandaloneHtmlEquityError("Standalone HTML contains an equity PNG although chart is disabled")
