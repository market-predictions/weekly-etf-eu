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
    "staged_cash_first_50pct": {"nl": "Gefaseerde cash-first migratie (vaste 50%)", "en": "Staged cash-first migration (fixed 50%)"},
    "staged_policy_driven_v1": {"nl": "Beleidsgestuurde cash-first migratie", "en": "Policy-driven cash-first migration"},
}

BLOCKER_LABELS = {
    "kid_missing": {"nl": "KID ontbreekt", "en": "KID missing"},
    "liquidity_below_threshold": {"nl": "liquiditeit onder drempel", "en": "liquidity below threshold"},
    "product_structure_review_required": {"nl": "productstructuur vereist beoordeling", "en": "product structure requires review"},
    "pricing_missing_or_stale": {"nl": "prijs ontbreekt of is verouderd", "en": "price missing or stale"},
    "trading_line_unverified": {"nl": "handelslijn niet geverifieerd", "en": "trading line unverified"},
    "no_ucits_equivalent": {"nl": "geen geschikt UCITS-equivalent", "en": "no suitable UCITS equivalent"},
    "product_type_blocked": {"nl": "producttype geblokkeerd", "en": "product type blocked"},
    "position_limit": {"nl": "positielimiet bereikt", "en": "position limit reached"},
    "stage_turnover_or_cash_budget": {"nl": "omzet- of cashbudget bereikt", "en": "turnover or cash budget reached"},
    "minimum_trade_size": {"nl": "onder minimale transactiegrootte", "en": "below minimum trade size"},
}


def e(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def money(value: Any, language: str) -> str:
    number = float(value or 0.0)
    raw = f"€{number:,.2f}"
    return raw.replace(",", "X").replace(".", ",").replace("X", ".") if language == "nl" else raw


def pct(value: Any, language: str, signed: bool = False) -> str:
    number = float(value or 0.0)
    prefix = "+" if signed and number > 0 else ""
    raw = f"{prefix}{number:,.2f}%"
    return raw.replace(",", "X").replace(".", ",").replace("X", ".") if language == "nl" else raw


def table(headers: list[str], rows: list[list[str]], css_class: str = "data-table") -> str:
    return (
        f'<table class="{e(css_class)}"><thead><tr>'
        + "".join(f"<th>{e(header)}</th>" for header in headers)
        + "</tr></thead><tbody>"
        + "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
        + "</tbody></table>"
    )


def policy_summary(allocator: dict[str, Any], preferred: dict[str, Any], language: str) -> str:
    policy_contract = allocator.get("policy_contract") if isinstance(allocator.get("policy_contract"), dict) else {}
    stage = policy_contract.get("stage_1") if isinstance(policy_contract.get("stage_1"), dict) else {}
    overlap = allocator.get("incumbent_overlap_review") if isinstance(allocator.get("incumbent_overlap_review"), dict) else {}
    embedded = overlap.get("embedded_exposure_lower_bounds") if isinstance(overlap.get("embedded_exposure_lower_bounds"), dict) else {}
    rows = [
        ["Omzetplafond" if language == "nl" else "Turnover ceiling", pct(stage.get("maximum_gross_turnover_pct_nav"), language)],
        ["Minimale cash" if language == "nl" else "Minimum cash", pct(stage.get("minimum_post_stage_cash_pct_nav"), language)],
        ["Max. nieuwe ETF" if language == "nl" else "Maximum new ETF", pct(stage.get("maximum_new_direct_position_pct_nav"), language)],
        ["Effectieve halfgeleiderlimiet" if language == "nl" else "Effective semiconductor cap", pct((stage.get("effective_theme_caps_pct_nav") or {}).get("ai_compute_infrastructure"), language)],
        ["Ingebedde halfgeleiders, ondergrens" if language == "nl" else "Embedded semiconductors, lower bound", pct(embedded.get("semiconductor_pct_nav"), language)],
    ]
    summary = preferred.get("summary") if isinstance(preferred.get("summary"), dict) else {}
    intro = (
        "De voorkeursvariant gebruikt geen vaste tranche. De ordergrootte volgt uit omzet-, cash-, positie-, liquiditeits- en effectieve exposurelimieten."
        if language == "nl" else
        "The preferred variant uses no fixed tranche. Order sizing follows turnover, cash, position, liquidity and effective-exposure controls."
    )
    outcome = (
        f"Uitkomst: {pct(summary.get('gross_turnover_pct_nav'), language)} omzet en {pct(summary.get('projected_cash_weight_pct'), language)} resterende cash."
        if language == "nl" else
        f"Outcome: {pct(summary.get('gross_turnover_pct_nav'), language)} turnover and {pct(summary.get('projected_cash_weight_pct'), language)} remaining cash."
    )
    return (
        '<div class="alignment-summary"><strong>' + e(intro) + "</strong><br>" + e(outcome) + "</div>"
        + table(["Controle" if language == "nl" else "Control", "Limiet / meting" if language == "nl" else "Limit / measure"], rows, "data-table allocator-policy-table")
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
        f"De allocator vergelijkt {len(variants)} schaduwvarianten. Geen variant heeft uitvoerings- of financieringsbevoegdheid."
        if language == "nl" else
        f"The allocator compares {len(variants)} shadow variants. No variant has execution or funding authority."
    )
    result = '<div class="alignment-summary"><strong>' + e(intro) + "</strong></div>" + table(headers, rows, "wide-table allocator-variant-table")
    if not preferred:
        return result
    result += policy_summary(allocator, preferred, language)

    intent_headers = (
        ["Bron", "Bestemming", "Delta bron %", "Delta bestemming %", "Geschatte waarde EUR", "Intentiestatus", "Toelichting"]
        if language == "nl" else
        ["Source", "Destination", "Source delta %", "Destination delta %", "Estimated value EUR", "Intent status", "Explanation"]
    )
    intent_rows: list[list[str]] = []
    for row in preferred.get("allocation_rows") or []:
        if not isinstance(row, dict):
            continue
        exposure_id = str(row.get("exposure_id") or "")
        candidate = row.get("candidate") if isinstance(row.get("candidate"), dict) else {}
        order = row.get("order") if isinstance(row.get("order"), dict) else {}
        blockers = [BLOCKER_LABELS.get(str(code), {}).get(language, str(code)) for code in (row.get("blockers") or [])]
        ticker = str(candidate.get("ticker") or "—")
        fund_name = str(candidate.get("fund_name") or "")
        selected = row.get("selected") is True
        destination_delta = float(row.get("variant_target_weight_pct") or 0.0)
        status = "Beleidsgestuurde fase-1 schaduwintentie" if language == "nl" else "Policy-driven stage-1 shadow intent"
        if selected:
            effective = row.get("effective_post_stage_exposure_lower_bound_pct_nav")
            cap = row.get("effective_theme_cap_pct_nav")
            explanation = (
                f"Koop {order.get('target_shares')} hele aandelen {ticker}. Effectieve exposure-ondergrens {pct(effective, language)} versus limiet {pct(cap, language)}. {fund_name}"
                if language == "nl" else
                f"Buy {order.get('target_shares')} whole shares of {ticker}. Effective exposure lower bound {pct(effective, language)} versus cap {pct(cap, language)}. {fund_name}"
            )
        else:
            explanation = "; ".join(blockers) if blockers else ("Uitgesteld" if language == "nl" else "Deferred")
        intent_rows.append([
            e("Cash"),
            e(ticker if selected else EXPOSURE_LABELS.get(exposure_id, {}).get(language, exposure_id)),
            e(pct(-destination_delta, language, signed=True) if selected else pct(0, language)),
            e(pct(destination_delta, language, signed=True) if selected else pct(0, language)),
            e(money(order.get("gross_trade_value_eur"), language)),
            e(status if selected else ("Geblokkeerd / uitgesteld" if language == "nl" else "Blocked / deferred")),
            e(explanation),
        ])
    result += ('<h3>Voorgestelde beleidsgestuurde fase-1 allocatie</h3>' if language == "nl" else '<h3>Proposed policy-driven stage-1 allocation</h3>')
    result += table(intent_headers, intent_rows, "wide-table allocator-order-table")

    legacy_headers = (
        ["Bestaande positie", "Doelaandelen", "Actie", "Rol in overgang"]
        if language == "nl" else ["Current position", "Target shares", "Action", "Transition role"]
    )
    legacy_rows = []
    for row in preferred.get("legacy_rows") or []:
        if not isinstance(row, dict):
            continue
        role = "Behouden in fase 1; herbeoordeling vóór fase 2" if language == "nl" else "Retained in stage 1; re-underwrite before stage 2"
        legacy_rows.append([e(row.get("ticker")), e(row.get("target_shares")), e(row.get("side")), e(role)])
    result += ('<h3>Behandeling huidige posities</h3>' if language == "nl" else '<h3>Treatment of current positions</h3>')
    result += table(legacy_headers, legacy_rows, "data-table allocator-legacy-table")
    summary = preferred.get("summary") if isinstance(preferred.get("summary"), dict) else {}
    note = (
        f"Fase 1 koopt voor {money(summary.get('gross_buy_value_eur'), language)}, verkoopt geen bestaande positie en eindigt met {money(summary.get('projected_cash_eur'), language)} cash. Geschatte transactiekosten: {money(summary.get('estimated_transaction_cost_eur'), language)}."
        if language == "nl" else
        f"Stage 1 buys {money(summary.get('gross_buy_value_eur'), language)}, sells no current position and ends with {money(summary.get('projected_cash_eur'), language)} cash. Estimated transaction costs: {money(summary.get('estimated_transaction_cost_eur'), language)}."
    )
    result += '<div class="alignment-summary">' + e(note) + "</div>"
    return result


def apply(manifest_path: Path, allocator_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    allocator = json.loads(allocator_path.read_text(encoding="utf-8"))
    if allocator.get("schema_version") != "etf_eu_target_allocator_shadow_v3":
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
        files["target_allocator_surface"] = "wp_sync_04_policy_driven_variant_and_stage_orders_v2"
    manifest["target_allocator_surface"] = {
        "applied": True,
        "source_allocator": str(allocator_path),
        "preferred_variant": allocator.get("preferred_shadow_variant"),
        "policy_driven": True,
        "overlap_review_applied": True,
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
