from __future__ import annotations

from pathlib import Path

OUTPUT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_20260703_000000.pdf")


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _text(x: int, y: int, size: float, text: str, font: str = "F1") -> str:
    return f"BT /{font} {size} Tf {x} {y} Td ({_escape(text)}) Tj ET\n"


def _rect(x: int, y: int, w: int, h: int, fill: tuple[float, float, float]) -> str:
    r, g, b = fill
    return f"q {r:.3f} {g:.3f} {b:.3f} rg {x} {y} {w} {h} re f Q\n"


def _stroke_rect(x: int, y: int, w: int, h: int, stroke: tuple[float, float, float], width: float = 0.7) -> str:
    r, g, b = stroke
    return f"q {width:.2f} w {r:.3f} {g:.3f} {b:.3f} RG {x} {y} {w} {h} re S Q\n"


def _line(x1: int, y1: int, x2: int, y2: int, stroke: tuple[float, float, float], width: float = 0.7) -> str:
    r, g, b = stroke
    return f"q {width:.2f} w {r:.3f} {g:.3f} {b:.3f} RG {x1} {y1} m {x2} {y2} l S Q\n"


def _badge(x: int, y: int, label: str, fill: tuple[float, float, float] = (0.89, 0.94, 0.98), w: int = 92) -> str:
    return _rect(x, y, w, 18, fill) + _stroke_rect(x, y, w, 18, (0.70, 0.78, 0.86), 0.5) + _text(x + 6, y + 6, 7.2, label, "F2")


def _card(x: int, y: int, w: int, h: int, title: str, lines: list[str], accent: tuple[float, float, float] = (0.09, 0.22, 0.36)) -> str:
    out = []
    out.append(_rect(x, y, w, h, (1, 1, 1)))
    out.append(_stroke_rect(x, y, w, h, (0.80, 0.84, 0.88), 0.7))
    out.append(_rect(x, y + h - 20, w, 20, (0.94, 0.97, 0.99)))
    out.append(_rect(x, y, 4, h, accent))
    out.append(_text(x + 12, y + h - 14, 8.2, title, "F2"))
    yy = y + h - 34
    for line in lines:
        out.append(_text(x + 12, yy, 7.2, line, "F1"))
        yy -= 11
    return "".join(out)


def _table(x: int, y: int, widths: list[int], header: list[str], rows: list[list[str]], row_h: int = 24) -> str:
    total_w = sum(widths)
    out = []
    out.append(_rect(x, y + row_h * len(rows), total_w, row_h, (0.10, 0.20, 0.31)))
    out.append(_stroke_rect(x, y, total_w, row_h * (len(rows) + 1), (0.74, 0.79, 0.85), 0.6))
    xx = x
    for i, h in enumerate(header):
        out.append(_text(xx + 5, y + row_h * len(rows) + 8, 7.0, h, "F2"))
        xx += widths[i]
        out.append(_line(xx, y, xx, y + row_h * (len(rows) + 1), (0.85, 0.88, 0.91), 0.4))
    for r, row in enumerate(rows):
        row_y = y + row_h * (len(rows) - 1 - r)
        if r % 2 == 0:
            out.append(_rect(x, row_y, total_w, row_h, (0.985, 0.990, 0.995)))
        out.append(_line(x, row_y, x + total_w, row_y, (0.88, 0.90, 0.93), 0.4))
        xx = x
        for i, cell in enumerate(row):
            out.append(_text(xx + 5, row_y + 9, 6.6, cell, "F1"))
            xx += widths[i]
    return "".join(out)


def _header(title: str, subtitle: str) -> str:
    out = []
    out.append(_rect(0, 0, 595, 842, (0.965, 0.975, 0.985)))
    out.append(_rect(34, 768, 527, 48, (0.075, 0.145, 0.235)))
    out.append(_text(50, 798, 15, title, "F2"))
    out.append(_text(50, 782, 8, subtitle, "F1"))
    out.append(_badge(378, 790, "REVIEW-ONLY", (0.94, 0.96, 0.99), 82))
    out.append(_badge(468, 790, "NIET GELEVERD", (0.99, 0.94, 0.90), 82))
    return "".join(out)


def _footer(page: int) -> str:
    return _line(42, 42, 553, 42, (0.78, 0.82, 0.86), 0.6) + _text(46, 28, 6.2, f"ETF-EU-WP15T | Nederlandse reviewkandidaat | geen levering | geen receipt | geen productie-manifest | pagina {page}/4", "F1")


def _page_one() -> str:
    out = [_header("ETF EU Cockpit", "Nederlandse reviewkandidaat - premium visuele verfijning - geen levering")]
    out.append(_text(42, 742, 17, "Beslissing nu", "F2"))
    out.append(_text(42, 724, 8.4, "Geen nieuwe posities. Cash blijft de enige gefinancierde positie totdat UCITS-, KID-, prijs- en bewijschecks slagen.", "F1"))
    out.append(_card(42, 660, 160, 60, "Portefeuillestatus", ["Cash-only reviewstand", "Gefinancierde ETF's: 0", "Mutatie portefeuille: nee"], (0.10, 0.33, 0.50)))
    out.append(_card(218, 660, 160, 60, "Beslisactie", ["Houden: cash", "Review: SXR8 / CSPX", "Wachtlijst: SMH UCITS"], (0.18, 0.43, 0.32)))
    out.append(_card(394, 660, 160, 60, "Autoriteit", ["Geen funding", "Geen delivery", "Geen live prijsupdate"], (0.62, 0.30, 0.18)))
    out.append(_text(42, 622, 11.5, "Actiekaart", "F2"))
    out.append(_table(42, 496, [72, 80, 122, 130, 106], ["Onderdeel", "Actie", "Waarom", "Voorwaarde", "Status"], [
        ["Cash", "Houden", "Geen bewijs voor funding", "Expliciet besluit later", "OK"],
        ["SXR8.DE", "Review", "Core VS UCITS", "Prijs/KID/lijn versheid", "OPEN"],
        ["SMH", "Wacht", "Semiconductor thema", "Exchange-line check", "OPEN"],
        ["Gold ETC", "Blokkeren", "Niet UCITS ETF", "Policy besluit", "BLOK"],
    ], 24))
    out.append(_text(42, 456, 11.5, "Kwaliteitsbadges", "F2"))
    labels = [("UCITS scheiding", "U.S. ETF's alleen proxy"), ("Prijsbewijs", "niet ververst in WP15T"), ("Client taal", "Nederlands eerst"), ("Levering", "geblokkeerd")]
    x = 42
    for title, line in labels:
        out.append(_card(x, 396, 120, 50, title, [line], (0.12, 0.25, 0.38)))
        x += 130
    out.append(_card(42, 306, 512, 62, "Wat is verbeterd t.o.v. WP15R", [
        "Minder technische labels, meer klanttaal en scanbare kaarten.",
        "Beslissing, bewijs en beperkingen staan in een logische volgorde.",
        "Kandidaten zijn als reviewregels zichtbaar, niet als gefinancierde posities.",
    ], (0.09, 0.22, 0.36)))
    out.append(_footer(1))
    return "".join(out)


def _page_two() -> str:
    out = [_header("ETF EU Cockpit", "UCITS-kandidaten en bewijs - Nederlandse klanttaal")]
    out.append(_text(42, 742, 14, "UCITS-kandidaten", "F2"))
    out.append(_table(42, 584, [70, 128, 72, 72, 80, 88], ["ISIN", "Fonds", "Lijn", "KID", "Prijs", "Besluit"], [
        ["IE00B5BMR087", "iShares Core S&P 500", "SXR8.DE", "beschikbaar", "niet ververst", "review"],
        ["IE00BMC38736", "VanEck Semiconductor", "SMH", "beschikbaar", "open", "wachtlijst"],
        ["TBD", "iShares Physical Gold ETC", "SGLN", "open", "n.v.t.", "policy blok"],
        ["TBD", "Infrastructure UCITS", "INFR", "open", "open", "niet promoten"],
    ], 26))
    out.append(_text(42, 544, 14, "Bewijs en versheid", "F2"))
    out.append(_card(42, 470, 245, 60, "Wat is bekend", ["SXR8/CSPX: kandidaat, niet gefinancierd", "SMH UCITS: thema, lijn nog onzeker", "US ETF's: proxy, geen holding"], (0.10, 0.33, 0.50)))
    out.append(_card(309, 470, 245, 60, "Wat ontbreekt", ["Live slotkoers en versheid", "Liquiditeit/spread bewijs", "Nederlandse kwaliteitsgate"], (0.62, 0.30, 0.18)))
    out.append(_text(42, 400, 11.5, "Evidence badges", "F2"))
    out.append(_badge(42, 404, "UCITS OK", (0.90, 0.96, 0.92), 86))
    out.append(_badge(140, 404, "KID OK", (0.90, 0.96, 0.92), 72))
    out.append(_badge(224, 404, "PRIJS OPEN", (1.00, 0.94, 0.86), 92))
    out.append(_badge(328, 404, "NIET GEFUND", (0.94, 0.96, 0.99), 92))
    out.append(_badge(432, 404, "PROXY ALLEEN", (0.98, 0.93, 0.95), 104))
    out.append(_card(42, 318, 512, 58, "Proxy-disclosure", [
        "SPY, SMH, GLD en PAVE zijn onderzoeksproxy's of benchmarks.",
        "Ze zijn geen Dutch/EU-investeerbare holdings in dit rapport.",
        "Alle investeerbare regels blijven ISIN-first en UCITS-first.",
    ], (0.13, 0.23, 0.36)))
    out.append(_card(42, 230, 512, 58, "Niet oplossen in WP15T", [
        "Geen live data fetch, geen koersupdate en geen waarderingsoppervlak.",
        "Geen kandidaatpromotie, geen funding en geen portefeuillewijziging.",
        "Geen delivery preflight, geen ontvangers en geen manifest."], (0.48, 0.20, 0.17)))
    out.append(_footer(2))
    return "".join(out)


def _page_three() -> str:
    out = [_header("ETF EU Cockpit", "Risico, beperkingen en volgende stap")]
    out.append(_text(42, 742, 14, "Risicobeeld", "F2"))
    out.append(_card(42, 666, 245, 60, "Marktrisico", ["Geen gefinancierde ETF exposure", "Risico zit in bewijs en proces", "Cash blijft uitgangspunt"], (0.15, 0.37, 0.49)))
    out.append(_card(309, 666, 245, 60, "Procesrisico", ["Prijsversheid ontbreekt", "Taalgate nog niet volledig", "Delivery authority blijft nee"], (0.62, 0.30, 0.18)))
    out.append(_text(42, 622, 14, "Beperkingen", "F2"))
    out.append(_table(42, 452, [142, 208, 160], ["Beperking", "Waarom zichtbaar", "Benodigde volgende stap"], [
        ["Live prijsdata", "Niet geautoriseerd in WP15T", "Apart data-refresh pakket"],
        ["Valuation grade", "Geen actuele prijzen", "Validator + bronbewijs"],
        ["Client delivery", "Geen receipt/manifest", "Expliciete autorisatie"],
        ["Dutch quality", "Refinement kandidaat", "Visual review WP15U"],
        ["Portfolio actie", "Geen funding authority", "Apart besluit later"],
    ], 26))
    out.append(_text(42, 400, 14, "Klantgrade status", "F2"))
    out.append(_card(42, 322, 512, 60, "Oordeel WP15T", [
        "Deze PDF is sterker als client cockpit kandidaat, maar blijft review-only.",
        "De Nederlandse taal, kaartstructuur en badges zijn verbeterd.",
        "Delivery preflight blijft geblokkeerd tot aparte kwaliteit- en autorisatiechecks slagen."], (0.09, 0.22, 0.36)))
    out.append(_card(42, 232, 512, 60, "Volgende stap", [
        "ETF-EU-WP15U: visuele review van deze premium Dutch refinement kandidaat.",
        "Doel: bepalen of nog lay-out, taal of bewijsverbetering nodig is.",
        "Geen delivery, geen data-refresh en geen portefeuillemutatie."], (0.18, 0.43, 0.32)))
    out.append(_footer(3))
    return "".join(out)


def _page_four() -> str:
    out = [_header("ETF EU Cockpit", "Governance en runbook - no delivery")]
    out.append(_text(42, 742, 14, "Governance footer", "F2"))
    out.append(_table(42, 538, [150, 120, 240], ["Controle", "Status", "Betekenis"], [
        ["Productie levering", "nee", "Geen e-mail of klantdistributie"],
        ["Funding authority", "nee", "Geen kapitaal naar kandidaten"],
        ["Portfolio mutatie", "nee", "Geen ledger of positie-update"],
        ["Live data fetch", "nee", "Geen nieuwe marktdata opgehaald"],
        ["Pricing evidence", "nee", "Geen valuation-grade bewijs"],
        ["Receipt / manifest", "nee", "Geen delivery claim toegestaan"],
    ], 25))
    out.append(_text(42, 488, 14, "Runbook voor review", "F2"))
    out.append(_card(42, 418, 245, 60, "Wat reviewer checkt", ["Scanbaarheid pagina 1", "Taal: Nederlands eerst", "Geen proxy als holding"], (0.10, 0.33, 0.50)))
    out.append(_card(309, 418, 245, 60, "Wat niet mag", ["Geen delivery", "Geen live prijsfetch", "Geen fund/promote actie"], (0.62, 0.30, 0.18)))
    out.append(_card(42, 308, 512, 70, "Authority statement", [
        "Dit is een review-only PDF kandidaat voor WP15T.",
        "Klantdistributie blijft geblokkeerd: geen receipt, geen manifest, geen ontvangers.",
        "Een latere delivery-preflight vereist expliciete autorisatie en echte bewijsvalidators."], (0.09, 0.22, 0.36)))
    out.append(_text(42, 260, 12, "Selectie volgende package", "F2"))
    out.append(_badge(42, 230, "ETF-EU-WP15U", (0.90, 0.96, 0.92), 110))
    out.append(_text(162, 236, 8.0, "Visuele review checkpoint van de premium Dutch refinement kandidaat - geen levering", "F1"))
    out.append(_footer(4))
    return "".join(out)


def _page_streams() -> list[str]:
    return [_page_one(), _page_two(), _page_three(), _page_four()]


def _build_pdf() -> bytes:
    page_streams = _page_streams()
    objects: list[bytes] = []

    def add(obj: str | bytes) -> None:
        objects.append(obj.encode("ascii") if isinstance(obj, str) else obj)

    add("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    add(b"__PAGES_PLACEHOLDER__")
    add("3 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
    add("4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>\nendobj\n")

    next_id = 5
    page_ids: list[int] = []
    page_objects: list[str] = []
    content_objects: list[bytes] = []
    for page_stream in page_streams:
        page_id = next_id
        content_id = next_id + 1
        next_id += 2
        page_ids.append(page_id)
        page_objects.append(
            f"{page_id} 0 obj\n"
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> "
            f"/Contents {content_id} 0 R >>\nendobj\n"
        )
        stream = page_stream.encode("ascii")
        content_objects.append(
            f"{content_id} 0 obj\n<< /Length {len(stream)} >>\nstream\n".encode("ascii")
            + stream
            + b"endstream\nendobj\n"
        )

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[1] = f"2 0 obj\n<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>\nendobj\n".encode("ascii")

    for page_object, content_object in zip(page_objects, content_objects):
        add(page_object)
        add(content_object)

    pdf = b"%PDF-1.4\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf += obj

    xref_pos = len(pdf)
    pdf += f"xref\n0 {len(objects) + 1}\n".encode("ascii")
    pdf += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        pdf += f"{offset:010d} 00000 n \n".encode("ascii")
    pdf += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("ascii")
    return pdf


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(_build_pdf())
    print(f"ETF_EU_COCKPIT_PDF_PREMIUM_DUTCH_REFINEMENT_CANDIDATE_BUILT | pdf={OUTPUT}")


if __name__ == "__main__":
    main()
