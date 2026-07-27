from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any

from weasyprint import HTML


SECTION_RE = re.compile(r'(<section id="section-14"[^>]*>)(.*?)(</section>)', re.DOTALL)

EXPOSURE_LABELS = {
    "ai_compute_infrastructure": {"nl": "AI-rekenkracht en halfgeleiders", "en": "AI compute and semiconductors"},
    "non_us_developed_equities": {"nl": "Ontwikkelde markten buiten de VS", "en": "Developed markets ex-U.S."},
    "cyber_security": {"nl": "Cybersecurityweerbaarheid", "en": "Cybersecurity resilience"},
    "broad_commodities": {"nl": "Brede grondstoffen", "en": "Broad commodities"},
    "grid_power": {"nl": "Netuitbreiding en elektrificatie", "en": "Grid buildout and electrification"},
    "biotech_innovation": {"nl": "Biotechinnovatie", "en": "Biotech innovation"},
    "healthcare_quality": {"nl": "Healthcarekwaliteit", "en": "Healthcare quality"},
    "uranium_nuclear": {"nl": "Uranium en nucleaire brandstofcyclus", "en": "Uranium and nuclear fuel cycle"},
    "power_utilities_capex": {"nl": "Nutsbedrijven en stroominfrastructuur", "en": "Utilities and power infrastructure"},
}

VARIANT_LABELS = {
    "strict_mapped_replication": {"nl": "Strikte gemapte replicatie", "en": "Strict mapped replication"},
    "efficient_max_eight_positions": {"nl": "Efficiënte portefeuille, maximaal 8 posities", "en": "Efficient portfolio, maximum 8 positions"},
    "staged_cash_first_50pct": {"nl": "Gefaseerde cash-first migratie (50%)", "en": "Staged cash-first migration (50%)"},
}

BLOCKER_LABELS = {
    "kid_missing": {"nl": "KID ontbreekt", "en": "KID missing"},
    "liquidity_below_threshold": {"nl": "liquiditeit onder drempel", "en": "liquidity below threshold"},
    "product_structure_review_required": {"nl": "productstructuur vereist beoordeling", "en": "product structure requires review"},
    "pricing_missing_or_stale": {"nl": "prijs ontbreekt of is verouderd", "en": "price missing or stale"},
    "trading_line_unverified": {"nl": "handelslijn niet geverifieerd", "en": "trading line unverified"},
    "no_ucits_equivalent": {"nl": "geen geschikt UCITS-equivalent", "en": "no suitable UCITS equivalent"},
    "product_type_blocked": {"nl": "producttype geblokkeerd", "en": "product type blocked"},
}


def e(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def money(value: Any, language: str) -> str:
    number = float(value or 0.0)
    raw = f"€{number:,.2f}"
    return raw.replace(",", "X").replace(".", ",").replace("X", ".") if language == "nl" else raw


def pct(value: Any, language: str) -> str:
    number = float(value or 0.0)
    raw = f"{number:,.2f}%"
    return raw.replace(",", "X").replace(".", ",").replace("X", ".") if language == "nl" else raw


def table(headers: list[str], rows: list[list[str]], css_class: str = "data-table") -> str:
    return (
        f'<table class="{e(css_class)}"><thead><tr>'
        + "".join(f"<th>{e(header)}</th>" for header in headers)
        + "</tr></thead><tbody>"
        + "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
        + "</tbody></table>"
    )


def variant_surface(allocator: dict[str, Any], language: str) -> str:
    preferred_id = str(allocator.get("preferred_shadow_variant") or "")
    variants = [row for row in (allocator.get("variants") or []) if isinstance(row, dict)]
    headers = (
        ["Variant", "Posities", "Cash", "Omzet", "Kosten", "Niet geïmplementeerd", "Status"]
        if language == "nl"
        else ["Variant", "Positions", "Cash", "Turnover", "Costs", "Unimplemented", "Status"]
    )
    rows: list[list[str]] = []
    preferred: dict[str, Any] | None = None
    for variant in variants:
        variant_id = str(variant.get("variant_id") or "")
        summary = variant.get("summary") if isinstance(variant.get("summary"), dict) else {}
        if variant_id == preferred_id:
            preferred = variant
        rows.append([
            e(VARIANT_LABELS.get(variant_id, {}).get(language, variant_id)),
            e(summary.get("position_count")),
            e(money(summary.get("projected_cash_eur"), language)),
            e(pct(summary.get("gross_turnover_pct_nav"), language)),
            e(money(summary.get("estimated_transaction_cost_eur"), language)),
            e(pct(summary.get("unimplemented_donor_target_weight_pct"), language)),
            '<span class="status status-good">Voorkeur</span>' if language == "nl" and variant_id == preferred_id else
            '<span class="status status-good">Preferred</span>' if language == "en" and variant_id == preferred_id else
            '<span class="status status-neutral">Alternatief</span>' if language == "nl" else '<span class="status status-neutral">Alternative</span>',
        ])
    intro = (
        "De allocator vergelijkt drie schaduwvarianten. Geen van deze varianten heeft uitvoerings- of financieringsbevoegdheid."
        if language == "nl" else
        "The allocator compares three shadow variants. None has execution or funding authority."
    )
    result = '<div class="alignment-summary"><strong>' + e(intro) + "</strong></div>" + table(headers, rows, "wide-table allocator-variant-table")
    if not preferred:
        return result

    order_headers = (
        ["Exposure", "Instrument", "Doelgewicht", "Doelaandelen", "Transactie", "Brutowaarde", "Status / blokkade"]
        if language == "nl" else
        ["Exposure", "Instrument", "Target weight", "Target shares", "Trade", "Gross value", "Status / blocker"]
    )
    order_rows: list[list[str]] = []
    for row in preferred.get("allocation_rows") or []:
        if not isinstance(row, dict):
            continue
        exposure_id = str(row.get("exposure_id") or "")
        candidate = row.get("candidate") if isinstance(row.get("candidate"), dict) else {}
        order = row.get("order") if isinstance(row.get("order"), dict) else {}
        blockers = [BLOCKER_LABELS.get(str(code), {}).get(language, str(code)) for code in (row.get("blockers") or [])]
        instrument = " — ".join(part for part in [str(candidate.get("ticker") or ""), str(candidate.get("fund_name") or "")] if part) or "—"
        status = (
            ("Opnemen in fase 1" if language == "nl" else "Include in stage 1")
            if row.get("selected") is True else
            ("; ".join(blockers) if blockers else ("Uitgesteld" if language == "nl" else "Deferred"))
        )
        order_rows.append([
            e(EXPOSURE_LABELS.get(exposure_id, {}).get(language, exposure_id)),
            e(instrument),
            e(pct(row.get("variant_target_weight_pct"), language)),
            e(order.get("target_shares")),
            e(order.get("side")),
            e(money(order.get("gross_trade_value_eur"), language)),
            e(status),
        ])
    result += (
        '<h3>Voorgestelde fase-1 allocatie</h3>' if language == "nl" else '<h3>Proposed stage-1 allocation</h3>'
    )
    result += table(order_headers, order_rows, "wide-table allocator-order-table")

    legacy_headers = (
        ["Bestaande positie", "Doelaandelen", "Actie", "Rol in overgang"]
        if language == "nl" else ["Current position", "Target shares", "Action", "Transition role"]
    )
    legacy_rows = []
    for row in preferred.get("legacy_rows") or []:
        if not isinstance(row, dict):
            continue
        role = "Tijdelijk behouden" if language == "nl" else "Temporarily retained"
        legacy_rows.append([e(row.get("ticker")), e(row.get("target_shares")), e(row.get("side")), e(role)])
    result += (
        '<h3>Behandeling huidige posities</h3>' if language == "nl" else '<h3>Treatment of current positions</h3>'
    )
    result += table(legacy_headers, legacy_rows, "data-table allocator-legacy-table")
    summary = preferred.get("summary") if isinstance(preferred.get("summary"), dict) else {}
    note = (
        f"Fase 1 koopt voor {money(summary.get('gross_buy_value_eur'), language)}, houdt de drie bestaande posities aan en eindigt met {money(summary.get('projected_cash_eur'), language)} cash. Geschatte transactiekosten: {money(summary.get('estimated_transaction_cost_eur'), language)}."
        if language == "nl" else
        f"Stage 1 buys {money(summary.get('gross_buy_value_eur'), language)}, retains the three current positions and ends with {money(summary.get('projected_cash_eur'), language)} cash. Estimated transaction costs: {money(summary.get('estimated_transaction_cost_eur'), language)}."
    )
    result += '<div class="alignment-summary">' + e(note) + "</div>"
    return result


def apply(manifest_path: Path, allocator_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    allocator = json.loads(allocator_path.read_text(encoding="utf-8"))
    if allocator.get("schema_version") != "etf_eu_target_allocator_shadow_v2":
        raise RuntimeError("Unsupported allocator artifact")
    for language, files in (manifest.get("languages") or {}).items():
        if language not in {"nl", "en"} or not isinstance(files, dict):
            continue
        html_path = Path(str(files.get("html") or ""))
        pdf_path = Path(str(files.get("pdf") or ""))
        text = html_path.read_text(encoding="utf-8")
        surface = variant_surface(allocator, language)
        def replace(match: re.Match[str]) -> str:
            body = match.group(2)
            header_end = body.find("</div>")
            if header_end < 0:
                raise RuntimeError("Section 14 header boundary not found")
            return match.group(1) + body[:header_end + 6] + surface + match.group(3)
        updated, count = SECTION_RE.subn(replace, text, count=1)
        if count != 1:
            raise RuntimeError(f"Could not replace Section 14 for {language}")
        html_path.write_text(updated, encoding="utf-8")
        HTML(string=updated, base_url=str(html_path.parent.resolve())).write_pdf(pdf_path)
        files["target_allocator_surface"] = "wp_sync_04_variant_and_stage_orders_v1"
    manifest["target_allocator_surface"] = {
        "applied": True,
        "source_allocator": str(allocator_path),
        "preferred_variant": allocator.get("preferred_shadow_variant"),
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--allocator", type=Path, required=True)
    args = parser.parse_args()
    apply(args.manifest, args.allocator)
    print(args.manifest)


if __name__ == "__main__":
    main()
