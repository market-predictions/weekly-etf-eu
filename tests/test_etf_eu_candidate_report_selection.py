from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_candidate_report import validate

EN_REPORT = """# Weekly ETF EU Review 2026-07-08

UCITS candidate registry
not a portfolio
not a buy recommendation
not valuation authority
not funded; no valuation authority
Pricing preflight: non-authoritative connectivity test
CSPX not funded; no valuation authority
"""

NL_REPORT = """# Weekly ETF EU Review Nederlands 2026-07-08

UCITS-kandidatenregister
geen portefeuille
geen koopadvies
geen waarderingsautoriteit
niet gefinancierd; geen waarderingsautoriteit
Pricing-preflight: niet-autoritatieve connectiviteitstest
CSPX niet gefinancierd; geen waarderingsautoriteit
"""


def test_candidate_report_validator_ignores_non_canonical_drafts_and_selects_latest_pair(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "weekly_etf_eu_review_260618_draft.md").write_text("legacy draft without required phrases", encoding="utf-8")
    (output_dir / "weekly_etf_eu_review_260618_mature_draft.md").write_text("legacy mature draft without required phrases", encoding="utf-8")
    (output_dir / "weekly_etf_eu_review_nl_260618_mature_draft.md").write_text("legacy mature draft without required phrases", encoding="utf-8")
    (output_dir / "weekly_etf_eu_review_260708.md").write_text(EN_REPORT, encoding="utf-8")
    (output_dir / "weekly_etf_eu_review_nl_260708.md").write_text(NL_REPORT, encoding="utf-8")

    validate(output_dir)


def test_candidate_report_validator_can_filter_requested_suffix(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "weekly_etf_eu_review_260708.md").write_text(EN_REPORT, encoding="utf-8")
    (output_dir / "weekly_etf_eu_review_nl_260708.md").write_text(NL_REPORT, encoding="utf-8")
    (output_dir / "weekly_etf_eu_review_260708_draft.md").write_text("draft without required phrases", encoding="utf-8")

    validate(output_dir, report_suffix="260708")
