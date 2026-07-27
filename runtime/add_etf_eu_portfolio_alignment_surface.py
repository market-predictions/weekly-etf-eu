from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any

from weasyprint import HTML


SECTION_RE = re.compile(r'(<section id="section-(?P<id>8|13)"[^>]*>)(?P<body>.*?)(</section>)', re.DOTALL)


def e(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def num(value: Any, language: str, decimals: int = 2, signed: bool = False) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "n/a"
    prefix = "+" if signed and number > 0 else ""
    raw = f"{number:,.{decimals}f}"
    if language == "nl":
        raw = raw.replace(",", "X").replace(".", ",").replace("X", ".")
    return prefix + raw


def pct(value: Any, language: str, signed: bool = False) -> str:
    return num(value, language, 2, signed=signed) + "%"


def candidate_label(row: dict[str, Any]) -> str:
    candidate = row.get("preferred_ucits_candidate") if isinstance(row.get("preferred_ucits_candidate"), dict) else None
    if not candidate:
        return "—"
    tickers = [
        str(line.get("exchange_ticker") or "")
        for line in (candidate.get("trading_lines") or [])
        if isinstance(line, dict) and line.get("exchange_ticker")
    ]
    return ("/".join(tickers) + " · " if tickers else "") + str(candidate.get("fund_name") or "")


def action_label(value: Any, language: str) -> str:
    labels = {
        "hold_near_target": ("Aanhouden nabij doel", "Hold near target"),
        "increase_after_separate_authorization": ("Verhogen na aparte autorisatie", "Increase after separate authorization"),
        "reduce_after_separate_authorization": ("Verlagen na aparte autorisatie", "Reduce after separate authorization"),
        "prepare_new_position_review": ("Nieuwe positie voorbereiden", "Prepare new-position review"),
        "resolve_ucits_implementation_then_review": ("UCITS-implementatie oplossen", "Resolve UCITS implementation"),
        "review_legacy_exposure_exit_or_retention": ("Legacy-exposure herbeoordelen", "Review legacy exposure"),
        "allocate_only_after_separate_transition_authorization": ("Alleen alloceren na transitieautorisatie", "Allocate only after transition authorization"),
    }
    pair = labels.get(str(value), (str(value), str(value)))
    return pair[0] if language == "nl" else pair[1]


def status_label(value: Any, language: str) -> str:
    labels = {
        "aligned_within_one_percentage_point": ("Uitgelijnd", "Aligned", "status-good"),
        "partially_aligned_weight_gap": ("Gewichtsafwijking", "Weight gap", "status-warn"),
        "missing_donor_target_exposure": ("Doel-exposure ontbreekt", "Target exposure missing", "status-bad"),
        "eu_only_legacy_exposure": ("Alleen in EU legacy", "EU legacy only", "status-warn"),
        "cash_weight_divergence": ("Cashafwijking", "Cash divergence", "status-warn"),
    }
    nl, en, css = labels.get(str(value), (str(value), str(value), "status-neutral"))
    text = nl if language == "nl" else en
    return f'<span class="status {css}">{e(text)}</span>'


def table(headers: list[str], rows: list[list[str]], css_class: str) -> str:
    return (
        f'<table class="{e(css_class)}"><thead><tr>'
        + "".join(f"<th>{e(header)}</th>" for header in headers)
        + "</tr></thead><tbody>"
        + "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
        + "</tbody></table>"
    )


def allocation_surface(sync: dict[str, Any], language: str) -> str:
    summary = sync.get("portfolio_alignment_summary") if isinstance(sync.get("portfolio_alignment_summary"), dict) else {}
    coverage = pct(summary.get("exact_exposure_coverage_pct_of_donor_invested_target"), language)
    intro = (
        f"Exacte donor-exposuredekking in de huidige EU-portefeuille: <strong>{coverage}</strong>. "
        "Dit meet dezelfde exposures; brede kernfondsen tellen niet als vervanging voor een andere thematische exposure."
        if language == "nl" else
        f"Exact donor-exposure coverage in the current EU portfolio: <strong>{coverage}</strong>. "
        "This measures like-for-like exposures; broad core funds do not count as substitutes for different thematic exposures."
    )
    headers = (
        ["Exposure", "Donordoel", "EU huidig", "Verschil", "EU-instrument", "Status", "Afwijkingsreden"]
        if language == "nl" else
        ["Exposure", "Donor target", "EU current", "Difference", "EU instrument", "Status", "Divergence reason"]
    )
    rows: list[list[str]] = []
    for row in sync.get("portfolio_alignment_rows") or []:
        if not isinstance(row, dict):
            continue
        rows.append([
            e(row.get("exposure_id")),
            e(pct(row.get("donor_target_weight_pct"), language)),
            e(pct(row.get("eu_current_weight_pct"), language)),
            e(pct(row.get("weight_gap_eu_minus_donor_pct"), language, signed=True)),
            e(candidate_label(row) if row.get("exposure_id") != "cash" else "Cash"),
            status_label(row.get("alignment_status"), language),
            e(", ".join(row.get("divergence_reason_codes") or []) or "—"),
        ])
    return '<div class="alignment-summary">' + intro + "</div>" + table(headers, rows, "wide-table alignment-table")


def final_action_surface(sync: dict[str, Any], language: str) -> str:
    headers = (
        ["Ticker/exposure", "ETF", "Huidig gewicht", "Doelgewicht", "Delta gewicht", "Actie", "Kapitaalbestemming", "Score", "Toelichting", "Override-status"]
        if language == "nl" else
        ["Ticker/exposure", "ETF", "Current weight", "Target weight", "Weight delta", "Action", "Capital destination", "Score", "Explanation", "Override status"]
    )
    rows: list[list[str]] = []
    for row in sync.get("portfolio_alignment_rows") or []:
        if not isinstance(row, dict):
            continue
        source_tickers = "/".join(str(value) for value in (row.get("donor_source_tickers") or []))
        eu_tickers = "/".join(str(value) for value in (row.get("eu_current_tickers") or []))
        instrument = candidate_label(row)
        if instrument == "—" and eu_tickers:
            instrument = eu_tickers
        explanation = ", ".join(row.get("divergence_reason_codes") or []) or str(row.get("alignment_status") or "")
        rows.append([
            e(row.get("exposure_id")),
            e(instrument),
            e(pct(row.get("eu_current_weight_pct"), language)),
            e(pct(row.get("donor_target_weight_pct"), language)),
            e(pct(-float(row.get("weight_gap_eu_minus_donor_pct") or 0), language, signed=True)),
            e(action_label(row.get("alignment_action"), language)),
            e("EU cash / controlled rotation" if language == "en" else "EU-cash / gecontroleerde rotatie"),
            e("—"),
            e((source_tickers + " · " if source_tickers else "") + explanation),
            e("Shadow - no execution" if language == "en" else "Schaduw - geen uitvoering"),
        ])
    return table(headers, rows, "wide-table final-alignment-table")


def inject_section(text: str, section_id: str, surface: str, replace_tables: bool) -> str:
    def repl(match: re.Match[str]) -> str:
        if match.group("id") != section_id:
            return match.group(0)
        body = match.group("body")
        if replace_tables:
            head_end = body.find("</div>")
            if head_end < 0:
                raise RuntimeError(f"Could not locate section header end for section {section_id}")
            body = body[: head_end + 6] + surface
        else:
            body = body + surface
        return match.group(1) + body + match.group(4)

    updated, count = SECTION_RE.subn(repl, text)
    if count < 2:
        raise RuntimeError("Could not identify both alignment target sections")
    return updated


def apply(manifest_path: Path, sync_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sync = json.loads(sync_path.read_text(encoding="utf-8"))
    for language, files in (manifest.get("languages") or {}).items():
        html_path = Path(str(files.get("html") or ""))
        pdf_path = Path(str(files.get("pdf") or ""))
        text = html_path.read_text(encoding="utf-8")
        text = inject_section(text, "8", allocation_surface(sync, language), replace_tables=False)
        text = inject_section(text, "13", final_action_surface(sync, language), replace_tables=True)
        if "donor-exposuredekking" not in text and "donor-exposure coverage" not in text:
            raise RuntimeError(f"Portfolio alignment summary missing after injection for {language}")
        html_path.write_text(text, encoding="utf-8")
        HTML(string=text, base_url=str(html_path.parent.resolve())).write_pdf(pdf_path)
        files["portfolio_alignment_surface"] = "donor_target_vs_eu_actual"
    manifest["portfolio_alignment_surface"] = {
        "applied": True,
        "source_sync_shadow": str(sync_path),
        "row_count": len(sync.get("portfolio_alignment_rows") or []),
        "portfolio_mutation": False,
        "recommendation_authority": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Add donor-to-EU portfolio alignment to sister-report shadow")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--sync-shadow", type=Path, required=True)
    args = parser.parse_args()
    apply(args.manifest, args.sync_shadow)
    print(args.manifest)


if __name__ == "__main__":
    main()
