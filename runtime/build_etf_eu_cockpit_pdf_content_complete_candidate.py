from __future__ import annotations

from pathlib import Path

OUTPUT = Path("output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_20260703_000000.pdf")


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _text(x: int, y: int, size: float, text: str, bold: bool = False) -> str:
    font = "/F2" if bold else "/F1"
    return f"BT {font} {size} Tf {x} {y} Td ({_escape(text)}) Tj ET\n"


def _rect(x: int, y: int, w: int, h: int, gray: float) -> str:
    return f"q {gray:.2f} g {x} {y} {w} {h} re f Q\n"


def _line(x1: int, y1: int, x2: int, y2: int, gray: float = 0.78) -> str:
    return f"q {gray:.2f} G {x1} {y1} m {x2} {y2} l S Q\n"


def _render_page(title: str, subtitle: str, rows: list[str | tuple[str, str]]) -> str:
    parts: list[str] = []
    parts.append(_rect(0, 0, 595, 842, 0.98))
    parts.append(_rect(36, 770, 523, 44, 0.12))
    parts.append(_text(52, 797, 14, title, True))
    parts.append(_text(52, 780, 8, subtitle))
    y = 742
    for row in rows:
        if isinstance(row, tuple):
            kind, value = row
            if kind == "h":
                parts.append(_rect(44, y - 4, 507, 18, 0.90))
                parts.append(_text(52, y, 9.5, value, True))
                y -= 24
            else:
                raise ValueError(f"unknown row kind: {kind}")
        else:
            parts.append(_text(62, y, 7.6, row))
            y -= 13
    parts.append(_line(44, 46, 551, 46))
    parts.append(_text(52, 32, 6.5, "ETF-EU-WP15R | review-only | no delivery | no receipt | no production manifest | valuation_grade=false"))
    return "".join(parts)


def _page_streams() -> list[str]:
    return [
        _render_page(
            "ETF EU Cockpit Content-Complete Candidate",
            "Review-only content-complete candidate - NOT DELIVERED - AUTHORITY BLOCKED",
            [
                ("h", "1. Cockpit header with report date and authority markers"),
                "report_date=2026-07-03 | work_package_id=ETF-EU-WP15R | content_completeness_candidate=true",
                "REVIEW-ONLY | NOT DELIVERED | NO RECEIPT | NO PRODUCTION MANIFEST | AUTHORITY BLOCKED",
                "production_delivery=false | valuation_grade=false | funding_authority=false | portfolio_mutation=false",
                ("h", "2. Executive read and action summary"),
                "Current posture: cash-only seed / no funded UCITS ETF holdings approved in this package.",
                "Client decision frame: prepare EU/UCITS cockpit content; do not promote or fund candidates.",
                "Action summary: HOLD CASH / REVIEW CANDIDATES / NO DELIVERY / NO LIVE DATA REFRESH.",
                "Key gap: pricing, KID, liquidity and line evidence must be refreshed in a later authorized package.",
                ("h", "3. Portfolio holdings and cash snapshot"),
                "Funded ETF holdings: none. Cash status: review-only cash placeholder; portfolio_mutation=false.",
                "Total valuation surface: not valuation-grade; no portfolio total is promoted by WP15R.",
                "Residual cash: not changed; no trade ledger mutation; no candidate funding authority.",
                ("h", "4. Allocation and concentration summary"),
                "Allocation: 100% cash placeholder because no UCITS ETF is funded under current authority.",
                "Concentration risk: no market exposure concentration; process risk is evidence incompleteness.",
                "Next risk control: content-complete build must remain visibly blocked until source/freshness gates pass.",
                ("h", "7. Holding-level decision table"),
                "Cash | action=hold_cash | thesis=preserve authority boundary | invalidation=explicit funding decision later.",
                "CSPX/SXR8 | action=review_candidate | thesis=core U.S. equity UCITS candidate | invalidation=pricing/KID/line gap.",
                "SMH UCITS | action=watch | thesis=semiconductor exposure candidate | invalidation=verification incomplete.",
                "Gold ETC | action=blocked_policy_review | thesis=hedge reference | invalidation=not UCITS ETF under current policy.",
            ],
        ),
        _render_page(
            "ETF EU Cockpit Content-Complete Candidate",
            "Input/state and investability evidence - review-only, no live refresh",
            [
                ("h", "5. UCITS investability table"),
                "IE00B5BMR087 | iShares Core S&P 500 UCITS ETF | provider=iShares/BlackRock | UCITS=confirmed | KID=available.",
                "Trading line: SXR8.DE | exchange=Xetra | currency=EUR | pricing_symbol=SXR8.DE | status=verified_candidate_not_funded.",
                "IE00BMC38736 | VanEck Semiconductor UCITS ETF | provider=VanEck | UCITS=confirmed_by_name | KID=available.",
                "Trading line: SMH | exchange=pending_verification | currency=USD | pricing_symbol=pending_verification.",
                "TBD | iShares Physical Gold ETC | provider=iShares/BlackRock | UCITS=not_ucits_etc | status=blocked_policy_review.",
                ("h", "6. Pricing and freshness evidence table"),
                "CSPX/SXR8 | latest_close_date=not_fetched_in_WP15R | latest_close=not_fetched_in_WP15R.",
                "CSPX/SXR8 | pricing_source=not_refreshed_in_WP15R | pricing_freshness_status=unresolved_for_review_candidate.",
                "SMH UCITS | latest_close_date=not_fetched_in_WP15R | latest_close=not_fetched_in_WP15R.",
                "Gold ETC | pricing not relevant to UCITS-only funding until policy permits ETC exposure.",
                "Disclosure: WP15R performs no live_data_fetch and creates no pricing_evidence_changed authority.",
                ("h", "8. Watchlist and candidate pipeline with promotion status"),
                "CSPX / SXR8 | pipeline=core_equity_candidate | promotion_status=not_promoted | required_next=pricing/KID/line freshness.",
                "SMH UCITS | pipeline=thematic_candidate | promotion_status=not_promoted | required_next=full exchange-line verification.",
                "INFR candidate | pipeline=infrastructure_placeholder | promotion_status=not_promoted | required_next=issuer/ISIN/KID verification.",
                "Gold ETC | pipeline=hedge_reference | promotion_status=blocked | required_next=policy decision on ETC eligibility.",
                ("h", "Minimum visible fields for funded or investable rows"),
                "isin | fund_name | provider | ucits_status | priips_kid_status | exchange_ticker | trading_currency | primary_exchange",
                "pricing_symbol | latest_close_date | latest_close | pricing_source | pricing_freshness_status | ter_or_cost_status",
                "replication_method_or_unknown | distribution_policy_or_unknown | hedged_unhedged_or_unknown",
            ],
        ),
        _render_page(
            "ETF EU Cockpit Content-Complete Candidate",
            "Risk, proxy disclosure, unresolved data and governance footer",
            [
                ("h", "9. Risk, regime and event context"),
                "Market/regime context: not refreshed in WP15R; this candidate is format/content completeness only.",
                "Risk posture: avoid funded exposure until UCITS pricing, freshness, KID, liquidity and source gates are satisfied.",
                "Event context: omitted as live macro/calendar fetch is outside WP15R authority.",
                ("h", "10. Proxy and benchmark disclosure"),
                "U.S. ETFs SPY, SMH, GLD and PAVE are research proxies / benchmark comparators only.",
                "U.S. ETFs are not EU portfolio holdings and must not be displayed as Dutch/EU-investable funded instruments.",
                "All investable instruments must remain ISIN-first and UCITS-first unless policy explicitly changes.",
                ("h", "11. Unresolved-data and limitation block"),
                "Unresolved: live pricing not fetched, valuation-grade evidence not created, portfolio not revalued.",
                "Unresolved: KID/TER/liquidity/replication gaps remain review-needed where registry marks pending_verification.",
                "Unresolved: Dutch language quality and bilingual parity gates not run against this candidate.",
                "Limitation: content-complete candidate build is not client-grade delivery and not delivery-preflight authority.",
                ("h", "12. Validation and governance footer"),
                "Required validators: content_completeness, no_us_etf_as_eu_holding, isin_first_holdings, ucits_status_present.",
                "Required validators: priips_kid_status_present, pricing_source_and_freshness_present, proxy_disclosure_present.",
                "Required validators: unresolved_data_block_present, delivery_boundary_markers_present.",
                "Output contract status: all 12 visible sections are present in this review-only candidate PDF.",
                "Authority: delivery_authorization_decision=remain_blocked | delivery_preflight_allowed=false | outbound_path_enabled=false.",
                "Artifacts: build artifact + notes + validator + tests; selected_next_package=ETF-EU-WP15S.",
            ],
        ),
    ]


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
    print(f"ETF_EU_COCKPIT_PDF_CONTENT_COMPLETE_CANDIDATE_BUILT | pdf={OUTPUT}")


if __name__ == "__main__":
    main()
