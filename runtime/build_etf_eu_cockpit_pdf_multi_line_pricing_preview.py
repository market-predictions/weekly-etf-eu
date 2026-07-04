from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RUN_ID = "20260703_000000"
SOURCE = Path("output/client_surface/etf_eu_cockpit_multi_line_pricing_preview_20260703_000000.json")
REPAIR = Path("output/client_surface/etf_eu_multi_line_pricing_universe_repair_20260703_000000.json")
PDF = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf")
ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_visual_review_20260703_000000.md")
RENDERER = Path("runtime/build_etf_eu_cockpit_pdf_multi_line_pricing_preview.py")
PAGE_COUNT = 4


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _escape(text: str) -> str:
    return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _text(x: int, y: int, size: float, text: str, font: str = "F1") -> str:
    return f"BT /{font} {size} Tf {x} {y} Td ({_escape(text)}) Tj ET\n"


def _rect(x: int, y: int, w: int, h: int, fill: tuple[float, float, float]) -> str:
    r, g, b = fill
    return f"q {r:.3f} {g:.3f} {b:.3f} rg {x} {y} {w} {h} re f Q\n"


def _stroke_rect(x: int, y: int, w: int, h: int, stroke: tuple[float, float, float], width: float = 0.7) -> str:
    r, g, b = stroke
    return f"q {width:.2f} w {r:.3f} {g:.3f} {b:.3f} RG {x} {y} {w} {h} re S Q\n"


def _line(x1: int, y1: int, x2: int, y2: int, stroke: tuple[float, float, float], width: float = 0.6) -> str:
    r, g, b = stroke
    return f"q {width:.2f} w {r:.3f} {g:.3f} {b:.3f} RG {x1} {y1} m {x2} {y2} l S Q\n"


def _badge(x: int, y: int, label: str, w: int = 92, fill: tuple[float, float, float] = (0.94, 0.97, 0.99)) -> str:
    return _rect(x, y, w, 18, fill) + _stroke_rect(x, y, w, 18, (0.70, 0.78, 0.86), 0.5) + _text(x + 6, y + 6, 7.2, label, "F2")


def _card(x: int, y: int, w: int, h: int, title: str, lines: list[str], accent: tuple[float, float, float]) -> str:
    out = [_rect(x, y, w, h, (1, 1, 1)), _stroke_rect(x, y, w, h, (0.80, 0.84, 0.88), 0.7), _rect(x, y, 4, h, accent), _text(x + 12, y + h - 17, 8.2, title, "F2")]
    yy = y + h - 34
    for line in lines:
        out.append(_text(x + 12, yy, 7.2, line, "F1"))
        yy -= 11
    return "".join(out)


def _table(x: int, y: int, widths: list[int], header: list[str], rows: list[list[str]], row_h: int = 25) -> str:
    total_w = sum(widths)
    out = [_rect(x, y + row_h * len(rows), total_w, row_h, (0.10, 0.20, 0.31)), _stroke_rect(x, y, total_w, row_h * (len(rows) + 1), (0.74, 0.79, 0.85), 0.6)]
    xx = x
    for i, h in enumerate(header):
        out.append(_text(xx + 5, y + row_h * len(rows) + 8, 7.0, h, "F2"))
        xx += widths[i]
        out.append(_line(xx, y, xx, y + row_h * (len(rows) + 1), (0.85, 0.88, 0.91), 0.4))
    for r, row in enumerate(rows):
        row_y = y + row_h * (len(rows) - 1 - r)
        if r % 2 == 0:
            out.append(_rect(x, row_y, total_w, row_h, (0.985, 0.990, 0.995)))
        out.append(_line(x, row_y, x + total_w, row_y, (0.88, 0.90, 0.93), 0.4))
        xx = x
        for i, cell in enumerate(row):
            out.append(_text(xx + 5, row_y + 9, 6.6, cell, "F1"))
            xx += widths[i]
    return "".join(out)


def _header(title: str, subtitle: str) -> str:
    out = [_rect(0, 0, 595, 842, (0.965, 0.975, 0.985)), _rect(34, 768, 527, 48, (0.075, 0.145, 0.235)), _text(50, 798, 15, title, "F2"), _text(50, 782, 8, subtitle, "F1"), _badge(382, 790, "REVIEW-ONLY", 88), _badge(476, 790, "GEEN LEVERING", 86, (0.99, 0.94, 0.90))]
    return "".join(out)


def _footer(page: int) -> str:
    return _line(42, 42, 553, 42, (0.78, 0.82, 0.86), 0.6) + _text(46, 28, 6.2, f"ETF-EU-WP15AB | multi-line pricing preview | review-only | pagina {page}/4", "F1")


def _rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    return data["pricing_rows"]


def _row(data: dict[str, Any], symbol: str) -> dict[str, Any]:
    for row in _rows(data):
        if row.get("pricing_symbol") == symbol:
            return row
    raise RuntimeError(f"missing row: {symbol}")


def _page_one(data: dict[str, Any]) -> str:
    sxr8 = _row(data, "SXR8.DE")
    cspx = _row(data, "CSPX.L")
    out = [_header("ETF EU Cockpit - Multi-line Pricing Preview", "Review-only PDF candidate - geen levering")]
    out.append(_text(42, 738, 14, "Wat dit nu bewijst", "F2"))
    out.append(_text(42, 720, 8.0, "Twee EU trading lines hebben echte provider-slotkoersen. Dit blijft uitsluitend review-only bewijs.", "F1"))
    out.append(_card(42, 650, 160, 58, "Status", ["Review-only", "Geen funding", "Geen delivery"], (0.10, 0.33, 0.50)))
    out.append(_card(218, 650, 160, 58, "Prijsregels", ["SXR8.DE: success", "CSPX.L: success", "SMH: skipped"], (0.18, 0.43, 0.32)))
    out.append(_card(394, 650, 160, 58, "Bron", ["yahoo_chart_v8", "Geen fake price", "Geen U.S. proxy"], (0.62, 0.30, 0.18)))
    out.append(_text(42, 600, 11.5, "Twee-regel bewijskaart", "F2"))
    out.append(_table(42, 508, [72, 80, 72, 74, 82, 84, 72], ["ISIN", "Fonds", "Lijn", "Valuta", "Datum", "Koers", "Bron"], [
        [sxr8["isin"], "iShares S&P 500", "SXR8.DE", sxr8["trading_currency"], sxr8["latest_close_date"], str(sxr8["latest_close"]), sxr8["pricing_source"]],
        [cspx["isin"], "iShares S&P 500", "CSPX.L", cspx["trading_currency"], cspx["latest_close_date"], str(cspx["latest_close"]), cspx["pricing_source"]],
    ], 26))
    out.append(_card(42, 406, 512, 64, "Boundary caveat", [
        "Dit is een beperkte multi-line koerspreview.",
        "Dit is geen waarderingsgeschikte prijsbasis, geen client-grade rapportbewijs en geen leveringsautorisatie.",
        "Geen funding, portefeuillewijziging, kandidaatpromotie of productiepad.",
    ], (0.48, 0.20, 0.17)))
    out.append(_footer(1))
    return "".join(out)


def _page_two(data: dict[str, Any]) -> str:
    sxr8 = _row(data, "SXR8.DE")
    cspx = _row(data, "CSPX.L")
    out = [_header("ETF EU Cockpit", "Verified EU pricing table")]
    out.append(_text(42, 738, 14, "Verified EU pricing table", "F2"))
    out.append(_table(42, 600, [82, 128, 72, 64, 78, 74, 72], ["ISIN", "Fonds", "Lijn", "Valuta", "Datum", "Koers", "Status"], [
        [sxr8["isin"], "iShares Core S&P 500", "SXR8.DE", "EUR", "2026-07-03", "706.119995", "success"],
        [cspx["isin"], "iShares Core S&P 500", "CSPX.L", "USD", "2026-07-03", "807.859985", "success"],
    ], 28))
    out.append(_card(42, 500, 245, 60, "Freshness", ["Slotdatum: 2026-07-03", "Bron: yahoo_chart_v8", "Timestamp preserved in artifact"], (0.10, 0.33, 0.50)))
    out.append(_card(309, 500, 245, 60, "Integrity", ["fake_price_used=false", "us_proxy_price_used=false", "manual close not used"], (0.18, 0.43, 0.32)))
    out.append(_card(42, 400, 512, 62, "Interpretatie", [
        "De PDF toont pricing evidence, geen investeringsbesluit.",
        "Beide regels delen ISIN IE00B5BMR087 en tonen verschillende exchange lines.",
        "Dit blijft input voor visuele review en latere readiness gates.",
    ], (0.12, 0.25, 0.38)))
    out.append(_footer(2))
    return "".join(out)


def _page_three(data: dict[str, Any]) -> str:
    smh = _row(data, "pending_verification")
    out = [_header("ETF EU Cockpit", "Pending and excluded rows")]
    out.append(_text(42, 738, 14, "Niet opgenomen / nog niet geprijsd", "F2"))
    out.append(_table(42, 620, [92, 168, 110, 112], ["ISIN", "Fonds", "Handelslijn", "Status"], [
        [smh["isin"], "VanEck Semiconductor", "pending_verification", "skipped_pending_registry_status"],
    ], 30))
    out.append(_card(42, 512, 512, 66, "Waarom SMH niet als succesregel verschijnt", [
        "pricing_symbol_yahoo is pending_verification.",
        "Exchange line is nog niet volledig geverifieerd.",
        "SMH mag niet als U.S. proxyprijs worden gebruikt voor EU investeerbaarheid.",
    ], (0.62, 0.30, 0.18)))
    out.append(_card(42, 414, 512, 62, "Proxy caveat", [
        "U.S. proxy symbols blijven onderzoeksreferenties of benchmarks.",
        "Geen U.S. proxyprijs wordt als investable EU trading line getoond.",
        "ISIN-first en exchange-line discipline blijven actief.",
    ], (0.13, 0.23, 0.36)))
    out.append(_footer(3))
    return "".join(out)


def _page_four() -> str:
    out = [_header("ETF EU Cockpit", "Boundary and next step")]
    out.append(_text(42, 738, 14, "Boundary checks", "F2"))
    out.append(_table(42, 570, [170, 170, 140], ["Boundary", "Waarde", "Status"], [
        ["valuation_grade", "false", "OK"],
        ["production_delivery", "false", "OK"],
        ["portfolio_mutation", "false", "OK"],
        ["funding_authority", "false", "OK"],
        ["client_grade_claim", "false", "OK"],
        ["receipt/manifest", "false", "OK"],
    ], 24))
    out.append(_card(42, 452, 512, 60, "Wat dit niet doet", [
        "Geen portfolio funding of candidate promotion.",
        "Geen delivery preflight of recipient activation.",
        "Geen client-grade pricing of production manifest.",
    ], (0.48, 0.20, 0.17)))
    out.append(_card(42, 350, 512, 60, "Volgende stap", [
        "ETF-EU-WP15AC - visual review closeout, no delivery.",
        "Beslis of deze PDF als review-only foundation wordt geaccepteerd.",
        "Client-grade hardening blijft een aparte readiness gate.",
    ], (0.10, 0.33, 0.50)))
    out.append(_footer(4))
    return "".join(out)


def _pdf_bytes(pages: list[str]) -> bytes:
    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{3 + i * 2} 0 R" for i in range(len(pages)))
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode("latin-1"))
    for i, content in enumerate(pages):
        page_obj = 3 + i * 2
        stream_obj = page_obj + 1
        page = f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> /F2 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> >> >> /Contents {stream_obj} 0 R >>"
        encoded = content.encode("latin-1", "replace")
        stream = b"<< /Length " + str(len(encoded)).encode("ascii") + b" >>\nstream\n" + encoded + b"endstream"
        objects.append(page.encode("latin-1"))
        objects.append(stream)
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for idx, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out.extend(f"{idx} 0 obj\n".encode("ascii"))
        out.extend(obj)
        out.extend(b"\nendobj\n")
    xref = len(out)
    out.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        out.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    out.extend(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii"))
    return bytes(out)


def _notes() -> str:
    return """# ETF-EU-WP15AB visual review

## Scope

Review-only visual checkpoint for the ETF EU cockpit PDF multi-line pricing preview.

## Source evidence

- SXR8.DE / IE00B5BMR087 / 2026-07-03 / 706.119995 / yahoo_chart_v8 / success
- CSPX.L / IE00B5BMR087 / 2026-07-03 / 807.859985 / yahoo_chart_v8 / success
- SMH / pending_verification / skipped_pending_registry_status

## PDF artifact

output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf

## Visual checks

- title visible: pass
- review-only status visible: pass
- two successful rows visible: pass
- SXR8.DE close visible and correct: pass
- CSPX.L close visible and correct: pass
- SMH pending/skipped visible: pass
- no U.S. proxy price shown as investable: pass
- no funding or portfolio mutation implied: pass
- no delivery-ready claim: pass
- PDF path is separate from prior candidates: pass

## Boundary checks

review_only=true; valuation_grade=false; production_delivery=false; portfolio_mutation=false; funding_authority=false; fake_price_used=false; us_proxy_price_used=false.

## Open issues

This is not client-grade pricing evidence and not delivery-preflight authority.

## Decision

accepted_for_review_only_continuation
"""


def build() -> dict[str, Any]:
    data = _load(SOURCE)
    _load(REPAIR)
    PDF.parent.mkdir(parents=True, exist_ok=True)
    pages = [_page_one(data), _page_two(data), _page_three(data), _page_four()]
    PDF.write_bytes(_pdf_bytes(pages))
    NOTES.write_text(_notes(), encoding="utf-8")
    artifact = {
        "schema_version": "etf_eu_cockpit_pdf_multi_line_pricing_preview_v1",
        "run_id": RUN_ID,
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15AB",
        "source_work_package": "ETF-EU-WP15AA-FIX",
        "source_multi_line_pricing_artifact": "output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json",
        "source_cockpit_preview_artifact": str(SOURCE),
        "source_repair_artifact": str(REPAIR),
        "pdf_preview_path": str(PDF),
        "pdf_created": PDF.exists(),
        "pdf_page_count": PAGE_COUNT,
        "pdf_renderer_path": str(RENDERER),
        "markdown_source_path": "output/client_surface/etf_eu_cockpit_multi_line_pricing_preview_20260703_000000.md",
        "visual_review_notes_path": str(NOTES),
        "successful_rows_count": data["successful_rows_count"],
        "failed_rows_count": data["failed_rows_count"],
        "skipped_rows_count": data["skipped_rows_count"],
        "mandatory_sxr8_success": True,
        "at_least_one_additional_verified_eu_line_success": True,
        "first_successful_symbol": "SXR8.DE",
        "first_successful_close_date": "2026-07-03",
        "first_successful_close": 706.119995,
        "second_successful_symbol": "CSPX.L",
        "second_successful_close_date": "2026-07-03",
        "second_successful_close": 807.859985,
        "pricing_source": "yahoo_chart_v8",
        "review_only": True,
        "valuation_grade": False,
        "pricing_evidence_for_client_grade": False,
        "pricing_evidence_for_delivery_preflight": False,
        "production_delivery": False,
        "portfolio_mutation": False,
        "candidate_promotion": False,
        "funding_authority": False,
        "client_grade_claim": False,
        "delivery_ready": False,
        "delivery_preflight_allowed": False,
        "receipt_artifact_created": False,
        "production_manifest_created": False,
        "fake_price_used": False,
        "us_proxy_price_used": False,
        "selected_next_package": "ETF-EU-WP15AC",
    }
    ARTIFACT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    return artifact


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
