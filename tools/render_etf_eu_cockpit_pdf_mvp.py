from __future__ import annotations

import json
import textwrap
import unicodedata
from pathlib import Path

RUN_ID = "20260618_000000"
TARGET = Path("output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf")
CLOSEOUT = Path("output/client_surface/etf_eu_cockpit_poc_coordinator_closeout_20260618_000000.json")
POC_PACKAGE = Path("output/client_surface/etf_eu_cockpit_poc_package_20260618_000000.json")
DUTCH_MD = Path("output/client_surface/weekly_etf_eu_review_nl_260618_cockpit_pricing_integrated.md")
ENGLISH_MD = Path("output/client_surface/weekly_etf_eu_review_260618_cockpit_pricing_integrated.md")


def _safe_text(value: str) -> str:
    value = value.replace("—", "-").replace("–", "-").replace("’", "'").replace("“", '"').replace("”", '"')
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")


def _pdf_escape(value: str) -> str:
    return _safe_text(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _read_required(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"required source missing: {path}")
    return path.read_text(encoding="utf-8")


def _first_content_lines(markdown: str, limit: int = 10) -> list[str]:
    lines: list[str] = []
    for raw in markdown.splitlines():
        clean = raw.strip()
        if not clean:
            continue
        if clean.startswith("| ---"):
            continue
        if clean.startswith("#"):
            clean = clean.lstrip("#").strip()
        clean = clean.replace("**", "").replace("`", "")
        lines.append(clean)
        if len(lines) >= limit:
            break
    return lines


def _build_lines() -> list[str]:
    closeout = json.loads(_read_required(CLOSEOUT))
    package = json.loads(_read_required(POC_PACKAGE))
    dutch_lines = _first_content_lines(_read_required(DUTCH_MD), limit=12)
    english_lines = _first_content_lines(_read_required(ENGLISH_MD), limit=12)

    baseline = package["current_pricing_baseline"]
    proxies = package["research_proxy_map"]
    blockers = package["blocked_or_incomplete_lanes"]

    lines = [
        "ETF EU Cockpit PDF MVP",
        f"run_id={RUN_ID}",
        "status=proof_of_concept_pdf_mvp",
        f"delivery_authorization_decision={closeout['delivery_authorization_decision']}",
        f"production_delivery={str(closeout['production_delivery']).lower()}",
        f"portfolio_mutation={str(closeout['portfolio_mutation']).lower()}",
        f"candidate_promotion={str(closeout['candidate_promotion']).lower()}",
        f"funding_authority={str(closeout['funding_authority']).lower()}",
        f"valuation_grade={str(closeout['valuation_grade']).lower()}",
        "",
        "Source package summary",
        f"source_closeout={CLOSEOUT}",
        f"source_poc_package={POC_PACKAGE}",
        f"dutch_source={DUTCH_MD}",
        f"english_source={ENGLISH_MD}",
        "",
        "Dutch-first cockpit content",
        *dutch_lines,
        "",
        "English reference cockpit content",
        *english_lines,
        "",
        "Pricing boundary",
        baseline["isin"],
        baseline["fund_name"],
        ", ".join(baseline["pricing_symbols"]),
        f"review_only={str(baseline['review_only']).lower()}",
        baseline["pricing_evidence_status"],
        f"valuation_grade={str(baseline['valuation_grade']).lower()}",
        f"funding_authority={str(baseline['funding_authority']).lower()}",
        f"candidate_promotion={str(baseline['candidate_promotion']).lower()}",
        "",
        "Blocked/incomplete lanes",
    ]
    for lane in blockers:
        lines.append(f"{lane['isin']} / {lane['fund_name']} / {lane['status']} / {lane['reason']}")
    lines.extend([
        "",
        "Research proxy separation",
        f"SPY={proxies['SPY']}",
        f"SMH={proxies['SMH']}",
        f"GLD={proxies['GLD']}",
        f"PAVE={proxies['PAVE']}",
        "",
        "MVP boundary",
        "This PDF is proof_of_concept_pdf_mvp only.",
        "no_email_action_occurred=true",
        "delivery_receipt_created=false",
        "portfolio_state_modified=false",
        "candidate_promoted=false",
        "funding_authority=false",
        "valuation_grade=false",
    ])

    wrapped: list[str] = []
    for line in lines:
        if not line:
            wrapped.append("")
        else:
            wrapped.extend(textwrap.wrap(_safe_text(line), width=90) or [""])
    return wrapped


def _build_pdf_bytes(lines: list[str]) -> bytes:
    line_height = 13
    top_y = 750
    bottom_y = 50
    max_lines = int((top_y - bottom_y) / line_height)
    pages = [lines[i : i + max_lines] for i in range(0, len(lines), max_lines)]

    objects: list[str | None] = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        None,
        "<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>",
    ]
    kids: list[str] = []
    for page_lines in pages:
        content_id = len(objects) + 1
        page_id = len(objects) + 2
        stream_lines = ["BT", "/F1 10 Tf", "42 750 Td"]
        first = True
        for line in page_lines:
            if not first:
                stream_lines.append(f"0 -{line_height} Td")
            stream_lines.append(f"({_pdf_escape(line)}) Tj")
            first = False
        stream_lines.append("ET")
        stream = "\n".join(stream_lines)
        objects.append(f"<< /Length {len(stream.encode('ascii'))} >>\nstream\n{stream}\nendstream")
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_id} 0 R >>"
        )
        kids.append(f"{page_id} 0 R")

    objects[1] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(kids)} >>"

    content = b"%PDF-1.4\n%EOF-MVP\n"
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


def render_pdf_mvp() -> Path:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(_build_pdf_bytes(_build_lines()))
    print(f"ETF_EU_COCKPIT_PDF_MVP_RENDERED | output={TARGET}")
    return TARGET


def main() -> None:
    render_pdf_mvp()


if __name__ == "__main__":
    main()
