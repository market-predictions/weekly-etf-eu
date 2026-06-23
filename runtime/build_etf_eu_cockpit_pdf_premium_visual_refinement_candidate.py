from __future__ import annotations

from pathlib import Path

OUTPUT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_visual_refinement_candidate_20260618_000000.pdf")


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _text(x: int, y: int, size: float, text: str, bold: bool = False) -> str:
    font = "/F2" if bold else "/F1"
    return f"BT {font} {size} Tf {x} {y} Td ({_escape(text)}) Tj ET\n"


def _rect(x: int, y: int, w: int, h: int, gray: float) -> str:
    return f"q {gray:.2f} g {x} {y} {w} {h} re f Q\n"


def _line(x1: int, y1: int, x2: int, y2: int, gray: float = 0.78) -> str:
    return f"q {gray:.2f} G {x1} {y1} m {x2} {y2} l S Q\n"


def _build_pdf() -> bytes:
    parts: list[str] = []
    parts.append(_rect(0, 0, 595, 842, 0.98))
    parts.append(_rect(36, 744, 523, 62, 0.12))
    parts.append(_text(52, 782, 18, "ETF EU Cockpit", True))
    parts.append(_text(52, 763, 10, "Premium visual refinement candidate - review-only", False))
    parts.append(_text(392, 782, 8, "NOT DELIVERED", True))
    parts.append(_text(392, 768, 7, "No receipt / no production manifest", False))

    # Status badges
    badges = [
        (52, 714, 104, "REVIEW-ONLY"),
        (166, 714, 104, "NOT DELIVERED"),
        (280, 714, 104, "NO RECEIPT"),
        (394, 714, 130, "AUTHORITY BLOCKED"),
    ]
    for x, y, w, label in badges:
        parts.append(_rect(x, y, w, 24, 0.88))
        parts.append(_text(x + 10, y + 8, 7, label, True))

    # Executive summary card
    parts.append(_rect(52, 624, 491, 72, 0.94))
    parts.append(_text(70, 674, 13, "Executive read", True))
    parts.append(_text(70, 654, 9, "This cockpit page is a visual review candidate for the EU/UCITS ETF surface.", False))
    parts.append(_text(70, 640, 9, "It improves the first-page hierarchy and client-facing scanability while keeping", False))
    parts.append(_text(70, 626, 9, "all delivery, funding, valuation and portfolio authority blocked.", False))

    # Three cards
    cards = [
        (52, 500, 150, "Build proof", ["PDF path works", "Deterministic builder", "Review-only candidate"]),
        (222, 500, 150, "Client surface", ["Cleaner status badges", "Less validator-like", "Better visual grouping"]),
        (392, 500, 150, "Still blocked", ["No delivery", "No receipt", "No manifest"]),
    ]
    for x, y, w, title, rows in cards:
        parts.append(_rect(x, y, w, 92, 0.93))
        parts.append(_text(x + 14, y + 68, 11, title, True))
        yy = y + 49
        for row in rows:
            parts.append(_text(x + 14, yy, 8, row, False))
            yy -= 16

    # Evidence separation card
    parts.append(_rect(52, 376, 491, 94, 0.95))
    parts.append(_text(70, 446, 12, "Evidence and authority separation", True))
    parts.append(_text(70, 426, 8.5, "Review evidence: this PDF candidate and checkpoint artifacts only.", False))
    parts.append(_text(70, 410, 8.5, "Pricing evidence: unchanged; no live market data refresh in this package.", False))
    parts.append(_text(70, 394, 8.5, "Valuation-grade evidence: not created; valuation_grade=false.", False))
    parts.append(_text(70, 378, 8.5, "UCITS/proxy separation is preserved; U.S. symbols remain non-authoritative proxies.", False))

    # Boundary band
    parts.append(_rect(52, 250, 491, 94, 0.91))
    parts.append(_text(70, 320, 12, "No-delivery boundary", True))
    parts.append(_text(70, 300, 8, "production_delivery=false | client_distribution_claimed=false | outbound_path_enabled=false", False))
    parts.append(_text(70, 284, 8, "receipt_artifact_created=false | production_manifest_created=false", False))
    parts.append(_text(70, 268, 8, "delivery_authorization_decision=remain_blocked | delivery_preflight_allowed=false", False))
    parts.append(_text(70, 252, 8, "portfolio_mutation=false | funding_authority=false | valuation_grade=false", False))

    parts.append(_line(52, 220, 543, 220))
    parts.append(_text(52, 198, 8.5, "Next: ETF-EU-WP15P visual review checkpoint before any delivery-preflight discussion.", False))
    parts.append(_text(52, 178, 7, "work_package_id=ETF-EU-WP15O; review-only; not delivered; no delivery receipt; no production manifest", False))
    parts.append(_text(52, 164, 7, "delivery_authorization_decision=remain_blocked; selected_next_package=ETF-EU-WP15P", False))

    stream = "".join(parts).encode("ascii")
    objects: list[bytes] = []

    def add(obj: str | bytes) -> None:
        objects.append(obj.encode("ascii") if isinstance(obj, str) else obj)

    add("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    add("2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    add("3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>\nendobj\n")
    add("4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
    add("5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>\nendobj\n")
    add(f"6 0 obj\n<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"endstream\nendobj\n")

    pdf = b"%PDF-1.4\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf += obj
    xref_pos = len(pdf)
    pdf += f"xref\n0 {len(objects) + 1}\n".encode("ascii")
    pdf += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        pdf += f"{offset:010d} 00000 n \n".encode("ascii")
    pdf += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("ascii")
    return pdf


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(_build_pdf())
    print(f"ETF_EU_COCKPIT_PDF_PREMIUM_VISUAL_REFINEMENT_CANDIDATE_BUILT | pdf={OUTPUT}")


if __name__ == "__main__":
    main()
