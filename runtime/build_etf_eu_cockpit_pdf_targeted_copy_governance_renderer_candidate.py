from __future__ import annotations

from pathlib import Path

OUTPUT = Path("output/client_surface/etf_eu_cockpit_pdf_targeted_copy_governance_renderer_candidate_20260618_000000.pdf")


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _line(x: int, y: int, size: float, text: str, bold: bool = False) -> str:
    font = "/F2" if bold else "/F1"
    return f"BT {font} {size} Tf {x} {y} Td ({_escape(text)}) Tj ET\n"


def _build_pdf() -> bytes:
    lines = [
        (50, 760, 18, "ETF EU Cockpit - Review-only PDF Candidate", True),
        (50, 738, 10, "ETF-EU-WP15M build package output - not delivered - no production delivery", False),
        (50, 722, 12, "Status", True),
        (50, 706, 10, "review-only | not delivered | no delivery receipt | no production manifest", False),
        (50, 690, 10, "delivery_authorization_decision=remain_blocked", False),
        (50, 674, 12, "Client-facing copy/governance refinement", True),
        (50, 658, 10, "Surface: Reviewversie voor controle - geen productie- of klantlevering.", False),
        (50, 642, 10, "Delivery: Niet verzonden; geen receipt of productiemanifest.", False),
        (50, 626, 10, "Evidence: review evidence, pricing evidence and valuation-grade evidence remain separated.", False),
        (50, 610, 10, "Proxy: UCITS candidates remain separated from U.S. proxy symbols.", False),
        (50, 594, 12, "Hard boundaries", True),
        (50, 578, 10, "production_delivery=false; client_distribution_claimed=false; receipt_artifact_created=false", False),
        (50, 562, 10, "production_manifest_created=false; portfolio_mutation=false; candidate_promotion=false", False),
        (50, 546, 10, "funding_authority=false; valuation_grade=false; premium_pdf_replaced=false", False),
        (50, 530, 10, "live_data_fetch_performed=false; pricing_evidence_changed=false; recommendation_logic_changed=false", False),
        (50, 514, 12, "Completion rule", True),
        (50, 498, 10, "This package is complete only because this review-only PDF candidate exists and validates.", False),
        (50, 482, 6, "work_package_id=ETF-EU-WP15M; review_only_pdf_candidate_created=true; selected_next_package=ETF-EU-WP15N", False),
    ]
    stream = "".join(_line(*item) for item in lines).encode("ascii")
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
    print(f"ETF_EU_COCKPIT_PDF_TARGETED_COPY_GOVERNANCE_RENDERER_CANDIDATE_BUILT | pdf={OUTPUT}")


if __name__ == "__main__":
    main()
