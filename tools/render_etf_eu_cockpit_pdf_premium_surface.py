from __future__ import annotations

import textwrap
import unicodedata
from pathlib import Path

RUN_ID = "20260618_000000"
TARGET = Path("output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf")
ORIGINAL_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf")
LAYOUT_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_mvp_layout_20260618_000000.pdf")
PLAN_MD = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_plan_20260618_000000.md")
PLAN_JSON = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_plan_20260618_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_surface_notes_20260618_000000.md")

AUTHORITY_MARKERS = [
    "delivery_authorization_decision=remain_blocked",
    "production_delivery=false",
    "portfolio_mutation=false",
    "candidate_promotion=false",
    "funding_authority=false",
    "valuation_grade=false",
]

PROXY_MARKERS = [
    "SPY=research_proxy_only",
    "SMH=research_proxy_only_and_ambiguous_as_pricing_symbol",
    "GLD=research_proxy_only_not_eu_holding",
    "PAVE=research_proxy_only_not_eu_holding",
]


def _safe_text(value: str) -> str:
    replacements = {"—": "-", "–": "-", "’": "'", "“": '"', "”": '"', "€": "EUR"}
    for source, target in replacements.items():
        value = value.replace(source, target)
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")


def _pdf_escape(value: str) -> str:
    return _safe_text(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _require(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"required source missing: {path}")


def _wrap(value: str, width: int = 78) -> list[str]:
    return textwrap.wrap(_safe_text(value), width=width) or [""]


def _text(text: str = "", size: int = 10, font: str = "F1", x: int = 44, gap: int | None = None) -> dict[str, object]:
    return {"kind": "text", "text": _safe_text(text), "size": size, "font": font, "x": x, "gap": gap or max(size + 5, 12)}


def _rect(x: int, y: int, w: int, h: int, label: str = "") -> dict[str, object]:
    return {"kind": "rect", "x": x, "y": y, "w": w, "h": h, "label": _safe_text(label)}


def _title(text: str) -> dict[str, object]:
    return _text(text, size=19, font="F2", x=44, gap=26)


def _section(text: str) -> dict[str, object]:
    return _text(text, size=13, font="F2", x=44, gap=19)


def _badge(text: str, x: int = 54) -> dict[str, object]:
    return _text(f"[ {text} ]", size=9, font="F3", x=x, gap=13)


def _marker(text: str, x: int = 60) -> dict[str, object]:
    return _text(text, size=8, font="F3", x=x, gap=11)


def _bullet(text: str, x: int = 58) -> list[dict[str, object]]:
    lines: list[dict[str, object]] = []
    wrapped = _wrap(text, width=74)
    for index, line in enumerate(wrapped):
        prefix = "- " if index == 0 else "  "
        lines.append(_text(prefix + line, size=9, font="F1", x=x, gap=12))
    return lines


def _card(title: str, facts: list[str], x: int = 54) -> list[dict[str, object]]:
    lines: list[dict[str, object]] = [_text(title, size=11, font="F2", x=x, gap=15)]
    for fact in facts:
        lines.append(_text(fact, size=8, font="F3", x=x + 12, gap=11))
    lines.append(_text("", size=4, gap=7))
    return lines


def _page_footer(page_number: int) -> list[dict[str, object]]:
    return [
        _text(f"WP15F premium surface - proof-of-concept / review-only - page {page_number}", size=8, font="F1", x=44, gap=10),
    ]


def _build_pages() -> list[list[dict[str, object]]]:
    for path in [ORIGINAL_PDF, LAYOUT_PDF, PLAN_MD, PLAN_JSON]:
        _require(path)
    if not ORIGINAL_PDF.read_bytes().startswith(b"%PDF"):
        raise ValueError(f"invalid original PDF header: {ORIGINAL_PDF}")
    if not LAYOUT_PDF.read_bytes().startswith(b"%PDF"):
        raise ValueError(f"invalid layout PDF header: {LAYOUT_PDF}")

    page1 = [
        _title("ETF EU Cockpit - Premium PDF Surface"),
        _badge("proof-of-concept / review-only"),
        _marker("premium_surface_page=executive_cockpit_cover"),
        _marker(f"run_id={RUN_ID}"),
        *_rect_block("Boundary badge block", AUTHORITY_MARKERS),
        _section("Dutch-first executive conclusion"),
        *_bullet("De cockpit is leesbaarder en premiumer gemaakt, maar blijft review-only: geen delivery, geen portfolio-mutatie en geen investeringsautoriteit."),
        _section("Compact summary"),
        *_bullet("Bruikbaar als reviewbewijs: IE00B5BMR087 met CSPX.L en SXR8.DE."),
        *_bullet("Geblokkeerd: Gold/ETC policy_blocked en infrastructure identity_incomplete."),
        *_bullet("Te verifieren: semiconductor UCITS pricing line blijft pricing_symbol_ambiguous."),
    ]

    page2 = [
        _title("Decision cockpit"),
        _marker("premium_surface_page=decision_cockpit"),
        *_card(
            "Review-only usable baseline",
            [
                "candidate=iShares Core S&P 500 UCITS ETF USD Acc",
                "ISIN=IE00B5BMR087",
                "pricing_symbols=CSPX.L,SXR8.DE",
                "pricing_evidence_status=usable_for_review_only",
                "research_proxy=SPY",
            ],
        ),
        *_card(
            "Candidate lane requiring verification",
            [
                "candidate=VanEck Semiconductor UCITS ETF",
                "ISIN=IE00BMC38736",
                "status=pricing_symbol_ambiguous",
                "pricing_symbol=pending_verification",
                "research_proxy=SMH",
            ],
        ),
        *_card(
            "Blocked or incomplete lanes",
            [
                "Gold/ETC=policy_blocked",
                "Infrastructure=identity_incomplete",
                "funding_authority=false",
                "valuation_grade=false",
            ],
        ),
    ]

    page3 = [
        _title("UCITS evidence cockpit"),
        _marker("premium_surface_page=ucits_evidence_cockpit"),
        _marker("isin_first_identity=true"),
        *_card(
            "Evidence row - current baseline",
            [
                "ISIN=IE00B5BMR087",
                "exchange_line=CSPX.L / SXR8.DE",
                "pricing_symbol_evidence=source_evidence_available",
                "ucits_status_placeholder=true",
                "priips_kid_status_placeholder=true",
                "trading_line_status_placeholder=true",
                "next_verification_action=true",
            ],
        ),
        *_card(
            "Evidence row - pending lanes",
            [
                "IE00BMC38736=verify exchange-specific UCITS line",
                "Gold/ETC=resolve policy decision before any promotion",
                "Infrastructure=verify ISIN and issuer evidence",
            ],
        ),
    ]

    page4 = [
        _title("Research proxy separation"),
        _marker("premium_surface_page=research_proxy_separation"),
        _section("Proxy use is research-only"),
        *_bullet("U.S. proxies may support research and benchmark context only. They are not EU holdings, EU pricing lines or funding sources."),
        *_card("Proxy map", PROXY_MARKERS),
        *_card(
            "Authority status",
            [
                "pricing_authority_status=review_only_or_blocked",
                "funding_authority=false",
                "valuation_grade=false",
            ],
        ),
    ]

    page5 = [
        _title("Action and validation checklist"),
        _marker("premium_surface_page=action_and_validation_checklist"),
        *_card(
            "Checklist markers",
            [
                "review_only_usable=true",
                "must_stay_blocked=true",
                "must_verify_before_promotion=true",
                "delivery_enablement_requires_separate_authority=true",
            ],
        ),
        *_card(
            "What must remain true",
            [
                "original_pdf_mvp_preserved=true",
                "layout_pdf_preserved=true",
                "live_data_fetch_performed=false",
                "pricing_evidence_changed=false",
                "recommendation_logic_changed=false",
            ],
        ),
        *_rect_block("Final authority markers", AUTHORITY_MARKERS),
        _section("Next package"),
        _marker("selected_next_package=WP15G"),
        _marker("selected_next_package_title=ETF EU cockpit PDF premium surface closeout, no delivery"),
    ]
    return [page1, page2, page3, page4, page5]


def _rect_block(title: str, markers: list[str]) -> list[dict[str, object]]:
    lines: list[dict[str, object]] = [_section(title)]
    for marker in markers:
        lines.append(_badge(marker, x=58))
    return lines


def _build_pdf_bytes(pages: list[list[dict[str, object]]]) -> bytes:
    objects: list[str | None] = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        None,
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>",
    ]
    kids: list[str] = []
    for page_number, page_items in enumerate(pages, start=1):
        content_id = len(objects) + 1
        page_id = len(objects) + 2
        stream_lines = ["0.96 0.96 0.96 rg", "0 0 612 792 re f", "0 0 0 rg"]
        stream_lines.extend([
            "0.88 0.88 0.88 rg 34 34 544 724 re f",
            "1 1 1 rg 38 38 536 716 re f",
            "0 0 0 rg",
        ])
        y = 742
        for item in page_items:
            if item["kind"] == "rect":
                stream_lines.append(f"0.92 0.92 0.92 rg {item['x']} {item['y']} {item['w']} {item['h']} re f 0 0 0 rg")
                continue
            text = str(item["text"])
            size = int(item["size"])
            font = str(item["font"])
            x = int(item["x"])
            gap = int(item["gap"])
            if text:
                stream_lines.append("BT")
                stream_lines.append(f"/{font} {size} Tf")
                stream_lines.append(f"1 0 0 1 {x} {y} Tm")
                stream_lines.append(f"({_pdf_escape(text)}) Tj")
                stream_lines.append("ET")
            y -= gap
        footer_y = 52
        for footer in _page_footer(page_number):
            stream_lines.append("BT")
            stream_lines.append(f"/{footer['font']} {footer['size']} Tf")
            stream_lines.append(f"1 0 0 1 {footer['x']} {footer_y} Tm")
            stream_lines.append(f"({_pdf_escape(str(footer['text']))}) Tj")
            stream_lines.append("ET")
            footer_y -= 10
        stream = "\n".join(stream_lines)
        objects.append(f"<< /Length {len(stream.encode('ascii'))} >>\nstream\n{stream}\nendstream")
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R >> >> /Contents {content_id} 0 R >>"
        )
        kids.append(f"{page_id} 0 R")
    objects[1] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(kids)} >>"

    content = b"%PDF-1.4\n%WP15F-PREMIUM-SURFACE\n"
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(content))
        content += f"{index} 0 obj\n{obj}\nendobj\n".encode("ascii")
    xref_offset = len(content)
    xref = f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
    for offset in offsets[1:]:
        xref += f"{offset:010d} 00000 n \n"
    trailer = f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n"
    return content + (xref + trailer).encode("ascii")


def render_premium_surface() -> Path:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(_build_pdf_bytes(_build_pages()))
    print(f"ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_RENDERED | output={TARGET}")
    return TARGET


def main() -> None:
    render_premium_surface()


if __name__ == "__main__":
    main()
