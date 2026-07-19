from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from bs4 import BeautifulSoup, Tag

MARKER_ATTRIBUTE = "data-etf-eu-email-inline-styled"
COCKPIT_CLASS = "etf-eu-cockpit-page"


def _parse_style(raw: str | None) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in str(raw or "").split(";"):
        if ":" not in item:
            continue
        key, value = item.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key and value:
            result[key] = value
    return result


def _merge_style(tag: Tag, **items: str) -> None:
    style = _parse_style(tag.get("style"))
    for key, value in items.items():
        css_key = key.replace("_", "-")
        if value and css_key not in style:
            style[css_key] = value
    tag["style"] = ";".join(f"{key}:{value}" for key, value in style.items())


def _inside_cockpit(tag: Tag) -> bool:
    current: Tag | None = tag
    while current is not None:
        if COCKPIT_CLASS in (current.get("class") or []):
            return True
        parent = current.parent
        current = parent if isinstance(parent, Tag) else None
    return False


def _outside(tags: Iterable[Tag]) -> list[Tag]:
    return [tag for tag in tags if not _inside_cockpit(tag)]


def inline_email_report_styles(html_text: str) -> str:
    """Inline the established EU report visual contract for mail clients.

    The function does not redesign or restructure the report. It maps existing
    renderer classes to deterministic inline declarations while leaving the
    already-inline cockpit fragment untouched.
    """

    soup = BeautifulSoup(html_text, "html.parser")
    html_tag = soup.find("html")
    if html_tag is None:
        raise RuntimeError("ETF EU email inliner requires an html element")
    html_tag[MARKER_ATTRIBUTE] = "true"

    body = soup.find("body")
    if isinstance(body, Tag):
        _merge_style(
            body,
            margin="0",
            background="#F6F2EC",
            color="#2B3742",
            font_family="Arial,Helvetica,sans-serif",
            font_size="13px",
            line_height="1.4",
        )
    main = soup.find("main")
    if isinstance(main, Tag):
        _merge_style(main, display="block", width="100%", max_width="780px", margin="0 auto")

    for tag in _outside(soup.select(".hero")):
        _merge_style(tag, background="#607887", color="#FBFAF7", padding="17px 20px", border_radius="12px 12px 0 0", margin="0")
    for tag in _outside(soup.select(".hero-row")):
        _merge_style(tag, display="table", width="100%", table_layout="fixed")
        children = [child for child in tag.find_all(recursive=False) if isinstance(child, Tag)]
        for index, child in enumerate(children):
            _merge_style(child, display="table-cell", vertical_align="middle", width="70%" if index == 0 else "30%")
            if index == len(children) - 1:
                _merge_style(child, text_align="right")
    for tag in _outside(soup.select(".masthead")):
        _merge_style(tag, font_family="Georgia,Times New Roman,serif", font_size="28px", font_weight="700", letter_spacing="0.04em")
    for tag in _outside(soup.select(".hero-date")):
        _merge_style(tag, margin_top="3px", font_size="12px")
    for tag in _outside(soup.select(".hero-type")):
        _merge_style(tag, font_size="16px", font_weight="700")
    for tag in _outside(soup.select(".hero-rule")):
        _merge_style(tag, height="4px", background="#D4B483", margin="5px 0 12px", border_radius="99px", font_size="1px", line_height="1px")

    for selector in (".notice", ".note-box", ".inactive"):
        for tag in _outside(soup.select(selector)):
            _merge_style(tag, background="#F8F4EE", border="1px solid #D9D3CB", border_radius="9px", padding="8px 10px", margin="0 0 10px", color="#596872")

    for tag in _outside(soup.select(".panel")):
        _merge_style(tag, background="#FCFAF7", border="1px solid #D9D3CB", border_radius="11px", padding="11px 13px", margin_bottom="10px")
    for tag in _outside(soup.select(".section-head")):
        _merge_style(tag, display="table", width="100%", border_bottom="1px solid #DDD7CE", padding_bottom="6px", margin_bottom="8px")
    for tag in _outside(soup.select(".badge")):
        _merge_style(tag, display="inline-block", width="28px", height="28px", line_height="28px", border_radius="50%", background="#2A5384", color="#FFFFFF", text_align="center", vertical_align="middle", font_weight="700")
    for tag in _outside(soup.select(".section-title")):
        _merge_style(tag, display="inline-block", vertical_align="middle", padding_left="9px", color="#6B7882", font_size="13px", font_weight="700", letter_spacing="0.06em", text_transform="uppercase")

    for tag in _outside(soup.find_all(["ul", "ol"])):
        _merge_style(tag, margin="0 0 8px 18px", padding="0")
    for tag in _outside(soup.find_all("li")):
        _merge_style(tag, margin_bottom="4px")
    for tag in _outside(soup.select(".takeaway")):
        _merge_style(tag, background="#F4EEE4", border="1px solid #E7D7BB", border_radius="8px", padding="8px 10px")
    for tag in _outside(soup.select(".freshness.warning")):
        _merge_style(tag, background="#FFF4DF", border="1px solid #E6C98C", color="#6C5423", border_radius="8px", padding="8px 10px", margin_bottom="8px", font_weight="700")

    for tag in _outside(soup.find_all("table")):
        _merge_style(tag, width="100%", border_collapse="collapse", margin="5px 0 8px", font_size="11px")
    for tag in _outside(soup.find_all(["th", "td"])):
        _merge_style(tag, border="1px solid #D8D5CE", padding="5px", vertical_align="top", overflow_wrap="anywhere")
    for tag in _outside(soup.find_all("th")):
        _merge_style(tag, background="#F1EBDD", text_align="left", font_weight="700")
    for table in _outside(soup.find_all("table")):
        body_rows = table.select("tbody > tr")
        for index, row in enumerate(body_rows, start=1):
            if index % 2 == 0:
                for cell in row.find_all(["td", "th"], recursive=False):
                    _merge_style(cell, background="#FEFCF9")
    for tag in _outside(soup.select(".wide-table")):
        _merge_style(tag, font_size="10px")
    for tag in _outside(soup.select(".pricing-table")):
        _merge_style(tag, font_size="9px", table_layout="fixed")
    for tag in _outside(soup.select(".summary-table")):
        _merge_style(tag, width="72%")
    for tag in _outside(soup.select(".funded-position-table")):
        _merge_style(tag, table_layout="fixed", font_size="9px")

    for tag in _outside(soup.select(".funnel-strip")):
        _merge_style(tag, display="block", width="100%", margin="0 0 11px")
    for tag in _outside(soup.select(".funnel-card")):
        _merge_style(tag, display="inline-block", width="18%", min_width="88px", background="#FCFAF7", border="1px solid #D9D3CB", border_radius="9px", padding="9px 6px", margin="0 1% 5px 0", vertical_align="top", text_align="center")
    for tag in _outside(soup.select(".funnel-value")):
        _merge_style(tag, font_family="Georgia,Times New Roman,serif", color="#2A5384", font_size="22px", font_weight="700")
    for tag in _outside(soup.select(".funnel-label")):
        _merge_style(tag, font_size="10px", color="#6B7882", font_weight="700", text_transform="uppercase", letter_spacing="0.05em")

    for tag in _outside(soup.select(".funded-identity-strip")):
        _merge_style(tag, margin="0 0 8px", padding="7px 9px", border="1px solid #C9D2D8", border_radius="7px", background="#F4F7F8", font_size="11px", line_height="1.35")
    for tag in _outside(soup.select(".funded-identity-item")):
        _merge_style(tag, white_space="nowrap")
    for tag in _outside(soup.select(".equity-curve-block")):
        _merge_style(tag, width="100%", margin_bottom="8px")
    for tag in _outside(soup.select(".equity-curve-svg")):
        _merge_style(tag, display="block", width="100%", height="auto")

    return str(soup)
