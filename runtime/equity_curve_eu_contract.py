from __future__ import annotations

import html
from datetime import datetime
from typing import Any, Callable


EquityPoint = tuple[str, float]


def _points_from_state(state: dict[str, Any]) -> list[EquityPoint]:
    curve = state.get("equity_curve") if isinstance(state.get("equity_curve"), dict) else {}
    points: list[EquityPoint] = []
    for row in curve.get("points") or []:
        if not isinstance(row, dict):
            continue
        try:
            points.append((str(row.get("date")), float(row.get("nav_eur"))))
        except (TypeError, ValueError):
            continue
    return points


def _select_tick_indices(
    parsed: list[tuple[datetime, float]],
    sx: Callable[[datetime], float],
    *,
    min_gap_px: float = 110.0,
) -> list[int]:
    """Keep representative ticks while preventing adjacent date-label collisions."""
    if len(parsed) <= 2:
        return list(range(len(parsed)))

    candidates = sorted({0, len(parsed) // 3, (2 * len(parsed)) // 3, len(parsed) - 1})
    first = candidates[0]
    last = candidates[-1]
    selected = [first]

    for idx in candidates[1:-1]:
        x = sx(parsed[idx][0])
        if x - sx(parsed[selected[-1]][0]) < min_gap_px:
            continue
        if sx(parsed[last][0]) - x < min_gap_px:
            continue
        selected.append(idx)

    if last != selected[-1]:
        selected.append(last)
    return selected


def render_equity_curve_svg(state: dict[str, Any], *, language: str = "nl") -> str:
    curve = state.get("equity_curve") if isinstance(state.get("equity_curve"), dict) else {}
    if curve.get("show_chart") is not True:
        return ""
    points = _points_from_state(state)
    if len(points) < 2:
        return ""

    parsed = [(datetime.strptime(date_str, "%Y-%m-%d"), float(value)) for date_str, value in points]
    min_x = min(date.toordinal() for date, _ in parsed)
    max_x = max(date.toordinal() for date, _ in parsed)
    min_y = min(value for _, value in parsed)
    max_y = max(value for _, value in parsed)
    x_span = max(max_x - min_x, 1)
    y_span = max(max_y - min_y, 1.0)
    pad_y = y_span * 0.08
    min_y -= pad_y
    max_y += pad_y
    y_span = max(max_y - min_y, 1.0)

    width = 920
    height = 390
    left = 88
    right = 30
    top = 54
    bottom = 60
    plot_w = width - left - right
    plot_h = height - top - bottom

    def sx(value: datetime) -> float:
        return left + ((value.toordinal() - min_x) / x_span) * plot_w

    def sy(value: float) -> float:
        return top + (1.0 - ((value - min_y) / y_span)) * plot_h

    coords = [(sx(date), sy(value)) for date, value in parsed]
    path_d = " ".join(("M" if idx == 0 else "L") + f" {x:.2f} {y:.2f}" for idx, (x, y) in enumerate(coords))
    is_nl = language.lower().startswith("nl")
    title = "Portefeuillecurve (EUR)" if is_nl else "Portfolio curve (EUR)"
    y_label = "Portefeuillewaarde (EUR)" if is_nl else "Portfolio value (EUR)"
    x_label = "Datum" if is_nl else "Date"

    grid: list[str] = []
    for idx in range(5):
        value = min_y + (y_span * idx / 4)
        y = sy(value)
        label = f"{value:,.0f}".replace(",", "." if is_nl else ",")
        grid.append(
            f'<line x1="{left}" y1="{y:.2f}" x2="{width-right}" y2="{y:.2f}" stroke="#d7dde1" stroke-width="1" />'
            f'<text x="{left-12}" y="{y+5:.2f}" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#4d5b65">{html.escape(label)}</text>'
        )

    tick_indices = _select_tick_indices(parsed, sx)
    ticks: list[str] = []
    for idx in tick_indices:
        point_date, _ = parsed[idx]
        x = sx(point_date)
        label = point_date.strftime("%d-%m-%Y" if is_nl else "%Y-%m-%d")
        anchor = "start" if idx == 0 else ("end" if idx == len(parsed) - 1 else "middle")
        ticks.append(
            f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{height-bottom}" stroke="#e8ecef" stroke-width="1" />'
            f'<text x="{x:.2f}" y="{height-bottom+24}" text-anchor="{anchor}" font-family="Arial, sans-serif" font-size="12" fill="#4d5b65">{html.escape(label)}</text>'
        )

    circles = "".join(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4.8" fill="#2A5384" />' for x, y in coords)
    return f"""
<div class="equity-curve-block">
<svg class="equity-curve-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid meet">
  <rect x="0" y="0" width="{width}" height="{height}" rx="14" fill="#ffffff" />
  <text x="{width/2:.2f}" y="31" text-anchor="middle" font-family="Georgia, serif" font-size="21" font-weight="700" fill="#2B3742">{html.escape(title)}</text>
  {''.join(grid)}
  {''.join(ticks)}
  <rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#667783" stroke-width="1.2" />
  <path d="{path_d}" fill="none" stroke="#2A5384" stroke-width="4" stroke-linejoin="round" stroke-linecap="round" />
  {circles}
  <text x="{width/2:.2f}" y="{height-10}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#4d5b65">{html.escape(x_label)}</text>
  <text transform="translate(20 {height/2:.2f}) rotate(-90)" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#4d5b65">{html.escape(y_label)}</text>
</svg>
</div>
""".strip()


def validate_equity_curve_contract(state: dict[str, Any], rendered_html: str) -> list[str]:
    blockers: list[str] = []
    curve = state.get("equity_curve") if isinstance(state.get("equity_curve"), dict) else {}
    show_chart = curve.get("show_chart") is True
    has_svg = "class=\"equity-curve-svg\"" in rendered_html
    if show_chart and not has_svg:
        blockers.append("equity curve should be visible but SVG is missing")
    if not show_chart and has_svg:
        blockers.append("equity curve SVG is visible despite cash-only/insufficient history rule")
    if show_chart and curve.get("latest_nav_matches_state") is not True:
        blockers.append("latest equity-curve point does not reconcile to current NAV")
    return blockers
