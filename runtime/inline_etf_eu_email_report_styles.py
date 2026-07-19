from __future__ import annotations

from html import escape
from html.parser import HTMLParser

MARKER_ATTRIBUTE = "data-etf-eu-email-inline-styled"
COCKPIT_CLASS = "etf-eu-cockpit-page"
VOID_TAGS = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"})


CLASS_STYLES: dict[str, dict[str, str]] = {
    "hero": {"background": "#607887", "color": "#FBFAF7", "padding": "17px 20px", "border-radius": "12px 12px 0 0", "margin": "0"},
    "hero-row": {"display": "table", "width": "100%", "table-layout": "fixed"},
    "masthead": {"font-family": "Georgia,Times New Roman,serif", "font-size": "28px", "font-weight": "700", "letter-spacing": "0.04em"},
    "hero-date": {"margin-top": "3px", "font-size": "12px"},
    "hero-type": {"font-size": "16px", "font-weight": "700"},
    "hero-rule": {"height": "4px", "background": "#D4B483", "margin": "5px 0 12px", "border-radius": "99px", "font-size": "1px", "line-height": "1px"},
    "notice": {"background": "#F8F4EE", "border": "1px solid #D9D3CB", "border-radius": "9px", "padding": "8px 10px", "margin": "0 0 10px", "color": "#596872"},
    "note-box": {"background": "#F8F4EE", "border": "1px solid #D9D3CB", "border-radius": "9px", "padding": "8px 10px", "margin": "0 0 10px", "color": "#596872"},
    "inactive": {"background": "#F8F4EE", "border": "1px solid #D9D3CB", "border-radius": "9px", "padding": "8px 10px", "margin": "0 0 10px", "color": "#596872"},
    "panel": {"background": "#FCFAF7", "border": "1px solid #D9D3CB", "border-radius": "11px", "padding": "11px 13px", "margin-bottom": "10px"},
    "section-head": {"display": "table", "width": "100%", "border-bottom": "1px solid #DDD7CE", "padding-bottom": "6px", "margin-bottom": "8px"},
    "badge": {"display": "inline-block", "width": "28px", "height": "28px", "line-height": "28px", "border-radius": "50%", "background": "#2A5384", "color": "#FFFFFF", "text-align": "center", "vertical-align": "middle", "font-weight": "700"},
    "section-title": {"display": "inline-block", "vertical-align": "middle", "padding-left": "9px", "color": "#6B7882", "font-size": "13px", "font-weight": "700", "letter-spacing": "0.06em", "text-transform": "uppercase"},
    "takeaway": {"background": "#F4EEE4", "border": "1px solid #E7D7BB", "border-radius": "8px", "padding": "8px 10px"},
    "wide-table": {"font-size": "10px"},
    "pricing-table": {"font-size": "9px", "table-layout": "fixed"},
    "summary-table": {"width": "72%"},
    "funded-position-table": {"table-layout": "fixed", "font-size": "9px"},
    "funnel-strip": {"display": "block", "width": "100%", "margin": "0 0 11px"},
    "funnel-card": {"display": "inline-block", "width": "18%", "min-width": "88px", "background": "#FCFAF7", "border": "1px solid #D9D3CB", "border-radius": "9px", "padding": "9px 6px", "margin": "0 1% 5px 0", "vertical-align": "top", "text-align": "center"},
    "funnel-value": {"font-family": "Georgia,Times New Roman,serif", "color": "#2A5384", "font-size": "22px", "font-weight": "700"},
    "funnel-label": {"font-size": "10px", "color": "#6B7882", "font-weight": "700", "text-transform": "uppercase", "letter-spacing": "0.05em"},
    "funded-identity-strip": {"margin": "0 0 8px", "padding": "7px 9px", "border": "1px solid #C9D2D8", "border-radius": "7px", "background": "#F4F7F8", "font-size": "11px", "line-height": "1.35"},
    "funded-identity-item": {"white-space": "nowrap"},
    "equity-curve-block": {"width": "100%", "margin-bottom": "8px"},
    "equity-curve-svg": {"display": "block", "width": "100%", "height": "auto"},
}

TAG_STYLES: dict[str, dict[str, str]] = {
    "body": {"margin": "0", "background": "#F6F2EC", "color": "#2B3742", "font-family": "Arial,Helvetica,sans-serif", "font-size": "13px", "line-height": "1.4"},
    "main": {"display": "block", "width": "100%", "max-width": "780px", "margin": "0 auto"},
    "ul": {"margin": "0 0 8px 18px", "padding": "0"},
    "ol": {"margin": "0 0 8px 18px", "padding": "0"},
    "li": {"margin-bottom": "4px"},
    "table": {"width": "100%", "border-collapse": "collapse", "margin": "5px 0 8px", "font-size": "11px"},
    "th": {"border": "1px solid #D8D5CE", "padding": "5px", "vertical-align": "top", "overflow-wrap": "anywhere", "background": "#F1EBDD", "text-align": "left", "font-weight": "700"},
    "td": {"border": "1px solid #D8D5CE", "padding": "5px", "vertical-align": "top", "overflow-wrap": "anywhere"},
}


def _parse_style(raw: str | None) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in str(raw or "").split(";"):
        if ":" not in item:
            continue
        key, value = item.split(":", 1)
        if key.strip() and value.strip():
            result[key.strip()] = value.strip()
    return result


def _merge_style(raw: str | None, additions: dict[str, str]) -> str:
    styles = _parse_style(raw)
    for key, value in additions.items():
        if key not in styles:
            styles[key] = value
    return ";".join(f"{key}:{value}" for key, value in styles.items())


def _attribute(attrs: list[tuple[str, str | None]], name: str) -> str | None:
    for key, value in attrs:
        if key == name:
            return value
    return None


def _set_attribute(attrs: list[tuple[str, str | None]], name: str, value: str) -> list[tuple[str, str | None]]:
    updated = list(attrs)
    for index, (key, _) in enumerate(updated):
        if key == name:
            updated[index] = (name, value)
            return updated
    updated.append((name, value))
    return updated


def _serialize_attrs(attrs: list[tuple[str, str | None]]) -> str:
    parts: list[str] = []
    for key, value in attrs:
        if value is None:
            parts.append(key)
        else:
            parts.append(f'{key}="{escape(value, quote=True)}"')
    return (" " + " ".join(parts)) if parts else ""


class _EmailStyleInliner(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.output: list[str] = []
        self.stack: list[dict[str, object]] = []
        self.html_seen = False

    def _start(self, tag: str, attrs: list[tuple[str, str | None]], self_closing: bool) -> None:
        classes = set(str(_attribute(attrs, "class") or "").split())
        parent = self.stack[-1] if self.stack else None
        parent_classes = set(parent.get("classes", set())) if parent else set()
        in_cockpit = bool(parent and parent.get("in_cockpit")) or COCKPIT_CLASS in classes
        child_index = int(parent.get("child_count", 0)) if parent else 0
        if parent is not None:
            parent["child_count"] = child_index + 1

        if tag == "html":
            attrs = _set_attribute(attrs, MARKER_ATTRIBUTE, "true")
            self.html_seen = True

        additions: dict[str, str] = {}
        if not in_cockpit:
            additions.update(TAG_STYLES.get(tag, {}))
            for class_name in classes:
                additions.update(CLASS_STYLES.get(class_name, {}))
            if {"freshness", "warning"}.issubset(classes):
                additions.update({"background": "#FFF4DF", "border": "1px solid #E6C98C", "color": "#6C5423", "border-radius": "8px", "padding": "8px 10px", "margin-bottom": "8px", "font-weight": "700"})
            if "hero-row" in parent_classes and tag == "div":
                additions.update({"display": "table-cell", "vertical-align": "middle", "width": "70%" if child_index == 0 else "30%"})
                if child_index > 0:
                    additions["text-align"] = "right"
            if tag in {"td", "th"} and parent and parent.get("row_even"):
                additions.setdefault("background", "#FEFCF9")

        if additions:
            attrs = _set_attribute(attrs, "style", _merge_style(_attribute(attrs, "style"), additions))

        self.output.append(f"<{tag}{_serialize_attrs(attrs)}{' /' if self_closing else ''}>")
        if not self_closing and tag not in VOID_TAGS:
            row_even = False
            if tag == "tr" and parent and parent.get("tag") == "tbody":
                row_even = (child_index + 1) % 2 == 0
            self.stack.append({
                "tag": tag,
                "classes": classes,
                "in_cockpit": in_cockpit,
                "child_count": 0,
                "row_even": row_even,
            })

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._start(tag, attrs, False)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._start(tag, attrs, True)

    def handle_endtag(self, tag: str) -> None:
        self.output.append(f"</{tag}>")
        if self.stack:
            self.stack.pop()

    def handle_data(self, data: str) -> None:
        self.output.append(data)

    def handle_entityref(self, name: str) -> None:
        self.output.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.output.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        self.output.append(f"<!--{data}-->")

    def handle_decl(self, decl: str) -> None:
        self.output.append(f"<!{decl}>")

    def handle_pi(self, data: str) -> None:
        self.output.append(f"<?{data}>")

    def unknown_decl(self, data: str) -> None:
        self.output.append(f"<![{data}]>")


def inline_email_report_styles(html_text: str) -> str:
    """Inline the established EU report visual contract without external packages."""

    parser = _EmailStyleInliner()
    parser.feed(html_text)
    parser.close()
    if not parser.html_seen:
        raise RuntimeError("ETF EU email inliner requires an html element")
    return "".join(parser.output)
