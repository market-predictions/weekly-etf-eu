from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any

from weasyprint import HTML


EXPOSURE_LABELS = {
    "ai_compute_infrastructure": {
        "nl": "AI-rekenkracht en halfgeleiders",
        "en": "AI compute and semiconductors",
    },
    "non_us_developed_equities": {
        "nl": "Ontwikkelde markten buiten de VS",
        "en": "Developed markets ex-U.S.",
    },
    "cyber_security": {
        "nl": "Cybersecurityweerbaarheid",
        "en": "Cybersecurity resilience",
    },
    "broad_commodities": {
        "nl": "Brede grondstoffen",
        "en": "Broad commodities",
    },
    "grid_power": {
        "nl": "Netuitbreiding en elektrificatie",
        "en": "Grid buildout and electrification",
    },
    "biotech_innovation": {
        "nl": "Biotechinnovatie",
        "en": "Biotech innovation",
    },
    "healthcare_quality": {
        "nl": "Healthcarekwaliteit",
        "en": "Healthcare quality",
    },
    "defense_resilience": {
        "nl": "Defensie-innovatie en strategische weerbaarheid",
        "en": "Defense innovation and sovereign resilience",
    },
    "agri_food_security": {
        "nl": "Voedselzekerheid en landbouwinputs",
        "en": "Food security and agriculture inputs",
    },
    "uranium_nuclear": {
        "nl": "Uranium en nucleaire brandstofcyclus",
        "en": "Uranium and nuclear fuel cycle",
    },
    "power_utilities_capex": {
        "nl": "Nutsbedrijven en stroominfrastructuur",
        "en": "Utilities and power infrastructure",
    },
    "aggregate_bonds": {
        "nl": "Wereldwijde obligaties",
        "en": "Global aggregate bonds",
    },
    "core_us_equity": {
        "nl": "Amerikaanse kernaandelen",
        "en": "Core U.S. equity",
    },
    "global_equity_core": {
        "nl": "Wereldwijde aandelenkern",
        "en": "Global equity core",
    },
}

REASON_LABELS = {
    "trading_line_unverified": {
        "nl": "handelslijn nog niet geverifieerd",
        "en": "trading line not yet verified",
    },
    "ucits_identity_unverified": {
        "nl": "UCITS-identiteit nog niet geverifieerd",
        "en": "UCITS identity not yet verified",
    },
    "product_type_blocked": {
        "nl": "producttype valt buiten huidig beleid",
        "en": "product type blocked by current policy",
    },
    "cash_reserve": {
        "nl": "cashreserve",
        "en": "cash reserve",
    },
    "existing_position_transition": {
        "nl": "bestaande portefeuille moet gecontroleerd worden omgebouwd",
        "en": "existing portfolio requires a controlled transition",
    },
    "pricing_missing_or_stale": {
        "nl": "actuele prijsbasis ontbreekt",
        "en": "current pricing basis missing",
    },
    "kid_missing": {
        "nl": "KID ontbreekt",
        "en": "KID missing",
    },
    "liquidity_below_threshold": {
        "nl": "liquiditeit onder minimumdrempel",
        "en": "liquidity below minimum threshold",
    },
    "currency_policy_blocked": {
        "nl": "valutabeleid blokkeert uitvoering",
        "en": "currency policy blocks implementation",
    },
    "whole_share_rounding": {
        "nl": "afronding naar hele aandelen",
        "en": "whole-share rounding",
    },
    "position_limit": {
        "nl": "positielimiet",
        "en": "position limit",
    },
    "factor_overlap_limit": {
        "nl": "factoroverlap boven limiet",
        "en": "factor overlap above limit",
    },
    "turnover_guard": {
        "nl": "omloopsnelheidslimiet",
        "en": "turnover guard",
    },
    "no_ucits_equivalent": {
        "nl": "geen geschikt UCITS-equivalent",
        "en": "no suitable UCITS equivalent",
    },
}

PHRASE_LABELS = {
    "nl": {
        "VWCE is incumbent; shared-strategy fit must be re-underwritten.":
            "VWCE is een bestaande kernpositie en moet opnieuw worden getoetst aan de gedeelde strategie.",
        "SXR8 is incumbent and must be tested against promoted thematic exposures.":
            "SXR8 is een bestaande positie en moet worden afgewogen tegen de gepromoveerde thematische exposures.",
        "EUNA remains separate from donor opportunity ranking.":
            "EUNA vervult een stabilisatierol en valt buiten de thematische kansenrangschikking van de donor.",
        "6 promoted exposures are not yet implemented.":
            "Zes gepromoveerde exposures zijn nog niet in de EU-portefeuille geïmplementeerd.",
        "Promoted exposures pending implementation":
            "Gepromoveerde exposures wachten op een gevalideerde implementatie",
        "Shadow only": "Alleen schaduwstatus",
        "shadow_candidate": "schaduwkandidaat",
        "line pending": "handelslijn in afwachting",
        "Existing position transition": "Gecontroleerde overgang van bestaande positie",
        "Review incumbent": "Bestaande positie herbeoordelen",
        "Review role and contribution": "Rol en bijdrage opnieuw beoordelen",
        "Opportunity cost": "Opportuniteitskosten beoordelen",
        "Sustaining aggregate bonds": "Stabiliserende wereldwijde obligaties",
        "Global core equity": "Wereldwijde aandelenkern",
        "U.S. equity overweight": "Amerikaanse aandelenoverweging",
        "No authorized changes": "Geen geautoriseerde wijzigingen",
        "No intent": "Geen intentie",
    },
    "en": {
        "line pending": "trading line pending",
        "shadow_candidate": "shadow candidate",
    },
}

CLIENT_SECTION_END = '<section id="section-16"'
INTERNAL_TOKEN_RE = re.compile(
    r"\b(?:trading_line_unverified|ucits_identity_unverified|product_type_blocked|"
    r"existing_position_transition|pricing_missing_or_stale|shadow_candidate)\b"
)


def _replace_visible_token(text: str, raw: str, replacement: str) -> str:
    escaped_raw = html.escape(raw)
    escaped_replacement = html.escape(replacement)
    return text.replace(escaped_raw, escaped_replacement).replace(raw, escaped_replacement)


def _polish_client_sections(text: str, language: str) -> str:
    if CLIENT_SECTION_END not in text:
        raise RuntimeError("Could not find Section 16 boundary")
    client, continuity = text.split(CLIENT_SECTION_END, 1)

    for raw, labels in EXPOSURE_LABELS.items():
        client = _replace_visible_token(client, raw, labels[language])
    # `cash` is a normal prose word and a section-title word. Localize only the
    # exact machine exposure cell, never every occurrence in the document.
    client = client.replace("<td>cash</td>", "<td>Cash</td>")
    for raw, labels in REASON_LABELS.items():
        client = _replace_visible_token(client, raw, labels[language])
    # Keep this layer limited to specific phrases. Generic labels such as Core,
    # Hold, Stabilizer and n/a are handled later as exact table-cell values so
    # official product names and prose cannot be corrupted.
    for raw, replacement in sorted(PHRASE_LABELS[language].items(), key=lambda item: len(item[0]), reverse=True):
        client = _replace_visible_token(client, raw, replacement)

    if language == "nl":
        client = client.replace(
            "cashreserve, bestaande portefeuille moet gecontroleerd worden omgebouwd",
            "cashreserve; bestaande portefeuille moet gecontroleerd worden omgebouwd",
        )
    else:
        client = client.replace(
            "cash reserve, existing portfolio requires a controlled transition",
            "cash reserve; existing portfolio requires a controlled transition",
        )

    if INTERNAL_TOKEN_RE.search(html.unescape(client)):
        matches = sorted(set(INTERNAL_TOKEN_RE.findall(html.unescape(client))))
        raise RuntimeError("Internal client-surface tokens remain: " + ", ".join(matches))
    return client + CLIENT_SECTION_END + continuity


def apply(manifest_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    languages = manifest.get("languages") if isinstance(manifest.get("languages"), dict) else {}
    for language, files in languages.items():
        if language not in {"nl", "en"} or not isinstance(files, dict):
            continue
        html_path = Path(str(files.get("html") or ""))
        pdf_path = Path(str(files.get("pdf") or ""))
        text = html_path.read_text(encoding="utf-8")
        polished = _polish_client_sections(text, language)
        html_path.write_text(polished, encoding="utf-8")
        HTML(string=polished, base_url=str(html_path.parent.resolve())).write_pdf(pdf_path)
        files["client_surface_polish"] = "bilingual_exposure_reason_and_phrase_normalization"

    manifest["client_surface_polish"] = {
        "applied": True,
        "scope": "sections_1_through_15_only",
        "canonical_section_16_ids_preserved": True,
        "portfolio_mutation": False,
        "recommendation_change": False,
        "valuation_change": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Polish Weekly ETF EU sister-report client surface")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    apply(args.manifest)
    print(args.manifest)


if __name__ == "__main__":
    main()
