from __future__ import annotations

from pathlib import Path

from tools.validate_etf_eu_output_contract import validate

EN_REPORT = """# Weekly ETF EU Review 2026-06-18

cash-only bootstrap
Funded UCITS holdings: none
research proxies only
require ISIN, KID/PRIIPs and trading-line verification
Production delivery: disabled
No PDF rendering, portfolio execution or email delivery was performed

## Production report maturity
Dutch report is the primary client report
companion/operator-facing version
no funded UCITS holdings
no buy recommendation
no portfolio mutation
no production delivery
no delivery receipt
fundability gate status visible
candidate_promotion=false
"""

NL_REPORT = """# Weekly ETF EU Review Nederlands 2026-06-18

cash-only bootstrap
Gefinancierde UCITS-posities: geen
alleen onderzoeksproxy
vereisen ISIN-, KID-/PRIIPs- en handelslijnverificatie
Productielevering: uitgeschakeld
geen PDF-rendering, portefeuille-executie of e-mailverzending uitgevoerd

## Productierapport-volwassenheid
Nederlandse hoofdrapportage
primaire clientrapportage
Engelse rapportage is companion/operator-facing
geen gefinancierde UCITS-posities
geen koopadvies
geen portefeuille-mutatie
geen productielevering
geen delivery receipt
fundability gate status zichtbaar
candidate_promotion=false
"""


def test_report_suffix_validation_ignores_non_canonical_draft_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "weekly_etf_eu_review_260618.md").write_text(EN_REPORT, encoding="utf-8")
    (output_dir / "weekly_etf_eu_review_nl_260618.md").write_text(NL_REPORT, encoding="utf-8")
    (output_dir / "weekly_etf_eu_review_260618_draft.md").write_text("legacy draft", encoding="utf-8")

    validate(output_dir, require_production_dutch_first=True, report_suffix="260618")
