from __future__ import annotations

import argparse
from pathlib import Path

from weasyprint import HTML


NL_REPLACEMENTS = {
    "AI / semiconductor leadership remains the dominant equity impulse.": "AI- en semiconductorleiderschap blijft de dominante aandelenimpuls.",
    "AI and semiconductor leadership remains the dominant equity impulse.": "AI- en semiconductorleiderschap blijft de dominante aandelenimpuls.",
    "Gold hedge behavior remains under review rather than automatic ballast.": "Goud blijft als hedge onder herbeoordeling en is geen automatische stabilisator.",
    "Prefer quality, profitable growth and cash discipline over weak balance-sheet beta.": "Geef voorkeur aan kwaliteit, winstgevende groei en kasdiscipline boven zwakke balans-bèta.",
    "Non-U.S. developed exposure remains watchlist, not automatic add.": "Blootstelling aan ontwikkelde markten buiten de VS blijft op de volglijst en is geen automatische toevoeging.",
    "AI infrastructure and semiconductor supply chains": "AI-infrastructuur en semiconductor-toeleveringsketens",
    "Capital spending and strategic supply-chain policy continue to support semiconductor and infrastructure lanes.": "Kapitaaluitgaven en strategisch toeleveringsbeleid blijven halfgeleider- en infrastructuurthema’s ondersteunen.",
    "Defense and sovereign resilience": "Defensie en strategische weerbaarheid",
    "Defense-budget durability remains a structural support, but ETF vehicle choice still matters.": "De duurzaamheid van defensiebudgetten blijft een structurele steun, maar de keuze van het ETF-instrument blijft belangrijk.",
    "Do not rotate aggressively unless a regime shift persists for at least two runs or cross-asset confirmation becomes broad.": "Roteer niet agressief tenzij een regimeverschuiving minstens twee runs aanhoudt of de bevestiging over meerdere activaklassen breed wordt.",
    "Initial cash-only EU/UCITS bootstrap state": "Initiële EU/UCITS-modelportefeuille volledig in cash",
    "refresh macro policy pack": "Ververs het macrobeleidspakket.",
    "verify broker availability and preferred EUR trading lines": "Verifieer brokerbeschikbaarheid en de gewenste EUR-handelslijnen.",
    "strengthen pricing source agreement": "Versterk de overeenstemming tussen prijsbronnen.",
    "take a separate allocation decision before funding": "Neem een afzonderlijk allocatiebesluit voordat kapitaal wordt ingezet.",
    "Inverse of leveraged producten": "Inverse en hefboomproducten",
    "3–12 months": "3–12 mnd",
    "6–18 months": "6–18 mnd",
    "<th>UCITS-kandidaten</th>": "<th>UCITS-lijnen</th>",
    "<th>Onderzoeksreferentie</th>": "<th>Referentie</th>",
    "<th>Waarom relevant</th>": "<th>Relevantie</th>",
    "<th>Structureel</th>": "<th>S</th>",
    "<th>Implementatie</th>": "<th>I</th>",
    "<th>Benodigde bevestiging</th>": "<th>Volgende bevestiging</th>",
    "<th>Handelslijn</th>": "<th>Lijn</th>",
    "<th>Peildatum</th>": "<th>Datum</th>",
}

EN_REPLACEMENTS = {
    "<th>UCITS candidates</th>": "<th>UCITS lines</th>",
    "<th>Research reference</th>": "<th>Reference</th>",
    "<th>Why relevant</th>": "<th>Relevance</th>",
    "<th>Structural</th>": "<th>S</th>",
    "<th>Implementation</th>": "<th>I</th>",
    "<th>Required confirmation</th>": "<th>Next confirmation</th>",
    "<th>Trading line</th>": "<th>Line</th>",
    "<th>Pricing date</th>": "<th>Date</th>",
}

NL_FORBIDDEN_RESIDUALS = [
    "remains the dominant equity impulse",
    "Prefer quality, profitable growth",
    "Non-U.S. developed exposure remains",
    "Capital spending and strategic supply-chain policy",
    "Defense-budget durability remains",
    "refresh macro policy pack",
    "verify broker availability",
    "strengthen pricing source agreement",
    "take a separate allocation decision before funding",
    "Inverse of leveraged producten",
]


def _append_print_polish(html_text: str, *, language: str) -> str:
    page_word = "Pagina" if language == "nl" else "Page"
    extra = f"""
<style id="etf-eu-client-grade-final-polish">
  @page {{
    @bottom-right {{ content: "{page_word} " counter(page) " van " counter(pages); }}
  }}
  th {{ overflow-wrap: normal; word-break: normal; hyphens: none; }}
  .wide-table {{ font-size: 6.45pt; }}
  .pricing-table {{ font-size: 6.15pt; }}
  .pricing-table th:nth-child(1) {{ width: 6%; }}
  .pricing-table th:nth-child(2) {{ width: 25%; }}
  .pricing-table th:nth-child(3) {{ width: 10%; }}
  .pricing-table th:nth-child(4) {{ width: 12%; }}
  .pricing-table th:nth-child(5) {{ width: 8%; }}
  .pricing-table th:nth-child(6) {{ width: 6%; }}
  .pricing-table th:nth-child(7) {{ width: 6%; }}
  .pricing-table th:nth-child(8) {{ width: 15%; }}
  .pricing-table th:nth-child(9) {{ width: 12%; }}
</style>
"""
    if language == "nl":
        extra = extra.replace("</style>", "  .masthead { font-size: 19pt; letter-spacing: .025em; }\n</style>")
    return html_text.replace("</head>", extra + "</head>", 1)


def polish(html_text: str, *, language: str) -> str:
    replacements = NL_REPLACEMENTS if language == "nl" else EN_REPLACEMENTS
    for source, target in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        html_text = html_text.replace(source, target)
    html_text = _append_print_polish(html_text, language=language)
    if language == "nl":
        residuals = [token for token in NL_FORBIDDEN_RESIDUALS if token.casefold() in html_text.casefold()]
        if residuals:
            raise RuntimeError("Dutch client-grade HTML contains untranslated or malformed wording: " + ", ".join(residuals))
    return html_text


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply narrow bilingual editorial polish to ETF EU client-grade HTML.")
    parser.add_argument("--html", required=True)
    parser.add_argument("--language", choices=["nl", "en"], required=True)
    parser.add_argument("--pdf", required=True)
    args = parser.parse_args()

    html_path = Path(args.html)
    rendered = polish(html_path.read_text(encoding="utf-8"), language=args.language)
    html_path.write_text(rendered, encoding="utf-8")
    pdf_path = Path(args.pdf)
    HTML(string=rendered, base_url=str(html_path.parent.resolve())).write_pdf(str(pdf_path))
    if not pdf_path.exists() or pdf_path.stat().st_size <= 0:
        raise RuntimeError(f"Polished PDF was not created: {pdf_path}")
    print(f"ETF_EU_CLIENT_GRADE_POLISH_OK | language={args.language} | pdf={pdf_path}")


if __name__ == "__main__":
    main()
