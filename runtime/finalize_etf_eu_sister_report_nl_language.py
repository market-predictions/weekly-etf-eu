from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

from weasyprint import HTML


SECTION_16_MARKER = '<section id="section-16"'

EXACT_PHRASES = {
    "Risk-on growth": "Risk-on groei",
    "Do not rotate aggressively unless a regime shift persists across at least two distinct report dates or cross-asset confirmation becomes broad.":
        "Roteer niet agressief tenzij een regimeverschuiving minstens twee afzonderlijke rapportdatums aanhoudt of de cross-assetbevestiging breed wordt.",
    "No material regime change was recorded versus the prior review; the Risk-on growth backdrop remained intact, market breadth is mixed, and cross-asset confirmation is mixed.":
        "Ten opzichte van de vorige review is geen materiële regimeverandering vastgesteld. De achtergrond van risk-on groei bleef intact, terwijl marktbreedte en cross-assetbevestiging gemengd zijn.",
    "Cybersecurity resilience": "Cybersecurityweerbaarheid",
    "AI compute infrastructure": "AI-rekenkrachtinfrastructuur",
    "Grid buildout / electrification": "Netuitbreiding / elektrificatie",
    "Healthcare quality and defensive growth": "Healthcarekwaliteit en defensieve groei",
    "Defense innovation / sovereign resilience": "Defensie-innovatie / strategische weerbaarheid",
    "Food security / agriculture inputs": "Voedselzekerheid / landbouwinputs",
    "Power infrastructure and utilities capex": "Stroominfrastructuur en investeringen in nutsbedrijven",
    "Broad commodity inflation hedge": "Brede grondstoffen-inflatiehedge",
    "Biotech innovation / therapeutic platforms": "Biotechinnovatie / therapeutische platforms",
    "Agricultural commodities": "Agrarische grondstoffen",
    "Non-U.S. developed market diversification": "Diversificatie naar ontwikkelde markten buiten de VS",
    "Water infrastructure / treatment": "Waterinfrastructuur / waterbehandeling",
    "Financial infrastructure and market plumbing": "Financiële infrastructuur en marktinfrastructuur",
    "Europe defense and security rearmament": "Europese defensie en veiligheidsopbouw",
    "Offers digital-infrastructure exposure with less direct semiconductor cyclicality.":
        "Biedt digitale-infrastructuurblootstelling met minder directe semiconductorcycliciteit.",
    "AI infrastructure leadership remains persistent, but position-size discipline matters.":
        "Het leiderschap van AI-infrastructuur houdt aan, maar discipline in positiegrootte blijft noodzakelijk.",
    "PAVE remains useful, but GRID is the cleaner thematic challenger.":
        "PAVE blijft bruikbaar, maar GRID is de zuiverdere thematische uitdager.",
    "More useful if broad equity leadership narrows further.":
        "Wordt relevanter wanneer het brede aandelenleiderschap verder versmalt.",
    "The lane remains relevant, but PPA must justify itself versus ITA.":
        "De exposure blijft relevant, maar PPA moet zijn meerwaarde tegenover ITA aantonen.",
    "identify and verify a suitable UCITS utilities or power-infrastructure implementation":
        "identificeer en verifieer een geschikte UCITS-implementatie voor nutsbedrijven of stroominfrastructuur",
    "determine whether an eligible UCITS fund exists or an ETC policy decision is required":
        "bepaal of een geschikt UCITS-fonds bestaat of dat een beleidsbesluit over ETC’s nodig is",
    "identify and verify a suitable UCITS biotech implementation":
        "identificeer en verifieer een geschikte UCITS-biotechimplementatie",
    "identify and verify a pure developed-markets-ex-US UCITS implementation":
        "identificeer en verifieer een zuivere UCITS-implementatie voor ontwikkelde markten buiten de VS",
    "identify and verify a Europe-focused UCITS defense implementation":
        "identificeer en verifieer een op Europa gerichte UCITS-defensie-implementatie",
    "identify and verify a suitable UCITS cybersecurity implementation":
        "identificeer en verifieer een geschikte UCITS-cybersecurity-implementatie",
    "identify and verify a broad, liquid UCITS healthcare implementation":
        "identificeer en verifieer een brede, liquide UCITS-healthcare-implementatie",
    "identify and verify a suitable UCITS defense implementation":
        "identificeer en verifieer een geschikte UCITS-defensie-implementatie",
    "identify and verify a suitable UCITS agriculture-equity implementation":
        "identificeer en verifieer een geschikte UCITS-implementatie voor landbouwaandelen",
    "identify and verify a suitable UCITS uranium or nuclear implementation":
        "identificeer en verifieer een geschikte UCITS-implementatie voor uranium of nucleaire energie",
    "6 promoted exposures are not represented":
        "Zes gepromoveerde exposures zijn niet vertegenwoordigd",
    "3 current positions require re-underwriting":
        "Drie huidige posities moeten opnieuw worden beoordeeld",
    "Stabilising aggregate bonds": "Stabiliserende wereldwijde obligaties",
    "defense_resilience": "Defensie-innovatie en strategische weerbaarheid",
    "agri_food_security": "Voedselzekerheid en landbouwinputs",
}

EXACT_CELL_LABELS = {
    "hold_or_monitor": "Aanhouden / bewaken",
    "watch": "Volgen",
    "Core": "Kernpositie",
    "Core satellite": "Kernsatelliet",
    "Stabilizer": "Stabilisator",
    "n/a": "n.v.t.",
    "shadow candidate": "Schaduwkandidaat",
    "schaduwkandidaat": "Schaduwkandidaat",
}

# Restore official product names that were touched by an earlier broad wording pass.
OFFICIAL_NAME_REPAIRS = {
    "iShares Kernpositie Global Aggregate Bond UCITS ETF EUR Hedged Acc":
        "iShares Core Global Aggregate Bond UCITS ETF EUR Hedged Acc",
}

FORBIDDEN_PATTERNS = [
    re.compile(r"\bhold_or_monitor\b"),
    re.compile(r"\bdefense_resilience\b"),
    re.compile(r"\bagri_food_security\b"),
    re.compile(r"\bDo not rotate aggressively\b"),
    re.compile(r"\bNo material regime change\b"),
    re.compile(r"\bidentify and verify\b", re.IGNORECASE),
    re.compile(r"\bdetermine whether an eligible\b", re.IGNORECASE),
    re.compile(r"\bcurrent positions require re-underwriting\b", re.IGNORECASE),
    re.compile(r"\bpromoted exposures are not represented\b", re.IGNORECASE),
    re.compile(r"\b(?:Cybersecurity resilience|AI compute infrastructure|Grid buildout / electrification|"
               r"Healthcare quality and defensive growth|Defense innovation / sovereign resilience|"
               r"Food security / agriculture inputs|Broad commodity inflation hedge|"
               r"Biotech innovation / therapeutic platforms|Agricultural commodities|"
               r"Non-U\.S\. developed market diversification|Water infrastructure / treatment|"
               r"Financial infrastructure and market plumbing|Europe defense and security rearmament)\b"),
]


def _replace_phrase(text: str, raw: str, replacement: str) -> str:
    return text.replace(html.escape(raw), html.escape(replacement)).replace(raw, html.escape(replacement))


def _replace_exact_cell(text: str, raw: str, replacement: str) -> str:
    escaped_raw = html.escape(raw)
    escaped_replacement = html.escape(replacement)
    return text.replace(f">{escaped_raw}<", f">{escaped_replacement}<")


def finalize(text: str) -> str:
    if SECTION_16_MARKER not in text:
        raise RuntimeError("Could not locate Section 16 boundary")
    client, continuity = text.split(SECTION_16_MARKER, 1)

    for raw, replacement in sorted(OFFICIAL_NAME_REPAIRS.items(), key=lambda item: len(item[0]), reverse=True):
        client = _replace_phrase(client, raw, replacement)
    # Replace longer sentences before short tokens that may be embedded in them.
    # This prevents a short translation such as `Risk-on growth` from breaking
    # the exact match for the complete regime-change sentence.
    for raw, replacement in sorted(EXACT_PHRASES.items(), key=lambda item: len(item[0]), reverse=True):
        client = _replace_phrase(client, raw, replacement)
    for raw, replacement in sorted(EXACT_CELL_LABELS.items(), key=lambda item: len(item[0]), reverse=True):
        client = _replace_exact_cell(client, raw, replacement)

    visible = html.unescape(client)
    leaked = [pattern.pattern for pattern in FORBIDDEN_PATTERNS if pattern.search(visible)]
    if leaked:
        raise RuntimeError("Dutch client surface still contains untranslated/internal text: " + "; ".join(leaked))
    if "iShares Kernpositie" in visible:
        raise RuntimeError("Official iShares product name is still corrupted")
    return client + SECTION_16_MARKER + continuity


def apply(manifest_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = (manifest.get("languages") or {}).get("nl")
    if not isinstance(files, dict):
        raise RuntimeError("Dutch language output is missing from manifest")
    html_path = Path(str(files.get("html") or ""))
    pdf_path = Path(str(files.get("pdf") or ""))
    text = html_path.read_text(encoding="utf-8")
    final = finalize(text)
    html_path.write_text(final, encoding="utf-8")
    HTML(string=final, base_url=str(html_path.parent.resolve())).write_pdf(pdf_path)
    files["dutch_language_finalization"] = "exact_phrase_and_cell_contract_v1"

    manifest["dutch_language_finalization"] = {
        "applied": True,
        "scope": "sections_1_through_15_only",
        "official_product_names_preserved": True,
        "canonical_section_16_ids_preserved": True,
        "portfolio_mutation": False,
        "recommendation_change": False,
        "valuation_change": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Finalize Dutch Weekly ETF EU sister-report language")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    apply(args.manifest)
    print(args.manifest)


if __name__ == "__main__":
    main()
