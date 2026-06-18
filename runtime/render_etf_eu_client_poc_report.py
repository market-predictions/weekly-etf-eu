from __future__ import annotations

import html
import json
from pathlib import Path

RUN_ID = "20260618_000000"
POC_DIR = Path("output/poc")
EN_MD = POC_DIR / "weekly_etf_eu_review_260618_client_poc.md"
NL_MD = POC_DIR / "weekly_etf_eu_review_nl_260618_client_poc.md"
EN_HTML = POC_DIR / "weekly_etf_eu_review_260618_client_poc.html"
NL_HTML = POC_DIR / "weekly_etf_eu_review_nl_260618_client_poc.html"
MANIFEST = POC_DIR / "etf_eu_client_poc_surface_20260618_000000.json"

EN_SOURCE = Path("output/weekly_etf_eu_review_260618_mature_draft.md")
NL_SOURCE = Path("output/weekly_etf_eu_review_nl_260618_mature_draft.md")
AUTH_DECISION = Path("output/delivery/etf_eu_delivery_authorization_decision_20260618_000000.json")


ENGLISH_MARKDOWN = """# Weekly ETF EU Review — Proof of Concept

This is a client-facing proof of concept for the Weekly ETF EU report. It is review-only and uses UCITS ETFs as the investable instrument layer.

## 1. Executive summary

The first EU report surface can now show real UCITS exchange-line pricing evidence without treating U.S.-listed ETFs as investable EU holdings. The current proof of concept focuses on one confirmed UCITS fund, iShares Core S&P 500 UCITS ETF USD (Acc), ISIN IE00B5BMR087, visible through the CSPX.L and SXR8.DE trading lines.

The report is not yet a portfolio recommendation engine. It shows that the EU/UCITS identity, pricing, proxy separation and reader-facing structure can work together in one readable weekly report concept.

## 2. Market and portfolio context

This proof of concept starts from a cautious EU-client framing. The current state is not a funded portfolio decision. It is a report-surface test showing how UCITS candidates can be reviewed before any capital allocation is considered.

The practical client question is simple: can a Dutch/EU investor see which UCITS instruments are visible, what price evidence exists, and which U.S. ETFs are only research proxies? This surface answers that first question.

## 3. UCITS candidates currently visible

| Fund | ISIN | Trading line | Currency | Status |
| --- | --- | --- | --- | --- |
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | CSPX.L | USD | visible candidate |
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | SXR8.DE | EUR | visible candidate |

Both lines point to the same UCITS fund. The different exchange lines and currencies matter for execution, reporting and later suitability checks.

## 4. Pricing evidence used

| Pricing symbol | Close date | Close | Currency | Source role |
| --- | --- | ---: | --- | --- |
| CSPX.L | 2026-06-17 | 809.24 | USD | daily close evidence |
| SXR8.DE | 2026-06-17 | 698.02 | EUR | daily close evidence |

The pricing evidence is useful for report review, but it is not valuation-grade pricing authority yet. A later valuation-grade layer would need stronger source agreement, freshness checks and promotion rules.

## 5. Research proxy separation

SPY may appear in this EU report only as a benchmark or research proxy for U.S. large-cap equity exposure. SPY is not presented as an EU investable holding.

The investable EU candidate shown here is the UCITS instrument with ISIN IE00B5BMR087. This distinction is central to the EU report concept.

## 6. Watchlist and next development priorities

- Expand the UCITS universe beyond the first S&P 500 UCITS candidate.
- Add KID/PRIIPs, TER, spread, liquidity and exchange-suitability fields.
- Improve the Dutch report surface so the report reads like a client document, not a development log.
- Keep proxy and investable-instrument roles visually separated.
- Keep delivery blocked until a later authorization package exists.

## 7. Current limitations

This proof of concept is review-only. It is not investment advice, not a production delivery, not a funded portfolio change, and not valuation-grade pricing authority.

The current report proves the first readable EU/UCITS surface. It does not yet prove a complete weekly production process.

## Appendix — Technical evidence

Source report: `output/weekly_etf_eu_review_260618_mature_draft.md`

Dutch source report: `output/weekly_etf_eu_review_nl_260618_mature_draft.md`

Authorization decision: `output/delivery/etf_eu_delivery_authorization_decision_20260618_000000.json`

POC surface manifest: `output/poc/etf_eu_client_poc_surface_20260618_000000.json`
"""


DUTCH_MARKDOWN = """# Weekly ETF EU-review — proof of concept

Dit is een eerste klantgerichte proof of concept voor het Weekly ETF EU-rapport. De rapportage is review-only en gebruikt UCITS ETF's als belegbare instrumentlaag.

## 1. Kernsamenvatting

De eerste EU-rapportoppervlakte kan nu echte prijsinformatie tonen voor UCITS-beurslijnen, zonder Amerikaanse ETF's als belegbare EU-posities te presenteren. Deze proof of concept richt zich op één bevestigde UCITS-fondsstructuur: iShares Core S&P 500 UCITS ETF USD (Acc), ISIN IE00B5BMR087, zichtbaar via CSPX.L en SXR8.DE.

Het rapport is nog geen portefeuillemotor of koopadvies. Het laat zien dat UCITS-identiteit, prijsbewijs, researchproxy-scheiding en een leesbare rapportstructuur samen kunnen werken.

## 2. Markt- en portefeuillecontext

Deze proof of concept start vanuit een voorzichtige EU-klantcontext. De huidige status is geen gefinancierde portefeuilleroute. Het is een rapporttest die laat zien hoe UCITS-kandidaten kunnen worden beoordeeld voordat er ooit kapitaal wordt toegewezen.

De praktische vraag is: ziet een Nederlandse/EU-gebruiker welke UCITS-instrumenten zichtbaar zijn, welk prijsbewijs bestaat en welke Amerikaanse ETF's alleen researchproxy zijn? Deze eerste oppervlakte beantwoordt die vraag.

## 3. Zichtbare UCITS-kandidaten

| Fonds | ISIN | Beurslijn | Valuta | Status |
| --- | --- | --- | --- | --- |
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | CSPX.L | USD | zichtbare kandidaat |
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | SXR8.DE | EUR | zichtbare kandidaat |

Beide beurslijnen horen bij hetzelfde UCITS-fonds. De beurslijn en valuta blijven belangrijk voor uitvoering, rapportage en latere geschiktheidscontrole.

## 4. Gebruikt prijsbewijs

| Prijssymbool | Slotdatum | Slotkoers | Valuta | Rol van bron |
| --- | --- | ---: | --- | --- |
| CSPX.L | 2026-06-17 | 809.24 | USD | dagelijkse slotkoers |
| SXR8.DE | 2026-06-17 | 698.02 | EUR | dagelijkse slotkoers |

Deze prijsinformatie is nuttig voor rapportreview, maar is nog geen waarderingsautoriteit. Daarvoor zijn later bronovereenstemming, versheidscontrole en expliciete promotieregels nodig.

## 5. Scheiding tussen researchproxy en belegbare UCITS

SPY mag in dit EU-rapport alleen voorkomen als benchmark of researchproxy voor Amerikaanse large-cap aandelenblootstelling. SPY wordt niet gepresenteerd als belegbare EU-positie.

De belegbare EU-kandidaat in deze proof of concept is het UCITS-instrument met ISIN IE00B5BMR087. Dat onderscheid is essentieel voor het EU-rapportconcept.

## 6. Watchlist en volgende ontwikkelpunten

- Breid het UCITS-universum uit voorbij de eerste S&P 500 UCITS-kandidaat.
- Voeg KID/PRIIPs, TER, spread, liquiditeit en beursgeschiktheid toe.
- Maak de Nederlandse rapportage rustiger en klantgerichter.
- Houd researchproxy en belegbaar instrument visueel gescheiden.
- Houd levering geblokkeerd totdat een latere autorisatiepackage bestaat.

## 7. Huidige beperkingen

Deze proof of concept is alleen bedoeld voor review. Dit is geen beleggingsadvies, geen productielevering, geen portefeuillemutatie en geen waarderingsautoriteit.

De huidige rapportage bewijst de eerste leesbare EU/UCITS-oppervlakte. Het bewijst nog geen volledig wekelijks productieproces.

## Bijlage — technisch bewijs

Bronrapport: `output/weekly_etf_eu_review_260618_mature_draft.md`

Nederlands bronrapport: `output/weekly_etf_eu_review_nl_260618_mature_draft.md`

Autorisatiebesluit: `output/delivery/etf_eu_delivery_authorization_decision_20260618_000000.json`

POC-oppervlaktemanifest: `output/poc/etf_eu_client_poc_surface_20260618_000000.json`
"""


STYLE = """
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 40px auto; max-width: 980px; line-height: 1.55; color: #111827; }
  h1 { font-size: 30px; margin-bottom: 12px; }
  h2 { margin-top: 34px; border-bottom: 1px solid #e5e7eb; padding-bottom: 6px; }
  table { border-collapse: collapse; width: 100%; margin: 16px 0; }
  th, td { border: 1px solid #e5e7eb; padding: 8px 10px; text-align: left; }
  th { background: #f9fafb; }
  code { background: #f3f4f6; padding: 2px 4px; border-radius: 4px; }
  .notice { border-left: 4px solid #9ca3af; background: #f9fafb; padding: 12px 14px; margin: 18px 0; }
</style>
"""


def markdown_to_html(markdown: str, *, lang: str) -> str:
    lines = markdown.splitlines()
    html_lines: list[str] = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_table:
                html_lines.append("</tbody></table>")
                in_table = False
            continue
        if stripped.startswith("# "):
            html_lines.append(f"<h1>{html.escape(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            if in_table:
                html_lines.append("</tbody></table>")
                in_table = False
            html_lines.append(f"<h2>{html.escape(stripped[3:])}</h2>")
        elif stripped.startswith("- "):
            html_lines.append(f"<p>• {html.escape(stripped[2:])}</p>")
        elif stripped.startswith("|") and stripped.endswith("|"):
            parts = [html.escape(part.strip()) for part in stripped.strip("|").split("|")]
            if all(set(part.replace(" ", "")) <= {"-", ":"} for part in parts):
                continue
            if not in_table:
                html_lines.append("<table><tbody>")
                in_table = True
            cells = "".join(f"<td>{part}</td>" for part in parts)
            html_lines.append(f"<tr>{cells}</tr>")
        else:
            html_lines.append(f"<p>{html.escape(stripped)}</p>")
    if in_table:
        html_lines.append("</tbody></table>")
    return "<!doctype html>\n<html lang=\"{}\"><head><meta charset=\"utf-8\">{}<title>ETF EU POC</title></head><body>{}</body></html>\n".format(lang, STYLE, "\n".join(html_lines))


def build_manifest() -> dict[str, object]:
    return {
        "schema_version": "etf_eu_client_poc_surface_v1",
        "run_id": RUN_ID,
        "status": "completed",
        "created_at_utc": "2026-06-18T00:00:00Z",
        "english_source_report_path": str(EN_SOURCE),
        "dutch_source_report_path": str(NL_SOURCE),
        "english_poc_markdown_path": str(EN_MD),
        "dutch_poc_markdown_path": str(NL_MD),
        "english_poc_html_path": str(EN_HTML),
        "dutch_poc_html_path": str(NL_HTML),
        "authorization_decision_artifact_path": str(AUTH_DECISION),
        "delivery_authorization_decision": "remain_blocked",
        "client_surface_created": True,
        "debug_surface_reduced": True,
        "technical_evidence_moved_to_appendix": True,
        "ucits_identity_preserved": True,
        "proxy_separation_preserved": True,
        "pricing_evidence_preserved": True,
        "delivery_authorized": False,
        "production_delivery": False,
        "portfolio_mutation": False,
        "candidate_promotion": False,
        "funding_authority": False,
        "valuation_grade": False,
        "validators_run": ["tools/validate_etf_eu_client_poc_surface.py"],
        "tests_expected": ["tests/test_etf_eu_client_poc_surface.py"],
        "selected_next_package": "WP14N",
        "selected_next_package_title": "ETF EU POC review and roadmap consolidation, no delivery",
    }


def render_all() -> dict[str, object]:
    POC_DIR.mkdir(parents=True, exist_ok=True)
    EN_MD.write_text(ENGLISH_MARKDOWN, encoding="utf-8")
    NL_MD.write_text(DUTCH_MARKDOWN, encoding="utf-8")
    EN_HTML.write_text(markdown_to_html(ENGLISH_MARKDOWN, lang="en"), encoding="utf-8")
    NL_HTML.write_text(markdown_to_html(DUTCH_MARKDOWN, lang="nl"), encoding="utf-8")
    manifest = build_manifest()
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    render_all()
    print(f"ETF_EU_CLIENT_POC_RENDERED | manifest={MANIFEST}")
