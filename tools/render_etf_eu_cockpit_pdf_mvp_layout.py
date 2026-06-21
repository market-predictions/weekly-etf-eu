from __future__ import annotations

import json
import textwrap
import unicodedata
from pathlib import Path

RUN_ID = "20260618_000000"
TARGET = Path("output/client_surface/weekly_etf_eu_cockpit_mvp_layout_20260618_000000.pdf")
ORIGINAL_PDF = Path("output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf")
POC_PACKAGE = Path("output/client_surface/etf_eu_cockpit_poc_package_20260618_000000.json")
PDF_CLOSEOUT = Path("output/client_surface/etf_eu_cockpit_pdf_mvp_closeout_20260618_000000.json")
DUTCH_MD = Path("output/client_surface/weekly_etf_eu_review_nl_260618_cockpit_pricing_integrated.md")
ENGLISH_MD = Path("output/client_surface/weekly_etf_eu_review_260618_cockpit_pricing_integrated.md")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_mvp_layout_notes_20260618_000000.md")
MANIFEST = Path("output/client_surface/etf_eu_cockpit_pdf_mvp_layout_manifest_20260618_000000.json")


def _safe_text(value: str) -> str:
    replacements = {
        "—": "-",
        "–": "-",
        "’": "'",
        "“": '"',
        "”": '"',
        "€": "EUR",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")


def _pdf_escape(value: str) -> str:
    return _safe_text(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _read_required(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"required source missing: {path}")
    return path.read_text(encoding="utf-8")


def _load_json(path: Path) -> dict:
    return json.loads(_read_required(path))


def _wrap(text: str, width: int = 82) -> list[str]:
    return textwrap.wrap(_safe_text(text), width=width) or [""]


def _line(text: str = "", size: int = 10, font: str = "F1", indent: int = 0) -> dict[str, object]:
    return {"text": _safe_text(text), "size": size, "font": font, "indent": indent}


def _section(title: str) -> dict[str, object]:
    return _line(title, size=14, font="F2")


def _marker(text: str) -> dict[str, object]:
    return _line(text, size=9, font="F3", indent=10)


def _table_row(label: str, value: str) -> list[dict[str, object]]:
    lines = [_line(label, size=10, font="F2", indent=8)]
    for wrapped in _wrap(value, width=76):
        lines.append(_line(wrapped, size=9, font="F1", indent=22))
    return lines


def _candidate_block(name: str, facts: list[tuple[str, str]]) -> list[dict[str, object]]:
    lines = [_line(name, size=11, font="F2", indent=6)]
    for key, value in facts:
        lines.append(_line(f"{key}: {value}", size=9, font="F3", indent=18))
    lines.append(_line("", size=7))
    return lines


def _build_pages() -> list[list[dict[str, object]]]:
    package = _load_json(POC_PACKAGE)
    closeout = _load_json(PDF_CLOSEOUT)
    _read_required(DUTCH_MD)
    _read_required(ENGLISH_MD)
    if not ORIGINAL_PDF.exists():
        raise FileNotFoundError(f"original PDF missing: {ORIGINAL_PDF}")

    baseline = package["current_pricing_baseline"]
    blockers = package["blocked_or_incomplete_lanes"]
    proxies = package["research_proxy_map"]

    page1 = [
        _line("ETF EU Cockpit - PDF MVP layout iteration", size=19, font="F2"),
        _line("Proof-of-concept / review-only / no delivery", size=12, font="F2"),
        _line(f"run_id={RUN_ID}", size=10, font="F3"),
        _line(""),
        _section("Boundary badge block"),
        _marker(f"delivery_authorization_decision={closeout['delivery_authorization_decision']}"),
        _marker(f"production_delivery={str(closeout['production_delivery']).lower()}"),
        _marker(f"portfolio_mutation={str(closeout['portfolio_mutation']).lower()}"),
        _marker(f"candidate_promotion={str(closeout['candidate_promotion']).lower()}"),
        _marker(f"funding_authority={str(closeout['funding_authority']).lower()}"),
        _marker(f"valuation_grade={str(closeout['valuation_grade']).lower()}"),
        _line(""),
        _section("Dutch-first conclusion"),
        _line("Eerste PDF-MVP is technisch werkend; deze iteratie verbetert leesbaarheid en presentatie", size=10),
        _line("zonder delivery of beleggingsautoriteit te wijzigen.", size=10),
        _line(""),
        _section("What improved versus WP15A"),
        *_table_row("Structure", "Four clear pages: cover, UCITS universe, pricing boundary, research proxy separation."),
        *_table_row("Readability", "Larger headings, explicit sections, more whitespace and grouped candidate facts."),
        *_table_row("Dutch-first", "The first reader-facing conclusion and cockpit table are Dutch-first."),
    ]

    page2 = [
        _line("Dutch-first cockpit table", size=17, font="F2"),
        _line("Zichtbaar UCITS-universum - gestructureerd voor PDF-lezen", size=11, font="F2"),
        _line(""),
        *_candidate_block(
            "iShares Core S&P 500 UCITS ETF USD (Acc)",
            [
                ("ISIN", baseline["isin"]),
                ("pricing_line_status", baseline["pricing_line_status"]),
                ("pricing_symbols", ", ".join(baseline["pricing_symbols"])),
                ("pricing_evidence_status", baseline["pricing_evidence_status"]),
                ("research_proxy", "SPY"),
                ("review_only", str(baseline["review_only"]).lower()),
            ],
        ),
        *_candidate_block(
            "VanEck Semiconductor UCITS ETF",
            [
                ("ISIN", "IE00BMC38736"),
                ("pricing_line_status", "pricing_symbol_ambiguous"),
                ("pricing_symbols", "pending_verification"),
                ("research_proxy", "SMH"),
                ("safe_for_pricing_evidence", "false"),
            ],
        ),
        *_candidate_block(
            "iShares Physical Gold ETC",
            [("ISIN", "TBD"), ("status", "policy_blocked"), ("research_proxy", "GLD"), ("safe_for_pricing_evidence", "false")],
        ),
        *_candidate_block(
            "iShares Global Infrastructure UCITS ETF",
            [("ISIN", "TBD"), ("status", "identity_incomplete"), ("research_proxy", "PAVE"), ("safe_for_pricing_evidence", "false")],
        ),
    ]

    page3 = [
        _line("Pricing boundary and blocked lanes", size=17, font="F2"),
        _line("Current usable review-only baseline", size=12, font="F2"),
        _marker(f"{baseline['isin']} / CSPX.L / SXR8.DE / usable_for_review_only"),
        _line(""),
        _section("Blocked or incomplete lanes"),
    ]
    for lane in blockers:
        if lane["isin"] == "IE00BMC38736":
            page3.append(_marker("IE00BMC38736 / SMH / pricing_symbol_ambiguous"))
        elif lane["status"] == "policy_blocked":
            page3.append(_marker("Gold/ETC / policy_blocked"))
        elif lane["status"] == "identity_incomplete":
            page3.append(_marker("Infrastructure / identity_incomplete"))
    page3.extend([
        _line(""),
        _section("Explicit boundary note"),
        _marker("No lane is valuation-grade."),
        _marker("No lane has funding authority."),
        _marker("No candidate is promoted."),
        _line(""),
        _section("Authority markers"),
        _marker("valuation_grade=false"),
        _marker("funding_authority=false"),
        _marker("candidate_promotion=false"),
    ])

    page4 = [
        _line("Research proxy separation and next step", size=17, font="F2"),
        _line("Research proxies stay separate from EU holdings and pricing authority.", size=10),
        _line(""),
        _marker(f"SPY={proxies['SPY']}"),
        _marker(f"SMH={proxies['SMH']}"),
        _marker(f"GLD={proxies['GLD']}"),
        _marker(f"PAVE={proxies['PAVE']}"),
        _line(""),
        _section("Next package"),
        _marker("selected_next_package=WP15D"),
        _marker("selected_next_package_title=ETF EU cockpit PDF MVP layout closeout, no delivery"),
        _line(""),
        _section("Operational boundary"),
        _marker("proof_of_concept_pdf_mvp=true"),
        _marker("review-only=true"),
        _marker("no_email_action_occurred=true"),
        _marker("portfolio_state_modified=false"),
        _marker("production_delivery=false"),
        _marker("portfolio_mutation=false"),
        _marker("candidate_promotion=false"),
        _marker("funding_authority=false"),
        _marker("valuation_grade=false"),
    ]
    return [page1, page2, page3, page4]


def _build_pdf_bytes(pages: list[list[dict[str, object]]]) -> bytes:
    objects: list[str | None] = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        None,
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>",
    ]
    kids: list[str] = []
    for page_number, page_lines in enumerate(pages, start=1):
        content_id = len(objects) + 1
        page_id = len(objects) + 2
        stream_lines = ["BT"]
        cursor_y = 748
        for entry in page_lines:
            text = str(entry["text"])
            size = int(entry["size"])
            font = str(entry["font"])
            indent = int(entry["indent"])
            x = 42 + indent
            if text:
                stream_lines.append(f"/{font} {size} Tf")
                stream_lines.append(f"1 0 0 1 {x} {cursor_y} Tm")
                stream_lines.append(f"({_pdf_escape(text)}) Tj")
            cursor_y -= max(size + 6, 13)
        stream_lines.append("/F1 8 Tf")
        stream_lines.append("1 0 0 1 42 30 Tm")
        stream_lines.append(f"(WP15C layout iteration - page {page_number} - proof-of-concept / review-only) Tj")
        stream_lines.append("ET")
        stream = "\n".join(stream_lines)
        objects.append(f"<< /Length {len(stream.encode('ascii'))} >>\nstream\n{stream}\nendstream")
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R >> >> /Contents {content_id} 0 R >>"
        )
        kids.append(f"{page_id} 0 R")
    objects[1] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(kids)} >>"

    content = b"%PDF-1.4\n%WP15C-LAYOUT\n"
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


def render_pdf_mvp_layout() -> Path:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(_build_pdf_bytes(_build_pages()))
    print(f"ETF_EU_COCKPIT_PDF_MVP_LAYOUT_RENDERED | output={TARGET}")
    return TARGET


def main() -> None:
    render_pdf_mvp_layout()


if __name__ == "__main__":
    main()
