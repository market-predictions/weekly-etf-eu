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
}

NL_FORBIDDEN_RESIDUALS = [
    "remains the dominant equity impulse",
    "Prefer quality, profitable growth",
    "Non-U.S. developed exposure remains",
    "Capital spending and strategic supply-chain policy",
    "Defense-budget durability remains",
]


def polish(html_text: str, *, language: str) -> str:
    if language == "nl":
        for source, target in sorted(NL_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
            html_text = html_text.replace(source, target)
        residuals = [token for token in NL_FORBIDDEN_RESIDUALS if token.casefold() in html_text.casefold()]
        if residuals:
            raise RuntimeError("Dutch client-grade HTML contains untranslated macro wording: " + ", ".join(residuals))
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
