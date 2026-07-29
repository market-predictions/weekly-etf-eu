from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any

from weasyprint import HTML


SECTION_IDS = ("1", "2", "2A", "4", "11", "12", "13")
SECTION_PATTERNS = {
    section_id: re.compile(fr'(<section id="section-{re.escape(section_id)}"[^>]*>)(.*?)(</section>)', re.DOTALL)
    for section_id in SECTION_IDS
}

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
    "defense_resilience": {"nl": "Defensie-innovatie en soevereine weerbaarheid", "en": "Defense innovation and sovereign resilience"},
    "agri_food_security": {"nl": "Voedselzekerheid en landbouwinputs", "en": "Food security and agriculture inputs"},
}

BLOCKER_LABELS = {
    "kid_missing": {"nl": "KID nog niet geverifieerd", "en": "KID not yet verified"},
    "liquidity_below_threshold": {"nl": "liquiditeit onder de beleidsdrempel", "en": "liquidity below the policy threshold"},
    "product_structure_review_required": {"nl": "product- en tegenpartijstructuur vereist beoordeling", "en": "product and counterparty structure requires review"},
    "pricing_missing_or_stale": {"nl": "actuele prijsbasis ontbreekt", "en": "current price basis unavailable"},
    "trading_line_unverified": {"nl": "exacte handelslijn niet geverifieerd", "en": "exact trading line not verified"},
    "no_ucits_equivalent": {"nl": "geen geschikt UCITS-equivalent geverifieerd", "en": "no suitable UCITS equivalent verified"},
    "product_type_blocked": {"nl": "producttype door beleid geblokkeerd", "en": "product type blocked by policy"},
    "position_limit": {"nl": "positielimiet bereikt", "en": "position limit reached"},
    "stage_turnover_or_cash_budget": {"nl": "omzet- of cashbudget bereikt", "en": "turnover or cash budget reached"},
    "minimum_trade_size": {"nl": "onder minimale transactiegrootte", "en": "below minimum trade size"},
}


def e(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def pct(value: Any, language: str, signed: bool = False) -> str:
    number = num(value)
    prefix = "+" if signed and number > 0 else ""
    raw = f"{prefix}{number:,.2f}%"
    return raw.replace(",", "X").replace(".", ",").replace("X", ".") if language == "nl" else raw


def money(value: Any, language: str, decimals: int = 2) -> str:
    number = num(value)
    raw = f"€{number:,.{decimals}f}"
    return raw.replace(",", "X").replace(".", ",").replace("X", ".") if language == "nl" else raw


def table(headers: list[str], rows: list[list[str]], css_class: str) -> str:
    return (
        f'<table class="{e(css_class)}"><thead><tr>'
        + "".join(f"<th>{e(header)}</th>" for header in headers)
        + "</tr></thead><tbody>"
        + "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
        + "</tbody></table>"
    )


def section_header(body: str) -> str:
    match = re.match(r'(\s*<div class="section-head">.*?</div>)', body, re.DOTALL)
    if not match:
        raise RuntimeError("Section header boundary not found")
    return match.group(1)


def replace_section(text: str, section_id: str, content: str) -> str:
    pattern = SECTION_PATTERNS[section_id]

    def replace(match: re.Match[str]) -> str:
        return match.group(1) + section_header(match.group(2)) + content + match.group(3)

    updated, count = pattern.subn(replace, text, count=1)
    if count != 1:
        raise RuntimeError(f"Could not reconcile section {section_id}")
    return updated


def preferred_variant(allocator: dict[str, Any]) -> dict[str, Any]:
    preferred_id = str(allocator.get("preferred_shadow_variant") or "")
    for row in allocator.get("variants") or []:
        if isinstance(row, dict) and str(row.get("variant_id")) == preferred_id:
            return row
    raise RuntimeError("Preferred allocator variant not found")


def allocation_index(preferred: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("exposure_id")): row
        for row in preferred.get("allocation_rows") or []
        if isinstance(row, dict)
    }


def lane_index(sync: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("exposure_id")): row
        for row in sync.get("exposure_rows") or []
        if isinstance(row, dict)
    }


def promoted_rows(sync: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [row for row in sync.get("promoted_exposure_comparison") or [] if isinstance(row, dict)]
    return sorted(rows, key=lambda row: (num(row.get("shared_rank"), 9999), str(row.get("exposure_id"))))


def candidate_text(row: dict[str, Any]) -> str:
    candidate = row.get("candidate") if isinstance(row.get("candidate"), dict) else {}
    ticker = str(candidate.get("ticker") or "").strip()
    name = str(candidate.get("fund_name") or "").strip()
    return " · ".join(part for part in (ticker, name) if part) or "—"


def blocker_text(row: dict[str, Any], language: str) -> str:
    labels = [BLOCKER_LABELS.get(str(code), {}).get(language, str(code)) for code in row.get("blockers") or []]
    return "; ".join(labels) if labels else ("Geen technische blokkade; officiële activatie ontbreekt" if language == "nl" else "No technical blocker; official activation is pending")


def status_badge(text: str, kind: str) -> str:
    return f'<span class="status status-{e(kind)}">{e(text)}</span>'


def exposure_name(exposure_id: str, language: str, fallback: Any = None) -> str:
    return EXPOSURE_LABELS.get(exposure_id, {}).get(language) or str(fallback or exposure_id)


def selected_explanation(row: dict[str, Any], language: str) -> str:
    order = row.get("order") if isinstance(row.get("order"), dict) else {}
    candidate = row.get("candidate") if isinstance(row.get("candidate"), dict) else {}
    shares = int(num(order.get("target_shares")))
    price_date = candidate.get("price_date")
    liquidity = num(candidate.get("median_daily_traded_value_eur_20d"))
    if language == "nl":
        return (
            f"{shares} hele aandelen; koersdatum {price_date}; mediane dagomzet {money(liquidity, language, 0)}. "
            "Exacte lijn, KID, prijs en liquiditeit voldoen aan de schaduwpoort; geen uitvoeringsbevoegdheid."
        )
    return (
        f"{shares} whole shares; price date {price_date}; median daily traded value {money(liquidity, language, 0)}. "
        "Exact line, KID, price and liquidity pass the shadow gate; no execution authority."
    )


def section_1(preferred: dict[str, Any], language: str) -> str:
    summary = preferred.get("summary") if isinstance(preferred.get("summary"), dict) else {}
    selected = [row for row in preferred.get("allocation_rows") or [] if isinstance(row, dict) and row.get("selected") is True]
    selected_text = ", ".join(str((row.get("candidate") or {}).get("ticker")) for row in selected)
    if language == "nl":
        items = [
            ("Primair regime", "Risk-on groei"),
            ("Gedeelde strategische conclusie", "Cybersecurity en AI/halfgeleiders zijn de twee direct implementeerbare donor-exposures"),
            ("Beleidsgestuurde fase 1", f"{selected_text}; {pct(summary.get('gross_turnover_pct_nav'), language)} omzet; {pct(summary.get('projected_cash_weight_pct'), language)} resterende cash"),
            ("Hoofdconclusie", "De instrument- en allocatiepoorten zijn voor twee schaduwposities gereed, maar de officiële EU-portefeuille blijft ongewijzigd"),
        ]
    else:
        items = [
            ("Primary regime", "Risk-on growth"),
            ("Shared strategic conclusion", "Cybersecurity and AI/semiconductors are the two immediately implementable donor exposures"),
            ("Policy-driven Stage 1", f"{selected_text}; {pct(summary.get('gross_turnover_pct_nav'), language)} turnover; {pct(summary.get('projected_cash_weight_pct'), language)} remaining cash"),
            ("Main conclusion", "Instrument and allocation gates are ready for two shadow positions, while the official EU portfolio remains unchanged"),
        ]
    return "<ul>" + "".join(f"<li><strong>{e(label)}:</strong> {e(value)}</li>" for label, value in items) + "</ul>"


def section_2(sync: dict[str, Any], preferred: dict[str, Any], language: str) -> str:
    allocations = allocation_index(preferred)
    headers = (
        ["Exposure", "Actie", "UCITS-implementatie", "Huidig gewicht", "Afwijkingsreden"]
        if language == "nl" else
        ["Exposure", "Action", "UCITS implementation", "Current weight", "Divergence reason"]
    )
    rows: list[list[str]] = []
    for promoted in promoted_rows(sync):
        exposure_id = str(promoted.get("exposure_id"))
        allocation = allocations.get(exposure_id, {})
        selected = allocation.get("selected") is True
        candidate = candidate_text(allocation)
        if selected:
            order = allocation.get("order") if isinstance(allocation.get("order"), dict) else {}
            shares = int(num(order.get("target_shares")))
            target = pct(allocation.get("variant_target_weight_pct"), language)
            action = f"Fase-1 schaduwkoop gereed: {shares} aandelen, doel {target}" if language == "nl" else f"Stage-1 shadow buy ready: {shares} shares, target {target}"
            reason = "Officiële modelportefeuille nog niet geactiveerd; schaduwpoort geslaagd" if language == "nl" else "Official model portfolio not activated; shadow gate passed"
        else:
            action = "Capaciteit reserveren en blokkade oplossen" if language == "nl" else "Reserve capacity and resolve blocker"
            reason = blocker_text(allocation, language)
        rows.append([
            e(exposure_name(exposure_id, language, promoted.get("lane_name"))),
            e(action),
            e(candidate),
            e(pct(0, language)),
            e(reason),
        ])
    return table(headers, rows, "wide-table")


def section_2a(sync: dict[str, Any], preferred: dict[str, Any], language: str) -> str:
    summary = preferred.get("summary") if isinstance(preferred.get("summary"), dict) else {}
    selected_count = sum(1 for row in preferred.get("allocation_rows") or [] if isinstance(row, dict) and row.get("selected") is True)
    promoted_count = len(promoted_rows(sync))
    if language == "nl":
        cards = [
            f"{promoted_count} donor-exposures zijn gepromoveerd.",
            f"{selected_count} exacte UCITS-implementaties zijn beleidsgestuurd geschaald voor fase 1.",
            f"Fase 1 gebruikt {pct(summary.get('gross_turnover_pct_nav'), language)} omzet en houdt {pct(summary.get('projected_cash_weight_pct'), language)} cash aan.",
            "Geen portefeuillewijziging of order: afzonderlijke activatie en actuele waarderingskwaliteit blijven verplicht.",
        ]
    else:
        cards = [
            f"{promoted_count} donor exposures are promoted.",
            f"{selected_count} exact UCITS implementations are policy-sized for Stage 1.",
            f"Stage 1 uses {pct(summary.get('gross_turnover_pct_nav'), language)} turnover and retains {pct(summary.get('projected_cash_weight_pct'), language)} cash.",
            "No portfolio change or order: separate activation and current valuation-grade evidence remain required.",
        ]
    return '<div class="cockpit-grid">' + "".join(f'<div class="cockpit-card">{e(card)}</div>' for card in cards) + "</div>"


def section_4(sync: dict[str, Any], preferred: dict[str, Any], language: str) -> str:
    allocations = allocation_index(preferred)
    headers = (
        ["Rang", "Thema", "UCITS-kandidaat", "Donorscore", "Implementatiestatus", "Benodigde actie", "Blokkade"]
        if language == "nl" else
        ["Rank", "Theme", "UCITS candidate", "Donor score", "Implementation status", "Required action", "Blocker"]
    )
    rows: list[list[str]] = []
    for promoted in promoted_rows(sync):
        exposure_id = str(promoted.get("exposure_id"))
        allocation = allocations.get(exposure_id, {})
        selected = allocation.get("selected") is True
        if selected:
            status = status_badge("Beleidsgestuurd geschaald" if language == "nl" else "Policy-sized", "good")
            order = allocation.get("order") if isinstance(allocation.get("order"), dict) else {}
            action = (f"Schaduwdoel {pct(allocation.get('variant_target_weight_pct'), language)}; {int(num(order.get('target_shares')))} aandelen")
            blocker = "Alleen activatie- en waarderingspoort resteert" if language == "nl" else "Only activation and valuation-grade gate remain"
        else:
            status = status_badge("Geblokkeerd voor fase 1" if language == "nl" else "Blocked for Stage 1", "bad")
            action = "Blokkade oplossen; doelgewicht fase 1 blijft 0%" if language == "nl" else "Resolve blocker; Stage-1 target remains 0%"
            blocker = blocker_text(allocation, language)
        rows.append([
            e(promoted.get("shared_rank")),
            e(exposure_name(exposure_id, language, promoted.get("lane_name"))),
            e(candidate_text(allocation)),
            e(f"{num(promoted.get('shared_score')):.2f}"),
            status,
            e(action),
            e(blocker),
        ])
    return table(headers, rows, "wide-table")


def section_11(sync: dict[str, Any], preferred: dict[str, Any], language: str) -> str:
    allocations = allocation_index(preferred)
    headers = (
        ["Gedeelde kans", "UCITS-alternatief", "Status", "Prijs-/productbasis", "Beslisimplicatie"]
        if language == "nl" else
        ["Shared opportunity", "UCITS alternative", "Status", "Pricing/product basis", "Decision implication"]
    )
    rows: list[list[str]] = []
    for promoted in promoted_rows(sync):
        exposure_id = str(promoted.get("exposure_id"))
        allocation = allocations.get(exposure_id, {})
        selected = allocation.get("selected") is True
        if selected:
            status = status_badge("Schaduwpoort geslaagd" if language == "nl" else "Shadow gate passed", "good")
            basis = selected_explanation(allocation, language)
            implication = "Opnemen in beleidsgestuurde fase 1 na afzonderlijke activatie" if language == "nl" else "Include in policy-driven Stage 1 after separate activation"
        else:
            status = status_badge("Niet investeerbaar in fase 1" if language == "nl" else "Not investable in Stage 1", "bad")
            basis = blocker_text(allocation, language)
            implication = "Niet financieren; bewijs of productmapping voltooien" if language == "nl" else "Do not fund; complete evidence or product mapping"
        rows.append([
            e(exposure_name(exposure_id, language, promoted.get("lane_name"))),
            e(candidate_text(allocation)),
            status,
            e(basis),
            e(implication),
        ])
    return table(headers, rows, "wide-table")


def section_12(preferred: dict[str, Any], language: str) -> str:
    headers = (
        ["Sluiten", "Verlagen", "Aanhouden", "Toevoegen / bestemming", "Vervangen", "Status"]
        if language == "nl" else
        ["Close", "Reduce", "Hold", "Add / destination", "Replace", "Status"]
    )
    selected = [row for row in preferred.get("allocation_rows") or [] if isinstance(row, dict) and row.get("selected") is True]
    additions = []
    for row in selected:
        order = row.get("order") if isinstance(row.get("order"), dict) else {}
        ticker = (row.get("candidate") or {}).get("ticker")
        additions.append(f"{int(num(order.get('target_shares')))} {ticker}")
    rows = [[
        e("Geen" if language == "nl" else "None"),
        e("Geen in fase 1" if language == "nl" else "None in Stage 1"),
        e("VWCE, EUNA, SXR8"),
        e(", ".join(additions)),
        e("SXR8 eerst herbeoordelen in fase 2" if language == "nl" else "Re-underwrite SXR8 first in Stage 2"),
        e("Schaduwplan; geen financierings- of uitvoeringsbevoegdheid" if language == "nl" else "Shadow plan; no funding or execution authority"),
    ]]
    return table(headers, rows, "data-table")


def section_13(sync: dict[str, Any], preferred: dict[str, Any], allocator: dict[str, Any], language: str) -> str:
    allocations = allocation_index(preferred)
    lanes = lane_index(sync)
    headers = (
        ["Ticker/exposure", "ETF", "Huidig gewicht", "Doelgewicht", "Delta gewicht", "Actie", "Kapitaalbestemming", "Score", "Toelichting", "Override-status"]
        if language == "nl" else
        ["Ticker/exposure", "ETF", "Current weight", "Target weight", "Weight delta", "Action", "Capital destination", "Score", "Explanation", "Override status"]
    )
    rows: list[list[str]] = []
    for allocation in preferred.get("allocation_rows") or []:
        if not isinstance(allocation, dict):
            continue
        exposure_id = str(allocation.get("exposure_id"))
        selected = allocation.get("selected") is True
        target = num(allocation.get("variant_target_weight_pct"))
        donor_target = num(allocation.get("donor_target_weight_pct"))
        lane = lanes.get(exposure_id, {})
        if selected:
            action = "Voorbereiden voor afzonderlijke fase-1 activatie" if language == "nl" else "Prepare for separate Stage-1 activation"
            explanation = selected_explanation(allocation, language) + (f" Strategisch donordoel: {pct(donor_target, language)}." if language == "nl" else f" Strategic donor target: {pct(donor_target, language)}.")
            capital = "Cash" if language == "nl" else "Cash"
        else:
            action = "Uitstellen in fase 1" if language == "nl" else "Defer in Stage 1"
            explanation = blocker_text(allocation, language) + (f" Strategisch donordoel blijft {pct(donor_target, language)}." if language == "nl" else f" Strategic donor target remains {pct(donor_target, language)}.")
            capital = "Geen toewijzing" if language == "nl" else "No allocation"
        rows.append([
            e(exposure_name(exposure_id, language, lane.get("lane_name"))),
            e(candidate_text(allocation)),
            e(pct(0, language)),
            e(pct(target, language)),
            e(pct(target, language, signed=True)),
            e(action),
            e(capital),
            e(f"{num(lane.get('shared_score')):.2f}" if lane else "—"),
            e(explanation),
            e("Schaduw – geen uitvoering" if language == "nl" else "Shadow – no execution"),
        ])

    summary = preferred.get("summary") if isinstance(preferred.get("summary"), dict) else {}
    current_cash = num((allocator.get("current_portfolio") or {}).get("cash_eur")) / num((allocator.get("current_portfolio") or {}).get("nav_eur")) * 100.0
    target_cash = num(summary.get("projected_cash_weight_pct"))
    rows.append([
        e("Cash"), e("CASH"), e(pct(current_cash, language)), e(pct(target_cash, language)), e(pct(target_cash - current_cash, language, signed=True)),
        e("Fase 1 financieren en reserve aanhouden" if language == "nl" else "Fund Stage 1 and retain reserve"),
        e("VVSM en LOCK"), e("—"),
        e((f"Bruto aankopen {money(summary.get('gross_buy_value_eur'), language)}; kostenraming {money(summary.get('estimated_transaction_cost_eur'), language)}." if language == "nl" else f"Gross purchases {money(summary.get('gross_buy_value_eur'), language)}; estimated costs {money(summary.get('estimated_transaction_cost_eur'), language)}.")),
        e("Schaduw – geen uitvoering" if language == "nl" else "Shadow – no execution"),
    ])

    dispositions = {
        str(row.get("ticker")): row
        for row in (allocator.get("incumbent_overlap_review") or {}).get("incumbent_dispositions") or []
        if isinstance(row, dict)
    }
    for legacy in preferred.get("legacy_rows") or []:
        if not isinstance(legacy, dict):
            continue
        ticker = str(legacy.get("ticker"))
        disposition = dispositions.get(ticker, {})
        weight = num(disposition.get("current_weight_pct"))
        if ticker == "VWCE":
            explanation = "Kernpositie behouden; permanent kerngewicht bepalen na voltooiing van de ex-VS- en themamapping." if language == "nl" else "Retain as core; set permanent core weight after ex-U.S. and thematic mapping are complete."
        elif ticker == "SXR8":
            explanation = "Aanhouden in fase 1; eerste kandidaat voor overlapreductie zodra een ex-VS-kern investeerbaar is." if language == "nl" else "Hold in Stage 1; first candidate for overlap reduction once an ex-U.S. core is fundable."
        else:
            explanation = "Aanhouden totdat een expliciete risico- en drawdownbudgettoets de stabilisatierol beoordeelt." if language == "nl" else "Hold until an explicit risk and drawdown budget test evaluates the stabilisation role."
        rows.append([
            e(ticker), e(str(legacy.get("fund_name") or ticker)), e(pct(weight, language)), e(pct(weight, language)), e(pct(0, language)),
            e("Aanhouden in fase 1" if language == "nl" else "Hold in Stage 1"), e("Geen verkoop" if language == "nl" else "No sale"), e("—"), e(explanation),
            e("Schaduw – geen uitvoering" if language == "nl" else "Shadow – no execution"),
        ])
    return table(headers, rows, "wide-table final-alignment-table")


def apply(manifest_path: Path, allocator_path: Path, sync_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    allocator = json.loads(allocator_path.read_text(encoding="utf-8"))
    sync = json.loads(sync_path.read_text(encoding="utf-8"))
    if allocator.get("schema_version") != "etf_eu_target_allocator_shadow_v3":
        raise RuntimeError("Policy report reconciliation requires allocator v3")
    preferred = preferred_variant(allocator)
    if preferred.get("variant_id") != "staged_policy_driven_v1":
        raise RuntimeError("Unexpected preferred allocator variant")

    for language, files in (manifest.get("languages") or {}).items():
        if language not in {"nl", "en"} or not isinstance(files, dict):
            continue
        html_path = Path(str(files.get("html") or ""))
        pdf_path = Path(str(files.get("pdf") or ""))
        text = html_path.read_text(encoding="utf-8")
        contents = {
            "1": section_1(preferred, language),
            "2": section_2(sync, preferred, language),
            "2A": section_2a(sync, preferred, language),
            "4": section_4(sync, preferred, language),
            "11": section_11(sync, preferred, language),
            "12": section_12(preferred, language),
            "13": section_13(sync, preferred, allocator, language),
        }
        for section_id, content in contents.items():
            text = replace_section(text, section_id, content)
        html_path.write_text(text, encoding="utf-8")
        HTML(string=text, base_url=str(html_path.parent.resolve())).write_pdf(pdf_path)
        files["policy_allocator_reconciliation"] = "stage_1_status_and_feasible_target_contract_v1"

    manifest["policy_allocator_reconciliation"] = {
        "applied": True,
        "source_allocator": str(allocator_path),
        "source_sync_shadow": str(sync_path),
        "preferred_variant": allocator.get("preferred_shadow_variant"),
        "sections_reconciled": list(SECTION_IDS),
        "official_portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
        "production_delivery_authority": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Reconcile the EU client report with the policy-driven allocator")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--allocator", type=Path, required=True)
    parser.add_argument("--sync-shadow", type=Path, required=True)
    args = parser.parse_args()
    apply(args.manifest, args.allocator, args.sync_shadow)
    print(args.manifest)


if __name__ == "__main__":
    main()
