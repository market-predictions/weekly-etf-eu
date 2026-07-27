from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any

from weasyprint import HTML


SECTION_RE = re.compile(r'(<section id="section-10"[^>]*>)(.*?)(</section>)', re.DOTALL)


def e(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def pct(value: Any, language: str) -> str:
    number = float(value or 0.0)
    raw = f"{number:,.2f}%"
    return raw.replace(",", "X").replace(".", ",").replace("X", ".") if language == "nl" else raw


def table(headers: list[str], rows: list[list[str]], css_class: str) -> str:
    return (
        f'<table class="{e(css_class)}"><thead><tr>'
        + "".join(f"<th>{e(header)}</th>" for header in headers)
        + "</tr></thead><tbody>"
        + "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
        + "</tbody></table>"
    )


def pair_index(review: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(row.get("left_fund")), str(row.get("right_fund"))): row
        for row in review.get("pairwise_overlap_rows") or []
        if isinstance(row, dict)
    }


def surface(review: dict[str, Any], language: str) -> str:
    pairs = pair_index(review)
    embedded = review.get("portfolio_embedded_exposure_lower_bounds") if isinstance(review.get("portfolio_embedded_exposure_lower_bounds"), dict) else {}
    by_semis = embedded.get("semiconductor_by_incumbent_pct_nav") if isinstance(embedded.get("semiconductor_by_incumbent_pct_nav"), dict) else {}
    dispositions = {
        str(row.get("ticker")): row
        for row in review.get("incumbent_dispositions") or []
        if isinstance(row, dict)
    }

    headers = (
        ["Ticker", "Huidig gewicht", "Gemeten overlap-ondergrens", "Ingebedde exposure-ondergrens", "Fase 1", "Vervolgrol", "Bewijsbeperking"]
        if language == "nl" else
        ["Ticker", "Current weight", "Measured overlap lower bound", "Embedded exposure lower bound", "Stage 1", "Future role", "Evidence limitation"]
    )

    vwce = dispositions.get("VWCE", {})
    sxr8 = dispositions.get("SXR8", {})
    euna = dispositions.get("EUNA", {})
    vwce_semis = (pairs.get(("VWCE", "VVSM")) or {}).get("measured_overlap_lower_bound_pct")
    sxr8_semis = (pairs.get(("SXR8", "VVSM")) or {}).get("measured_overlap_lower_bound_pct")
    core_overlap = (pairs.get(("VWCE", "SXR8")) or {}).get("measured_overlap_lower_bound_pct")

    rows = [
        [
            e("VWCE"),
            e(pct(vwce.get("current_weight_pct"), language)),
            e((f"{pct(vwce_semis, language)} versus VVSM" if language == "nl" else f"{pct(vwce_semis, language)} versus VVSM")),
            e(pct(by_semis.get("VWCE"), language) + (" van NAV" if language == "nl" else " of NAV")),
            e("Aanhouden" if language == "nl" else "Hold"),
            e("Kernpositie behouden en later permanent gewicht begrenzen" if language == "nl" else "Retain as core and set a permanent cap later"),
            e("Alleen gedocumenteerde top-posities; werkelijke overlap is hoger of gelijk" if language == "nl" else "Documented top holdings only; actual overlap is at least this high"),
        ],
        [
            e("SXR8"),
            e(pct(sxr8.get("current_weight_pct"), language)),
            e((f"{pct(core_overlap, language)} versus VWCE; {pct(sxr8_semis, language)} versus VVSM")),
            e(pct(by_semis.get("SXR8"), language) + (" van NAV" if language == "nl" else " of NAV")),
            e("Aanhouden" if language == "nl" else "Hold"),
            e("Prioritaire bron voor fase-2 overlapreductie zodra ex-VS-kern investeerbaar is" if language == "nl" else "Priority source for stage-2 overlap reduction once ex-U.S. core is fundable"),
            e("Ondergrens op basis van gedocumenteerde top-posities" if language == "nl" else "Lower bound based on documented top holdings"),
        ],
        [
            e("EUNA"),
            e(pct(euna.get("current_weight_pct"), language)),
            e("Niet vergelijkbaar via aandelenposities" if language == "nl" else "Not comparable through equity holdings"),
            e("Roldiversificatie" if language == "nl" else "Role diversification"),
            e("Aanhouden" if language == "nl" else "Hold"),
            e("Alleen wijzigen na expliciete risico- en drawdownbudgettoets" if language == "nl" else "Change only after an explicit risk and drawdown budget test"),
            e("Beoordelen op duration, volatiliteit en stabilisatierol" if language == "nl" else "Assess through duration, volatility and stabilisation role"),
        ],
    ]

    note = (
        f"De gedocumenteerde halfgeleiderexposure in VWCE en SXR8 bedraagt samen minimaal {pct(embedded.get('semiconductor_pct_nav'), language)} van de portefeuille. Een gemeten nul voor cybersecurity is geen bewijs van nul werkelijke overlap, omdat voor LOCK slechts een deel van de posities zichtbaar is."
        if language == "nl" else
        f"Documented semiconductor exposure embedded in VWCE and SXR8 totals at least {pct(embedded.get('semiconductor_pct_nav'), language)} of the portfolio. A measured zero for cybersecurity does not prove zero actual overlap because only part of LOCK's holdings set is documented."
    )
    title = "Overlap- en dispositiebeoordeling" if language == "nl" else "Overlap and disposition review"
    return f"<h3>{e(title)}</h3>" + table(headers, rows, "wide-table incumbent-overlap-table") + '<div class="alignment-summary">' + e(note) + "</div>"


def apply(manifest_path: Path, review_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    review = json.loads(review_path.read_text(encoding="utf-8"))
    if review.get("schema_version") != "etf_eu_incumbent_overlap_review_v1":
        raise RuntimeError("Unsupported overlap review")
    for language, files in (manifest.get("languages") or {}).items():
        if language not in {"nl", "en"} or not isinstance(files, dict):
            continue
        html_path = Path(str(files.get("html") or ""))
        pdf_path = Path(str(files.get("pdf") or ""))
        text = html_path.read_text(encoding="utf-8")
        addition = surface(review, language)

        def replace(match: re.Match[str]) -> str:
            return match.group(1) + match.group(2) + addition + match.group(3)

        updated, count = SECTION_RE.subn(replace, text, count=1)
        if count != 1:
            raise RuntimeError(f"Could not augment Section 10 for {language}")
        html_path.write_text(updated, encoding="utf-8")
        HTML(string=updated, base_url=str(html_path.parent.resolve())).write_pdf(pdf_path)
        files["incumbent_overlap_surface"] = "documented_lower_bound_and_disposition_v1"
    manifest["incumbent_overlap_surface"] = {
        "applied": True,
        "source_review": str(review_path),
        "lower_bound_only": True,
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--review", type=Path, required=True)
    args = parser.parse_args()
    apply(args.manifest, args.review)
    print(args.manifest)


if __name__ == "__main__":
    main()
